
data "aws_iam_policy_document" "downloads_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem"]
    resources = [var.downloads_table_arn]
  }
}

resource "aws_iam_role_policy" "downloads_access" {
  name   = "${var.name_prefix}-download-downloads-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.downloads_access.json
}

data "aws_iam_policy_document" "photos_access" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:BatchGetItem", "dynamodb:Query"]
    resources = [var.photos_table_arn, "${var.photos_table_arn}/index/*"]
  }
}

resource "aws_iam_role_policy" "photos_access" {
  name   = "${var.name_prefix}-download-photos-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_access.json
}

data "aws_iam_policy_document" "photos_bucket_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${var.photos_bucket_arn}/photos/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:AbortMultipartUpload"]
    resources = ["${var.photos_bucket_arn}/downloads/*"]
  }
}

resource "aws_iam_role_policy" "photos_bucket_access" {
  name   = "${var.name_prefix}-download-photos-bucket-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.photos_bucket_access.json
}

data "aws_iam_policy_document" "self_invoke" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.this.arn]
  }
}

resource "aws_iam_role_policy" "self_invoke" {
  name   = "${var.name_prefix}-download-self-invoke"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.self_invoke.json
}
