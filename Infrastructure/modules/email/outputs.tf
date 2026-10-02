output "sender_email" {
  value = aws_sesv2_email_identity.sender.email_identity
}

output "sender_identity_arn" {
  value = aws_sesv2_email_identity.sender.arn
}

output "sender_verification_status" {
  value = aws_sesv2_email_identity.sender.verification_status
}
