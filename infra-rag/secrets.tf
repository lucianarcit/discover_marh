# ─── Secrets Manager ─────────────────────────────────────────────────────────
# Armazena configurações do RAG HML que não devem estar em variáveis de ambiente
# visíveis no console Lambda.

# Configuração RAG — modelo, threshold, KB ID
resource "aws_secretsmanager_secret" "rag_config" {
  name        = "marh-agent/${local.env_lower}/rag-config"
  description = "Configuracao do pipeline RAG HML (modelo, threshold, KB ID)"

  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "rag_config" {
  secret_id = aws_secretsmanager_secret.rag_config.id

  secret_string = jsonencode({
    bedrock_model_id          = var.bedrock_model_id
    bedrock_knowledge_base_id = aws_bedrockagent_knowledge_base.rag.id
    retrieval_score_threshold = tostring(var.retrieval_score_threshold)
    retrieval_top_k           = tostring(var.retrieval_top_k)
    bedrock_region            = var.aws_region
    # threshold_status: USE_0_65_PROVISIONALLY — calibrar no Passo 10
  })

  # Não sobrescrever se alterado manualmente (ex: atualização do modelo)
  lifecycle {
    ignore_changes = [secret_string]
  }
}
