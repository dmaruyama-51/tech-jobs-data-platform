import pytest
import pandas as pd
from datetime import datetime
from shared.gcs import get_data_bucket_name, save_to_gcs


@pytest.fixture
def mock_storage_client(mocker):
    """GCSクライアントのモックを提供するフィクスチャ"""
    return mocker.patch("shared.gcs.storage.Client")


@pytest.fixture
def mock_env_vars(mocker):
    """環境変数のモックを提供するフィクスチャ"""
    mocker.patch.dict("os.environ", {"PROJECT_ID": "test-project"})


@pytest.fixture
def sample_dataframe():
    """テスト用のDataFrameを提供するフィクスチャ"""
    return pd.DataFrame({"job_title": ["Python開発者"], "monthly_salary": [500000]})


def test_get_data_bucket_name(mock_env_vars, mocker):
    """バケット名生成をテスト

    検証内容:
    1. PROJECT_ID環境変数から正しくバケット名が生成されること
    2. 環境変数が未設定の場合、適切なエラーが発生すること
    """
    # 正常系
    bucket_name = get_data_bucket_name()
    assert bucket_name == "test-project-scraping-data"

    # 異常系（環境変数未設定）
    mocker.patch.dict("os.environ", {}, clear=True)
    with pytest.raises(ValueError) as exc_info:
        get_data_bucket_name()
    assert "Environment variable PROJECT_ID is not set" in str(exc_info.value)


def test_save_to_gcs(mock_storage_client, sample_dataframe, mocker):
    """GCSへのデータ保存をテスト
    検証内容:
    1. 正しいパスでファイルが保存されること
    2. 同じ日付の古いファイルが削除されること
    3. DataFrameが正しくCSVとして保存されること
    """
    # モックの設定
    mock_bucket = mocker.Mock()
    mock_blob = mocker.Mock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # MagicMockを使用してファイル操作をモック化
    mock_blob.open.return_value = mocker.MagicMock()

    # 既存ブロブのモック
    existing_blob = mocker.Mock()
    mock_bucket.list_blobs.return_value = [existing_blob]

    # 日付を固定
    current_date = datetime(2024, 3, 15)
    mocker.patch("shared.gcs.datetime")
    mocker.patch("shared.gcs.datetime.now", return_value=current_date)

    # テスト実行
    bucket_name = "test-bucket"
    result = save_to_gcs(sample_dataframe, bucket_name)

    # 検証
    expected_path = "raw/jobs/partition_date=20240315/jobs.csv"
    assert result == expected_path

    # メソッドが正しく呼び出されたことを確認
    mock_bucket.blob.assert_called_once_with(expected_path)
    mock_blob.open.assert_called_once_with("w", encoding="utf-8")
    existing_blob.delete.assert_called_once()
