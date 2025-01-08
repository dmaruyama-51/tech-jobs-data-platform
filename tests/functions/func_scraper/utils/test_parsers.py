import pandas as pd
import pytest
from func_scraper.utils.parsers import JobDataParser


@pytest.fixture
def list_page_html():
    """一覧ページのHTMLフィクスチャ"""
    return """
    <html>
        <div class="job-Title">Python開発者募集</div>
        <div class="time-Stamp">掲載開始日：2024年3月1日</div>
        <li class="detail-Btn02"><a href="/jobs/123">詳細</a></li>
    </html>
    """


@pytest.fixture
def detail_page_html():
    """詳細ページのHTMLフィクスチャ"""
    return """
    <html>
        <div class="job-Box">
            <ul>
                <li>〜500000円</li>
                <li>システムエンジニア</li>
                <li>正社員</li>
                <li>東京都</li>
                <li>IT・通信</li>
            </ul>
        </div>
        <table>
            <tr><th>案件内容</th><td>Webアプリケーション開発</td></tr>
            <tr><th>必須スキル</th><td>Python, SQL</td></tr>
            <tr><th>言語</th><td>Python</td></tr>
        </table>
    </html>
    """


def test_parse_list_page(mocker, list_page_html):  # フィクスチャを引数として受け取る
    """一覧ページのパース処理をテスト"""
    parser = JobDataParser()
    mock_response = mocker.Mock()
    mock_response.content = list_page_html  # 直接呼び出さない

    df = parser.parse_list_page(mock_response)

    assert len(df) == 1
    assert df.iloc[0]["job_title"] == "Python開発者募集"
    assert df.iloc[0]["detail_link"] == "/jobs/123"
    assert (
        pd.to_datetime(df.iloc[0]["listing_start_date"]).strftime("%Y-%m-%d")
        == "2024-03-01"
    )


def test_parse_detail_page(
    mocker, detail_page_html
):  # フィクスチャを引数として受け取る
    """詳細ページのパース処理をテスト"""
    parser = JobDataParser()
    mock_response = mocker.Mock()
    mock_response.content = detail_page_html  # 直接呼び出さない

    df = parser.parse_detail_page(mock_response)

    assert df.iloc[0]["monthly_salary"] == 500000
    assert df.iloc[0]["occupation"] == "システムエンジニア"
    assert df.iloc[0]["work_type"] == "正社員"
    assert df.iloc[0]["work_location"] == "東京都"
    assert df.iloc[0]["industry"] == "IT・通信"
    assert df.iloc[0]["job_content"] == "Webアプリケーション開発"
    assert df.iloc[0]["required_skills"] == "Python, SQL"
    assert df.iloc[0]["programming_language"] == "Python"
