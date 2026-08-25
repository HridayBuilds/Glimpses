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
