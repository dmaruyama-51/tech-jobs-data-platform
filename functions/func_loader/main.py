import os
from pathlib import Path
from typing import Any, Dict, Tuple

import functions_framework
from dotenv import load_dotenv
from flask import Request, jsonify
from flask.wrappers import Response
from google.cloud import bigquery, storage  # type: ignore
from shared.date_utils import get_yesterday_jst
from shared.logger_config import setup_logger

from functions.shared.bigquery_utils import ensure_dataset_exists, ensure_table_exists
from functions.shared.gcs_utils import get_data_bucket_name

load_dotenv()


class JobDataLoader:
    """スクレイピングデータをBigQueryへロードする"""

    def __init__(self) -> None:
        self.logger = setup_logger("job_loader")
        self.project_id = os.environ.get("PROJECT_ID")
        if not self.project_id:
            raise ValueError("Environment variable PROJECT_ID is not set")

        self.bq_client = bigquery.Client()
        self.storage_client = storage.Client()

        self.dataset_id = "bigdata_navi"
        self.table_id = "lake__joblist"
        self.table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"

        # SQLファイルのディレクトリパス
        self.sql_dir = Path(__file__).parent / "sql"

    def _read_sql_file(self, filename: str) -> str:
        """SQLファイルを読み込む"""
        file_path = self.sql_dir / filename
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _check_source_file(self, bucket_name: str, blob_name: str) -> bool:
        """ソースファイルの存在確認と内容チェック"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                self.logger.warning(f"Source file not found: {blob_name}")
                return False

            # フタデータを取得してサイズをチェック
            blob.reload()

            # サイズが取得できない、または極端に小さい場合はエラー
            if not blob.size or blob.size < 50:
                self.logger.warning(f"Source file is empty or too small: {blob_name}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking source file: {str(e)}")
            return False

    def _load_to_temp_table(
        self, source_path: str, temp_table: str, schema: list
    ) -> int:
        """一時テーブルへのデータロード"""
        self.logger.info("Loading data to temporary table...")
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            allow_quoted_newlines=True,
            encoding="UTF-8",
        )
        load_job = self.bq_client.load_table_from_uri(
            source_path, temp_table, job_config=job_config
        )
        load_job.result()
        self.logger.info(f"Loaded {load_job.output_rows} rows to temporary table")
        return load_job.output_rows

    def _merge_data(self, temp_table: str) -> None:
        """データのマージ処理"""
        self.logger.info("Executing merge operation...")
        merge_query = self._read_sql_file("merge.sql").format(
            table_ref=self.table_ref, temp_table=temp_table
        )
        merge_job = self.bq_client.query(merge_query)
        merge_job.result()
        self.logger.info("Merge operation completed")

    def execute(self) -> Dict[str, Any]:
        """ロード処理を実行"""
        try:
            self.logger.info("Starting data load process...")
            partition_date = get_yesterday_jst().strftime("%Y%m%d")
            bucket_name = get_data_bucket_name()
            blob_name = f"raw/jobs/partition_date={partition_date}/jobs.csv"
            source_path = f"gs://{bucket_name}/{blob_name}"

            # テーブル参照を分解
            table_ref_parts = self.table_ref.split(".")
            if len(table_ref_parts) != 3:
                raise ValueError(f"Invalid table reference format: {self.table_ref}")

            project_id, dataset_id, table_id = table_ref_parts
            dataset_ref = f"{project_id}.{dataset_id}"
            temp_table = f"{self.table_ref}_temp"

            # スキーマ定義
            schema = [
                bigquery.SchemaField("monthly_salary", "INTEGER"),
                bigquery.SchemaField("occupation", "STRING"),
                bigquery.SchemaField("work_type", "STRING"),
                bigquery.SchemaField("work_location", "STRING"),
                bigquery.SchemaField("industry", "STRING"),
                bigquery.SchemaField("job_content", "STRING"),
                bigquery.SchemaField("required_skills", "STRING"),
                bigquery.SchemaField("preferred_skills", "STRING"),
                bigquery.SchemaField("programming_language", "STRING"),
                bigquery.SchemaField("tool", "STRING"),
                bigquery.SchemaField("framework", "STRING"),
                bigquery.SchemaField("rate_of_work", "STRING"),
                bigquery.SchemaField("number_of_recruitment_interviews", "STRING"),
                bigquery.SchemaField("number_of_days_worked", "STRING"),
                bigquery.SchemaField("number_of_applicants", "STRING"),
                bigquery.SchemaField("job_title", "STRING"),
                bigquery.SchemaField("listing_start_date", "DATE"),
                bigquery.SchemaField("detail_link", "STRING", mode="REQUIRED"),
            ]

            # ソースファイルのチェック
            if not self._check_source_file(bucket_name, blob_name):
                return {
                    "status": "success",
                    "message": "No data to load",
                    "loaded_rows": 0,
                }

            ensure_dataset_exists(self.bq_client, dataset_ref)
            ensure_table_exists(self.bq_client, self.table_ref, schema)

            # データのロードとマージ
            loaded_rows = self._load_to_temp_table(source_path, temp_table, schema)
            self._merge_data(temp_table)

            # 一時テーブルの削除
            self.logger.info("Cleaning up temporary table...")
            self.bq_client.delete_table(temp_table, not_found_ok=True)
            self.logger.info("Temporary table deleted")

            result = {
                "status": "success",
                "message": f"Data loaded to {self.table_ref}",
                "loaded_rows": loaded_rows,
            }
            self.logger.info(f"Load process completed: {result}")
            return result

        except Exception as e:
            error_message = f"Error during data loading: {str(e)}"
            self.logger.error(error_message)
            return {"status": "error", "message": error_message}


@functions_framework.http
def load_to_bigquery(request: Request) -> Tuple[Response, int]:
    """Cloud Functions のエントリーポイント"""
    try:
        loader = JobDataLoader()
        result = loader.execute()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
