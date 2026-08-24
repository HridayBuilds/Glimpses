# Jenkins's push target for every Lambda's build.zip (T-06's deploy discipline) — Terraform
# only ever creates this bucket, never writes to it; the code push itself is a Jenkins
# `aws s3 cp`/`update-function-code` step, out of band.
resource "aws_s3_bucket" "deploy_artifacts" {
  bucket = "${var.name_prefix}-deploy-artifacts"
}

resource "aws_s3_bucket_public_access_block" "deploy_artifacts" {
  bucket                  = aws_s3_bucket.deploy_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
