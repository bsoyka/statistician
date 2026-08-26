data "aws_kms_alias" "ssm" {
  name = "alias/aws/ssm"
}

resource "aws_ssm_parameter" "unsplash" {
  name  = "/statistician/prod/external/unsplash"
  type  = "SecureString"
  value = "PLACEHOLDER"

  tags = var.tags

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "strava" {
  name  = "/statistician/prod/external/strava"
  type  = "SecureString"
  value = "PLACEHOLDER"

  tags = var.tags

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_iam_role_policy" "recompute_stats_secrets" {
  name = "${local.name_prefix}-recompute-stats-secrets"
  role = aws_iam_role.recompute_stats_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadUnsplashParameter"
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = aws_ssm_parameter.unsplash.arn
      },
      {
        Sid    = "ReadWriteStravaParameter"
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ]
        Resource = aws_ssm_parameter.strava.arn
      },
      {
        Sid    = "DecryptSsmParameters"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = data.aws_kms_alias.ssm.target_key_arn
      }
    ]
  })
}
