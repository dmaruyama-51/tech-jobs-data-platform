import functions_framework
from flask import jsonify
import pandas as pd
from utils.scraper import JobListScraper, JobDetailScraper
from utils.parsers import JobDataParser
from utils.http_client import HttpClient
from shared.logger_config import setup_logger
from google.cloud import storage
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class JobScrapingService:
    """スクレイピング全体の制御を担当"""

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

            detail_df_list = []
            total = len(list_df.detail_link)

            self.logger.info(f"Starting detail page scraping for {total} jobs")
            for i, url in enumerate(list_df.detail_link, 1):
                self.logger.info(f"Scraping detail page {i}/{total}")
                detail_df = self.detail_scraper.scrape_detail(url)
                detail_df_list.append(detail_df)

            final_df = pd.concat(detail_df_list)
            self.logger.info("Scraping completed successfully")
            return final_df

        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}", exc_info=True)
            raise


def save_to_gcs(df: pd.DataFrame, bucket_name: str) -> str:
    """DataFrameをGCSにCSV形式で保存し、同じ日の古いファイルを削除"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # 日付のみのパーティションフォルダを使用
    partition_date = datetime.now().strftime("%Y%m%d")
    blob_name = f"raw/jobs/partition_date={partition_date}/jobs.csv"

    # 保存前に同じ日の古いファイルを削除
    prefix = f"raw/jobs/partition_date={partition_date}/"
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        blob.delete()

    # 新しいデータを保存
    blob = bucket.blob(blob_name)
    with blob.open("w") as f:
        df.to_csv(f, index=False, encoding="utf-8")

    return blob_name


def get_data_bucket_name() -> str:
    """スクレイピングデータ保存用のバケット名を生成"""
    project_id = os.environ.get("PROJECT_ID")
    if not project_id:
        raise ValueError("Environment variable PROJECT_ID is not set")
    return f"{project_id}-scraping-data"


@functions_framework.http
def scraping(request):
    """Cloud Functions のエントリーポイント"""
    try:
        service = JobScrapingService("2024-12-27")
        final_df = service.execute()

        # project_idから動的にバケット名を生成
        bucket_name = get_data_bucket_name()
        saved_path = save_to_gcs(final_df, bucket_name)

        return jsonify(
            {
                "status": "success",
                "message": f"Data saved to gs://{bucket_name}/{saved_path}",
                "record_count": len(final_df),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # ローカルテスト用
    service = JobScrapingService()
    final_df = service.execute()
    print(final_df)
