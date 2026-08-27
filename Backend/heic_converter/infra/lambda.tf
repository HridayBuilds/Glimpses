resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-heic-converter"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "heic_converter/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 120
  memory_size   = 512

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
