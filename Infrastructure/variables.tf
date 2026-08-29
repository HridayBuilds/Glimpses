variable "aws_region" {
  description = "AWS region Glimpses deploys into. Parameterised to allow for multi-region deployments."
  type        = string
  default     = "ap-south-1"
}

variable "alarm_email" {
  description = "Email address subscribed to the shared operator-alerts SNS topic (T-07)"
  type        = string
  default     = "johndoe@gmail.com"
}

variable "frontend_domain_name" {
  description = "Frontend app's CloudFront distribution's default domain, fetched by Jenkins from Frontend/frontend's own Terraform state and passed in at apply time. Only module.events consumes it, but Terraform resolves every root variable before honoring -target, so every other per-module Jenkins job needs a default here to keep applying."
  type        = string
  default     = ""
}
