# Deployment — MARH Agent

## Pré-requisitos

| Item | Versão mínima | Comando para verificar |
|------|---------------|----------------------|
| Python | 3.12 | `python --version` |
| Terraform | 1.5+ | `terraform --version` |
| AWS CLI | 2.x | `aws --version` |
| Conta AWS | — | `aws sts get-caller-identity` |

## URLs dos Ambientes

| Ambiente | Frontend | API |
|----------|----------|-----|
| **Local** | `http://localhost:8080` | `http://localhost:8000` |
| **HML (AWS)** | `https://d1vtu9x0di76z9.cloudfront.net` | `https://pzn843po3h.execute-api.sa-east-1.amazonaws.com` |
| **PRD** | *(Fase 5)* | *(Fase 5)* |

## Variáveis de Ambiente da Lambda

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `AGENT_MODE` | Sim | `MOCK_LOCAL` | `MOCK_LOCAL` ou `INTEGRATED` |
| `ENVIRONMENT` | Sim | `HML` | `HML` ou `PRD` |
| `LOG_LEVEL` | Não | `INFO` | Nível de log |
| `MAX_MESSAGE_LENGTH` | Não | `2000` | Tamanho máximo da mensagem |
| `MA_HR_ORCH_BASE_URL` | Fase 2+ | — | URL base da API ma-hr-orch |
| `MA_HR_ORCH_TIMEOUT_SECONDS` | Não | `10` | Timeout das chamadas HTTP |
| `BEDROCK_REGION` | Fase 3+ | `sa-east-1` | Região do Bedrock |
| `BEDROCK_MODEL_ID` | Fase 4+ | `anthropic.claude-3-haiku-*` | Model ID do classificador |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Fase 3+ | — | ID da Knowledge Base |
| `CORS_ALLOWED_ORIGINS` | Sim | *(ver tfvars)* | Origens permitidas (vírgula) |

## Deploy com Script (recomendado)

O jeito mais simples — testa, commita, pusha e deploya tudo de uma vez:

```powershell
.\deploy.ps1 "sua mensagem de commit"
```

O script faz:
1. Roda pytest (107+ testes)
2. Git add + commit
3. Git push para GitHub
4. Terraform apply (atualiza Lambda + infra)
5. S3 sync (atualiza frontend)
6. CloudFront invalidation (limpa cache)

Se qualquer passo falhar, ele para.

## Deploy Manual (passo a passo)

### 1. Configurar credenciais AWS

```bash
aws configure
# ou usar SSO:
aws sso login
```

### 2. Primeiro deploy (apenas uma vez)

```bash
cd infra
terraform init
terraform apply
```

### 3. Deploys subsequentes

```bash
# Backend (Lambda)
cd infra
terraform apply -auto-approve

# Frontend (S3 + CloudFront)
aws s3 sync poc_marh_agent/frontend/ s3://marh-agent-frontend-hml/ --delete
aws cloudfront create-invalidation --distribution-id E29TLS56TW0RXY --paths "/*"
```

### 4. Verificar o deploy

```bash
# Health check
curl https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/health

# Testar chat
curl -X POST https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "emp-001",
    "user_id": "usr-001",
    "session_id": "sess-001",
    "message": "O que posso fazer?",
    "environment": "HML"
  }'
```

## Rodar Localmente

```bash
# Backend (FastAPI com mocks)
cd poc_marh_agent/backend
pip install -e ".[dev]"
uvicorn marh_agent.api.local_api:app --reload --port 8000

# Frontend (qualquer servidor estático)
cd poc_marh_agent/frontend
python -m http.server 8080
```

## Rollback

### Via Terraform

```bash
cd infra
git checkout COMMIT_ANTERIOR -- infra/ poc_marh_agent/backend/src/
terraform apply -auto-approve
```

### Via Console AWS (hotfix)

Lambda → escolher versão anterior → publicar

## Deploy Automático (CI/CD — GitHub Actions)

Configurado mas requer OIDC (ver `.github/SETUP_AWS_OIDC.md`):

- **Push em `main`** → test → lint → build → deploy HML
- **Pull Request** → test + lint (sem deploy)
- **Deploy PRD** → manual com aprovação (Fase 5)

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| 502 Bad Gateway | Lambda timeout ou crash | Verificar logs: `aws logs tail /aws/lambda/marh-agent-hml` |
| 403 Forbidden | CORS | Verificar `CORS_ALLOWED_ORIGINS` no tfvars |
| 429 Too Many Requests | Throttling | Aumentar limits no terraform.tfvars |
| `ModuleNotFoundError` | Faltam deps no Layer | Rebuild: `bash infra/build_layer.sh` + terraform apply |
| Frontend não atualiza | Cache CloudFront | Invalidar: `aws cloudfront create-invalidation --distribution-id E29TLS56TW0RXY --paths "/*"` |
| CSP bloqueando API | Content-Security-Policy no HTML | Adicionar URL da API no `connect-src` |
