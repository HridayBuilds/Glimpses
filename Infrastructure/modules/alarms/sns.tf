# T-07: one shared operator-alerts topic, every Lambda's CloudWatch error alarm (Errors >
# 0 over 5 minutes) is wired to it in that Lambda's own infra/cloudwatch.tf.
resource "aws_sns_topic" "alerts" {
  name = "${var.name_prefix}-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}
