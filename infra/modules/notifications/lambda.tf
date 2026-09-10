data "archive_file" "dispatch_notifications" {
  type        = "zip"
  source_dir  = "${path.module}/../../../backend/notifications/src"
  output_path = "${path.module}/../../.build/dispatch-notifications.zip"
}

resource "aws_lambda_function" "dispatch_notifications" {
  function_name = "plantCatalog-dispatch-notifications-dev"
  role          = aws_iam_role.dispatch_notifications.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.14"
  timeout       = 3
  memory_size   = 128

  filename         = data.archive_file.dispatch_notifications.output_path
  source_code_hash = data.archive_file.dispatch_notifications.output_base64sha256
}
