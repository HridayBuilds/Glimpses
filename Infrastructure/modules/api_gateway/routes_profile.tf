
resource "aws_api_gateway_resource" "profile" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "profile"
}

resource "aws_api_gateway_resource" "profile_selfie" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.profile.id
  path_part   = "selfie"
}

resource "aws_api_gateway_resource" "profile_selfie_confirm" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.profile_selfie.id
  path_part   = "confirm"
}

locals {
  profile_routes = {
    profile_get = {
      resource_id   = aws_api_gateway_resource.profile.id
      http_method   = "GET"
      function_name = var.profile_function_name
      function_arn  = var.profile_function_arn
      request_model = null
    }
    profile_put = {
      resource_id   = aws_api_gateway_resource.profile.id
      http_method   = "PUT"
      function_name = var.profile_function_name
      function_arn  = var.profile_function_arn
      request_model = aws_api_gateway_model.profile_update.name
    }
    profile_selfie_put = {
      resource_id   = aws_api_gateway_resource.profile_selfie.id
      http_method   = "PUT"
      function_name = var.profile_function_name
      function_arn  = var.profile_function_arn
      request_model = null
    }
    profile_selfie_delete = {
      resource_id   = aws_api_gateway_resource.profile_selfie.id
      http_method   = "DELETE"
      function_name = var.profile_function_name
      function_arn  = var.profile_function_arn
      request_model = null
    }
    profile_selfie_confirm_post = {
      resource_id   = aws_api_gateway_resource.profile_selfie_confirm.id
      http_method   = "POST"
      function_name = var.profile_function_name
      function_arn  = var.profile_function_arn
      request_model = null
    }
  }
}
