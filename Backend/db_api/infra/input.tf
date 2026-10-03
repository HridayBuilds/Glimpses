variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "jobs_table_name" {
  description = "Name of the Jobs DynamoDB table, the only table this Lambda touches"
  type        = string
}

variable "jobs_table_arn" {
  description = "ARN of the Jobs DynamoDB table, for IAM"
  type        = string
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic, subscribed alarms publish here"
  type        = string
}
