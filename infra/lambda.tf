data "archive_file" "plants_backend" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/src"
  output_path = "${path.module}/.build/plants-backend.zip"
}

resource "aws_lambda_function" "plants_backend" {
  function_name = "plantCatalog-backend-dev"
  role          = aws_iam_role.plants_backend.arn
  handler       = "app.lambda_handler"
  runtime       = "python3.13"
  timeout       = 10
  memory_size   = 128

  filename         = data.archive_file.plants_backend.output_path
  source_code_hash = data.archive_file.plants_backend.output_base64sha256
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.plants_backend.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.plant_api.execution_arn}/*/*"
}
