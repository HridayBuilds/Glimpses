
resource "aws_api_gateway_request_validator" "body" {
  name                        = "${var.name_prefix}-validate-body"
  rest_api_id                 = aws_api_gateway_rest_api.this.id
  validate_request_body       = true
  validate_request_parameters = false
}

resource "aws_api_gateway_model" "profile_update" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "ProfileUpdate"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "ProfileUpdate"
    type      = "object"
    properties = {
      displayName = { type = "string", minLength = 1 }
    }
    required = ["displayName"]
  })
}

resource "aws_api_gateway_model" "event_create" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "EventCreate"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "EventCreate"
    type      = "object"
    properties = {
      name        = { type = "string", minLength = 1 }
      description = { type = "string" }
    }
    required = ["name"]
  })
}

resource "aws_api_gateway_model" "event_update" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "EventUpdate"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "EventUpdate"
    type      = "object"
    properties = {
      name               = { type = "string" }
      description        = { type = "string" }
      joinPolicy         = { type = "string" }
      contributionPolicy = { type = "string" }
    }
  })
}

resource "aws_api_gateway_model" "event_join_body" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "EventJoinBody"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "EventJoinBody"
    type      = "object"
    properties = {
      accessCode = { type = "string", minLength = 1 }
    }
    required = ["accessCode"]
  })
}

resource "aws_api_gateway_model" "photo_ids_body" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "PhotoIDsBody"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "PhotoIDsBody"
    type      = "object"
    properties = {
      photoIDs = { type = "array", items = { type = "string" } }
    }
  })
}

resource "aws_api_gateway_model" "download_kickoff_body" {
  rest_api_id  = aws_api_gateway_rest_api.this.id
  name         = "DownloadKickoffBody"
  content_type = "application/json"
  schema = jsonencode({
    "$schema" = "http://json-schema.org/draft-04/schema#"
    title     = "DownloadKickoffBody"
    type      = "object"
    properties = {
      photoIds = { type = "array", items = { type = "string" } }
    }
  })
}
