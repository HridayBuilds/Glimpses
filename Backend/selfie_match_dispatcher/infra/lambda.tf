resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-selfie-match-dispatcher"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "selfie_match_dispatcher/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      USERS_TABLE_NAME           = var.users_table_name
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      INGESTION_FUNCTION_NAME    = var.ingestion_function_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
