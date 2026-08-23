# Permissions derived from this Lambda's actual AWS calls only (T-07).

# EventAttendees is Membership's own table: GetItem/PutItem/UpdateItem for join/leave/
# admit/deny/eject, plus Query on eventID-status-index for the roster/lobby list.
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

# Read-only Events grant, ruled 2026-08-23: join needs joinPolicy/status, and the
# roster/lobby/admit/deny/eject endpoints need organizerID for authorization. Membership
# never writes Events — write ownership stays exclusively with the events Lambda.
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.events_table_arn]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-membership-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

# Read-only Users grant, ruled 2026-08-23: P-82's roster/lobby screen needs display name
# and email, read live (BatchGetItem) at roster-read time rather than snapshotted, since
# P-84 makes displayName freely editable and a snapshot would go stale.
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
