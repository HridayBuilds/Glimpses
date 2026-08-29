locals {
  state_machine_name = "${var.name_prefix}-ingestion-pipeline"

  definition = templatefile("${path.module}/templates/ingestion_pipeline.asl.json.tftpl", {
    ingestion_function_arn             = var.ingestion_function_arn
    db_api_function_arn                = var.db_api_function_arn
    rekognition_index_max_concurrency  = var.rekognition_index_max_concurrency
    rekognition_search_max_concurrency = var.rekognition_search_max_concurrency
    photo_processing_max_concurrency   = var.photo_processing_max_concurrency
    photos_bucket_name                 = var.photos_bucket_name
  })
}

resource "aws_sfn_state_machine" "this" {
  name       = local.state_machine_name
  role_arn   = aws_iam_role.this.arn
  type       = "STANDARD"
  definition = local.definition
}
