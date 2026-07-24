output "api_base_url" {
  description = "URL base da API RAG HML (API Gateway)"
  value       = aws_apigatewayv2_api.agent.api_endpoint
}

output "health_check_url" {
  description = "URL do health check do ambiente RAG HML"
  value       = "${aws_apigatewayv2_api.agent.api_endpoint}/health"
}

output "lambda_function_name" {
  description = "Nome da Lambda RAG HML"
  value       = aws_lambda_function.agent.function_name
}

output "knowledge_base_id" {
  description = "ID da Knowledge Base RAG HML"
  value       = aws_bedrockagent_knowledge_base.rag.id
  sensitive   = true
}

output "data_source_id" {
  description = "ID do Data Source (S3) da Knowledge Base"
  value       = aws_bedrockagent_data_source.corpus.data_source_id
  sensitive   = true
}

output "model_id" {
  description = "ID do modelo de geração configurado"
  value       = var.bedrock_model_id
}

output "region" {
  description = "Região AWS do ambiente RAG HML"
  value       = var.aws_region
}

output "score_threshold" {
  description = "Threshold de recuperação configurado (provisório — calibrar no Passo 10)"
  value       = var.retrieval_score_threshold
}

output "corpus_bucket_name" {
  description = "Nome do bucket S3 do corpus"
  value       = aws_s3_bucket.corpus.bucket
  sensitive   = true
}

output "vector_bucket_arn" {
  description = "ARN do S3 Vector bucket"
  value       = aws_s3vectors_vector_bucket.rag.vector_bucket_arn
  sensitive   = true
}

output "vector_index_arn" {
  description = "ARN do S3 Vector index"
  value       = aws_s3vectors_index.rag.index_arn
  sensitive   = true
}

output "rag_config_secret_arn" {
  description = "ARN do secret com configuração RAG"
  value       = aws_secretsmanager_secret.rag_config.arn
  sensitive   = true
}
