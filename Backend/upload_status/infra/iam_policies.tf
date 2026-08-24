# Permissions derived from this Lambda's actual AWS calls only (T-07).

# Read-only: this Lambda never writes Jobs — InitializeJob/the status updates all live
# in db_api. GetItem for /jobs/{jobId}/status, Query on the eventUploaderKey GSI for
# /jobs/latest.
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

# Prefix-scoped (T-09): mints a pre-signed PUT for the browser's zip upload only —
# this Lambda never reads or deletes objects, just signs the one PUT the browser
# performs directly against S3.
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
