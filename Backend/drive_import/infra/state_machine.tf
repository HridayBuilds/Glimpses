locals {
  ingestion = jsondecode(templatefile("${path.module}/../../../Infrastructure/modules/state_machine/templates/ingestion_pipeline.asl.json.tftpl", {
    ingestion_function_arn             = var.ingestion_function_arn
    db_api_function_arn                = var.db_api_function_arn
    photos_bucket_name                 = var.photos_bucket_name
    photo_processing_max_concurrency   = 4
    rekognition_index_max_concurrency  = 5
    rekognition_search_max_concurrency = 5
  }))
  drive_states = jsondecode(templatefile("${path.module}/drive_states.json.tftpl", {
    drive_function_arn = aws_lambda_function.this.arn
    photos_bucket_name = var.photos_bucket_name
  }))
  shared_states = { for name, state in local.ingestion.States : name => state if !contains(["InitializeJob", "UpdateStatusExtracting", "StageUpload"], name) }
  drive_definition = {
    Comment       = "Public flat Drive folder import, reusing the ingestion processing states."
    QueryLanguage = "JSONata"
    StartAt       = "DriveInitialize"
    States = merge(local.shared_states, local.drive_states, {
      SummarizeResults = merge(local.ingestion.States.SummarizeResults, { Next = "DriveCombine" })
      MatchAttendees = merge(local.ingestion.States.MatchAttendees, { ToleratedFailurePercentage = 0 })
    })
  }
}
resource "aws_sfn_state_machine" "drive" {
  name       = local.state_machine_name
  role_arn   = aws_iam_role.workflow.arn
  type       = "STANDARD"
  definition = jsonencode(local.drive_definition)
  depends_on = [aws_iam_role_policy.workflow_access, aws_iam_role_policy.access]
}
resource "aws_cloudwatch_metric_alarm" "workflow_errors" {
  alarm_name          = "${var.name_prefix}-drive-import-workflow-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ExecutionsFailed"
  namespace           = "AWS/States"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  dimensions          = { StateMachineArn = aws_sfn_state_machine.drive.arn }
  alarm_actions       = [var.alarm_sns_topic_arn]
}
