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

output "signing_private_key_parameter_name" {
  description = "SSM parameter name holding the private signing key - the gallery Lambda reads this at runtime"
  value       = aws_ssm_parameter.photos_signing_private_key.name
}

output "signing_private_key_parameter_arn" {
  description = "SSM parameter ARN, for IAM scoping on whichever Lambda is granted read access"
  value       = aws_ssm_parameter.photos_signing_private_key.arn
}

output "ssm_default_kms_key_arn" {
  description = "Account-default SSM KMS key ARN - kms:Decrypt on this is also required to read the SecureString"
  value       = data.aws_kms_alias.ssm_default.target_key_arn
}
