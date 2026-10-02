resource "aws_lambda_event_source_mapping" "attendees" {
  event_source_arn  = var.event_attendees_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"
  batch_size        = 10
}

resource "aws_lambda_event_source_mapping" "jobs" {
  event_source_arn  = var.jobs_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"
  batch_size        = 10
}

resource "aws_lambda_event_source_mapping" "events" {
  event_source_arn  = var.events_stream_arn
  function_name     = aws_lambda_function.this.arn
  starting_position = "LATEST"
  batch_size        = 10
}
