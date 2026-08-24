# T-03 (2026-08-24 ruling): WAF on, minimal shape — one Web ACL, one rate-based rule,
# no managed rule groups, ~$6/month against the $200 credit — against Rohan's threat
# model (P-07), the reason REST API was chosen over HTTP API in the first place.
resource "aws_wafv2_web_acl" "this" {
  name  = "${var.name_prefix}-api-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rate-limit-per-ip"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000 # requests per 5-minute window per IP; adjustable
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.name_prefix}-rate-limit-per-ip"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-api-waf"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_association" "this" {
  resource_arn = aws_api_gateway_stage.prod.arn
  web_acl_arn  = aws_wafv2_web_acl.this.arn
}
