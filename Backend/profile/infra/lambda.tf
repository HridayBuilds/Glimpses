resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-profile"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "profile/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      USERS_TABLE_NAME = var.users_table_name
      PHOTOS_BUCKET    = var.photos_bucket_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
