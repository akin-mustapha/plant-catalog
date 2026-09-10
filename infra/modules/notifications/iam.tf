resource "aws_iam_role" "post_notifications" {
  name = "plantCatalog-post-notifications-dev-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "post_notifications_logs" {
  name = "plantCatalog-post-notifications-dev-logs"
  role = aws_iam_role.post_notifications.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Logs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:*"
      },
      {
        Sid    = "DynamoDbTableAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.notification.arn,
          "${aws_dynamodb_table.notification.arn}/index/*",
          aws_dynamodb_table.notification_type.arn
        ]
      }
    ]
  })
}
