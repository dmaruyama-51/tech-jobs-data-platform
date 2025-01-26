import pytest
from func_scraper.utils.http_client import HttpClient
from requests.exceptions import RequestException


def test_get_with_absolute_url(mocker):
    """絶対URLでのGETリクエストをテスト"""
    # google-cloud-logging の初期化をモック化
    mocker.patch("google.cloud.logging.Client")

    mock_response = mocker.Mock()
    mock_response.encoding = None
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    client = HttpClient("https://example.com")
    url = "https://another-example.com/path"
    client.get(url)

    # 最後のコールのみを検証
    assert mock_get.call_args_list[-1] == mocker.call(url)


def test_get_with_relative_url(mocker):
    """相対URLでのGETリクエストをテスト"""
    # google-cloud-logging の初期化をモック化
    mocker.patch("google.cloud.logging.Client")

    mock_response = mocker.Mock()
    mock_response.encoding = None
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    base_url = "https://example.com"
    path = "/api/data"
    client = HttpClient(base_url)
    client.get(path)

    expected_url = f"{base_url}{path}"
    # 最後のコールのみを検証
    assert mock_get.call_args_list[-1] == mocker.call(expected_url)


def test_get_request_error(mocker):
    """リクエストエラーのハンドリングをテスト"""
    mocker.patch("requests.get", side_effect=RequestException("Network error"))

    client = HttpClient("https://example.com")

    with pytest.raises(RequestException) as exc_info:
        client.get("/test")

    assert "Network error" in str(exc_info.value)
