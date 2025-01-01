 variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "region" {
  description = "リージョン"
  type        = string
}

variable "function_name" {
  description = "Cloud Function の名前"
  type        = string
}

variable "source_dir" {
  description = "ソースコードのディレクトリパス"
  type        = string
}

variable "bucket" {
  description = "ソースコードを格納するGCSバケット名"
  type        = string
}

variable "entry_point" {
  description = "Cloud Function のエントリーポイント"
  type        = string
} 