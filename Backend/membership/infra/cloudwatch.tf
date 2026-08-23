resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 3 # T-07: log_event=True captures request data, so retention is kept short
}

# T-07: identical alarm shape on every Lambda — Errors > 0 over 5 minutes, wired to the
# shared operator-alerts SNS topic. Lives in this Lambda's own module so a new Lambda's
# alarm ships with it, never a separately-remembered central list.
resource "aws_cloudwatch_metric_alarm" "errors" {
  alarm_name          = "${var.name_prefix}-membership-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  dimensions = {
    FunctionName = aws_lambda_function.this.function_name
  }
  alarm_actions = [var.alarm_sns_topic_arn]
}
