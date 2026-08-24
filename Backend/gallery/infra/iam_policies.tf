# Permissions derived from this Lambda's actual AWS calls only (T-07).

# Read-only — gallery's own code never writes Photos; CascadeDelete does the actual row
# deletion, per its own already-locked scope. GetItem for single-photo lookup, Query for
# the gallery GSI page, BatchGetItem for mine=true/download-urls/bulk-delete.
data "aws_iam_policy_document" "photos_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:BatchGetItem"]
    resources = [var.photos_table_arn, "${var.photos_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "photos_access" {
  name   = "${var.name_prefix}-gallery-photos-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_access.json
}

# Read-only, ruled 2026-08-24: P-44's organizer-delete-any-photo right needs
# Events.organizerID, which isn't on Photos.
data "aws_iam_policy_document" "events_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.events_table_arn]
  }
}

resource "aws_iam_role_policy" "events_access" {
  name   = "${var.name_prefix}-gallery-events-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.events_access.json
}

# Read-only, caller's own row only, ruled 2026-08-24: P-16/P-17's mine=true is a
# face-match filter resolved off EventAttendees.matchedPhotoIDs — GetItem only, never
# Query/Scan across other attendees.
data "aws_iam_policy_document" "event_attendees_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem"]
    resources = [var.event_attendees_table_arn]
  }
}

resource "aws_iam_role_policy" "event_attendees_access" {
  name   = "${var.name_prefix}-gallery-event-attendees-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.event_attendees_access.json
}

# GetObject only, photos/ prefix only, ruled 2026-08-24: the sole S3 dependency is
# download-urls' pre-signed GETs — a local signature computation with no AWS call at
# mint time, so this grant is only exercised later when the browser uses the URL.
data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${var.photos_bucket_arn}/photos/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-gallery-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

# delete/bulk-delete hand off the actual cascade to CascadeDelete (P-44/P-52) — this
# Lambda only ever fires the async InvocationType=Event call, never touches
# Photos/Faces/EventAttendees rows directly.
data "aws_iam_policy_document" "invoke_cascade_delete" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.cascade_delete_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_cascade_delete" {
  count  = var.cascade_delete_function_arn == "" ? 0 : 1
  name   = "${var.name_prefix}-gallery-invoke-cascade-delete"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_cascade_delete.json
}
