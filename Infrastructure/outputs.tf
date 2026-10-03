output "cognito_user_pool_id" {
  description = "User Pool ID, for the frontend's .env.production"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "App Client ID, for the frontend's .env.production"
  value       = module.cognito.user_pool_client_id
}

output "api_gateway_invoke_url" {
  description = "API base URL, for the frontend's .env.production"
  value       = module.api_gateway.invoke_url
}
