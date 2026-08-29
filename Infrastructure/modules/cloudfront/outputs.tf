output "distribution_domain_name" {
  value = aws_cloudfront_distribution.photos.domain_name
}

output "distribution_id" {
  value = aws_cloudfront_distribution.photos.id
}

output "signing_key_pair_id" {
  description = "CloudFront's ID for the public signing key - required as part of a valid signature"
  value       = aws_cloudfront_public_key.photos_signing.id
}

output "signing_private_key_pem" {
  description = "Private half of the CloudFront signing key pair, passed straight into the gallery Lambda's environment"
  value       = tls_private_key.photos_signing.private_key_pem
  sensitive   = true
}
