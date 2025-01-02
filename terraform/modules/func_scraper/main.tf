# 共有モジュールをコピーするためのnullリソース
resource "null_resource" "prepare_source" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    working_dir = path.root
    command = <<EOT
      rm -rf /tmp/function-source-temp
      mkdir -p /tmp/function-source-temp
      
      # requirements.txtを生成
      poetry export -f requirements.txt --only main,scraper --output ${var.source_dir}/requirements.txt --without-hashes --no-interaction --no-ansi
      
      # var.source_dir だけでなく shared ディレクトリも含める
      cp -r ${var.source_dir}/* /tmp/function-source-temp/
      cp -r ${path.root}/../functions/shared /tmp/function-source-temp/
    EOT
  }
}

# ソースコードをZIPファイルにアーカイブ
data "archive_file" "source" {
  depends_on  = [null_resource.prepare_source]
  type        = "zip"
  source_dir  = "/tmp/function-source-temp"
  output_path = "/tmp/function-source.zip"
}

# ZIPファイルをGCSバケットにアップロード
resource "google_storage_bucket_object" "source" {
  name   = "function-source-${data.archive_file.source.output_md5}.zip"
  bucket = var.bucket
  source = data.archive_file.source.output_path
}

# Cloud Function のデプロイ設定
resource "google_cloudfunctions2_function" "function" {
  name     = var.function_name
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = var.entry_point
    source {
      storage_source {
        bucket = var.bucket
        object = google_storage_bucket_object.source.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "1024Mi"
    timeout_seconds    = 600
    environment_variables = {
      PYTHONUNBUFFERED = "true"
    }
  }
} 