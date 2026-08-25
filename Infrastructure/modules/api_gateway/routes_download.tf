
resource "aws_api_gateway_resource" "event_photos_download" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_photos.id
  path_part   = "download"
}

resource "aws_api_gateway_resource" "event_downloads" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "downloads"
}

resource "aws_api_gateway_resource" "event_download_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_downloads.id
  path_part   = "{downloadId}"
}

resource "aws_api_gateway_resource" "event_download_status" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_download_id.id
  path_part   = "status"
}

locals {
  download_routes = {
    event_photos_download_post = {
      resource_id   = aws_api_gateway_resource.event_photos_download.id
      http_method   = "POST"
      function_name = var.download_function_name
      function_arn  = var.download_function_arn
      request_model = aws_api_gateway_model.download_kickoff_body.name
    }
    event_download_status_get = {
      resource_id   = aws_api_gateway_resource.event_download_status.id
      http_method   = "GET"
      function_name = var.download_function_name
      function_arn  = var.download_function_arn
      request_model = null
    }
  }
}
