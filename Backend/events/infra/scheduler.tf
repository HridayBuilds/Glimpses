# P-77/P-78 archive sweep: EventBridge Scheduler invokes this same Lambda once a day via
# its internal "action" entry point (Handler.handle_internal_action), never through API
# Gateway — mirrors the self-invoke shape download's build step already uses.

data "aws_iam_policy_document" "scheduler_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_invoke" {
  name               = "${var.name_prefix}-events-archive-sweep-role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_role.json
}

data "aws_iam_policy_document" "scheduler_invoke" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.this.arn]
  }
}

resource "aws_iam_role_policy" "scheduler_invoke" {
  name   = "${var.name_prefix}-events-archive-sweep-policy"
  role   = aws_iam_role.scheduler_invoke.id
  policy = data.aws_iam_policy_document.scheduler_invoke.json
}

resource "aws_scheduler_schedule" "archive_sweep" {
  name       = "${var.name_prefix}-events-archive-sweep"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.archive_sweep_schedule_expression

  target {
    arn      = aws_lambda_function.this.arn
    role_arn = aws_iam_role.scheduler_invoke.arn
    input    = jsonencode({ action = "run_archive_sweep" })
  }
}
