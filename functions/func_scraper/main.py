import os
from datetime import datetime
from typing import Tuple

import functions_framework
import pandas as pd
from dotenv import load_dotenv
from flask import Request, jsonify
from flask.wrappers import Response
from shared.date_utils import get_yesterday_jst
from shared.gcs_utils import get_data_bucket_name, save_to_gcs
from shared.logger_config import setup_logger
from shared.pubsub_utils import MessageProcessor, is_valid_pubsub_message
from utils.http_client import HttpClient
from utils.parsers import JobDataParser
from utils.scraper import JobDetailScraper, JobListScraper

# 環境変数でエンコーディングを設定
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "ja_JP.UTF-8"

logger = setup_logger("job_scraper_main")

load_dotenv()


class JobScrapingService:
    """スクレイピング全体の制御"""

    def __init__(self, scrape_limit_date: str = "2024-12-27"):
        self.logger = setup_logger("job_scraper")
        http_client = HttpClient("https://www.bigdata-navi.com")
        parser = JobDataParser()
        self.list_scraper = JobListScraper(http_client, parser)
        self.detail_scraper = JobDetailScraper(http_client, parser)
        self.scrape_limit_date = pd.to_datetime(scrape_limit_date)
        self.logger.info(
            f"Initialized scraping service with limit date: {scrape_limit_date}"
        )

    def execute(self) -> pd.DataFrame:
        """スクレイピングを実行"""
        try:
            self.logger.info("Starting job list scraping")
            list_df = self.list_scraper.scrape_all_pages(self.scrape_limit_date)
            self.logger.info(f"Found {len(list_df)} jobs in list pages")

            # リストが空の場合は空のDataFrameを返す
            if len(list_df) == 0:
                self.logger.info("No new jobs found within the date range")
                return pd.DataFrame()

            detail_df_list = []
            total = len(list_df.detail_link)

            self.logger.info(f"Starting detail page scraping for {total} jobs")
            for i, url in enumerate(list_df.detail_link, 1):
                self.logger.info(f"Scraping detail page {i}/{total}")
                detail_df = self.detail_scraper.scrape_detail(url)
                detail_df = pd.concat(
                    [detail_df, list_df.iloc[[i - 1]].reset_index(drop=True)], axis=1
                )
                detail_df_list.append(detail_df)

            # detail_df_listが空でない場合のみconcatを実行
            if detail_df_list:
                final_df = pd.concat(detail_df_list)
                self.logger.info("Scraping completed successfully")
                return final_df
            else:
                self.logger.info("No detail pages were scraped")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}", exc_info=True)
            raise


@functions_framework.http
def scraping(request: Request) -> Tuple[Response, int]:
    """Cloud Functions のエントリーポイント"""
    try:
        # Pub/Subメッセージの検証
        if not is_valid_pubsub_message(request):
            # 不正なメッセージの場合は200を返して処理を終了
            # ref) https://stackoverflow.com/questions/76669801/avoid-infinite-pubsub-loop-when-cloud-run-returns-an-error
            return jsonify(
                {"status": "invalid", "message": "Invalid Pub/Sub message format"}
            ), 200

        # ==============================================
        # 無限ループを防ぐため, message_idが処理済みかチェック
        # ==============================================

        # メッセージIDの取得
        message = request.get_json()["message"]
        message_id = message.get("messageId")

        # MessageProcessorの初期化
        bucket_name = get_data_bucket_name()
        processor = MessageProcessor(bucket_name)

        # べき等性チェック
        if processor.is_message_processed(message_id):
            logger.info(f"Message {message_id} has already been processed. Skipping.")
            return jsonify(
                {"status": "skipped", "message": "Message already processed"}
            ), 200

        # ==============================================
        # スクレイピング実行
        # ==============================================

        # 昨日の日付を使用
        limit_date = get_yesterday_jst().strftime("%Y-%m-%d")

        try:
            service = JobScrapingService(limit_date)
            final_df = service.execute()

            bucket_name = get_data_bucket_name()
            saved_path = save_to_gcs(final_df, bucket_name)

            # 処理成功時にメッセージを処理済みとしてマーク
            processor.mark_message_as_processed(
                message_id,
                {
                    "limit_date": limit_date,
                    "record_count": len(final_df),
                    "saved_path": saved_path,
                    "processed_at": datetime.utcnow().isoformat(),
                },
            )

            return jsonify(
                {
                    "status": "success",
                    "message": f"Data saved to gs://{bucket_name}/{saved_path}",
                    "record_count": len(final_df),
                    "limit_date": limit_date,
                }
            ), 200

        except Exception as e:
            # 処理中のエラーでも200を返してPub/Subの再試行を防ぐ
            logger.error(f"Error during scraping: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 200

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        return jsonify(
            {"status": "critical_error", "message": str(e)}
        ), 200  # すべてのケースで200を返す
