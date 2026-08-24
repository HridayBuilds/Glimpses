variable "name_prefix" {
  description = "Prefix applied to the topic's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "alarm_email" {
  description = "Email address subscribed to the shared operator-alerts SNS topic (T-07) — every Lambda's error alarm publishes here"
  type        = string
}
