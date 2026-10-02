resource "aws_api_gateway_resource" "event_drive_import" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "drive-import"
}

resource "aws_api_gateway_model" "drive_import" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "DriveImport"
  content_type = "application/json"
  schema = jsonencode({
    type     = "object"
    required = ["folderUrl", "requestId"]
    properties = {
      folderUrl = { type = "string" }
      requestId = { type = "string" }
    }
  })
}

locals {
  drive_import_routes = {
    event_drive_import_post = {
      resource_id   = aws_api_gateway_resource.event_drive_import.id
      http_method   = "POST"
      function_name = var.drive_import_function_name
      function_arn  = var.drive_import_function_arn
      request_model = aws_api_gateway_model.drive_import.name
    }
  }
}
