import logging
import os
from logging.handlers import RotatingFileHandler

import google.cloud.logging


def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """ロガーの設定を行う"""

    # Google Cloud Loggingの設定
    client = google.cloud.logging.Client()
    client.setup_logging()

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 標準出力用のハンドラー
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # ファイル出力用のハンドラー
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    # フォーマッターの設定
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 各ハンドラーにフォーマッターを設定
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # ハンドラーの追加（既存のハンドラーがある場合は削除）
    logger.handlers.clear()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
