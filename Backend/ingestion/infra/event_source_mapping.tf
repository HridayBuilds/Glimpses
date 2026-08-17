# MatchOneAttendee's trigger: a DynamoDB Stream on EventAttendees, filtered to the exact
# transition that means "someone just became ATTENDEE" — admit, open-policy join, and
# rejoin (P-46) alike, one SearchFaces call each. A matchedPhotoIDs-only write never
# matches this filter, which is what stops MatchAttendees' own writes from re-triggering
# this Lambda in a loop. Deliberately a Stream trigger, not a direct Membership invoke —
# Membership never gains an invoke permission and never learns matching exists (T-04's
# one-table-per-Lambda isolation).
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
