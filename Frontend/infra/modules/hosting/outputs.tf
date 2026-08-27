output "bucket_name" {
  value = aws_s3_bucket.hosting.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.hosting.arn
}

output "distribution_domain_name" {
  value = aws_cloudfront_distribution.hosting.domain_name
}

output "distribution_id" {
  value = aws_cloudfront_distribution.hosting.id
}
