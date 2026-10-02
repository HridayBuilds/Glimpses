data "aws_iam_policy_document" "read_membership" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:Query"]
    resources = [var.event_attendees_table_arn]
  }
}

resource "aws_iam_role_policy" "read_membership" {
  name   = "${var.name_prefix}-selfie-match-dispatcher-read-membership"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.read_membership.json
}

data "aws_iam_policy_document" "read_user" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.users_table_arn]
  }
}

resource "aws_iam_role_policy" "read_user" {
  name   = "${var.name_prefix}-selfie-match-dispatcher-read-user"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.read_user.json
}

data "aws_iam_policy_document" "invoke_ingestion" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.ingestion_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_ingestion" {
  name   = "${var.name_prefix}-selfie-match-dispatcher-invoke-ingestion"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_ingestion.json
}
