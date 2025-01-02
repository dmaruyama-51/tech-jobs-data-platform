from bs4 import BeautifulSoup
from utils.models import JobTableData, JobBasicData, JobListData
import pandas as pd
from typing import List, Dict
import requests
from shared.logger_config import setup_logger


class JobDataParser:
    """HTMLパーサー"""

    def __init__(self):
        self.logger = setup_logger("job_parser")

    def parse_list_page(self, html_content: requests.Response) -> pd.DataFrame:
        """一覧ページのパース"""
        self.logger.info("Parsing list page")
        soup = BeautifulSoup(html_content.content, "html.parser", from_encoding='utf-8')
        
        # 各要素を個別に取得
        job_titles = self._extract_job_titles(soup)
        listing_dates = self._extract_listing_dates(soup)
        detail_links = self._extract_detail_links(soup)
        
        # 各要素をリストとしてDataFrameを作成
        job_list_data = [
            JobListData(
                job_title=title,
                listing_start_date=date,
                detail_link=link
            )
            for title, date, link in zip(job_titles, listing_dates, detail_links)
        ]
        
        df = pd.DataFrame([vars(data) for data in job_list_data])
        
        # 掲載開始日を日付型に変換
        df["listing_start_date"] = pd.to_datetime(
            df["listing_start_date"].tolist(),
            format="%Y年%m月%d日"
        )

        self.logger.info(f"Found {len(df)} jobs in list page")
        return df

    def parse_detail_page(self, html_content: requests.Response) -> pd.DataFrame:
        """詳細ページのパース"""
        self.logger.info("Parsing detail page")
        try:
            soup = BeautifulSoup(html_content.content, "html.parser")
            basic_info = self._extract_basic_info(soup)
            table_info = self._extract_table_info(soup)
            return pd.concat([basic_info, table_info], axis=1)
        except Exception as e:
            self.logger.error(f"Error parsing detail page: {str(e)}")
            raise

    def _extract_job_titles(self, soup: BeautifulSoup) -> List[str]:
        """求人タイトルを抽出"""
        return [
            job_title_element.text.strip()
            for job_title_element in soup.find_all(class_="job-Title")
        ]

    def _extract_listing_dates(self, soup: BeautifulSoup) -> List[str]:
        """掲載開始日を抽出"""
        # 6文字目以降を取得するのは、「掲載開示日：」を削除するため
        return [
            date_element.text.strip()[6:]
            for date_element in soup.find_all(class_="time-Stamp")
        ]

    def _extract_detail_links(self, soup: BeautifulSoup) -> List[str]:
        """詳細ページのURLを抽出"""
        return [
            li_element.find("a")["href"]
            for li_element in soup.find_all(class_="detail-Btn02")
        ]

    def _extract_basic_info(self, soup: BeautifulSoup) -> pd.DataFrame:
        """基本情報を抽出"""
        self.logger.info("Extracting basic info")
        elements = [
            li_elements.text.strip()
            for li_elements in soup.find(class_="job-Box").find("ul").find_all("li")
        ]

        basic_data = JobBasicData(
            monthly_salary=self._transform_salary(elements[0]),
            occupation=elements[1],
            work_type=elements[2],
            work_location=elements[3],
            industry=elements[4],
        )

        return pd.DataFrame([vars(basic_data)])

    def _extract_table_info(self, soup: BeautifulSoup) -> pd.DataFrame:
        """テーブル情報を抽出"""
        self.logger.info("Extracting table info")
        rows: Dict[str, List[str]] = {"th": [], "td": []}
        for row in soup.find("table").find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            rows["th"].append(th.text.strip())
            rows["td"].append(td.text.strip())
        table_df = pd.DataFrame(rows)
        table_df.index = table_df.th

        table_data = JobTableData(
            job_content=table_df.loc["案件内容", "td"]
            if "案件内容" in table_df.index
            else None,
            required_skills=table_df.loc["必須スキル", "td"]
            if "必須スキル" in table_df.index
            else None,
            preferred_skills=table_df.loc["尚可スキル", "td"]
            if "尚可スキル" in table_df.index
            else None,
            programming_language=table_df.loc["言語", "td"]
            if "言語" in table_df.index
            else None,
            tool=table_df.loc["環境・ツール", "td"]
            if "環境・ツール" in table_df.index
            else None,
            framework=table_df.loc["フレームワーク・ライブラリ", "td"]
            if "フレームワーク・ライブラリ" in table_df.index
            else None,
            rate_of_work=table_df.loc["稼働率", "td"]
            if "稼働率" in table_df.index
            else None,
            number_of_recruitment_interviews=table_df.loc["面談回数", "td"]
            if "面談回数" in table_df.index
            else None,
            number_of_days_worked=table_df.loc["稼働日数", "td"]
            if "稼働日数" in table_df.index
            else None,
            number_of_applicants=table_df.loc["募集人数", "td"]
            if "募集人数" in table_df.index
            else None,
        )

        return pd.DataFrame([vars(table_data)])

    def _transform_salary(self, salary_text: str) -> int:
        """月給のテキストを数値に変換"""
        salary_num = int("".join(filter(str.isdigit, salary_text)))
        return salary_num
