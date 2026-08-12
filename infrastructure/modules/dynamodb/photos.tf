resource "aws_dynamodb_table" "photos" {
  name         = "${var.name_prefix}-photos"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "photoID"

  attribute {
    name = "photoID"
    type = "S"
  }

  attribute {
    name = "eventID"
    type = "S"
  }

  attribute {
    name = "uploadedAtFilename"
    type = "S"
  }

  attribute {
    name = "contentHash"
    type = "S"
  }

  # Gallery, newest-first, filename tiebreak; DynamoDB's own LastEvaluatedKey is the cursor (P-57/P-16)
  global_secondary_index {
    name            = "eventID-uploadedAtFilename-index"
    hash_key        = "eventID"
    range_key       = "uploadedAtFilename"
    projection_type = "ALL"
  }

  # Per-event duplicate check (P-38)
  global_secondary_index {
    name            = "eventID-contentHash-index"
    hash_key        = "eventID"
    range_key       = "contentHash"
    projection_type = "ALL"
  }
}
