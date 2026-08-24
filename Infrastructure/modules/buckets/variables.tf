variable "name_prefix" {
  description = "Prefix applied to every bucket's AWS-visible name, matching T-06's naming convention"
  type        = string
  default     = "glimpses"
}

variable "downloads_expiration_days" {
  description = "Lifecycle-expiry window for built zip objects under downloads/ (T-09/T-04 follow-up, default 48h)"
  type        = number
  default     = 2
}
