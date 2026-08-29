data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  state_machine_arn                  = "arn:aws:states:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:stateMachine:${local.state_machine_name}"
  state_machine_execution_arn_prefix = "arn:aws:states:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:execution:${local.state_machine_name}:*"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "this" {
  name               = "${var.name_prefix}-state-machines-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "invoke_ingestion" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.ingestion_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_ingestion" {
  name   = "${var.name_prefix}-state-machines-invoke-ingestion"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_ingestion.json
}

data "aws_iam_policy_document" "invoke_db_api" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [var.db_api_function_arn]
  }
}

resource "aws_iam_role_policy" "invoke_db_api" {
  name   = "${var.name_prefix}-state-machines-invoke-db-api"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.invoke_db_api.json
}

data "aws_iam_policy_document" "manifest_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${var.photos_bucket_arn}/uploads/*"]
  }
}

resource "aws_iam_role_policy" "manifest_access" {
  name   = "${var.name_prefix}-state-machines-manifest-access"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.manifest_access.json
}

data "aws_iam_policy_document" "distributed_map_self_execution" {
  statement {
    effect    = "Allow"
    actions   = ["states:StartExecution"]
    resources = [local.state_machine_arn]
  }
  statement {
    effect    = "Allow"
    actions   = ["states:DescribeExecution", "states:StopExecution"]
    resources = [local.state_machine_execution_arn_prefix]
  }
}

resource "aws_iam_role_policy" "distributed_map_self_execution" {
  name   = "${var.name_prefix}-state-machines-distributed-map"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.distributed_map_self_execution.json
}
