resource "aws_dynamodb_table" "singleton_stats" {
  name         = "${local.name_prefix}-singleton-stats"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "stat_key"

  attribute {
    name = "stat_key"
    type = "S"
  }
}
