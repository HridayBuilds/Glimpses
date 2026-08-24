# T-03 (2026-08-09 follow-up): REST API, not HTTP API, for AWS WAF support against
# Rohan's threat model (P-07). Endpoint type REGIONAL, single prod stage, no custom
# domain — all ruled 2026-08-24, see LOCKED_TECH_DECISIONS.md's decision log.
resource "aws_api_gateway_rest_api" "this" {
  name = "${var.name_prefix}-api"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# T-01/T-03 (2026-08-23): Cognito enforces auth on every route below — no unauthenticated
# path exists, even join/leave need a caller identity (P-16/P-46).
resource "aws_api_gateway_authorizer" "cognito" {
  name          = "${var.name_prefix}-cognito-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.this.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [var.cognito_user_pool_arn]
}

# One route table entry per locked path+method (T-03 §3) — the explicit-tree option
# ruled 2026-08-24, so each real endpoint gets its own method/integration and can carry
# its own request model, not a single {proxy+} shared across a Lambda's whole territory.
locals {
  routes = merge(
    local.profile_routes,
    local.events_routes,
    local.membership_routes,
    local.upload_status_routes,
    local.gallery_routes,
    local.download_routes,
  )
}

resource "aws_api_gateway_method" "route" {
  for_each = local.routes

  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = each.value.resource_id
  http_method   = each.value.http_method
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_validator_id = each.value.request_model != null ? aws_api_gateway_request_validator.body.id : null
  request_models       = each.value.request_model != null ? { "application/json" = each.value.request_model } : null
}

resource "aws_api_gateway_integration" "route" {
  for_each = local.routes

  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = each.value.resource_id
  http_method             = aws_api_gateway_method.route[each.key].http_method
  integration_http_method = "POST" # Lambda proxy integrations always invoke via POST, regardless of the method's own verb
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${each.value.function_arn}/invocations"
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode(local.routes))
  }

  depends_on = [aws_api_gateway_method.route, aws_api_gateway_integration.route]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  deployment_id = aws_api_gateway_deployment.this.id
  stage_name    = "prod"
}
