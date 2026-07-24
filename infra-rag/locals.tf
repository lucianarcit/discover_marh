locals {
  env_lower = lower(var.environment)
  prefix    = "marh-agent-rag-${local.env_lower}"

  # Corpus — único arquivo aprovado para ingestão
  corpus_s3_key = "knowledge/marh_feature_knowledge.md"

  # Configuração do índice S3 Vectors — validada no gate Passo 8A
  vector_dimension    = 1024
  vector_distance     = "cosine"
  vector_data_type    = "float32"
  non_filterable_keys = ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]

  # Modelo de embedding — confirmado ativo em sa-east-1 no probe regional
  embed_model_id  = "amazon.titan-embed-text-v2:0"
  embed_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/${local.embed_model_id}"
}
