# Permissions derived from this Lambda's actual AWS calls only (T-07). This is the one
# Lambda in the system trusted with any multi-table delete cascade — every grant below
# stays scoped to exactly the tables/prefixes its own two actions touch.

# get_event (both actions), decrement_event_counters (delete_photos), delete_event_row
# and the TTL Stream's own trigger source (delete_event).
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

# get_photo/delete_photo_row (delete_photos), query_photos_by_event/batch_delete_photos
# (delete_event, via the gallery GSI) — BatchWriteItem is what boto3's batch_writer()
# actually issues under the hood for its per-item delete_item calls.
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

# query_faces_by_event/query_faces_by_event_and_photo (eventID-photoID-index),
# batch_delete_faces (BatchWriteItem via batch_writer()).
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

# query_attendees_by_event (eventID-status-index), batch_delete_attendees — whole-event
# teardown only (2026-08-24 ruling); delete_photos never touches this table at all.
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

# One bucket, prefix-scoped (T-09): delete-only, photos/ and thumbnails/ only — every
# other prefix is untouched by this Lambda.
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

# T-05: DeleteCollection (delete_event) and DeleteFaces (delete_photos) — no
# resource-level IAM scoping for Rekognition collection operations.
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
