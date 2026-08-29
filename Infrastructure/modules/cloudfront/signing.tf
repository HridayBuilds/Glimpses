resource "tls_private_key" "photos_signing" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_cloudfront_public_key" "photos_signing" {
  name        = "${var.name_prefix}-photos-signing-key"
  encoded_key = tls_private_key.photos_signing.public_key_pem
}

resource "aws_cloudfront_key_group" "photos_signing" {
  name    = "${var.name_prefix}-photos-signing-key-group"
  items   = [aws_cloudfront_public_key.photos_signing.id]
  comment = "Trusted key group for signed photo/thumbnail URLs (45 min expiry, minted by the gallery Lambda)"
}
