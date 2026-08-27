resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-download"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "download/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 300
  memory_size   = 1024

  environment {
    variables = {
      DOWNLOADS_TABLE_NAME = var.downloads_table_name
      PHOTOS_TABLE_NAME    = var.photos_table_name
      PHOTOS_BUCKET        = var.photos_bucket_name
      FUNCTION_NAME        = "${var.name_prefix}-download"
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
