# Permissions derived from this Lambda's actual AWS calls only (T-07).

# Extract writes new rows + queries the dedup GSI; nothing else in this Lambda touches Photos.
data "aws_iam_policy_document" "photos_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem", "dynamodb:Query"]
    resources = [var.photos_table_arn, "${var.photos_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "photos_access" {
  name   = "${var.name_prefix}-ingestion-photos-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_access.json
}

# IndexOnePhoto/MatchAttendees read the event's Rekognition collection ID; Extract increments counters.
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:UpdateItem"]
    resources = [var.events_table_arn]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-ingestion-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

# IndexOnePhoto writes one row per indexed face; MatchAttendees/MatchOneAttendee resolve
# SearchFaces hits back to photoIDs via GetItem/BatchGetItem on the PK (rekognitionFaceID) —
# no GSI needed for that direction (T-04 follow-up).
data "aws_iam_policy_document" "faces_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem", "dynamodb:BatchGetItem"]
    resources = [var.faces_table_arn]
  }
}

resource "aws_iam_role_policy" "faces_access" {
  name   = "${var.name_prefix}-ingestion-faces-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.faces_access.json
}

# MatchAttendees/MatchOneAttendee write the matchedPhotoIDs String Set; the row itself is
# never read here (the trigger delivers the changed keys via the DynamoDB Stream record).
data "aws_iam_policy_document" "event_attendees_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:UpdateItem"]
    resources = [var.event_attendees_table_arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:DescribeStream", "dynamodb:ListStreams"]
    resources = [var.event_attendees_stream_arn]
  }
}

resource "aws_iam_role_policy" "event_attendees_access" {
  name   = "${var.name_prefix}-ingestion-event-attendees-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.event_attendees_access.json
}

# Read-only: Extract snapshots the uploader's displayName/email onto each Photos row at
# write time (P-99); this Lambda never writes Users.
data "aws_iam_policy_document" "users_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.users_table_arn]
  }
}

resource "aws_iam_role_policy" "users_access" {
  name   = "${var.name_prefix}-ingestion-users-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.users_access.json
}

# One bucket, prefix-scoped (T-09): read the uploaded zip, read+write the converted
# photo/thumbnail, and read photos/selfies so Rekognition (via this role's credentials)
# can fetch the images it's asked to index/search — downloads/ and qrcodes/ are never
# granted here.
data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${var.photos_bucket_arn}/uploads/*", "${var.photos_bucket_arn}/selfies/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.photos_bucket_arn}/photos/*", "${var.photos_bucket_arn}/thumbnails/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-ingestion-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

# IndexOnePhoto/MatchAttendees call Rekognition against the event's collection.
data "aws_iam_policy_document" "rekognition_access" {
  statement {
    effect    = "Allow"
    actions   = ["rekognition:IndexFaces", "rekognition:SearchFacesByImage"]
    resources = ["*"] # Rekognition collection operations do not support resource-level IAM scoping
  }
}

resource "aws_iam_role_policy" "rekognition_access" {
  name   = "${var.name_prefix}-ingestion-rekognition-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.rekognition_access.json
}

# Extract synchronously invokes heic_converter to convert HEIC uploads to JPEG (P-35).
data "aws_iam_policy_document" "invoke_heic_converter" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.heic_converter_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_heic_converter" {
  name   = "${var.name_prefix}-ingestion-invoke-heic-converter"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_heic_converter.json
}
