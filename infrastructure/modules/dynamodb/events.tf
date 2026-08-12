resource "aws_dynamodb_table" "events" {
  name         = "${var.name_prefix}-events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "eventID"

  stream_enabled   = true
  stream_view_type = "OLD_IMAGE"

  attribute {
    name = "eventID"
    type = "S"
  }

  attribute {
    name = "organizerID"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "accessCode"
    type = "S"
  }

  attribute {
    name = "lastUploadAt"
    type = "S"
  }

  # Organizer dashboard: "show this organizer their events"
  global_secondary_index {
    name            = "organizerID-status-index"
    hash_key        = "organizerID"
    range_key       = "status"
    projection_type = "ALL"
  }

  # Join flow: "which event does this access code belong to"
  global_secondary_index {
    name            = "accessCode-index"
    hash_key        = "accessCode"
    projection_type = "ALL"
  }

  # P-77/P-78 archive sweep: "which ACTIVE events are >30 days past their last upload"
  global_secondary_index {
    name            = "status-lastUploadAt-index"
    hash_key        = "status"
    range_key       = "lastUploadAt"
    projection_type = "ALL"
  }

  # P-77: archive-to-delete TTL, attribute written at archive time (archivedAt + 30d)
  ttl {
    attribute_name = "deleteAt"
    enabled        = true
  }
}
