output "notification_table_arn" {
  value = aws_dynamodb_table.notification.arn
}

output "notification_log_table_arn" {
  value = aws_dynamodb_table.notification_log.arn
}