resource "aws_lambda_function" "public_stats" {
  function_name = "${local.name_prefix}-public-stats"
  role          = aws_iam_role.public_stats_lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip["public_stats"].output_path
  source_code_hash = data.archive_file.lambda_zip["public_stats"].output_base64sha256

  environment {
    variables = {
      STATS_TABLE = aws_dynamodb_table.singleton_stats.name
    }
  }
}

resource "aws_lambda_function" "public_facts" {
  function_name = "${local.name_prefix}-public-facts"
  role          = aws_iam_role.public_stats_lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip["public_facts"].output_path
  source_code_hash = data.archive_file.lambda_zip["public_facts"].output_base64sha256

  environment {
    variables = {
      STATS_TABLE = aws_dynamodb_table.singleton_stats.name
    }
  }
}

resource "aws_lambda_function" "private_stats" {
  function_name = "${local.name_prefix}-private-stats"
  role          = aws_iam_role.private_stats_lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip["private_stats"].output_path
  source_code_hash = data.archive_file.lambda_zip["private_stats"].output_base64sha256

  environment {
    variables = {
      STATS_TABLE = aws_dynamodb_table.singleton_stats.name
    }
  }
}
