
resource "aws_api_gateway_resource" "events" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "events"
}

resource "aws_api_gateway_resource" "event_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.events.id
  path_part   = "{eventId}"
}

resource "aws_api_gateway_resource" "events_my_events" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.events.id
  path_part   = "my-events"
}

resource "aws_api_gateway_resource" "event_archive" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "archive"
}

resource "aws_api_gateway_resource" "event_stats" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "stats"
}

resource "aws_api_gateway_resource" "event_qrcode" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "qrcode"
}

locals {
  events_routes = {
    events_post = {
      resource_id   = aws_api_gateway_resource.events.id
      http_method   = "POST"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = aws_api_gateway_model.event_create.name
    }
    events_get = {
      resource_id   = aws_api_gateway_resource.events.id
      http_method   = "GET"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    events_my_events_get = {
      resource_id   = aws_api_gateway_resource.events_my_events.id
      http_method   = "GET"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    event_get = {
      resource_id   = aws_api_gateway_resource.event_id.id
      http_method   = "GET"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    event_put = {
      resource_id   = aws_api_gateway_resource.event_id.id
      http_method   = "PUT"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = aws_api_gateway_model.event_update.name
    }
    event_delete = {
      resource_id   = aws_api_gateway_resource.event_id.id
      http_method   = "DELETE"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    event_archive_post = {
      resource_id   = aws_api_gateway_resource.event_archive.id
      http_method   = "POST"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    event_stats_get = {
      resource_id   = aws_api_gateway_resource.event_stats.id
      http_method   = "GET"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
    event_qrcode_get = {
      resource_id   = aws_api_gateway_resource.event_qrcode.id
      http_method   = "GET"
      function_name = var.events_function_name
      function_arn  = var.events_function_arn
      request_model = null
    }
  }
}
