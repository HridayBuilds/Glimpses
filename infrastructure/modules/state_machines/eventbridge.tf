data "aws_iam_policy_document" "eventbridge_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eventbridge_start_execution" {
  name               = "${var.name_prefix}-ingestion-trigger-role"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role.json
}

data "aws_iam_policy_document" "eventbridge_start_execution" {
  statement {
    effect    = "Allow"
    actions   = ["states:StartExecution"]
    resources = [aws_sfn_state_machine.this.arn]
  }
}

resource "aws_iam_role_policy" "eventbridge_start_execution" {
  name   = "${var.name_prefix}-ingestion-trigger-policy"
  role   = aws_iam_role.eventbridge_start_execution.id
  policy = data.aws_iam_policy_document.eventbridge_start_execution.json
}

# T-09: S3 Event Notification -> EventBridge -> StartExecution directly, no glue Lambda, no
# client "upload complete" callback. A wildcard match, not separate prefix+suffix
# conditions — EventBridge's content filtering can't AND two conditions on the same field —
# against the exact upload key shape: uploads/event/{eventID}/user/{userId}/job/{jobId}/original.zip (T-09).
resource "aws_cloudwatch_event_rule" "upload_complete" {
  name = "${var.name_prefix}-upload-complete"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [var.photos_bucket_name]
      }
      object = {
        key = [
          { wildcard = "uploads/event/*/user/*/job/*/original.zip" }
        ]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "start_ingestion" {
  rule     = aws_cloudwatch_event_rule.upload_complete.name
  arn      = aws_sfn_state_machine.this.arn
  role_arn = aws_iam_role.eventbridge_start_execution.arn

  input_transformer {
    input_paths = {
      bucket = "$.detail.bucket.name"
      key    = "$.detail.object.key"
    }
    input_template = "{\"bucket\": <bucket>, \"key\": <key>}"
  }
}
