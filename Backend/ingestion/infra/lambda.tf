# Code is not packaged/deployed by Terraform (T-06's deploy discipline): Jenkins builds
# the zip and pushes it to the deployment-artifacts bucket, then calls
# `aws lambda update-function-code` directly. Terraform only needs the object to exist
# at s3_key for the function's initial creation — after that, ignore_changes below stops
# Terraform from fighting the out-of-band code push on every apply.
resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-ingestion"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "ingestion/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 900 # per-photo/per-attendee step, but IndexFaces/SearchFaces round trips can be slow
  memory_size   = 512

  environment {
    variables = {
      PHOTOS_TABLE_NAME            = var.photos_table_name
      EVENTS_TABLE_NAME            = var.events_table_name
      FACES_TABLE_NAME             = var.faces_table_name
      EVENT_ATTENDEES_TABLE_NAME   = var.event_attendees_table_name
      USERS_TABLE_NAME             = var.users_table_name
      PHOTOS_BUCKET                = var.photos_bucket_name
      HEIC_CONVERTER_FUNCTION_NAME = var.heic_converter_function_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
