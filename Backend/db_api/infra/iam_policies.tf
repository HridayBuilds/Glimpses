data "aws_iam_policy_document" "jobs_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem"]
    resources = [var.jobs_table_arn]
  }
}

resource "aws_iam_role_policy" "jobs_access" {
  name   = "${var.name_prefix}-db-api-jobs-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.jobs_access.json
}
