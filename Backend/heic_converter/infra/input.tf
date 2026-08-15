variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to (T-06)"
  type        = string
}

variable "photos_bucket_arn" {
  description = "ARN of the shared S3 bucket holding uploaded photos, for GetObject/PutObject IAM"
  type        = string
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic (T-07), subscribed alarms publish here"
  type        = string
}
