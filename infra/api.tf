resource "aws_apigatewayv2_api" "http" {
  name          = "${local.name_prefix}-http"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "public_stats" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.public_stats.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "private_stats" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.private_stats.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_public_stats" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /public/stats"
  target    = "integrations/${aws_apigatewayv2_integration.public_stats.id}"
}

resource "aws_apigatewayv2_route" "get_public_stat" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /public/stats/{key}"
  target    = "integrations/${aws_apigatewayv2_integration.public_stats.id}"
}

resource "aws_apigatewayv2_route" "get_private_stats" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/stats"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "get_private_stat" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /private/stats/{key}"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_route" "put_private_stat" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "PUT /private/stats/{key}"
  target             = "integrations/${aws_apigatewayv2_integration.private_stats.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_lambda_permission" "public_stats" {
  statement_id  = "AllowAPIGatewayInvokePublicStats"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.public_stats.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_lambda_permission" "private_stats" {
  statement_id  = "AllowAPIGatewayInvokePrivateStats"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.private_stats.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
