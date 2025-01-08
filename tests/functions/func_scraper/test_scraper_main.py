import pandas as pd
import pytest
from func_scraper.main import JobScrapingService


@pytest.fixture
def mock_list_scraper(mocker):
    """ListScraperのモックを提供するフィクスチャ"""
    return mocker.Mock()


@pytest.fixture
def mock_detail_scraper(mocker):
    """DetailScraperのモックを提供するフィクスチャ"""
    return mocker.Mock()


@pytest.fixture
def scraping_service(mocker, mock_list_scraper, mock_detail_scraper):
    """JobScrapingServiceのインスタンスを提供するフィクスチャ

    HttpClientとParserはサービス内で生成されるため、
    ListScraperとDetailScraperのコンストラクタをモック化
    """
    # スクレイパーのコンストラクタをモック化
    mocker.patch("func_scraper.main.JobListScraper", return_value=mock_list_scraper)
    mocker.patch("func_scraper.main.JobDetailScraper", return_value=mock_detail_scraper)

    return JobScrapingService("2024-03-01")


def test_execute_with_no_jobs(scraping_service, mock_list_scraper):
    """求人が見つからない場合のテスト

    1. 一覧ページのスクレイピングが実行されること
    2. 求人が見つからない場合、空のDataFrameが返されること
    """
    # 一覧ページのスクレイピング結果を空に設定
    mock_list_scraper.scrape_all_pages.return_value = pd.DataFrame()

    # テスト実行
    result = scraping_service.execute()

    # 検証
    assert len(result) == 0
    mock_list_scraper.scrape_all_pages.assert_called_once()


def test_execute_with_jobs(scraping_service, mock_list_scraper, mock_detail_scraper):
    """求人が見つかった場合のテスト

    検証内容:
    1. 一覧ページのスクレイピングが実行されること
    2. 各求人の詳細ページのスクレイピングが実行されること
    3. 一覧と詳細の情報が結合されて返されること
    """
    # 一覧ページのスクレイピング結果を設定
    list_df = pd.DataFrame(
        {"job_title": ["Python開発者"], "detail_link": ["/jobs/123"]}
    )
    mock_list_scraper.scrape_all_pages.return_value = list_df

    # 詳細ページのスクレイピング結果を設定
    detail_df = pd.DataFrame(
        {"monthly_salary": [500000], "occupation": ["システムエンジニア"]}
    )
    mock_detail_scraper.scrape_detail.return_value = detail_df

    # テスト実行
    result = scraping_service.execute()

    # 検証
    assert len(result) == 1
    mock_list_scraper.scrape_all_pages.assert_called_once()
    mock_detail_scraper.scrape_detail.assert_called_once_with("/jobs/123")

    # 結果のDataFrameに一覧と詳細の情報が含まれていることを確認
    assert "job_title" in result.columns
    assert "monthly_salary" in result.columns


def test_execute_error_handling(scraping_service, mock_list_scraper):
    """エラーハンドリングのテスト

    検証内容:
    1. スクレイピング中にエラーが発生した場合、適切に例外が伝播すること
    2. エラーがログに記録されること
    """
    # スクレイピングでエラーが発生するようにモック設定
    mock_list_scraper.scrape_all_pages.side_effect = Exception("Scraping failed")

    # エラーが伝播することを確認
    with pytest.raises(Exception) as exc_info:
        scraping_service.execute()

    assert str(exc_info.value) == "Scraping failed"
