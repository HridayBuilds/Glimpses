# Permissions derived from this Lambda's actual AWS calls only (T-07).

# GetItem/PutItem/UpdateItem for the CRUD endpoints, plus Query for all three GSIs
# (organizerID-status-index for list, accessCode-index for uniqueness checks,
# status-lastUploadAt-index for the archive sweep).
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query"]
    resources = [var.events_table_arn, "${var.events_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-events-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

# One bucket, prefix-scoped (T-09): qrcodes/ only — every other prefix is untouched by
# this Lambda.
data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${var.photos_bucket_arn}/qrcodes/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-events-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

# CreateCollection/DeleteCollection: no resource-level IAM scoping for Rekognition
# collection management (T-05).
data "aws_iam_policy_document" "rekognition_access" {
  statement {
    effect    = "Allow"
    actions   = ["rekognition:CreateCollection", "rekognition:DeleteCollection"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "rekognition_access" {
  name   = "${var.name_prefix}-events-rekognition-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.rekognition_access.json
}

# delete_event hands off the actual cascade to CascadeDelete (P-34) — this Lambda only
# ever fires the async InvocationType=Event call, never touches Photos/Faces/EventAttendees.
data "aws_iam_policy_document" "invoke_cascade_delete" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.cascade_delete_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_cascade_delete" {
  count  = var.cascade_delete_function_arn == "" ? 0 : 1
  name   = "${var.name_prefix}-events-invoke-cascade-delete"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_cascade_delete.json
}
