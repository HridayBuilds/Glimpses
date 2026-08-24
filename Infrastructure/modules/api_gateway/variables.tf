variable "name_prefix" {
  description = "Prefix applied to every resource's AWS-visible name (T-06)"
  type        = string
  default     = "glimpses"
}

variable "aws_region" {
  description = "AWS region, needed to build each Lambda integration's URI"
  type        = string
  default     = "ap-south-1"
}

variable "cognito_user_pool_arn" {
  description = "User Pool ARN from the cognito module, wired into the REST API's Cognito authorizer"
  type        = string
}

variable "profile_function_name" {
  type = string
}
variable "profile_function_arn" {
  type = string
}

variable "events_function_name" {
  type = string
}
variable "events_function_arn" {
  type = string
}

variable "membership_function_name" {
  type = string
}
variable "membership_function_arn" {
  type = string
}

variable "upload_status_function_name" {
  type = string
}
variable "upload_status_function_arn" {
  type = string
}

variable "gallery_function_name" {
  type = string
}
variable "gallery_function_arn" {
  type = string
}

variable "download_function_name" {
  type = string
}
variable "download_function_arn" {
  type = string
}
