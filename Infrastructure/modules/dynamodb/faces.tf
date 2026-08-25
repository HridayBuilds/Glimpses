resource "aws_dynamodb_table" "faces" {
  name         = "${var.name_prefix}-faces"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "rekognitionFaceID"

  attribute {
    name = "rekognitionFaceID"
    type = "S"
  }

  attribute {
    name = "eventID"
    type = "S"
  }

  attribute {
    name = "photoID"
    type = "S"
  }

  global_secondary_index {
    name = "eventID-photoID-index"
    key_schema {
      attribute_name = "eventID"
      key_type       = "HASH"
    }
    key_schema {
      attribute_name = "photoID"
      key_type       = "RANGE"
    }
    projection_type = "ALL"
  }
}
