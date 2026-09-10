resource "aws_iam_role" "plants_backend" {
  name = "plants-backend-role"

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

resource "aws_iam_role_policy" "plants_backend" {
  name = "plants-backend-policy"
  role = aws_iam_role.plants_backend.id

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
          "dynamodb:Scan",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.plants.arn,
          aws_dynamodb_table.activity.arn,
          "${aws_dynamodb_table.activity.arn}/index/*",
          aws_dynamodb_table.activity_type.arn,
          module.notifications.notification_table_arn
        ]
      },
      {
        Sid      = "S3PlantImageUpload"
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.plant_images.arn}/uploads/*"
      }
    ]
  })
}
