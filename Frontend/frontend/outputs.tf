output "bucket_name" {
  description = "Frontend hosting bucket name, for the Jenkins app job's S3 sync"
  value       = module.hosting.bucket_name
}

output "distribution_id" {
  description = "Frontend CloudFront distribution ID, for the Jenkins app job's cache invalidation"
  value       = module.hosting.distribution_id
}

output "distribution_domain_name" {
  description = "Frontend CloudFront domain name, the live URL for the deployed app"
  value       = module.hosting.distribution_domain_name
}
