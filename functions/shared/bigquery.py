from google.cloud import bigquery
from shared.logger_config import setup_logger

logger = setup_logger("shared.bigquery_utils")

def ensure_dataset_exists(client: bigquery.Client, dataset_ref: str):
    """データセットの存在確認と作成"""
    try:
        client.get_dataset(dataset_ref)
        logger.info(f"Dataset {dataset_ref} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-northeast1"
        dataset = client.create_dataset(dataset, exists_ok=True)
        logger.info(f"Created dataset: {dataset_ref}")

def ensure_table_exists(client: bigquery.Client, table_ref: str, schema: list):
    """テーブルの存在確認と作成"""
    try:
        client.get_table(table_ref)
        logger.info(f"Table {table_ref} already exists")
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        
        # パーティション設定
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="listing_start_date"
        )
        
        # クラスタリング設定
        table.clustering_fields = ["occupation", "work_location"]
        
        # テーブルを作成
        table = client.create_table(table, exists_ok=True)
        logger.info(f"Created partitioned table: {table_ref}")
        
        # Primary Key制約を追加
        ddl_statement = f"""
        ALTER TABLE `{table_ref}`
        ADD PRIMARY KEY (detail_link) NOT ENFORCED
        """
        try:
            client.query(ddl_statement).result()
            logger.info(f"Primary key constraint added on: detail_link")
        except Exception as e:
            logger.warning(f"Failed to add primary key constraint: {str(e)}") 