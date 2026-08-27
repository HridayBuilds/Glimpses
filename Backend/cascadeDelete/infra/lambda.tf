resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-cascade-delete"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "cascade_delete/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 120
  memory_size   = 512

  environment {
    variables = {
      EVENTS_TABLE_NAME          = var.events_table_name
      PHOTOS_TABLE_NAME          = var.photos_table_name
      FACES_TABLE_NAME           = var.faces_table_name
      EVENT_ATTENDEES_TABLE_NAME = var.event_attendees_table_name
      PHOTOS_BUCKET              = var.photos_bucket_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
