locals {
  public_routes = {
    public_stats = {
      route_key   = "GET /public/stats"
      path        = "/public/stats"
      method      = "GET"
      lambda_arn  = aws_lambda_function.public_stats.invoke_arn
      lambda_name = aws_lambda_function.public_stats.function_name
    }
    public_facts = {
      route_key   = "GET /public/facts"
      path        = "/public/facts"
      method      = "GET"
      lambda_arn  = aws_lambda_function.public_facts.invoke_arn
      lambda_name = aws_lambda_function.public_facts.function_name
    }
  }
}

resource "aws_apigatewayv2_api" "http" {
  name          = "${local.name_prefix}-http"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["Content-Type"]
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "public" {
  for_each = local.public_routes

  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = each.value.lambda_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "public" {
  for_each = local.public_routes

  api_id    = aws_apigatewayv2_api.http.id
  route_key = each.value.route_key
  target    = "integrations/${aws_apigatewayv2_integration.public[each.key].id}"
}

resource "aws_lambda_permission" "public_apigw" {
  for_each = local.public_routes

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/${each.value.method}${each.value.path}"
}

resource "aws_apigatewayv2_integration" "private_stats" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.private_stats.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "private_stats_list" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/stats"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_stats_get" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/stats/{key}"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_stats_put" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "PUT /private/stats/{key}"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_lambda_permission" "private_stats_apigw" {
  statement_id  = "AllowExecutionFromAPIGateway-private-stats"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.private_stats.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*/private/stats*"
}

resource "aws_apigatewayv2_integration" "private_volunteer" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.private_volunteer.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "private_volunteer_entries_post" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "POST /private/volunteer/entries"
  target             = "integrations/${aws_apigatewayv2_integration.private_volunteer.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_volunteer_entries_get" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/volunteer/entries"
  target             = "integrations/${aws_apigatewayv2_integration.private_volunteer.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_volunteer_summary_get" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/volunteer/summary"
  target             = "integrations/${aws_apigatewayv2_integration.private_volunteer.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_lambda_permission" "private_volunteer_apigw" {
  statement_id  = "AllowExecutionFromAPIGateway-private-volunteer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.private_volunteer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*/private/volunteer/*"
}

resource "aws_apigatewayv2_integration" "private_ctl" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.private_ctl.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "private_ctl_weeks_put" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "PUT /private/ctl/weeks/{week_end_date}"
  target             = "integrations/${aws_apigatewayv2_integration.private_ctl.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_ctl_weeks_get" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/ctl/weeks"
  target             = "integrations/${aws_apigatewayv2_integration.private_ctl.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "private_ctl_summary_get" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/ctl/summary"
  target             = "integrations/${aws_apigatewayv2_integration.private_ctl.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_lambda_permission" "private_ctl_apigw" {
  statement_id  = "AllowExecutionFromAPIGateway-private-ctl"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.private_ctl.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*/private/ctl/*"
}
