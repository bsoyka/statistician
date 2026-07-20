resource "aws_secretsmanager_secret" "unsplash" {
  name = "statistician/prod/external/unsplash"

  tags = var.tags
}

resource "aws_iam_role_policy" "recompute_stats_unsplash_secret" {
  name = "${local.name_prefix}-recompute-stats-unsplash-secret"
  role = aws_iam_role.recompute_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "ReadUnsplashSecret"
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue"
      ]
      Resource = aws_secretsmanager_secret.unsplash.arn
    }]
  })
}
