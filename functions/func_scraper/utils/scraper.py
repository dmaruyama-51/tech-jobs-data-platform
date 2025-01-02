import pandas as pd
from utils.parsers import JobDataParser
from utils.http_client import HttpClient
import time


class JobListScraper:
    """求人一覧ページのスクレイピング"""

    def __init__(self, http_client: HttpClient, parser: JobDataParser):
        self.http_client = http_client
        self.parser = parser

    def scrape_all_pages(
        self, scrape_limit_date: pd.Timestamp, sleep_time: int = 5
    ) -> pd.DataFrame:
        """すべての一覧ページをスクレイピング"""
        job_df_list = []
        for page_num in range(1, 100):
            list_df = self.scrape_page(page_num)
            job_df_list.append(list_df)

            if list_df.listing_start_date.min() < scrape_limit_date:
                break
            else:
                print(f"page {page_num} is not less than {scrape_limit_date}")
                time.sleep(sleep_time)  # ページ間のスリープ

        return pd.concat(job_df_list).query("listing_start_date >= @scrape_limit_date")

    def scrape_page(self, page_num: int) -> pd.DataFrame:
        """1ページ分の求人一覧を取得"""
        response = self.http_client.get(f"/item/page/{page_num}/?sort=new")
        return self.parser.parse_list_page(response)


class JobDetailScraper:
    """求人詳細ページのスクレイピング"""

    def __init__(self, http_client: HttpClient, parser: JobDataParser):
        self.http_client = http_client
        self.parser = parser

    def scrape_detail(self, url: str, sleep_time: int = 3) -> pd.DataFrame:
        """詳細ページの情報を取得"""
        response = self.http_client.get(url)
        result = self.parser.parse_detail_page(response)
        time.sleep(sleep_time)  # 詳細ページ取得後のスリープ
        return result
