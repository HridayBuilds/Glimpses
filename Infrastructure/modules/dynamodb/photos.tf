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

  global_secondary_index {
    name = "eventID-uploadedAtFilename-index"
    key_schema {
      attribute_name = "eventID"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "uploadedAtFilename"
      key_type       = "RANGE"
    }
    projection_type = "ALL"
  }

  global_secondary_index {
    name = "eventID-contentHash-index"
    key_schema {
      attribute_name = "eventID"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "contentHash"
      key_type       = "RANGE"
    }
    projection_type = "ALL"
  }
}
