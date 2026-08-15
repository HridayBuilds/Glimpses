# T-09: CloudFront + Origin Access Control (OAC) in front of the shared photos bucket.
# The distribution itself doesn't restrict by prefix — the bucket policy below is the
# real enforcement boundary, scoping the OAC's grant to exactly photos/, thumbnails/,
# qrcodes/. uploads/, selfies/, downloads/ stay unreachable through CloudFront even if a
# valid-looking path is guessed, since S3 rejects the OAC's request outside those prefixes.
resource "aws_cloudfront_origin_access_control" "photos" {
  name                              = "${var.name_prefix}-photos-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "photos" {
  enabled = true

  origin {
    domain_name              = var.photos_bucket_regional_domain_name
    origin_id                = "photos-bucket"
    origin_access_control_id = aws_cloudfront_origin_access_control.photos.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "photos-bucket"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# The actual enforcement: grants the OAC identity s3:GetObject on exactly photos/,
# thumbnails/, qrcodes/ — every other prefix is never granted, not merely unlinked.
data "aws_iam_policy_document" "photos_oac_access" {
  statement {
    effect  = "Allow"
    actions = ["s3:GetObject"]
    resources = [
      "${var.photos_bucket_arn}/photos/*",
      "${var.photos_bucket_arn}/thumbnails/*",
      "${var.photos_bucket_arn}/qrcodes/*",
    ]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.photos.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "photos_oac_access" {
  bucket = var.photos_bucket_name
  policy = data.aws_iam_policy_document.photos_oac_access.json
}
