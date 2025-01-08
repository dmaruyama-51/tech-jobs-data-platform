from func_scraper.utils.models import JobBasicData, JobListData, JobTableData


def test_job_list_data_creation():
    """JobListDataの作成と属性アクセスをテスト

    検証内容:
    1. 必須フィールドで正しくインスタンス化できること
    2. 各属性に正しくアクセスできること
    """
    data = JobListData(
        job_title="Python開発者",
        listing_start_date="2024年3月1日",
        detail_link="/jobs/123",
    )

    assert data.job_title == "Python開発者"
    assert data.listing_start_date == "2024年3月1日"
    assert data.detail_link == "/jobs/123"


def test_job_basic_data_creation():
    """JobBasicDataの作成と属性アクセスをテスト

    検証内容:
    1. 必須フィールドで正しくインスタンス化できること
    2. 各属性に正しくアクセスできること
    """
    data = JobBasicData(
        monthly_salary=500000,
        occupation="システムエンジニア",
        work_type="正社員",
        work_location="東京都",
        industry="IT・通信",
    )

    assert data.monthly_salary == 500000
    assert data.occupation == "システムエンジニア"
    assert data.work_type == "正社員"
    assert data.work_location == "東京都"
    assert data.industry == "IT・通信"


def test_job_table_data_creation():
    """JobTableDataの作成と属性アクセスをテスト

    検証内容:
    1. オプショナルフィールドがNoneでも作成できること
    2. 一部のフィールドのみで作成できること
    3. 全フィールドで作成できること
    """
    # 全てデフォルト値（None）で作成
    data1 = JobTableData()
    assert data1.job_content is None
    assert data1.required_skills is None

    # 一部のフィールドのみ指定
    data2 = JobTableData(
        job_content="Webアプリケーション開発", required_skills="Python, SQL"
    )
    assert data2.job_content == "Webアプリケーション開発"
    assert data2.required_skills == "Python, SQL"
    assert data2.preferred_skills is None  # 未指定フィールド

    # 全フィールドを指定
    data3 = JobTableData(
        job_content="Webアプリケーション開発",
        required_skills="Python, SQL",
        preferred_skills="AWS",
        programming_language="Python",
        tool="VSCode",
        framework="Django",
        rate_of_work="100%",
        number_of_recruitment_interviews="2回",
        number_of_days_worked="週5日",
        number_of_applicants="10名",
    )
    assert data3.framework == "Django"
    assert data3.rate_of_work == "100%"
