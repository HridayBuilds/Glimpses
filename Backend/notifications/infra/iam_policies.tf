data "aws_iam_policy_document" "access" {
  statement {
    actions   = ["dynamodb:GetItem"]
    resources = [var.users_table_arn, var.events_table_arn]
  }

  statement {
    actions   = ["dynamodb:Query"]
    resources = ["${var.event_attendees_table_arn}/index/eventID-status-index"]
  }

  statement {
    actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem"]
    resources = [var.notifications_table_arn]
  }

  statement {
    actions   = ["dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:DescribeStream", "dynamodb:ListStreams"]
    resources = [var.event_attendees_stream_arn, var.events_stream_arn, var.jobs_stream_arn]
  }

  statement {
    actions   = ["ses:SendEmail"]
    resources = [var.sender_identity_arn]
  }
}

resource "aws_iam_role_policy" "access" {
  name   = "${var.name_prefix}-notifications-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.access.json
}
