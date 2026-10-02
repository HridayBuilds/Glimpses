data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
locals {
  state_machine_name = "${var.name_prefix}-drive-import"
  state_machine_arn  = "arn:aws:states:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:stateMachine:${local.state_machine_name}"
  parameter_arn      = "arn:aws:ssm:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:parameter${var.drive_api_key_parameter}"
}
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-drive-import"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "drive_import/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 300
  memory_size   = 1024
  environment {
    variables = {
      JOBS_TABLE_NAME            = var.jobs_table_name
      DB_API_FUNCTION_NAME       = var.db_api_function_arn
      EVENTS_TABLE_NAME          = var.events_table_name
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      USERS_TABLE_NAME           = var.users_table_name
      PHOTOS_BUCKET              = var.photos_bucket_name
      DRIVE_API_KEY_PARAMETER    = var.drive_api_key_parameter
      DRIVE_STATE_MACHINE_ARN    = local.state_machine_arn
    }
  }
  lifecycle { ignore_changes = [s3_key, source_code_hash] }
}
