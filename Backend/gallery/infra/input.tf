variable "name_prefix" {
  description = "Prefix applied to this Lambda's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "deploy_artifacts_bucket" {
  description = "Name of the shared glimpses-deploy-artifacts S3 bucket Jenkins pushes this Lambda's zip to (T-06)"
  type        = string
}

variable "photos_table_name" {
  description = "Name of the Photos DynamoDB table (T-04); read-only here — CascadeDelete owns row deletion"
  type        = string
}

variable "photos_table_arn" {
  description = "ARN of the Photos DynamoDB table, for IAM (read-only)"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table (T-04); read-only here for P-44's organizer-delete-any-photo check"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM (read-only)"
  type        = string
}

variable "event_attendees_table_name" {
  description = "Name of the EventAttendees DynamoDB table (T-04); read-only here for P-16/P-17's mine=true match set"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "ARN of the EventAttendees DynamoDB table, for IAM (read-only, caller's own row only)"
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
  description = "CloudFront distribution's default domain, for signed photoUrl/thumbnailUrl construction (T-09)"
  type        = string
}

variable "cloudfront_signing_key_pair_id" {
  description = "CloudFront's ID for the public signing key, required to build a valid signed URL"
  type        = string
}

variable "cloudfront_signing_private_key_pem" {
  description = "Private half of the CloudFront signing key pair, set directly as this Lambda's env var"
  type        = string
  sensitive   = true
}

variable "cascade_delete_function_name" {
  description = "Function name of CascadeDelete (P-34/P-44/P-52), for delete/bulk-delete's invoke; empty until that module lands"
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
