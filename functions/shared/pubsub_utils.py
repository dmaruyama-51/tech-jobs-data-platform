from google.cloud import storage
from datetime import datetime
import json
import logging
from flask import Request
import base64

logger = logging.getLogger(__name__)

def is_valid_pubsub_message(request: Request) -> bool:
    """Pub/Subからのメッセージかどうかを検証"""
    if not request.is_json:
        return False
    
    data = request.get_json()
    
    # Pub/Subメッセージの基本構造を確認
    if not isinstance(data, dict):
        return False
    if 'message' not in data or 'subscription' not in data:
        return False
    
    try:
        # メッセージデータをデコード
        message_data = base64.b64decode(data['message'].get('data', '')).decode()
        message_json = json.loads(message_data)
        
        # daily_scrapingメッセージであることを確認
        return message_json.get('type') == 'daily_scraping'
    except:
        return False

class MessageProcessor:
    def __init__(self, bucket_name: str):
        """
        Args:
            bucket_name (str): 処理済みメッセージを保存するバケット名
        """
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.processed_prefix = "processed_messages"  # 処理済みメッセージを保存するプレフィックス

    def _get_message_path(self, message_id: str) -> str:
        """メッセージIDからCloud Storage内のパスを生成"""
        return f"{self.processed_prefix}/{message_id}.json"

    def is_message_processed(self, message_id: str) -> bool:
        """
        メッセージが既に処理済みかチェックする
        
        Args:
            message_id (str): チェックするメッセージID
            
        Returns:
            bool: 処理済みの場合True、未処理の場合False
        """
        try:
            blob = self.bucket.blob(self._get_message_path(message_id))
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking message status: {str(e)}")
            # エラーの場合は安全のためFalseを返す
            return False

    def mark_message_as_processed(self, message_id: str, metadata: dict = None) -> None:
        """
        メッセージを処理済みとしてマークする
        
        Args:
            message_id (str): 処理済みとしてマークするメッセージID
            metadata (dict, optional): 保存する追加のメタデータ
        """
        try:
            blob = self.bucket.blob(self._get_message_path(message_id))
            
            # 保存するデータの作成
            data = {
                "message_id": message_id,
                "processed_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # JSONとしてアップロード
            blob.upload_from_string(
                json.dumps(data),
                content_type='application/json'
            )
            
            logger.info(f"Message {message_id} marked as processed")
            
        except Exception as e:
            logger.error(f"Error marking message as processed: {str(e)}")
            raise 