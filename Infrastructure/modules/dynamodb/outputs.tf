output "table_names" {
  description = "Map of entity name to DynamoDB table name, for per-Lambda IAM policies."
  value = {
    users           = aws_dynamodb_table.users.name
    events          = aws_dynamodb_table.events.name
    jobs            = aws_dynamodb_table.jobs.name
    photos          = aws_dynamodb_table.photos.name
    faces           = aws_dynamodb_table.faces.name
    event_attendees = aws_dynamodb_table.event_attendees.name
    downloads       = aws_dynamodb_table.downloads.name
  }
}

output "table_arns" {
  description = "Map of entity name to DynamoDB table ARN, for per-Lambda IAM policies."
  value = {
    users           = aws_dynamodb_table.users.arn
    events          = aws_dynamodb_table.events.arn
    jobs            = aws_dynamodb_table.jobs.arn
    photos          = aws_dynamodb_table.photos.arn
    faces           = aws_dynamodb_table.faces.arn
    event_attendees = aws_dynamodb_table.event_attendees.arn
    downloads       = aws_dynamodb_table.downloads.arn
  }
}

output "events_stream_arn" {
  description = "Events table's DynamoDB Stream ARN, for CascadeDelete's event-source-mapping."
  value       = aws_dynamodb_table.events.stream_arn
}

output "event_attendees_stream_arn" {
  description = "EventAttendees table's DynamoDB Stream ARN, for MatchOneAttendee's event-source-mapping."
  value       = aws_dynamodb_table.event_attendees.stream_arn
}
