resource "aws_s3_bucket" "hosting" {
  bucket = "${var.name_prefix}-frontend"
}

resource "aws_s3_bucket_public_access_block" "hosting" {
  bucket                  = aws_s3_bucket.hosting.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
