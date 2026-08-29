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
    trusted_key_groups     = [aws_cloudfront_key_group.photos_signing.id]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  ordered_cache_behavior {
    path_pattern           = "qrcodes/*"
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
