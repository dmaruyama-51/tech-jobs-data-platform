import pytest
from func_scraper.utils.http_client import HttpClient
from requests.exceptions import RequestException

def test_get_with_absolute_url(mocker):
    """絶対URLでのGETリクエストをテスト"""
    mock_response = mocker.Mock()
    mock_response.encoding = None
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    client = HttpClient('https://example.com')
    url = 'https://another-example.com/path'
    client.get(url)
    
    mock_get.assert_called_once_with(url)
    assert mock_response.encoding == 'utf-8'

def test_get_with_relative_url(mocker):
    """相対URLでのGETリクエストをテスト"""
    mock_response = mocker.Mock()
    mock_response.encoding = None
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    base_url = 'https://example.com'
    path = '/api/data'
    client = HttpClient(base_url)
    client.get(path)
    
    expected_url = f'{base_url}{path}'
    mock_get.assert_called_once_with(expected_url)
    assert mock_response.encoding == 'utf-8'

def test_get_request_error(mocker):
    """リクエストエラーのハンドリングをテスト"""
    mock_get = mocker.patch('requests.get', side_effect=RequestException('Network error'))
    
    client = HttpClient('https://example.com')
    
    with pytest.raises(RequestException):
        client.get('/api/data') 