import functions_framework
from flask import jsonify
import pandas as pd
from utils.scraper import JobListScraper, JobDetailScraper
from utils.parsers import JobDataParser
from utils.http_client import HttpClient
from shared.logger_config import setup_logger


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

@functions_framework.http
def scraping(request):
    """Cloud Functions のエントリーポイント"""
    try:
        service = JobScrapingService("2024-12-27")
        final_df = service.execute()
        result = final_df.to_dict(orient='records')
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    # ローカルテスト用
    service = JobScrapingService()
    final_df = service.execute()
    print(final_df)