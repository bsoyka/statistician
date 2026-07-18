output "default_invoke_url" {
  value       = aws_apigatewayv2_stage.default.invoke_url
  description = "Default execute-api URL."
}

output "custom_domain_url" {
  value       = "https://${aws_apigatewayv2_domain_name.api.domain_name}"
  description = "Custom domain URL for the Statistician API."
}

output "api_domain_target" {
  value       = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].target_domain_name
  description = "DNS target for the custom API domain."
}

output "api_domain_hosted_zone_id" {
  value       = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].hosted_zone_id
  description = "Hosted zone ID for alias/CNAME-style DNS configuration."
}

output "api_domain_acm_validation_records" {
  description = "DNS validation records that must be created outside this repo."
  value = [
    for dvo in aws_acm_certificate.api_domain.domain_validation_options : {
      domain_name  = dvo.domain_name
      record_name  = dvo.resource_record_name
      record_type  = dvo.resource_record_type
      record_value = dvo.resource_record_value
    }
  ]
}

output "singleton_stats_table_name" {
  value       = aws_dynamodb_table.singleton_stats.name
  description = "Singleton stats DynamoDB table name."
}
