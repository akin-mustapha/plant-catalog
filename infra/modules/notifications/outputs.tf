output "notification_table_arn" {
  value = aws_dynamodb_table.notification.arn
}


output "contact_table_arn" {
  value = aws_dynamodb_table.contact.arn
}


output "notification_contact_table_arn" {
  value = aws_dynamodb_table.notification_contact.arn
}