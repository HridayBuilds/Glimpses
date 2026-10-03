variable "name_prefix" {
  description = "Prefix applied to the Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "jobs_table_name" {
  description = "Name of the Jobs DynamoDB table, this Lambda's own table"
  type        = string
}

variable "jobs_table_arn" {
  description = "ARN of the Jobs DynamoDB table, for IAM"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table, read to check the event's contributionPolicy and organizerID"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM"
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
  description = "ARN of the shared operator-alerts SNS topic, which subscribed alarms publish to"
  type        = string
}
