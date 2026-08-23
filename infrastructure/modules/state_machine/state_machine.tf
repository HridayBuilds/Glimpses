locals {
  state_machine_name = "${var.name_prefix}-ingestion-pipeline"

  # Every Task invokes the same physical ingestion Lambda, branching internally on `step`
  # (Handler/handler.py). ResultSelector/OutputPath unwrap the lambda:invoke integration's
  # {Payload: ...} envelope so each Manager function's own return dict becomes the state's
  # plain output, matching what the next step's Manager function expects as its payload.
  definition = templatefile("${path.module}/templates/ingestion_pipeline.asl.json.tftpl", {
    ingestion_function_arn             = var.ingestion_function_arn
    db_api_function_arn                = var.db_api_function_arn
    rekognition_index_max_concurrency  = var.rekognition_index_max_concurrency
    rekognition_search_max_concurrency = var.rekognition_search_max_concurrency
  })
}

resource "aws_sfn_state_machine" "this" {
  name       = local.state_machine_name
  role_arn   = aws_iam_role.this.arn
  type       = "STANDARD"
  definition = local.definition
}
