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
      poetry export -f requirements.txt --only main,loader --output ${var.source_dir}/requirements.txt --without-hashes --no-interaction --no-ansi
      
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

# ===============================================
# Cloud Functions リソース
# ===============================================

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
      PROJECT_ID = var.project_id
    }
  }

  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.source
    ]
  }
}

# ===============================================
# Cloud Storage トリガー
# ===============================================

# Cloud Storage トリガーのサービスアカウント
resource "google_service_account" "storage_trigger" {
  account_id   = "job-loader-trigger"
  display_name = "Job Loader Storage Trigger"
}

# サービスアカウントへの権限付与
resource "google_project_iam_member" "storage_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.storage_trigger.email}"
}

# Cloud Storage トリガーの設定
resource "google_storage_notification" "notification" {
  bucket         = var.data_bucket
  payload_format = "JSON_API_V1"
  # 新しいオブジェクトが作成されるか、既存のオブジェクトが上書きされ、そのオブジェクトの新しい世代が作成されると送信
  # ref: https://cloud.google.com/functions/docs/calling/storage?hl=ja
  event_types    = ["OBJECT_FINALIZE"]
  topic         = google_pubsub_topic.storage_trigger_topic.id
  depends_on    = [google_pubsub_topic_iam_member.storage_publisher]
}

# Pub/Sub トピック
resource "google_pubsub_topic" "storage_trigger_topic" {
  name = "job-loader-trigger-topic"
}

# Cloud Storage に Pub/Sub への発行権限を付与
resource "google_pubsub_topic_iam_member" "storage_publisher" {
  topic  = google_pubsub_topic.storage_trigger_topic.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

# Cloud Storage のサービスアカウントを取得
data "google_storage_project_service_account" "gcs_account" {
}

# Pub/Sub サブスクリプション
resource "google_pubsub_subscription" "storage_trigger_subscription" {
  name  = "job-loader-trigger-subscription"
  topic = google_pubsub_topic.storage_trigger_topic.name

  push_config {
    push_endpoint = google_cloudfunctions2_function.function.url
    oidc_token {
      service_account_email = google_service_account.storage_trigger.email
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = "604800s"  # 7日
  }
}
