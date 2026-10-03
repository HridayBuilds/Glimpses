variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to"
  type        = string
}

variable "event_attendees_table_name" {
  description = "Name of the EventAttendees DynamoDB table, this Lambda's own table"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "ARN of the EventAttendees DynamoDB table, for IAM"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table; read-only here for joinPolicy/status at join time and organizerID authorization"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM (read-only)"
  type        = string
}

variable "users_table_name" {
  description = "Name of the Users DynamoDB table; read-only here for P-82's roster/lobby display name and email"
  type        = string
}

variable "users_table_arn" {
  description = "ARN of the Users DynamoDB table, for IAM (read-only)"
  type        = string
}

variable "cloudfront_domain_name" {
  description = "CloudFront distribution's default domain, for GET /events/{eventId}/info's qrcodeUrl (P-30: no custom domain)"
  type        = string
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic, subscribed alarms publish here"
  type        = string
}
