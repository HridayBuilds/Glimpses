variable "aws_region" {
  description = "AWS region Glimpses deploys into. Parameterised to allow for multi-region deployments."
  type        = string
  default     = "ap-south-1"
}

variable "alarm_email" {
  description = "Email address subscribed to the shared operator-alerts SNS topic (T-07)"
  type        = string
  default     = "hridaymulchandani21@gmail.com"
}
