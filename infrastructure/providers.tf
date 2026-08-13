terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # T-06: S3 backend, native locking (no DynamoDB lock table).
  # Backend config cannot reference variables, so bucket/region are literals here
  # even though provider region below is parameterised.
  backend "s3" {
    bucket       = "glimpses-terraform-state"
    key          = "glimpses/terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}
