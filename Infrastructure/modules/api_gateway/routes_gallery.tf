
resource "aws_api_gateway_resource" "event_photos" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "photos"
}

resource "aws_api_gateway_resource" "event_photo_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_photos.id
  path_part   = "{photoId}"
}

resource "aws_api_gateway_resource" "event_photos_download_urls" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_photos.id
  path_part   = "download-urls"
}

resource "aws_api_gateway_resource" "event_photos_bulk_delete" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_photos.id
  path_part   = "bulk-delete"
}

locals {
  gallery_routes = {
    event_photos_get = {
      resource_id   = aws_api_gateway_resource.event_photos.id
      http_method   = "GET"
      function_name = var.gallery_function_name
      function_arn  = var.gallery_function_arn
      request_model = null
    }
    event_photo_id_get = {
      resource_id   = aws_api_gateway_resource.event_photo_id.id
      http_method   = "GET"
      function_name = var.gallery_function_name
      function_arn  = var.gallery_function_arn
      request_model = null
    }
    event_photo_id_delete = {
      resource_id   = aws_api_gateway_resource.event_photo_id.id
      http_method   = "DELETE"
      function_name = var.gallery_function_name
      function_arn  = var.gallery_function_arn
      request_model = null
    }
    event_photos_download_urls_post = {
      resource_id   = aws_api_gateway_resource.event_photos_download_urls.id
      http_method   = "POST"
      function_name = var.gallery_function_name
      function_arn  = var.gallery_function_arn
      request_model = aws_api_gateway_model.photo_ids_body.name
    }
    event_photos_bulk_delete_post = {
      resource_id   = aws_api_gateway_resource.event_photos_bulk_delete.id
      http_method   = "POST"
      function_name = var.gallery_function_name
      function_arn  = var.gallery_function_arn
      request_model = aws_api_gateway_model.photo_ids_body.name
    }
  }
}
