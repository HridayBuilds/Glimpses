
resource "aws_api_gateway_resource" "event_upload_url" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "upload-url"
}

resource "aws_api_gateway_resource" "event_jobs" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_id.id
  path_part   = "jobs"
}

resource "aws_api_gateway_resource" "event_job_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_jobs.id
  path_part   = "{jobId}"
}

resource "aws_api_gateway_resource" "event_job_status" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_job_id.id
  path_part   = "status"
}

resource "aws_api_gateway_resource" "event_jobs_latest" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.event_jobs.id
  path_part   = "latest"
}

locals {
  upload_status_routes = {
    event_upload_url_post = {
      resource_id   = aws_api_gateway_resource.event_upload_url.id
      http_method   = "POST"
      function_name = var.upload_status_function_name
      function_arn  = var.upload_status_function_arn
      request_model = null
    }
    event_job_status_get = {
      resource_id   = aws_api_gateway_resource.event_job_status.id
      http_method   = "GET"
      function_name = var.upload_status_function_name
      function_arn  = var.upload_status_function_arn
      request_model = null
    }
    event_jobs_latest_get = {
      resource_id   = aws_api_gateway_resource.event_jobs_latest.id
      http_method   = "GET"
      function_name = var.upload_status_function_name
      function_arn  = var.upload_status_function_arn
      request_model = null
    }
  }
}
