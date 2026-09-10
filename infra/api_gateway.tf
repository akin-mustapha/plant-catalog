resource "aws_apigatewayv2_api" "plant_api" {
  name          = "plant-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://main.d2dl67h6vhyf6v.amplifyapp.com", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    allow_headers = ["Content-Type"]
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.plant_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.plant_api.id
  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.plant_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.plants_backend.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 30000
}

locals {
  plant_routes = {
    list_plants         = "GET /plants"
    create_plant        = "POST /plants"
    get_plant           = "GET /plants/{id}"
    update_plant        = "PUT /plants/{id}"
    delete_plant        = "DELETE /plants/{id}"
    image_upload_url    = "POST /plants/{id}/image/upload-url"
    image_confirm       = "POST /plants/{id}/image/confirm"
    create_activity     = "POST /plants/{id}/activities"
    list_activities     = "GET /plants/{id}/activities"
    delete_activity     = "DELETE /plants/{id}/activities/{activityId}"
    list_activity_types = "GET /activity-types"
    create_notification = "POST /notifications"
    get_notification    = "GET /notifications"
  }
}

resource "aws_apigatewayv2_route" "plant_routes" {
  for_each = local.plant_routes

  api_id    = aws_apigatewayv2_api.plant_api.id
  route_key = each.value
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}
