resource "aws_lambda_event_source_mapping" "event_attendees_stream" {
  event_source_arn  = var.event_attendees_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"

  filter_criteria {
    filter {
      # Existing attendee row transitioning onto ATTENDEE (approval, rejoin).
      pattern = jsonencode({
        dynamodb = {
          OldImage = {
            status = { S = [{ "anything-but" = "ATTENDEE" }] }
          }
          NewImage = {
            status = { S = ["ATTENDEE"] }
          }
        }
      })
    }
    filter {
      # Brand-new row created directly at ATTENDEE (e.g. first-time OPEN-policy join) -
      # an INSERT has no OldImage, so the transition pattern above can't match it.
      pattern = jsonencode({
        eventName = ["INSERT"]
        dynamodb = {
          NewImage = {
            status = { S = ["ATTENDEE"] }
          }
        }
      })
    }
  }
}
