variable "project_name" {
  type        = string
  default     = "statistician"
  description = "Project name."
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region."
}

variable "api_domain" {
  type        = string
  description = "Custom domain for the Statistician API."
  default     = "statistician.bensoyka.com"
}

variable "gatekeeper_issuer_url" {
  type        = string
  description = "JWT issuer URL from Gatekeeper outputs."
}

variable "gatekeeper_statistician_client_id" {
  type        = string
  description = "Statistician web app client ID from Gatekeeper outputs."
}

variable "gatekeeper_statistician_api_keys_client_id" {
  type        = string
  description = "Statistician API keys client ID from Gatekeeper outputs."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags."
}
