variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "downloads_table_name" {
  description = "Name of the Downloads DynamoDB table, this Lambda's own table"
  type        = string
}

variable "downloads_table_arn" {
  description = "ARN of the Downloads DynamoDB table, for IAM"
  type        = string
}

variable "photos_table_name" {
  description = "Name of the Photos DynamoDB table, read-only lookup for each photo's s3Key"
  type        = string
}

variable "photos_table_arn" {
  description = "ARN of the Photos DynamoDB table, for IAM"
  type        = string
}

variable "event_attendees_table_name" {
  description = "EventAttendees table used to resolve Photos of me downloads"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "EventAttendees table ARN, for read access to matched photo IDs"
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
