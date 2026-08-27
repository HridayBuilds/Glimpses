variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to (T-06)"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table (T-04), this Lambda's own table"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM"
  type        = string
}

variable "event_attendees_table_name" {
  description = "Name of the EventAttendees DynamoDB table (T-04); read-only here for GET /events/my-events"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "ARN of the EventAttendees DynamoDB table, for IAM (read-only)"
  type        = string
}

variable "photos_bucket_name" {
  description = "Name of the shared glimpses-photos S3 bucket (T-09) — one bucket, six prefixes"
  type        = string
}

variable "photos_bucket_arn" {
  description = "ARN of the shared glimpses-photos S3 bucket, for IAM prefix scoping"
  type        = string
}

variable "cloudfront_domain_name" {
  description = "Photos CloudFront distribution's default domain; used for qrcodeUrl, where the QR PNG itself is stored"
  type        = string
}

variable "frontend_domain_name" {
  description = "Frontend app's CloudFront distribution's default domain (P-30: join links/QR codes never use a custom domain); used for the QR's encoded join URL"
  type        = string
}

variable "cascade_delete_function_name" {
  description = "Function name of CascadeDelete (P-34), for delete_event's self-invoke; empty until that module lands"
  type        = string
  default     = ""
}

variable "cascade_delete_function_arn" {
  description = "ARN of CascadeDelete, for IAM; empty until that module lands (no invoke policy is created)"
  type        = string
  default     = ""
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic (T-07), subscribed alarms publish here"
  type        = string
}

variable "archive_sweep_schedule_expression" {
  description = "EventBridge Scheduler cron/rate expression for the daily archive sweep (P-77/P-78)"
  type        = string
  default     = "rate(1 day)"
}
