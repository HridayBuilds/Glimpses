# T-01/T-03 auth config, ruled 2026-08-23: email+password login (P-02), no social
# providers (P-03, so no aws_cognito_identity_provider is configured), numeric-code
# email verification and password reset (P-91), display name captured at signup (P-84),
# MFA off and long (30-day) refresh token expiry — both set explicitly below, even though
# they match Cognito's own defaults, so the ruling stays visible in code rather than
# resting on an unstated default (the same drift this rebuild exists to avoid).
resource "aws_cognito_user_pool" "this" {
  name = "${var.name_prefix}-users"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  mfa_configuration        = "OFF"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  schema {
    name                = "name"
    attribute_data_type = "String"
    mutable             = true
    required            = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.name_prefix}-app-client"
  user_pool_id = aws_cognito_user_pool.this.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  refresh_token_validity = 30
  token_validity_units {
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
}
