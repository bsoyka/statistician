resource "aws_iam_role" "private_activity_lambda" {
  name = "${local.name_prefix}-private-activity-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "private_activity_lambda_basic" {
  role       = aws_iam_role.private_activity_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "private_activity_dynamodb" {
  name = "${local.name_prefix}-private-activity-dynamodb"
  role = aws_iam_role.private_activity_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ]
      Resource = aws_dynamodb_table.activity_records.arn
    }]
  })
}

resource "aws_iam_role" "public_stats_lambda" {
  name = "${local.name_prefix}-public-stats-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "private_stats_lambda" {
  name = "${local.name_prefix}-private-stats-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "public_stats_basic" {
  role       = aws_iam_role.public_stats_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "private_stats_basic" {
  role       = aws_iam_role.private_stats_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "public_stats_dynamodb" {
  name = "${local.name_prefix}-public-stats-dynamodb"
  role = aws_iam_role.public_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.singleton_stats.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "private_stats_dynamodb" {
  name = "${local.name_prefix}-private-stats-dynamodb"
  role = aws_iam_role.private_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.singleton_stats.arn
      }
    ]
  })
}

resource "aws_iam_role" "recompute_stats_lambda" {
  name = "${local.name_prefix}-recompute-stats-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "recompute_stats_lambda_basic" {
  role       = aws_iam_role.recompute_stats_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "recompute_stats_dynamodb" {
  name = "${local.name_prefix}-recompute-stats-dynamodb"
  role = aws_iam_role.recompute_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.activity_records.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem"
        ]
        Resource = aws_dynamodb_table.singleton_stats.arn
      }
    ]
  })
}
