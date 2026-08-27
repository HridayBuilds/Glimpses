resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-membership"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "membership/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      EVENTS_TABLE_NAME          = var.events_table_name
      USERS_TABLE_NAME           = var.users_table_name
      CLOUDFRONT_DOMAIN          = var.cloudfront_domain_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
