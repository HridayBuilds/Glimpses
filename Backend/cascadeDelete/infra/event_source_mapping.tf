# P-77's automatic 60-day delete trigger: a DynamoDB Stream on Events, filtered to only
# genuine TTL expirations. AWS stamps a TTL-driven delete's stream record with
# userIdentity.type = "Service" / principalId = "dynamodb.amazonaws.com" — an
# application-driven DeleteItem (this Lambda's own delete_event_row call, or events'
# manual delete endpoint) never carries that field, so this filter is what stops
# CascadeDelete's own writes from re-triggering itself in a loop (same shape of
# self-trigger guard MatchOneAttendee's own filter already uses on EventAttendees).
resource "aws_lambda_event_source_mapping" "events_stream" {
  event_source_arn  = var.events_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["REMOVE"]
        userIdentity = {
          type        = ["Service"]
          principalId = ["dynamodb.amazonaws.com"]
        }
      })
    }
  }
}
