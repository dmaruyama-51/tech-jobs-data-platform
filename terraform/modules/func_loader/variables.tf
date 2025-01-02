variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "region" {
  description = "デプロイするリージョン"
  type        = string
}

variable "function_name" {
  description = "Cloud Functionsの関数名"
  type        = string
}

variable "source_dir" {
  description = "ソースコードのディレクトリパス"
  type        = string
}

variable "bucket" {
  description = "ソースコードを保存するGCSバケット名"
  type        = string
}

variable "entry_point" {
  description = "エントリーポイントとなる関数名"
  type        = string
}
