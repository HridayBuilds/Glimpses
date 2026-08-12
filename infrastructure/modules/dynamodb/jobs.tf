resource "aws_dynamodb_table" "jobs" {
  name         = "${var.name_prefix}-jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "jobId"

  attribute {
    name = "jobId"
    type = "S"
  }

  attribute {
    name = "eventUploaderKey"
    type = "S"
  }

  attribute {
    name = "startedAt"
    type = "S"
  }

  # "This uploader's own most recent job in this event" (P-100), no cross-uploader mixing
  global_secondary_index {
    name            = "eventUploaderKey-startedAt-index"
    hash_key        = "eventUploaderKey"
    range_key       = "startedAt"
    projection_type = "ALL"
  }
}
