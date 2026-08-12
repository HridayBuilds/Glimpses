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

  # Serves CascadeDelete's single-photo lookup (Query eventID+photoID) and whole-event cleanup (Query eventID)
  global_secondary_index {
    name            = "eventID-photoID-index"
    hash_key        = "eventID"
    range_key       = "photoID"
    projection_type = "ALL"
  }
}
