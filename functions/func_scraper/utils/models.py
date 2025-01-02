from dataclasses import dataclass
from typing import Optional


@dataclass
class JobListData:
    """求人一覧ページのデータを格納するデータクラス"""

    job_title: str
    listing_start_date: str
    detail_link: str


@dataclass
class JobBasicData:
    """求人詳細ページの基本情報を格納するデータクラス"""

    monthly_salary: int
    occupation: str
    work_type: str
    work_location: str
    industry: str


@dataclass
class JobTableData:
    """求人詳細ページのテーブルデータを格納するデータクラス"""

    job_content: Optional[str] = None
    required_skills: Optional[str] = None
    preferred_skills: Optional[str] = None
    programming_language: Optional[str] = None
    tool: Optional[str] = None
    framework: Optional[str] = None
    rate_of_work: Optional[str] = None
    number_of_recruitment_interviews: Optional[str] = None
    number_of_days_worked: Optional[str] = None
    number_of_applicants: Optional[str] = None
