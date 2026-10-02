variable "name_prefix" {
  type    = string
  default = "glimpses"
}

variable "deploy_artifacts_bucket" { type = string }
variable "users_table_name" { type = string }
variable "users_table_arn" { type = string }
variable "events_table_name" { type = string }
variable "events_table_arn" { type = string }
variable "events_stream_arn" { type = string }
variable "jobs_stream_arn" { type = string }
variable "event_attendees_table_name" { type = string }
variable "event_attendees_table_arn" { type = string }
variable "event_attendees_stream_arn" { type = string }
variable "notifications_table_name" { type = string }
variable "notifications_table_arn" { type = string }
variable "sender_email" { type = string }
variable "sender_identity_arn" { type = string }
variable "frontend_domain_name" { type = string }
variable "alarm_sns_topic_arn" { type = string }
