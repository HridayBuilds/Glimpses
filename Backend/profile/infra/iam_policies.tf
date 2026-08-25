
data "aws_iam_policy_document" "users_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem"]
    resources = [var.users_table_arn]
  }
}

resource "aws_iam_role_policy" "users_access" {
  name   = "${var.name_prefix}-profile-users-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.users_access.json
}

data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.photos_bucket_arn}/selfies/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-profile-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

data "aws_iam_policy_document" "rekognition_access" {
  statement {
    effect    = "Allow"
    actions   = ["rekognition:DetectFaces"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "rekognition_access" {
  name   = "${var.name_prefix}-profile-rekognition-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.rekognition_access.json
}
