output "function_name" {
  description = "Lambda function name, for CI/CD and cross-Lambda references"
  value       = aws_lambda_function.this.function_name
}

output "function_arn" {
  description = "Lambda ARN, for callers' IAM policies (lambda:InvokeFunction grants)"
  value       = aws_lambda_function.this.arn
}
