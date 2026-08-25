
resource "aws_api_gateway_resource" "event_info" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "info"
}

resource "aws_api_gateway_resource" "event_join" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.events.id
  path_part   = "join"
}

resource "aws_api_gateway_resource" "event_leave" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "leave"
}

resource "aws_api_gateway_resource" "event_attendees" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "attendees"
}

resource "aws_api_gateway_resource" "event_attendee_user_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_attendees.id
  path_part   = "{userId}"
}

resource "aws_api_gateway_resource" "event_attendee_admit" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_attendee_user_id.id
  path_part   = "admit"
}

resource "aws_api_gateway_resource" "event_attendee_deny" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_attendee_user_id.id
  path_part   = "deny"
}

resource "aws_api_gateway_resource" "event_attendee_eject" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_attendee_user_id.id
  path_part   = "eject"
}

locals {
  membership_routes = {
    event_info_get = {
      resource_id   = aws_api_gateway_resource.event_info.id
      http_method   = "GET"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
    event_join_post = {
      resource_id   = aws_api_gateway_resource.event_join.id
      http_method   = "POST"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = aws_api_gateway_model.event_join_body.name
    }
    event_leave_post = {
      resource_id   = aws_api_gateway_resource.event_leave.id
      http_method   = "POST"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
    event_attendees_get = {
      resource_id   = aws_api_gateway_resource.event_attendees.id
      http_method   = "GET"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
    event_attendee_admit_post = {
      resource_id   = aws_api_gateway_resource.event_attendee_admit.id
      http_method   = "POST"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
    event_attendee_deny_post = {
      resource_id   = aws_api_gateway_resource.event_attendee_deny.id
      http_method   = "POST"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
    event_attendee_eject_post = {
      resource_id   = aws_api_gateway_resource.event_attendee_eject.id
      http_method   = "POST"
      function_name = var.membership_function_name
      function_arn  = var.membership_function_arn
      request_model = null
    }
  }
}
