output "api_url" {
  description = "URL base da API (API Gateway)"
  value       = aws_apigatewayv2_api.agent.api_endpoint
}

output "lambda_function_name" {
  description = "Nome da Lambda function"
  value       = aws_lambda_function.agent.function_name
}

output "lambda_function_arn" {
  description = "ARN da Lambda function"
  value       = aws_lambda_function.agent.arn
}

output "secret_arn" {
  description = "ARN do secret com credenciais ma-hr-orch"
  value       = aws_secretsmanager_secret.ma_hr_orch.arn
}

output "amplify_app_url" {
  description = "URL do frontend (S3 Website)"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}
