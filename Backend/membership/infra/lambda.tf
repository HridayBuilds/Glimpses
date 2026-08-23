# Code is not packaged/deployed by Terraform (T-06's deploy discipline): Jenkins builds
# the zip and pushes it to the deployment-artifacts bucket, then calls
# `aws lambda update-function-code` directly. Terraform only needs the object to exist
# at s3_key for the function's initial creation — after that, ignore_changes below stops
# Terraform from fighting the out-of-band code push on every apply.
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-membership"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "membership/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      EVENTS_TABLE_NAME          = var.events_table_name
      USERS_TABLE_NAME           = var.users_table_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
