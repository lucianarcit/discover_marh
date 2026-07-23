# Fase 1 — Fundação AWS (Concluída)

**Data de conclusão:** 2026-07-23  
**Status:** ✅ Completa e funcionando em produção (HML)

---

## Objetivo

Ter o Lambda funcional em HML respondendo com mocks — a mesma POC que funciona local, rodando na AWS com infraestrutura provisionada e pipeline de deploy.

---

## O que foi entregue

### Backend

| Entrega | Arquivo(s) | O que faz |
|---------|-----------|-----------|
| Config centralizado | `config.py` | Env vars para AWS (Bedrock, ma-hr-orch, CORS), Mode enum |
| Lambda handler | `lambda_handler.py` | Cold-start cache, seleção mock/real, GET /health, POST /chat |
| Local API refatorada | `local_api.py` | Usa mesma lógica de config do Lambda |
| Orchestrator dinâmico | `orchestrator.py` | Mode vem do config, não hardcoded |
| Fixtures no pacote | `src/marh_agent/fixtures/` | Acessíveis tanto local quanto no Lambda |
| Script de validação | `scripts/validate_lambda.py` | Testa 11 mensagens no handler local |

### Infraestrutura (Terraform)

| Arquivo | Recursos |
|---------|----------|
| `main.tf` | Provider AWS sa-east-1 |
| `lambda.tf` | Lambda + Layer + IAM Role + Policies + CloudWatch |
| `api_gateway.tf` | HTTP API + Rotas + Throttling + CORS + Access Logs |
| `amplify.tf` | S3 Bucket (frontend hosting) |
| `cloudfront.tf` | CloudFront distribution (HTTPS) |
| `secrets.tf` | Secrets Manager (placeholder para Fase 2) |
| `variables.tf` | Todas as variáveis parametrizáveis |
| `outputs.tf` | URLs, ARNs, nomes |

### CI/CD

| Arquivo | O que faz |
|---------|-----------|
| `.github/workflows/ci.yml` | Pipeline: test → lint → build → deploy (Terraform) |
| `.github/SETUP_AWS_OIDC.md` | Guia para conectar GitHub → AWS via OIDC |
| `deploy.ps1` | Script local: test → commit → push → terraform → s3 sync |

### Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `docs/architecture.md` | Diagrama, fluxo de dados, decisões de design |
| `docs/deployment.md` | Como deployar, rollback, troubleshooting |
| `docs/infra-resources.md` | Inventário completo dos recursos AWS |
| `docs/fase-1-completa.md` | Este documento |

---

## URLs Ativas

| Serviço | URL |
|---------|-----|
| **Frontend (HTTPS)** | https://d1vtu9x0di76z9.cloudfront.net |
| **API Gateway** | https://pzn843po3h.execute-api.sa-east-1.amazonaws.com |
| **Health Check** | https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/health |

---

## Validações Realizadas

### Testes automatizados
- 107/107 passando (unit + integração)
- Tempo: ~0.6s

### Validação das 11 mensagens (local + AWS)

| # | Mensagem | Intent | Variant | Status |
|---|----------|--------|---------|:---:|
| 1 | O que posso fazer? | INT-008 | capabilities_list | ✅ |
| 2 | Consultar colaborador Pessoa Colaboradora A | INT-001 | collaborator_summary | ✅ |
| 3 | Consultar CPF 000.000.000-00 | INT-002 | collaborator_summary | ✅ |
| 4 | Consultar pedido 342671 | INT-003 | order_summary | ✅ |
| 5 | Qual foi o último pedido? | INT-004 | order_summary | ✅ |
| 6 | Pedidos com status pago | INT-005 | order_list | ✅ |
| 7 | Rastrear cartões pelo CPF | INT-006 | clarification | ✅ |
| 8 | Rastrear pedido 342671 | INT-007 | warning_notice | ✅ |
| 9 | Cancele o pedido 342671 | INT-022 | transactional_redirect | ✅ |
| 10 | Troque para outra empresa | COMPANY_SWITCH | informational_notice | ✅ |
| 11 | O que é o MARH? | INT-019 | knowledge_answer | ✅ |

---

## Decisões tomadas durante a Fase 1

| Decisão | Razão |
|---------|-------|
| Terraform em vez de CDK | Preferência do time; multi-cloud futuro; sem gerenciar state no CloudFormation |
| S3 + CloudFront em vez de Amplify | Token fine-grained do GitHub incompatível com Amplify; S3 é mais simples |
| Lambda Layer para deps | Separa dependências do código; reduz tamanho do zip de deploy |
| Fixtures dentro do pacote (`src/marh_agent/fixtures/`) | Lambda não tem acesso ao filesystem fora do zip |
| CSP com URL da API | Browser bloqueia fetch sem `connect-src` explícito |
| CORS com múltiplas origens | CloudFront + localhost + domínio oficial |
| `AGENT_MODE` como env var | Permite trocar mock → real sem alterar código |

---

## Problemas encontrados e resolvidos

| Problema | Causa | Solução |
|----------|-------|---------|
| `ModuleNotFoundError: pydantic` | Zip do Lambda só tinha source, sem deps | Criado Lambda Layer com deps |
| Health check retornava 422 | Lambda não distinguia GET /health de POST /chat | Adicionado routing por `rawPath` + `httpMethod` |
| Fixtures não encontrados no Lambda | Path relativo (`parents[3]`) inválido no zip | Movido fixtures pra dentro do pacote; path = `parent.parent/fixtures` |
| Frontend não conectava na API | CSP `connect-src` só permitia localhost | Adicionado URL da API no CSP dos HTMLs |
| S3 (HTTP) → API (HTTPS) bloqueado | Browser bloqueia mixed content | Adicionado CloudFront para servir frontend via HTTPS |

---

## Fluxo de deploy atual

```
Desenvolvedor
     │
     ├── Edita código
     ├── Roda: python -m pytest
     ├── Roda: .\deploy.ps1 "mensagem"
     │         │
     │         ├── [1] pytest (107 testes)
     │         ├── [2] git add + commit
     │         ├── [3] git push origin main
     │         ├── [4] terraform apply (Lambda + infra)
     │         └── [5] aws s3 sync (frontend)
     │
     ▼
AWS (sa-east-1)
     ├── CloudFront → S3 (frontend)
     └── API Gateway → Lambda (backend)
```

---

## Próximos passos (Fase 2)

A Fase 2 foca na **integração com o ma-hr-orch real**:

1. Implementar `clients/http_ma_hr_orch.py` (HTTP com retry + backoff)
2. Mapear erros HTTP → exceções do router
3. Atualizar allowlists com schema real da API
4. Resolver gap de segurança do campo `steps`
5. Testes de contrato contra sandbox
6. Trocar `AGENT_MODE` de `MOCK_LOCAL` para `INTEGRATED`

**Critério de aceite:** INT-001 a INT-005 funcionando com dados reais em HML.
