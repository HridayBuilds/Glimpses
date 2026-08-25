
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem"]
    resources = [var.events_table_arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:DescribeStream", "dynamodb:ListStreams"]
    resources = [var.events_stream_arn]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-cascade-delete-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

data "aws_iam_policy_document" "photos_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:DeleteItem", "dynamodb:BatchWriteItem", "dynamodb:Query"]
    resources = [var.photos_table_arn, "${var.photos_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "photos_access" {
  name   = "${var.name_prefix}-cascade-delete-photos-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_access.json
}

data "aws_iam_policy_document" "faces_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:Query", "dynamodb:BatchWriteItem"]
    resources = [var.faces_table_arn, "${var.faces_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "faces_access" {
  name   = "${var.name_prefix}-cascade-delete-faces-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.faces_access.json
}

data "aws_iam_policy_document" "event_attendees_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:Query", "dynamodb:BatchWriteItem"]
    resources = [var.event_attendees_table_arn, "${var.event_attendees_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "event_attendees_access" {
  name   = "${var.name_prefix}-cascade-delete-event-attendees-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.event_attendees_access.json
}

data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:DeleteObject"]
    resources = ["${var.photos_bucket_arn}/photos/*", "${var.photos_bucket_arn}/thumbnails/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-cascade-delete-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

data "aws_iam_policy_document" "rekognition_access" {
  statement {
    effect    = "Allow"
    actions   = ["rekognition:DeleteCollection", "rekognition:DeleteFaces"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "rekognition_access" {
  name   = "${var.name_prefix}-cascade-delete-rekognition-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.rekognition_access.json
}
