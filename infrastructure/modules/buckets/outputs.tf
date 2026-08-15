output "deploy_artifacts_bucket_name" {
  value = aws_s3_bucket.deploy_artifacts.bucket
}

output "deploy_artifacts_bucket_arn" {
  value = aws_s3_bucket.deploy_artifacts.arn
}

output "photos_bucket_name" {
  value = aws_s3_bucket.photos.bucket
}

output "photos_bucket_arn" {
  value = aws_s3_bucket.photos.arn
}

output "photos_bucket_regional_domain_name" {
  value = aws_s3_bucket.photos.bucket_regional_domain_name
}
