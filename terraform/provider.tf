provider "google" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
    # バックエンドの設定は -backend-config オプションで外部から注入
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
} 