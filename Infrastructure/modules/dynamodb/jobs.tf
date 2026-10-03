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

  global_secondary_index {
    name = "eventUploaderKey-startedAt-index"
    key_schema {
      attribute_name = "eventUploaderKey"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "startedAt"
      key_type       = "RANGE"
    }
    projection_type = "ALL"
  }
}
