import functions_framework
from flask import jsonify
import pandas as pd
from utils.scraper import JobListScraper, JobDetailScraper
from utils.parsers import JobDataParser
from utils.http_client import HttpClient
from shared.logger_config import setup_logger
from shared.gcs import save_to_gcs, get_data_bucket_name
from shared.date_utils import get_yesterday_jst
from dotenv import load_dotenv
import os

# 環境変数でエンコーディングを設定
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "ja_JP.UTF-8"

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
def scraping(request):
    """Cloud Functions のエントリーポイント"""
    try:
        # リクエストからlimit_dateを取得（指定がない場合は昨日の日付を使用）
        request_json = request.get_json() if request.is_json else {}
        limit_date = request_json.get(
            "limit_date", get_yesterday_jst().strftime("%Y-%m-%d")
        )

        service = JobScrapingService(limit_date)
        final_df = service.execute()

        bucket_name = get_data_bucket_name()
        saved_path = save_to_gcs(final_df, bucket_name)

        return jsonify(
            {
                "status": "success",
                "message": f"Data saved to gs://{bucket_name}/{saved_path}",
                "record_count": len(final_df),
                "limit_date": limit_date,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
