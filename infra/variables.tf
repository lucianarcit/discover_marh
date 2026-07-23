variable "aws_region" {
  description = "Região AWS"
  type        = string
  default     = "sa-east-1"
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

variable "agent_mode" {
  description = "Modo do agente (MOCK_LOCAL ou INTEGRATED)"
  type        = string
  default     = "MOCK_LOCAL"
}

variable "lambda_memory_size" {
  description = "Memória da Lambda (MB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Timeout da Lambda (segundos)"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "Retenção de logs no CloudWatch (dias)"
  type        = number
  default     = 30
}

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
