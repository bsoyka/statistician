resource "aws_apigatewayv2_authorizer" "jwt" {
  api_id           = aws_apigatewayv2_api.http.id
  name             = "gatekeeper-jwt"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    issuer   = var.gatekeeper_issuer_url
    audience = [var.gatekeeper_statistician_client_id, var.gatekeeper_statistician_api_keys_client_id]
  }
}
