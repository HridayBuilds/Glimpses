variable "name_prefix" {
  type    = string
  default = "glimpses"
}
variable "deploy_artifacts_bucket" { type = string }
variable "jobs_table_name" { type = string }
variable "jobs_table_arn" { type = string }
variable "events_table_name" { type = string }
variable "events_table_arn" { type = string }
variable "event_attendees_table_name" { type = string }
variable "event_attendees_table_arn" { type = string }
variable "users_table_name" { type = string }
variable "users_table_arn" { type = string }
variable "photos_bucket_name" { type = string }
variable "photos_bucket_arn" { type = string }
variable "ingestion_function_arn" { type = string }
variable "db_api_function_arn" { type = string }
variable "alarm_sns_topic_arn" { type = string }
variable "drive_api_key_parameter" {
  type    = string
  default = "/glimpses/google-drive/api-key"
}
