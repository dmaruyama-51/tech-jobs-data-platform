variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "region" {
  description = "リージョン"
  type        = string
}

variable "terraform_service_account" {
  description = "Terraformの実行に使用するサービスアカウント"
  type        = string
} 