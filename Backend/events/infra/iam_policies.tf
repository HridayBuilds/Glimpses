
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:BatchGetItem"]
    resources = [var.events_table_arn, "${var.events_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-events-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

data "aws_iam_policy_document" "event_attendees_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:Query", "dynamodb:PutItem"]
    resources = [var.event_attendees_table_arn, "${var.event_attendees_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "event_attendees_access" {
  name   = "${var.name_prefix}-events-event-attendees-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.event_attendees_access.json
}

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
