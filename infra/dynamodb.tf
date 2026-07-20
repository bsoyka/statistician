resource "aws_dynamodb_table" "singleton_stats" {
  name         = "${local.name_prefix}-singleton-stats"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "stat_key"

  attribute {
    name = "stat_key"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "activity_records" {
  name         = "${local.name_prefix}-activity-records"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}
