resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-ingestion"
  s3_bucket     = var.deploy_artifacts_bucket
  s3_key        = "ingestion/build.zip"
  handler       = "routeHandler.lambda_handler"
  runtime       = "python3.13"
  architectures = ["x86_64"]
  role          = aws_iam_role.this.arn
  timeout       = 300
  memory_size   = 1024

  environment {
    variables = {
      PHOTOS_TABLE_NAME               = var.photos_table_name
      EVENTS_TABLE_NAME               = var.events_table_name
      FACES_TABLE_NAME                = var.faces_table_name
      EVENT_ATTENDEES_TABLE_NAME      = var.event_attendees_table_name
      USERS_TABLE_NAME                = var.users_table_name
      PHOTOS_BUCKET                   = var.photos_bucket_name
      HEIC_CONVERTER_FUNCTION_NAME    = var.heic_converter_function_name
      FACE_MATCH_SIMILARITY_THRESHOLD = tostring(var.face_match_similarity_threshold)
    }
  }

  lifecycle {
    ignore_changes = [s3_key, source_code_hash]
  }
}
