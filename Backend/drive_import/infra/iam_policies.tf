data "aws_iam_policy_document" "access" {
  statement {
    actions   = ["dynamodb:GetItem"]
    resources = [var.events_table_arn, var.event_attendees_table_arn, var.users_table_arn, var.jobs_table_arn]
  }
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [var.db_api_function_arn]
  }
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:AbortMultipartUpload"]
    resources = ["${var.photos_bucket_arn}/uploads/drive/*"]
  }
  statement {
    actions   = ["states:StartExecution"]
    resources = [local.state_machine_arn]
  }
  statement {
    actions   = ["ssm:GetParameter"]
    resources = [local.parameter_arn]
  }
  statement {
    actions   = ["kms:Decrypt"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["ssm.${data.aws_region.current.region}.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "kms:EncryptionContext:PARAMETER_ARN"
      values   = [local.parameter_arn]
    }
  }
}
resource "aws_iam_role_policy" "access" {
  name   = "${var.name_prefix}-drive-import-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.access.json
}
data "aws_iam_policy_document" "workflow_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "workflow" {
  name               = "${var.name_prefix}-drive-import-workflow"
  assume_role_policy = data.aws_iam_policy_document.workflow_assume.json
}
data "aws_iam_policy_document" "workflow_access" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.this.arn, var.ingestion_function_arn, var.db_api_function_arn]
  }
  statement {
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${var.photos_bucket_arn}/uploads/*"]
  }
  statement {
    actions   = ["states:StartExecution"]
    resources = [local.state_machine_arn]
  }
  statement {
    actions   = ["states:DescribeExecution", "states:StopExecution"]
    resources = ["arn:aws:states:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:execution:${local.state_machine_name}:*"]
  }
}
resource "aws_iam_role_policy" "workflow_access" {
  name   = "${var.name_prefix}-drive-import-workflow"
  role   = aws_iam_role.workflow.id
  policy = data.aws_iam_policy_document.workflow_access.json
}
