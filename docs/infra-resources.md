# Recursos AWS — MARH Agent

> Documento vivo — atualizar sempre que novos recursos forem adicionados ao Terraform.

**Última atualização:** 2026-07-23  
**Ambiente documentado:** HML (`sa-east-1`)

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS — sa-east-1                              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              API Gateway HTTP API                            │   │
│  │              marh-agent-hml                                  │   │
│  │              POST /chat    GET /health                       │   │
│  │              Throttling: 50 burst / 100 rate                 │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                           │                                         │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Lambda Function                                 │   │
│  │              marh-agent-hml                                  │   │
│  │              Python 3.12 · 512 MB · 30s timeout             │   │
│  │              X-Ray: Active                                   │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                           │                                         │
│          ┌────────────────┼────────────────┐                       │
│          ▼                ▼                ▼                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐       │
│  │ CloudWatch   │ │ Secrets      │ │ IAM Role             │       │
│  │ Log Groups   │ │ Manager      │ │ marh-agent-hml-      │       │
│  │ (2 groups)   │ │              │ │ lambda-role          │       │
│  └──────────────┘ └──────────────┘ └──────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Recursos Detalhados

### 1. Lambda Function

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml` |
| **Runtime** | Python 3.12 |
| **Handler** | `marh_agent.api.lambda_handler.lambda_handler` |
| **Memória** | 512 MB |
| **Timeout** | 30 segundos |
| **Tracing** | X-Ray Active |
| **Source** | `poc_marh_agent/backend/src/` (zipado pelo Terraform) |

**Variáveis de ambiente:**

| Variável | Valor (HML) | Descrição |
|----------|-------------|-----------|
| `AGENT_MODE` | `MOCK_LOCAL` | Mock (Fase 1) → `INTEGRATED` (Fase 2+) |
| `ENVIRONMENT` | `HML` | Ambiente |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `MAX_MESSAGE_LENGTH` | `2000` | Limite de caracteres da mensagem |
| `MA_HR_ORCH_BASE_URL` | *(vazio)* | Preenchido na Fase 2 |
| `MA_HR_ORCH_TIMEOUT_SECONDS` | `10` | Timeout HTTP |
| `BEDROCK_REGION` | `sa-east-1` | Região do Bedrock |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-*` | Modelo LLM |
| `BEDROCK_KNOWLEDGE_BASE_ID` | *(vazio)* | Preenchido na Fase 3 |
| `CORS_ALLOWED_ORIGINS` | `https://meualelo-webviews-hml.siteteste.inf.br` | Origens CORS |

---

### 2. API Gateway HTTP API

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml` |
| **Protocolo** | HTTP |
| **Stage** | `$default` (auto-deploy) |
| **Throttling (burst)** | 50 requests |
| **Throttling (rate)** | 100 requests/segundo |

**Rotas:**

| Método | Path | Destino |
|--------|------|---------|
| `POST` | `/chat` | Lambda `marh-agent-hml` |
| `GET` | `/health` | Lambda `marh-agent-hml` |

**CORS:**

| Config | Valor |
|--------|-------|
| Allow Origins | `https://meualelo-webviews-hml.siteteste.inf.br` |
| Allow Methods | `POST`, `OPTIONS` |
| Allow Headers | `Content-Type`, `Authorization`, `X-Correlation-Id` |
| Max Age | 3600s (1 hora) |

---

### 3. IAM Role

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml-lambda-role` |
| **Trusted entity** | `lambda.amazonaws.com` |

**Policies anexadas:**

| Policy | Tipo | Permissões |
|--------|------|------------|
| `AWSLambdaBasicExecutionRole` | AWS Managed | CloudWatch Logs (create, put) |
| `AWSXRayDaemonWriteAccess` | AWS Managed | X-Ray (put traces/segments) |
| `secrets-read` | Inline | `secretsmanager:GetSecretValue` no secret do ma-hr-orch |
| `bedrock-invoke` | Inline | `bedrock:InvokeModel`, `bedrock:Retrieve`, `bedrock:RetrieveAndGenerate` |

---

### 4. Secrets Manager

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent/hml/ma-hr-orch-credentials` |
| **Conteúdo** | `{"api_key": "PLACEHOLDER", "base_url": "PLACEHOLDER"}` |
| **Lifecycle** | `ignore_changes` no valor (preenchido manualmente) |

> ⚠️ Preencher manualmente no console AWS com as credenciais reais na Fase 2.

---

### 5. CloudWatch Log Groups

| Log Group | Retenção | Origem |
|-----------|----------|--------|
| `/aws/lambda/marh-agent-hml` | 30 dias | Lambda function |
| `/aws/apigateway/marh-agent-hml` | 30 dias | API Gateway access logs |

**Formato do access log (API Gateway):**

```json
{
  "requestId": "$context.requestId",
  "ip": "$context.identity.sourceIp",
  "method": "$context.httpMethod",
  "path": "$context.path",
  "status": "$context.status",
  "responseLength": "$context.responseLength",
  "latency": "$context.integrationLatency"
}
```

---

### 6. Lambda Permission

| Propriedade | Valor |
|-------------|-------|
| **Statement ID** | `AllowAPIGatewayInvoke` |
| **Action** | `lambda:InvokeFunction` |
| **Principal** | `apigateway.amazonaws.com` |
| **Source ARN** | `${api_execution_arn}/*/*` |

---

## Custos Estimados (HML com uso baixo)

| Recurso | Estimativa mensal |
|---------|-------------------|
| Lambda (poucas invocações) | ~$0 (free tier) |
| API Gateway (poucas requests) | ~$0 (free tier) |
| CloudWatch Logs (poucos MB) | ~$0.50 |
| Secrets Manager (1 secret) | ~$0.40 |
| X-Ray (poucos traces) | ~$0 (free tier) |
| **Total estimado** | **< $1/mês** |

---

## Recursos Futuros (por Fase)

| Fase | Recursos a adicionar |
|------|---------------------|
| **Fase 1** | Amplify Hosting (frontend estático com CI/CD) |
| **Fase 2** | Nenhum recurso novo (só muda env vars da Lambda) |
| **Fase 3** | S3 Bucket (documentos RAG), Bedrock Knowledge Base |
| **Fase 4** | Nenhum recurso novo (só muda `BEDROCK_MODEL_ID`) |
| **Fase 5** | API Gateway Authorizer (JWT), CloudWatch Alarms |

---

## Arquivo Terraform → Recurso

| Arquivo | Recursos |
|---------|----------|
| `main.tf` | Provider AWS, backend config |
| `lambda.tf` | Lambda function, IAM role, IAM policies, CloudWatch log group |
| `api_gateway.tf` | HTTP API, stage, integration, routes, lambda permission, log group |
| `secrets.tf` | Secrets Manager secret + version |
| `variables.tf` | Todas as variáveis de entrada |
| `locals.tf` | `env_lower` |
| `outputs.tf` | api_url, lambda_function_name, lambda_function_arn, secret_arn |
| `terraform.tfvars` | Valores para HML |
