
data "aws_iam_policy_document" "event_attendees_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query"]
    resources = [var.event_attendees_table_arn, "${var.event_attendees_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "event_attendees_access" {
  name   = "${var.name_prefix}-membership-event-attendees-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.event_attendees_access.json
}

data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.events_table_arn]
  }
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:Query"]
    resources = ["${var.events_table_arn}/index/accessCode-index"]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-membership-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

data "aws_iam_policy_document" "users_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:BatchGetItem"]
    resources = [var.users_table_arn]
  }
}

resource "aws_iam_role_policy" "users_access" {
  name   = "${var.name_prefix}-membership-users-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.users_access.json
}
