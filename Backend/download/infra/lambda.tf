# Code is not packaged/deployed by Terraform (T-06's deploy discipline): Jenkins builds
# the zip and pushes it to the deployment-artifacts bucket, then calls
# `aws lambda update-function-code` directly. Terraform only needs the object to exist
# at s3_key for the function's initial creation — after that, ignore_changes below stops
# Terraform from fighting the out-of-band code push on every apply.
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-download"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "download/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 900 # P-93's 1,000-photo/event ceiling estimates a few minutes to build; capped at Lambda's own max
  memory_size   = 512

  environment {
    variables = {
      DOWNLOADS_TABLE_NAME = var.downloads_table_name
      PHOTOS_TABLE_NAME    = var.photos_table_name
      PHOTOS_BUCKET        = var.photos_bucket_name
      FUNCTION_NAME        = "${var.name_prefix}-download" # for the build step's self-invoke
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
