import functions_framework
from flask import Request, Response, jsonify


@functions_framework.http
def hello_world(request: Request) -> Response:
    """
    シンプルなHello Worldレスポンスを返すエンドポイント

    Args:
        request (Request): HTTPリクエストオブジェクト

    Returns:
        Response: JSONレスポンス
    """
    response_data = {"message": "Hello, World! 2nd", "status": "success"}

    return jsonify(response_data)
