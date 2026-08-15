# One bucket, six prefixes (T-09) — uploads/, photos/, thumbnails/, selfies/, qrcodes/,
# downloads/. All public access is blocked here; CloudFront's read access to photos/,
# thumbnails/, qrcodes/ is granted by the cloudfront module's own bucket policy, not here,
# to avoid a circular dependency between this module and the OAC it's scoped to.
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

# T-04/T-09 follow-up: built zip objects are stored artifacts with a lifecycle, not kept
# indefinitely — matches the download Lambda's ruled 48h default.
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
