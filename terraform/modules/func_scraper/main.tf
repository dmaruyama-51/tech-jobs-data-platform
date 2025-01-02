# ===============================================
# local execution
# ===============================================

resource "null_resource" "prepare_source" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    working_dir = path.root
    command     = <<EOT
      rm -rf /tmp/function-source-temp-${var.function_name}
      mkdir -p /tmp/function-source-temp-${var.function_name}
      
      # requirements.txtを生成
      poetry export -f requirements.txt --only main,scraper --output ${var.source_dir}/requirements.txt --without-hashes --no-interaction --no-ansi
      
      # var.source_dir と shared ディレクトリを含める
      cp -r ${var.source_dir}/* /tmp/function-source-temp-${var.function_name}/
      cp -r ${path.root}/../functions/shared /tmp/function-source-temp-${var.function_name}/
    EOT
  }
}

# ===============================================
# Cloud Storage リソース
# ===============================================

# ソースコードをZIPファイルにアーカイブ
data "archive_file" "source" {
  depends_on  = [null_resource.prepare_source]
  type        = "zip"
  source_dir  = "/tmp/function-source-temp-${var.function_name}"
  output_path = "/tmp/function-source-${var.function_name}.zip"
}

# ZIPファイルをGCSバケットにアップロード
resource "google_storage_bucket_object" "source" {
  name   = "function-source-${data.archive_file.source.output_md5}.zip"
  bucket = var.bucket
  source = data.archive_file.source.output_path
}

# スクレイピング結果保存用のGCSバケット
resource "google_storage_bucket" "scraping_data_bucket" {
  name     = "${var.project_id}-scraping-data"
  location = var.region

  # バケットが既に存在する場合はエラーを無視
  lifecycle {
    prevent_destroy = false
    ignore_changes  = all
  }
}

# ===============================================
# Cloud Scheduler リソース
# ===============================================

# Cloud Scheduler Job
resource "google_cloud_scheduler_job" "scraper_scheduler" {
  name        = "daily-job-scraper"
  description = "Daily job data scraping scheduler"
  schedule    = "0 5 * * *" # 毎日午前5時に実行
  time_zone   = "Asia/Tokyo"

  pubsub_target {
    topic_name = google_pubsub_topic.scraper_topic.id
    data = base64encode(jsonencode({
      "type" : "daily_scraping"
    }))
  }
}

# ===============================================
# Pub/Sub リソース
# ===============================================

# Pub/Sub Topic
resource "google_pubsub_topic" "scraper_topic" {
  name = "job-scraper-topic"
}

# Cloud Functions の Pub/Sub トリガー用のサービスアカウント
resource "google_service_account" "pubsub_invoker" {
  account_id   = "job-scraper-invoker"
  display_name = "Job Scraper Pub/Sub Invoker"
}

# サービスアカウントへの権限付与
resource "google_project_iam_member" "invoker_permission" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.pubsub_invoker.email}"
}

# Pub/Sub サブスクリプション（Cloud Functions用）
resource "google_pubsub_subscription" "scraper_subscription" {
  name  = "job-scraper-subscription"
  topic = google_pubsub_topic.scraper_topic.name

  push_config {
    push_endpoint = google_cloudfunctions2_function.function.url
    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "604800s" # 7日
  }
}


# ===============================================
# Cloud Functions リソース
# ===============================================

# Cloud Function の設定を更新
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
      PROJECT_ID       = var.project_id
      PYTHONIOENCODING = "utf-8"
      LANG             = "ja_JP.UTF-8"
    }
    ingress_settings               = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
  }

  lifecycle {
    # ソースコードの変更をトリガーにしてリソースを置き換える
    replace_triggered_by = [
      google_storage_bucket_object.source
    ]
  }
} 