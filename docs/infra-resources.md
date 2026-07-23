# Recursos AWS — MARH Agent

> Documento vivo — atualizar sempre que novos recursos forem adicionados ao Terraform.

**Última atualização:** 2026-07-23  
**Ambiente documentado:** HML (`sa-east-1`)  
**Conta AWS:** 445358171379

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS — sa-east-1                              │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              CloudFront Distribution                           │ │
│  │              d1vtu9x0di76z9.cloudfront.net (HTTPS)            │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                              │                                      │
│                              ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              S3 Bucket (Frontend)                              │ │
│  │              marh-agent-frontend-hml                           │ │
│  │              HTML/CSS/JS estáticos                             │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              API Gateway HTTP API                              │ │
│  │              marh-agent-hml (pzn843po3h)                      │ │
│  │              POST /chat    GET /health                         │ │
│  │              Throttling: 50 burst / 100 rate                   │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                              │                                      │
│                              ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              Lambda Function                                   │ │
│  │              marh-agent-hml                                    │ │
│  │              Python 3.12 · 512 MB · 30s timeout               │ │
│  │              X-Ray: Active                                     │ │
│  │              Layer: marh-agent-hml-deps (pydantic)             │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                 │
│          ▼                   ▼                   ▼                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐   │
│  │ CloudWatch   │   │ Secrets      │   │ IAM Role             │   │
│  │ Log Groups   │   │ Manager      │   │ marh-agent-hml-      │   │
│  │ (2 groups)   │   │              │   │ lambda-role          │   │
│  └──────────────┘   └──────────────┘   └──────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Recursos Detalhados

### 1. CloudFront Distribution

| Propriedade | Valor |
|-------------|-------|
| **ID** | `E29TLS56TW0RXY` |
| **Domain** | `d1vtu9x0di76z9.cloudfront.net` |
| **Origin** | S3 bucket website endpoint |
| **Protocol** | HTTPS (redirect HTTP → HTTPS) |
| **Cache TTL** | 300s default, 3600s max |
| **Certificado** | CloudFront default (*.cloudfront.net) |

---

### 2. S3 Bucket (Frontend)

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-frontend-hml` |
| **Website** | Habilitado (index.html) |
| **Acesso** | Público (via bucket policy) |
| **Conteúdo** | HTML, CSS, JS, fixtures JSON |

**Comando de sync:**
```bash
aws s3 sync poc_marh_agent/frontend/ s3://marh-agent-frontend-hml/ --delete
```

---

### 3. Lambda Function

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml` |
| **ARN** | `arn:aws:lambda:sa-east-1:445358171379:function:marh-agent-hml` |
| **Runtime** | Python 3.12 |
| **Handler** | `marh_agent.api.lambda_handler.lambda_handler` |
| **Memória** | 512 MB |
| **Timeout** | 30 segundos |
| **Tracing** | X-Ray Active |
| **Layer** | `marh-agent-hml-deps` (pydantic + dependências) |
| **Source** | `poc_marh_agent/backend/src/` (zipado pelo Terraform) |

**Variáveis de ambiente:**

| Variável | Valor (HML) | Descrição |
|----------|-------------|-----------|
| `AGENT_MODE` | `MOCK_LOCAL` | Mock (Fase 1) → `INTEGRATED` (Fase 2+) |
| `ENVIRONMENT` | `HML` | Ambiente |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `MAX_MESSAGE_LENGTH` | `2000` | Limite de caracteres |
| `MA_HR_ORCH_BASE_URL` | *(vazio)* | Preenchido na Fase 2 |
| `MA_HR_ORCH_TIMEOUT_SECONDS` | `10` | Timeout HTTP |
| `BEDROCK_REGION` | `sa-east-1` | Região do Bedrock |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-*` | Modelo LLM |
| `BEDROCK_KNOWLEDGE_BASE_ID` | *(vazio)* | Preenchido na Fase 3 |
| `CORS_ALLOWED_ORIGINS` | *(ver tfvars)* | Origens CORS |

---

### 4. Lambda Layer

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml-deps` |
| **Runtime** | Python 3.12 |
| **Pacotes** | pydantic, pydantic-core, annotated-types, typing-inspection |
| **Tamanho** | ~3.5 MB |
| **Build** | `infra/build_layer.sh` |

---

### 5. API Gateway HTTP API

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml` |
| **ID** | `pzn843po3h` |
| **URL** | `https://pzn843po3h.execute-api.sa-east-1.amazonaws.com` |
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
| Allow Origins | CloudFront, localhost, meualelo-webviews |
| Allow Methods | `POST`, `OPTIONS` |
| Allow Headers | `Content-Type`, `Authorization`, `X-Correlation-Id` |
| Max Age | 3600s |

---

### 6. IAM Role

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent-hml-lambda-role` |
| **Trusted entity** | `lambda.amazonaws.com` |

**Policies:**

| Policy | Tipo | Permissões |
|--------|------|------------|
| `AWSLambdaBasicExecutionRole` | AWS Managed | CloudWatch Logs |
| `AWSXRayDaemonWriteAccess` | AWS Managed | X-Ray traces |
| `secrets-read` | Inline | `secretsmanager:GetSecretValue` |
| `bedrock-invoke` | Inline | `bedrock:InvokeModel`, `Retrieve`, `RetrieveAndGenerate` |

---

### 7. Secrets Manager

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `marh-agent/hml/ma-hr-orch-credentials` |
| **ARN** | `arn:aws:secretsmanager:sa-east-1:445358171379:secret:marh-agent/hml/ma-hr-orch-credentials-pNOdK4` |
| **Conteúdo** | `{"api_key": "PLACEHOLDER", "base_url": "PLACEHOLDER"}` |

> ⚠️ Preencher manualmente no console com credenciais reais na Fase 2.

---

### 8. CloudWatch Log Groups

| Log Group | Retenção | Origem |
|-----------|----------|--------|
| `/aws/lambda/marh-agent-hml` | 30 dias | Lambda function |
| `/aws/apigateway/marh-agent-hml` | 30 dias | API Gateway access logs |

---

## Custos Estimados (HML com uso baixo)

| Recurso | Estimativa mensal |
|---------|-------------------|
| Lambda (poucas invocações) | ~$0 (free tier) |
| API Gateway (poucas requests) | ~$0 (free tier) |
| CloudFront (pouco tráfego) | ~$0 (free tier) |
| S3 (poucos MB) | ~$0.01 |
| CloudWatch Logs (poucos MB) | ~$0.50 |
| Secrets Manager (1 secret) | ~$0.40 |
| X-Ray (poucos traces) | ~$0 (free tier) |
| **Total estimado** | **< $1/mês** |

---

## Recursos Futuros (por Fase)

| Fase | Recursos a adicionar |
|------|---------------------|
| **Fase 2** | Nenhum recurso novo (só muda env vars da Lambda) |
| **Fase 3** | S3 Bucket (documentos RAG), Bedrock Knowledge Base |
| **Fase 4** | Nenhum recurso novo (só muda `BEDROCK_MODEL_ID`) |
| **Fase 5** | API Gateway Authorizer (JWT), CloudWatch Alarms |

---

## Arquivo Terraform → Recurso

| Arquivo | Recursos |
|---------|----------|
| `main.tf` | Provider AWS, versão Terraform |
| `lambda.tf` | Lambda function, Lambda Layer, IAM role, IAM policies, CloudWatch log group |
| `api_gateway.tf` | HTTP API, stage, integration, routes, lambda permission, API log group |
| `amplify.tf` | S3 bucket, website config, public access, bucket policy |
| `cloudfront.tf` | CloudFront distribution |
| `secrets.tf` | Secrets Manager secret + version |
| `variables.tf` | Variáveis de entrada |
| `locals.tf` | `env_lower` |
| `outputs.tf` | api_url, frontend_url, lambda ARN/name, secret ARN |
| `terraform.tfvars` | Valores para HML |
