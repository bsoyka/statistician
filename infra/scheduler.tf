resource "aws_cloudwatch_event_rule" "recompute_stats_schedule" {
  name                = "${local.name_prefix}-recompute-stats-schedule"
  description         = "Recompute derived stats every 6 hours."
  schedule_expression = "cron(0 0/6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "recompute_stats_target" {
  rule      = aws_cloudwatch_event_rule.recompute_stats_schedule.name
  target_id = "invoke-recompute-stats"
  arn       = aws_lambda_function.recompute_stats.arn
}

resource "aws_lambda_permission" "recompute_stats_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.recompute_stats.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.recompute_stats_schedule.arn
}
