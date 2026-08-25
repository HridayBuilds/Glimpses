resource "aws_dynamodb_table" "event_attendees" {
  name         = "${var.name_prefix}-event-attendees"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userID"
  range_key    = "eventID"

  attribute {
    name = "userID"
    type = "S"
  }

  attribute {
    name = "eventID"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  global_secondary_index {
    name = "eventID-status-index"
    key_schema {
      attribute_name = "eventID"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "status"
      key_type       = "RANGE"
    }
    projection_type = "ALL"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}
