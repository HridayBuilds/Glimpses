resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-events"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "events/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 60
  memory_size   = 256

  environment {
    variables = {
      EVENTS_TABLE_NAME            = var.events_table_name
      EVENT_ATTENDEES_TABLE_NAME   = var.event_attendees_table_name
      PHOTOS_BUCKET                = var.photos_bucket_name
      CLOUDFRONT_DOMAIN            = var.cloudfront_domain_name
      FRONTEND_DOMAIN              = var.frontend_domain_name
      CASCADE_DELETE_FUNCTION_NAME = var.cascade_delete_function_name
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
