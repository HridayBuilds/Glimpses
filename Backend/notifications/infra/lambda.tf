resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-notifications"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "notifications/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 300
  memory_size   = 256

  environment {
    variables = {
      USERS_TABLE_NAME           = var.users_table_name
      EVENTS_TABLE_NAME          = var.events_table_name
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      NOTIFICATIONS_TABLE_NAME   = var.notifications_table_name
      SES_SENDER_EMAIL           = var.sender_email
      FRONTEND_URL               = "https://${var.frontend_domain_name}"
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
