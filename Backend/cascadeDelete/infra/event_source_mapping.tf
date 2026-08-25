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
