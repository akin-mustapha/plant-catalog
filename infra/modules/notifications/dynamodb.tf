resource "aws_dynamodb_table" "notification_type" {
  name         = "notification_type"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "type_id"

  attribute {
    name = "type_id"
    type = "S"
  }
}

resource "aws_dynamodb_table_item" "watering_reminder" {
  table_name = aws_dynamodb_table.notification_type.name
  hash_key   = aws_dynamodb_table.notification_type.hash_key

  item = jsonencode({
    type_id      = { S = "watering-reminder" }
    name         = { S = "Watering Reminder" }
    description  = { S = "Reminds a user to water their plants" }
    created_date = { S = "2026-09-10" }
  })
}

resource "aws_dynamodb_table" "notification" {
  name         = "notification"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "notification_id"

  attribute {
    name = "notification_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "next_run_date"
    type = "S"
  }

  global_secondary_index {
    name            = "status-next_run_date-index"
    hash_key        = "status"
    range_key       = "next_run_date"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "notification_log" {
  name         = "notification_log"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "notification_id"
  range_key    = "sent_at"

  attribute {
    name = "notification_id"
    type = "S"
  }

  attribute {
    name = "sent_at"
    type = "S"
  }
}
