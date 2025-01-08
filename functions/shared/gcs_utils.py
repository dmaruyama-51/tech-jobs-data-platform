import os
from datetime import datetime

import pandas as pd
from google.cloud import storage  # type: ignore

from .logger_config import setup_logger

logger = setup_logger("shared.gcs")


def get_data_bucket_name() -> str:
    """スクレイピングデータ保存用のバケット名を生成"""
    project_id = os.environ.get("PROJECT_ID")
    if not project_id:
        raise ValueError("Environment variable PROJECT_ID is not set")
    return f"{project_id}-scraping-data"


def save_to_gcs(df: pd.DataFrame, bucket_name: str, prefix: str = "raw/jobs") -> str:
    """DataFrameをGCSにCSV形式で保存し、同じ日の古いファイルを削除"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # 日付のみのパーティションフォルダを使用
    partition_date = datetime.now().strftime("%Y%m%d")
    blob_name = f"{prefix}/partition_date={partition_date}/jobs.csv"

    # 保存前に同じ日の古いファイルを削除
    prefix_path = f"{prefix}/partition_date={partition_date}/"
    blobs = bucket.list_blobs(prefix=prefix_path)
    for blob in blobs:
        blob.delete()
        logger.info(f"Deleted existing blob: {blob.name}")

    # データフレームを保存
    blob = bucket.blob(blob_name)
    with blob.open("w", encoding="utf-8") as f:
        df.to_csv(f, index=False, encoding="utf-8")
    logger.info(f"Saved DataFrame to: gs://{bucket_name}/{blob_name}")

    return blob_name
