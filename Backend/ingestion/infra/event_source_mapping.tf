resource "aws_lambda_event_source_mapping" "event_attendees_stream" {
  event_source_arn  = var.event_attendees_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"

  filter_criteria {
    filter {
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
  }
}
