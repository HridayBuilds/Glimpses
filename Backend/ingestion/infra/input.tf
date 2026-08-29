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
  description = "Name of the Photos DynamoDB table (T-04), written by Extract"
  type        = string
}

variable "photos_table_arn" {
  description = "ARN of the Photos DynamoDB table, for IAM"
  type        = string
}

variable "events_table_name" {
  description = "Name of the Events DynamoDB table (T-04), read for the Rekognition collection ID"
  type        = string
}

variable "events_table_arn" {
  description = "ARN of the Events DynamoDB table, for IAM"
  type        = string
}

variable "faces_table_name" {
  description = "Name of the Faces DynamoDB table (T-04), written by IndexOnePhoto and resolved by MatchAttendees"
  type        = string
}

variable "faces_table_arn" {
  description = "ARN of the Faces DynamoDB table, for IAM"
  type        = string
}

variable "event_attendees_table_name" {
  description = "Name of the EventAttendees DynamoDB table (T-04 follow-up), written by MatchAttendees/MatchOneAttendee"
  type        = string
}

variable "event_attendees_table_arn" {
  description = "ARN of the EventAttendees DynamoDB table, for IAM"
  type        = string
}

variable "event_attendees_stream_arn" {
  description = "ARN of the EventAttendees table's DynamoDB Stream, source for the MatchOneAttendee trigger"
  type        = string
}

variable "users_table_name" {
  description = "Name of the Users DynamoDB table, read-only for uploader displayName/email snapshotting (P-99)"
  type        = string
}

variable "users_table_arn" {
  description = "ARN of the Users DynamoDB table, for IAM"
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

variable "heic_converter_function_name" {
  description = "Function name of the heic_converter Lambda, invoked synchronously to convert HEIC uploads (P-35)"
  type        = string
}

variable "heic_converter_function_arn" {
  description = "ARN of the heic_converter Lambda, for the invoke IAM grant"
  type        = string
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the shared operator-alerts SNS topic (T-07), subscribed alarms publish here"
  type        = string
}

variable "face_match_similarity_threshold" {
  description = "Minimum Rekognition SearchFacesByImage similarity score (0-100) for a face to count as a match in MatchAttendees/MatchOneAttendee"
  type        = number
  default     = 90
}
