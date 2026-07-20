resource "aws_secretsmanager_secret" "unsplash" {
  name = "statistician/prod/external/unsplash"

  tags = var.tags
}

resource "aws_secretsmanager_secret" "strava" {
  name = "statistician/prod/external/strava"

  tags = var.tags
}

resource "aws_iam_role_policy" "recompute_stats_secrets" {
  name = "${local.name_prefix}-recompute-stats-secrets"
  role = aws_iam_role.recompute_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadUnsplashSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.unsplash.arn
      },
      {
        Sid    = "ReadWriteStravaSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = aws_secretsmanager_secret.strava.arn
      }
    ]
  })
}
