# Deployment — MARH Agent

## Pré-requisitos

| Item | Versão mínima | Comando para verificar |
|------|---------------|----------------------|
| Python | 3.12 | `python --version` |
| Node.js | 20 | `node --version` |
| AWS CDK CLI | 2.150+ | `cdk --version` |
| AWS CLI | 2.x | `aws --version` |
| Conta AWS | — | `aws sts get-caller-identity` |

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
| `CORS_ALLOWED_ORIGINS` | Sim | `localhost:8080` | Origens permitidas (vírgula) |

## Deploy Manual (primeira vez)

### 1. Bootstrap do CDK

```bash
# Configurar credenciais AWS
aws configure

# Bootstrap (uma vez por conta/região)
cdk bootstrap aws://ACCOUNT_ID/sa-east-1
```

### 2. Deploy do stack HML

```bash
cd infra
pip install -r requirements.txt
cdk deploy marh-agent-hml
```

O CDK vai mostrar os recursos que serão criados. Confirme com `y`.

### 3. Verificar o deploy

```bash
# O output do CDK mostra a URL da API
# Exemplo: https://abc123.execute-api.sa-east-1.amazonaws.com

# Health check
curl https://API_URL/health

# Testar chat
curl -X POST https://API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "emp-001",
    "user_id": "usr-001",
    "session_id": "sess-001",
    "message": "O que posso fazer?",
    "environment": "HML"
  }'
```

## Deploy Automático (CI/CD)

Após configurar o OIDC (ver `.github/SETUP_AWS_OIDC.md`):

- **Push em `main`** → test → build → deploy automático em HML
- **Pull Request** → test + build (sem deploy)
- **Deploy PRD** → manual com aprovação (Fase 5)

## Rollback

### Via CDK

```bash
cd infra
# Voltar para commit anterior
git checkout COMMIT_ANTERIOR -- infra/ poc_marh_agent/backend/src/
cdk deploy marh-agent-hml
```

### Via Console AWS

1. Lambda → Versions → selecionar versão anterior
2. Ou: CloudFormation → Stack → Roll back

### Via Lambda (hotfix rápido)

```bash
# Apontar alias para versão anterior
aws lambda update-alias \
  --function-name marh-agent-hml \
  --name live \
  --function-version VERSAO_ANTERIOR
```

## Estrutura de Ambientes

| Ambiente | Stack | AGENT_MODE | Deploy |
|----------|-------|-----------|--------|
| Local | — | MOCK_LOCAL | `uvicorn` |
| HML | `marh-agent-hml` | MOCK_LOCAL (Fase 1) → INTEGRATED (Fase 2+) | Automático no push |
| PRD | `marh-agent-prd` | INTEGRATED | Manual com aprovação |

## Monitoramento pós-deploy

| O que verificar | Como |
|-----------------|------|
| Lambda errors | CloudWatch → Log group `/aws/lambda/marh-agent-hml` |
| Latência | CloudWatch → Metrics → Lambda → Duration |
| Throttling | API Gateway → Metrics → 429 count |
| Tracing | X-Ray → Service map |

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| 502 Bad Gateway | Lambda timeout ou crash | Verificar logs no CloudWatch |
| 403 Forbidden | CORS ou IAM | Verificar `CORS_ALLOWED_ORIGINS` e role |
| 429 Too Many Requests | Throttling | Aumentar limits no API Gateway |
| Cold start lento (>3s) | Muitas deps no zip | Considerar Lambda Layer ou provisioned concurrency |
| `ModuleNotFoundError` | Empacotamento incorreto | Verificar que `marh_agent/` está no raiz do zip |
