variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table, read/written for both cascade actions"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM"
  type        = string
}

variable "events_stream_arn" {
  description = "ARN of the Events table's DynamoDB Stream, source for the TTL-delete trigger"
  type        = string
}

variable "photos_table_name" {
  description = "Name of the Photos DynamoDB table, row deletion owned by this Lambda"
  type        = string
}

variable "photos_table_arn" {
  description = "ARN of the Photos DynamoDB table, for IAM"
  type        = string
}

variable "faces_table_name" {
  description = "Name of the Faces DynamoDB table, row deletion owned by this Lambda"
  type        = string
}

variable "faces_table_arn" {
  description = "ARN of the Faces DynamoDB table, for IAM"
  type        = string
}

variable "event_attendees_table_name" {
  description = "Name of the EventAttendees DynamoDB table, rows deleted on whole-event teardown only"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "ARN of the EventAttendees DynamoDB table, for IAM"
  type        = string
}

variable "photos_bucket_name" {
  description = "Name of the shared glimpses-photos S3 bucket — one bucket, six prefixes"
  type        = string
}

variable "photos_bucket_arn" {
  description = "ARN of the shared glimpses-photos S3 bucket, for IAM prefix scoping"
  type        = string
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic, subscribed alarms publish here"
  type        = string
}
