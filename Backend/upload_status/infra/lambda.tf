resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-upload-status"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "upload_status/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      JOBS_TABLE_NAME   = var.jobs_table_name
      PHOTOS_BUCKET     = var.photos_bucket_name
      EVENTS_TABLE_NAME = var.events_table_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
