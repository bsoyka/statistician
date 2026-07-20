output "custom_domain_url" {
  value       = "https://${aws_apigatewayv2_domain_name.api.domain_name}"
  description = "Custom domain URL for the Statistician API."
}
