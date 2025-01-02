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