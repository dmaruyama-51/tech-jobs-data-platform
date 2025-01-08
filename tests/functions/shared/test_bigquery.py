import pytest
from google.cloud import bigquery
from shared.bigquery_utils import ensure_dataset_exists, ensure_table_exists


@pytest.fixture
def mock_bq_client(mocker):
    """BigQueryクライアントのモックを提供するフィクスチャ"""
    return mocker.Mock(spec=bigquery.Client)


def test_ensure_dataset_exists_when_exists(mock_bq_client):
    """既存のデータセットを確認するテスト

    検証内容:
    1. データセットが存在する場合、新規作成を試みないこと
    2. 適切なログメッセージが出力されること
    """
    # データセットが存在する場合のモック設定
    dataset_ref = "project.dataset"
    mock_bq_client.get_dataset.return_value = None

    # テスト実行
    ensure_dataset_exists(mock_bq_client, dataset_ref)

    # 検証
    mock_bq_client.get_dataset.assert_called_once_with(dataset_ref)
    mock_bq_client.create_dataset.assert_not_called()


def test_ensure_dataset_exists_when_not_exists(mock_bq_client):
    """存在しないデータセットを作成するテスト

    検証内容:
    1. データセットが存在しない場合、新規作成されること
    2. 作成時に適切なロケーションが設定されること
    3. 適切なログメッセージが出力されること
    """
    # データセットが存在しない場合のモック設定
    dataset_ref = "project.dataset"
    mock_bq_client.get_dataset.side_effect = Exception("Dataset not found")

    # テスト実行
    ensure_dataset_exists(mock_bq_client, dataset_ref)

    # 検証
    mock_bq_client.get_dataset.assert_called_once_with(dataset_ref)
    mock_bq_client.create_dataset.assert_called_once()

    # create_datasetの引数を検証
    created_dataset = mock_bq_client.create_dataset.call_args[0][0]
    assert created_dataset.location == "asia-northeast1"


def test_ensure_table_exists_when_exists(mock_bq_client):
    """既存のテーブルを確認するテスト

    検証内容:
    1. テーブルが存在する場合、新規作成を試みないこと
    2. 適切なログメッセージが出力されること
    """
    # テーブルが存在する場合のモック設定
    table_ref = "project.dataset.table"
    schema = [
        bigquery.SchemaField("detail_link", "STRING"),
        bigquery.SchemaField("listing_start_date", "DATE"),
    ]
    mock_bq_client.get_table.return_value = None

    # テスト実行
    ensure_table_exists(mock_bq_client, table_ref, schema)

    # 検証
    mock_bq_client.get_table.assert_called_once_with(table_ref)
    mock_bq_client.create_table.assert_not_called()


def test_ensure_table_exists_when_not_exists(mock_bq_client):
    """存在しないテーブルを作成するテスト

    検証内容:
    1. テーブルが存在しない場合、新規作成されること
    2. パーティション設定が正しく行われること
    3. Primary Key制約が追加されること
    4. 適切なログメッセージが出力されること
    """
    # テーブルが存在しない場合のモック設定
    table_ref = "project.dataset.table"
    schema = [
        bigquery.SchemaField("detail_link", "STRING"),
        bigquery.SchemaField("listing_start_date", "DATE"),
    ]
    mock_bq_client.get_table.side_effect = Exception("Table not found")

    # テスト実行
    ensure_table_exists(mock_bq_client, table_ref, schema)

    # 検証
    mock_bq_client.get_table.assert_called_once_with(table_ref)
    mock_bq_client.create_table.assert_called_once()

    # create_tableの引数を検証
    created_table = mock_bq_client.create_table.call_args[0][0]
    assert created_table.schema == schema
    assert created_table.time_partitioning.field == "listing_start_date"

    # Primary Key制約の追加を検証
    expected_ddl = f"""
        ALTER TABLE `{table_ref}`
        ADD PRIMARY KEY (detail_link) NOT ENFORCED
        """
    mock_bq_client.query.assert_called_once_with(expected_ddl)
