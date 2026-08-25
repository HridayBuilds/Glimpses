resource "aws_dynamodb_table" "downloads" {
  name         = "${var.name_prefix}-downloads"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "downloadId"

  attribute {
    name = "downloadId"
    type = "S"
  }
}
