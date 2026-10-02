resource "aws_dynamodb_table" "notifications" {
  name         = "${var.name_prefix}-notifications"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "notificationID"

  attribute {
    name = "notificationID"
    type = "S"
  }

  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }
}
