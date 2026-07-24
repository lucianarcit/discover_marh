variable "aws_region" {
  description = "Região AWS. Cross-region proibido — deve ser sa-east-1."
  type        = string
  default     = "sa-east-1"

  validation {
    condition     = var.aws_region == "sa-east-1"
    error_message = "Cross-region proibido. aws_region deve ser sa-east-1."
  }
}

variable "environment" {
  description = "Ambiente (HML ou PRD)"
  type        = string
  default     = "HML"

  validation {
    condition     = contains(["HML", "PRD"], var.environment)
    error_message = "Environment deve ser HML ou PRD."
  }
}

# ── Lambda ────────────────────────────────────────────────────

variable "lambda_memory_size" {
  description = "Memória da Lambda RAG HML (MB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Timeout da Lambda RAG HML (segundos). RAG pode ser mais lento que MOCK."
  type        = number
  default     = 60
}

variable "log_retention_days" {
  description = "Retenção de logs no CloudWatch (dias)"
  type        = number
  default     = 30
}

# ── API Gateway ───────────────────────────────────────────────

variable "throttling_burst_limit" {
  description = "API Gateway burst limit"
  type        = number
  default     = 50
}

variable "throttling_rate_limit" {
  description = "API Gateway rate limit (requests/segundo)"
  type        = number
  default     = 100
}

variable "cors_allowed_origins" {
  description = "Origens permitidas no CORS"
  type        = list(string)
  default     = ["https://meualelo-webviews-hml.siteteste.inf.br"]
}

# ── RAG ───────────────────────────────────────────────────────

variable "bedrock_model_id" {
  description = <<-EOT
    ID do modelo de geração Bedrock.
    Obrigatório. Sem valor padrão — seleção definitiva no Passo 10.
    Candidatos validados no probe regional (sa-east-1):
      mistral.magistral-small-2509
      mistral.mistral-large-2402-v1:0
      google.gemma-3-27b-it
    Excluídos: Claude 3 Haiku, Claude 3.5 Haiku, Claude 3 Sonnet.
  EOT
  type        = string

  validation {
    condition = !contains([
      "anthropic.claude-3-haiku-20240307-v1:0",
      "anthropic.claude-3-5-haiku-20241022-v1:0",
      "anthropic.claude-3-sonnet-20240229-v1:0",
    ], var.bedrock_model_id)
    error_message = "Modelo proibido. Não usar Haiku, Haiku 3.5 ou Sonnet v1."
  }
}

variable "retrieval_score_threshold" {
  description = <<-EOT
    Threshold de score para aprovação de chunks (query-level).
    Provisório 0.65 — calibrar no Passo 10 com dataset completo.
    Status: USE_0_65_PROVISIONALLY.
  EOT
  type        = number
  default     = 0.65

  validation {
    condition     = var.retrieval_score_threshold >= 0.0 && var.retrieval_score_threshold <= 1.0
    error_message = "retrieval_score_threshold deve estar em [0.0, 1.0]."
  }
}

variable "retrieval_top_k" {
  description = "Número máximo de chunks a recuperar por consulta"
  type        = number
  default     = 5

  validation {
    condition     = var.retrieval_top_k > 0 && var.retrieval_top_k <= 20
    error_message = "retrieval_top_k deve ser entre 1 e 20."
  }
}

variable "knowledge_base_chunking_parent_tokens" {
  description = "Tokens máximos por chunk pai (HIERARCHICAL)"
  type        = number
  default     = 500
}

variable "knowledge_base_chunking_child_tokens" {
  description = "Tokens máximos por chunk filho (HIERARCHICAL)"
  type        = number
  default     = 200
}

variable "knowledge_base_chunking_overlap_tokens" {
  description = "Tokens de overlap entre chunks"
  type        = number
  default     = 50
}
