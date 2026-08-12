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

  # Organizer's lobby (status=PENDING) / roster (status=ATTENDEE); also MatchAttendees' "who's admitted" lookup
  global_secondary_index {
    name            = "eventID-status-index"
    hash_key        = "eventID"
    range_key       = "status"
    projection_type = "ALL"
  }
}
