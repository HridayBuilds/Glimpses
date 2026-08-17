data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Computed rather than referencing aws_sfn_state_machine.this.arn, which would create a
# role <-> state-machine circular dependency (the role must exist before the state machine
# can be created, but Distributed Map's self-execution grant needs the state machine's own
# ARN). Step Functions ARNs are deterministic from name/region/account, so this is safe.
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

# Every Task state invokes the one ingestion Lambda via the optimized lambda:invoke
# integration.
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

# UpdateJobStatus invokes db_api directly to flip a Jobs row out of PENDING once Finalize
# has computed the run's outcome.
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

# IndexPhotos' Distributed Map ItemReader reads Extract's manifest from uploads/ (T-09).
data "aws_iam_policy_document" "read_manifest" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${var.photos_bucket_arn}/uploads/*"]
  }
}

resource "aws_iam_role_policy" "read_manifest" {
  name   = "${var.name_prefix}-state-machines-read-manifest"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.read_manifest.json
}

# Distributed Map runs each item's ItemProcessor as a child execution of this same state
# machine — AWS's own IAM requirement for Distributed Map, unrelated to any table/S3 access
# this pipeline does itself.
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
