output "invoke_url" {
  description = "Base invoke URL for the prod stage (default execute-api URL, no custom domain per 2026-08-24 ruling)"
  value       = aws_api_gateway_stage.prod.invoke_url
}

output "rest_api_id" {
  value = aws_api_gateway_rest_api.this.id
}
