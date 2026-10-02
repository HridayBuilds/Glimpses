variable "name_prefix" {
  type    = string
  default = "glimpses"
}

variable "deploy_artifacts_bucket" {
  type = string
}

variable "users_table_name" {
  type = string
}

variable "users_table_arn" {
  type = string
}

variable "event_attendees_table_name" {
  type = string
}

variable "event_attendees_table_arn" {
  type = string
}

variable "ingestion_function_name" {
  type = string
}

variable "ingestion_function_arn" {
  type = string
}

variable "alarm_sns_topic_arn" {
  type = string
}
