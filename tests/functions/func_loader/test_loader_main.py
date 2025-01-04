import pytest
from func_loader.main import load_to_bigquery, JobDataLoader
from google.cloud import bigquery, storage

@pytest.fixture
def mock_storage_client(mocker):
    """GCSクライアントのモック"""
    return mocker.patch('func_loader.main.storage.Client')

@pytest.fixture
def mock_bq_client(mocker):
    """BigQueryクライアントのモック"""
    return mocker.patch('func_loader.main.bigquery.Client')

@pytest.fixture
def mock_env_vars(mocker):
    """環境変数のモック"""
    mocker.patch.dict('os.environ', {'PROJECT_ID': 'test-project'})

@pytest.fixture
def job_loader(mock_bq_client, mock_storage_client, mock_env_vars):
    """JobDataLoaderのインスタンスを提供"""
    return JobDataLoader()


def test_job_data_loader_execute_success(job_loader, mock_bq_client, mocker):
    """JobDataLoader.executeの正常系テスト"""
    # GCSファイルの存在確認をモック
    mocker.patch.object(job_loader, '_check_source_file', return_value=True)
    
    # 一時テーブルへのロードをモック
    mocker.patch.object(job_loader, '_load_to_temp_table', return_value=10)
    
    # マージ処理をモック
    mocker.patch.object(job_loader, '_merge_data')
    
    # テスト実行
    result = job_loader.execute()
    
    # 結果の検証
    assert result["status"] == "success"
    assert result["loaded_rows"] == 10
    assert "Data loaded to" in result["message"]

def test_job_data_loader_execute_no_data(job_loader, mock_bq_client, mocker):
    """JobDataLoader.executeのデータなしテスト"""
    # ソースファイルが存在しない場合
    mocker.patch.object(job_loader, '_check_source_file', return_value=False)
    
    # テスト実行
    result = job_loader.execute()
    
    # 結果の検証
    assert result["status"] == "success"
    assert result["message"] == "No data to load"
    assert result["loaded_rows"] == 0

def test_job_data_loader_execute_error(job_loader, mock_bq_client, mocker):
    """JobDataLoader.executeのエラー系テスト"""
    # エラーを発生させる
    mocker.patch.object(job_loader, '_check_source_file', side_effect=Exception("Test error"))
    
    # テスト実行
    result = job_loader.execute()
    
    # 結果の検証
    assert result["status"] == "error"
    assert "Test error" in result["message"]