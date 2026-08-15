# Permissions derived from this Lambda's actual AWS calls only (T-07): it reads the
# source HEIC and writes the converted JPEG, nothing else.
data "aws_iam_policy_document" "s3_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${var.photos_bucket_arn}/*"]
  }
}

resource "aws_iam_role_policy" "s3_access" {
  name   = "${var.name_prefix}-heic-converter-s3-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.s3_access.json
}
