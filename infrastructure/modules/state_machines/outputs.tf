output "state_machine_arn" {
  description = "ARN of the ingestion pipeline's state machine"
  value       = aws_sfn_state_machine.this.arn
}
