# 00 — Resumo da Decisão Arquitetural

> **Data:** 2026-07-23  
> **Região:** `sa-east-1` exclusivamente  
> **Status:** Desenho — nenhum recurso criado

---

## Alternativa Recomendada

**Alternativa B — AWS Lambda com orquestração própria**

## Justificativa

| Critério | Resultado |
|---|---|
| Prazo de implementação | Menor — sem dependência de novo serviço |
| Latência | Controlável — provisioned concurrency disponível |
| Concorrência | Até 1.000 execuções simultâneas por padrão (aumento via quota) |
| Segurança | IAM nativo, sem secrets em variáveis, KMS integrado |
| Custo variável | Pay-per-use — R$0 quando inativo |
| Custo fixo | Zero (sem NAT, sem container always-on, sem OpenSearch Serverless) |
| Overhead operacional | Mínimo — serverless gerenciado |
| Facilidade de testes | Alta — invocação local, mocks, event-driven |
| Evolução para produção | Direta — adicionar provisioned concurrency, WAF, observabilidade |
| Disponibilidade em sa-east-1 | Confirmada para todos os componentes |
| Risco de lock-in | Baixo — lógica em Python/Node.js, modelo via API padrão |

## Componentes Selecionados

| Componente lógico | Serviço AWS | Justificativa |
|---|---|---|
| Entrada da API | Integração direta com API MARH (HTTPS) | Sem API Gateway extra — API MARH já é o gateway |
| Runtime do agente | AWS Lambda (Python 3.12) | Serverless, pay-per-use, escalável |
| Modelo LLM | Amazon Bedrock — Claude 3.5 Haiku | In-Region em sa-east-1, baixa latência, tool use, baixo custo |
| Modelo alternativo | Amazon Bedrock — Claude Sonnet 4 | In-Region via inference profile sa-east-1, maior capacidade |
| RAG — Knowledge Base | Amazon Bedrock Knowledge Bases | Gerenciado, integrado com S3 e embeddings |
| Armazenamento vetorial | Amazon S3 Vectors | Custo mínimo, sem servidor always-on, disponível em sa-east-1 |
| Fonte documental RAG | Amazon S3 (bucket versionado, KMS) | Padrão, baixo custo, versionamento nativo |
| Segredos | AWS Secrets Manager | Rotação automática, KMS |
| Estado de sessão | Stateless (contexto na requisição) | Sem DynamoDB na POC — mínimo necessário |
| Observabilidade | CloudWatch Logs + X-Ray | Regional, integrado com Lambda |
| Criptografia | AWS KMS (chave regional) | Criptografia at-rest e in-transit |

## Modelo Recomendado

| Papel | Modelo | Model ID | Justificativa |
|---|---|---|---|
| Principal (geração) | Claude 3.5 Haiku | anthropic.claude-3-5-haiku-20241022-v1:0 | Rápido, barato, tool use, português, in-region sa-east-1 |
| Alternativo (qualidade) | Claude Sonnet 4 | anthropic.claude-sonnet-4-20250514-v1:0 | Melhor raciocínio, para casos complexos |
| Classificação | Determinístico (sem LLM) | N/A | Keyword matching + regex — evita chamada ao modelo |

## Vector Store Recomendado

**Amazon S3 Vectors**

- Custo: ~$0.0065/milhão de vetores/hora + $0.020/10k queries
- Sem custo fixo mínimo (diferente de OpenSearch Serverless ~$700/mês)
- Disponível em sa-east-1 (expandido em março 2026)
- Integração nativa com Bedrock Knowledge Bases
- Adequado ao corpus pequeno (~1 documento markdown)

## Custo Fixo Estimado (POC)

| Item | Custo mensal |
|---|---|
| Lambda | $0 (free tier + pay-per-use) |
| S3 (documentos) | < $1 |
| S3 Vectors | < $5 |
| Secrets Manager | ~$1 |
| CloudWatch Logs | ~$5 |
| KMS | ~$1 |
| **Total fixo** | **< $13/mês** |

## Principais Custos Variáveis

- Tokens de entrada/saída no Bedrock (Claude 3.5 Haiku): ~$0.25/1M input, ~$1.25/1M output
- Embeddings (Titan Embed): ~$0.02/1M tokens
- Lambda invocations: incluídas no free tier para POC

## Latência Esperada por Rota

| Rota | P50 estimado | P95 estimado |
|---|---|---|
| STATIC_RESPONSE | < 100ms | < 200ms |
| RAG_ONLY | 1.5–2.5s | 3–4s |
| API_ONLY | 2–4s | 5–7s |
| HYBRID_RAG_API | 2.5–4.5s | 5–8s |

## Capacidade Estimada

Com quota padrão de Lambda (1.000 concurrent):
- ~200–500 usuários simultâneos (considerando 2–5s por request)
- Gargalo provável: quotas do Bedrock e latência da ma-hr-orch

## Principais Gargalos

1. Quotas de tokens/minuto do Bedrock em sa-east-1
2. Latência da ma-hr-orch (3.275ms observado para beneficiaries)
3. Cold start do Lambda (mitigável com provisioned concurrency)

## Controles de Segurança

- Sanitização determinística de PII antes do modelo
- Allowlist de campos por tool
- Validação de schema na entrada e saída
- Empresa vem do contexto confiável (API MARH)
- Sem cross-Region — dados permanecem em sa-east-1
- KMS para criptografia at-rest
- TLS 1.2+ para in-transit
- IAM least privilege

## Bloqueadores Regionais

**Nenhum identificado.** Todos os serviços propostos estão disponíveis em sa-east-1.

## Riscos Pendentes

1. Quotas de Bedrock em sa-east-1 podem ser menores que em us-east-1
2. Sanitização de PII na ma-hr-orch não confirmada (DP-006)
3. Endpoint de rastreamento não inventariado (DP-001)
4. Latência da ma-hr-orch pode dominar o orçamento total

## Escopo Exato da POC

12 cenários de demonstração (ver `12_plano_poc.md`):
1. Resposta estática (fora do escopo)
2–4. Perguntas RAG (informativas sobre MARH)
5. Consulta de colaborador por nome
6. Consulta de pedido por número
7. Consulta do último pedido
8. Consulta de pedidos por status
9. Falta de empresa selecionada
10. Usuário sem permissão
11. API indisponível
12. Tentativa de trocar empresa pelo chat

## Prazo Técnico Estimado

| Etapa | Duração |
|---|---|
| Setup AWS (Lambda, S3, Bedrock, KMS) | 2–3 dias |
| Implementação do classificador + roteador | 2–3 dias |
| Integração Bedrock (prompt + tool use) | 3–4 dias |
| Integração ma-hr-orch (cliente HTTP) | 3–4 dias |
| RAG (Knowledge Base + S3 Vectors) | 2–3 dias |
| Sanitização + segurança | 2–3 dias |
| Testes de integração | 3–4 dias |
| **Total estimado** | **17–24 dias úteis** |

---

*Decisão tomada com base em: discovery (2026-07-22), documentação AWS (2026-07-23), restrição regional sa-east-1*
