
data "aws_iam_policy_document" "jobs_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:Query"]
    resources = [var.jobs_table_arn, "${var.jobs_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "jobs_access" {
  name   = "${var.name_prefix}-upload-status-jobs-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.jobs_access.json
}

data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${var.photos_bucket_arn}/uploads/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-upload-status-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.events_table_arn]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-upload-status-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}
