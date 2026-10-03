variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "users_table_name" {
  description = "Name of the Users DynamoDB table, this Lambda's own table"
  type        = string
}

variable "users_table_arn" {
  description = "ARN of the Users DynamoDB table, for IAM"
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

variable "selfie_match_dispatcher_function_name" {
  description = "Function invoked after a valid selfie is confirmed"
  type        = string
}

variable "selfie_match_dispatcher_function_arn" {
  description = "Dispatcher ARN for the profile Lambda invoke policy"
  type        = string
}
