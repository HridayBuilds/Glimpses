output "user_pool_arn" {
  description = "User Pool ARN, for api_gateway's Cognito authorizer (provider_arns)"
  value       = aws_cognito_user_pool.this.arn
}

output "user_pool_id" {
  description = "User Pool ID, for the frontend's auth SDK configuration"
  value       = aws_cognito_user_pool.this.id
}

output "user_pool_client_id" {
  description = "App Client ID, for the frontend's auth SDK configuration"
  value       = aws_cognito_user_pool_client.this.id
}
