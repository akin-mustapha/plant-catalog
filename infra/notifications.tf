data "archive_file" "post_notifications" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/notifications/src"
  output_path = "${path.module}/.build/post-notifications.zip"
}

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
      }
    ]
  })
}

resource "aws_lambda_function" "post_notifications" {
  function_name = "plantCatalog-post-notifications-dev"
  role          = aws_iam_role.post_notifications.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.14"
  timeout       = 3
  memory_size   = 128

  filename         = data.archive_file.post_notifications.output_path
  source_code_hash = data.archive_file.post_notifications.output_base64sha256
}
