# Zip-download jobs (T-03/T-04 follow-up, ruled 2026-08-15). No GSI — unlike Jobs'
# eventUploaderKey GSI, no ruling requires a download to survive a closed/fresh session;
# the requester holds the downloadId returned synchronously from the kickoff call.
resource "aws_dynamodb_table" "downloads" {
  name         = "${var.name_prefix}-downloads"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "downloadId"

  attribute {
    name = "downloadId"
    type = "S"
  }
}
