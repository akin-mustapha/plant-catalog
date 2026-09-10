data "archive_file" "post_notifications" {
  type        = "zip"
  source_dir  = "${path.module}/../../../backend/notifications/src"
  output_path = "${path.module}/../../.build/post-notifications.zip"
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
