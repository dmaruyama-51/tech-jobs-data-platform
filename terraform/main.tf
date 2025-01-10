# ================================
# 共通処理
# ================================

# GCSバケット
resource "google_storage_bucket" "function_bucket" {
  name     = "${var.project_id}-function-source"
  location = var.region
}


# ================================
# デプロイする各関数
# ================================

# Hello World
# module "func_hello" {
#   source = "./modules/func_hello"

#  project_id    = var.project_id
#  region        = var.region
#  function_name = "hello"
#  source_dir    = "${path.module}/../functions/func_hello"
#  bucket        = google_storage_bucket.function_bucket.name
#  entry_point   = "hello_world"
#} 

# Scraping
module "func_scraper" {
  source = "./modules/func_scraper"

  project_id    = var.project_id
  region        = var.region
  function_name = "scraper"
  source_dir    = "${path.module}/../functions/func_scraper"
  bucket        = google_storage_bucket.function_bucket.name
  data_bucket   = "${var.project_id}-scraping-data"
  entry_point   = "scraping"
}

# Loader
module "func_loader" {
  source        = "./modules/func_loader"
  project_id    = var.project_id
  region        = var.region
  function_name = "loader"
  source_dir    = "${path.module}/../functions/func_loader"
  bucket        = google_storage_bucket.function_bucket.name
  entry_point   = "load_to_bigquery"
  data_bucket   = "${var.project_id}-scraping-data"
} 

# GithubActionsで実行するサービスアカウントへの権限付与
resource "google_project_iam_member" "terraform_service_account_roles" {
  for_each = toset([
    # Cloud Storage
    "roles/storage.objectViewer",
    "roles/storage.objectCreator",
    "roles/storage.buckets.get",
    "roles/storage.buckets.create",
    
    # Cloud Functions
    "roles/cloudfunctions.developer",
    
    # Cloud Run (Cloud Functions 2nd gen)
    "roles/run.developer",
    
    # Pub/Sub
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    
    # Cloud Scheduler
    "roles/cloudscheduler.admin",
    
    # IAM
    "roles/iam.serviceAccountUser",
    "roles/resourcemanager.projectIamAdmin"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.terraform_service_account}"
} 