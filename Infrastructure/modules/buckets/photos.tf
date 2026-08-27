resource "aws_s3_bucket" "photos" {
  bucket = "${var.name_prefix}-photos"
}

resource "aws_s3_bucket_public_access_block" "photos" {
  bucket                  = aws_s3_bucket.photos.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "photos" {
  bucket = aws_s3_bucket.photos.id

  cors_rule {
    allowed_methods = ["GET", "PUT", "HEAD"]
    allowed_origins = ["*"]
    allowed_headers = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "photos_eventbridge" {
  bucket      = aws_s3_bucket.photos.id
  eventbridge = true
}

resource "aws_s3_bucket_lifecycle_configuration" "photos" {
  bucket = aws_s3_bucket.photos.id

  rule {
    id     = "expire-downloads"
    status = "Enabled"

    filter {
      prefix = "downloads/"
    }

    expiration {
      days = var.downloads_expiration_days
    }
  }
}
