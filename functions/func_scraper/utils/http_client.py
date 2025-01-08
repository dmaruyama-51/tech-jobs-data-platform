from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException
from shared.logger_config import setup_logger


class HttpClient:
    """HTTPリクエスト"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = setup_logger("http_client")

    def get(self, path: str) -> requests.Response:
        """GETリクエストを実行"""
        try:
            url = path if path.startswith("http") else urljoin(self.base_url, path)
            self.logger.info(f"Sending GET request to: {url}")
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
