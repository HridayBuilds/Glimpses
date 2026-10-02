resource "aws_sesv2_email_identity" "sender" {
  email_identity = var.sender_email
}

resource "aws_sesv2_email_identity_feedback_attributes" "sender" {
  email_identity           = aws_sesv2_email_identity.sender.email_identity
  email_forwarding_enabled = true
}
