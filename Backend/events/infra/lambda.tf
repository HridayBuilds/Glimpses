# Code is not packaged/deployed by Terraform (T-06's deploy discipline): Jenkins builds
# the zip and pushes it to the deployment-artifacts bucket, then calls
# `aws lambda update-function-code` directly. Terraform only needs the object to exist
# at s3_key for the function's initial creation — after that, ignore_changes below stops
# Terraform from fighting the out-of-band code push on every apply.
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-events"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "events/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      EVENTS_TABLE_NAME            = var.events_table_name
      PHOTOS_BUCKET                = var.photos_bucket_name
      CLOUDFRONT_DOMAIN            = var.cloudfront_domain_name
      CASCADE_DELETE_FUNCTION_NAME = var.cascade_delete_function_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
