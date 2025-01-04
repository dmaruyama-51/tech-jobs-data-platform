import pytest
import pandas as pd
from func_scraper.utils.scraper import JobListScraper, JobDetailScraper


@pytest.fixture
def mock_http_client(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_parser(mocker):
    return mocker.Mock()


@pytest.fixture
def list_scraper(mock_http_client, mock_parser):
    return JobListScraper(mock_http_client, mock_parser)


@pytest.fixture
def detail_scraper(mock_http_client, mock_parser):
    return JobDetailScraper(mock_http_client, mock_parser)


def test_scrape_page(list_scraper, mock_http_client, mock_parser):
    """1ページ分の求人一覧取得をテスト
    1. 正しいURLでGETリクエストが行われること (/item/page/1/?sort=new)
    2. 取得したレスポンスがパーサーに渡されること
    3. パーサーの結果がそのまま返されること
    """
    # モックの戻り値を設定
    mock_response = "dummy_response"
    mock_http_client.get.return_value = mock_response
    expected_df = pd.DataFrame({"job_title": ["Python開発者"]})
    mock_parser.parse_list_page.return_value = expected_df

    # テスト実行
    result = list_scraper.scrape_page(1)

    # 検証
    mock_http_client.get.assert_called_once_with("/item/page/1/?sort=new")
    mock_parser.parse_list_page.assert_called_once_with(mock_response)
    pd.testing.assert_frame_equal(result, expected_df)


def test_scrape_all_pages(list_scraper, mock_http_client, mock_parser):
    """全ページのスクレイピングをテスト
    1. 日付による取得制限が機能すること
       - limit_date以降のデータのみが含まれること
    2. 古いデータを検出した時点でスクレイピングが終了すること
       - 1ページ目で古いデータを検出した場合、2ページ目以降は取得しないこと
    3. DataFrameの結合と日付フィルタリングが正しく行われること
    """
    # モックの戻り値を設定
    mock_df = pd.DataFrame(
        {"listing_start_date": [pd.Timestamp("2025-01-05"), pd.Timestamp("2024-12-28")]}
    )
    mock_parser.parse_list_page.return_value = mock_df

    # テスト実行
    limit_date = pd.Timestamp("2025-01-01")
    result = list_scraper.scrape_all_pages(limit_date, sleep_time=0)

    # 検証
    assert len(result) == 1  # limit_date以降のデータのみ
    assert mock_http_client.get.call_count == 1  # 1ページ目で終了


def test_scrape_detail(detail_scraper, mock_http_client, mock_parser):
    """詳細ページのスクレイピングをテスト
    1. 指定されたURLで正確にGETリクエストが行われること
    2. 取得したレスポンスがパーサーに渡されること
    3. パーサーの結果がそのまま返されること
    """
    # モックの戻り値を設定
    mock_response = "dummy_response"
    mock_http_client.get.return_value = mock_response
    expected_df = pd.DataFrame({"monthly_salary": [500000]})
    mock_parser.parse_detail_page.return_value = expected_df

    # テスト実行
    result = detail_scraper.scrape_detail("https://example.com/job/1", sleep_time=0)

    # 検証
    mock_http_client.get.assert_called_once_with("https://example.com/job/1")
    mock_parser.parse_detail_page.assert_called_once_with(mock_response)
    pd.testing.assert_frame_equal(result, expected_df)
