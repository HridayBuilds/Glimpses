# Code not packaged/deployed by Terraform (T-06's deploy discipline): Jenkins builds the
# zip and pushes it to the deployment-artifacts bucket, then calls
# `aws lambda update-function-code` directly. Terraform only needs the object to exist at
# the function's initial creation — ignore_changes stops Terraform fighting the
# out-of-band code push on every apply.
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-upload-status"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "upload_status/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      JOBS_TABLE_NAME = var.jobs_table_name
      PHOTOS_BUCKET   = var.photos_bucket_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
