# 04 — Arquitetura Recomendada

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1 (São Paulo)
**Status:** DRAFT

---

## 1. Visão Geral

A arquitetura do Agente Consultivo MARH opera exclusivamente na região `sa-east-1`, sem VPC, sem API Gateway
e sem estado persistente (stateless). O agente é invocado diretamente pela API MARH via InvokeFunction (AWS SDK) — opção preferencial — ou Function URL com AWS_IAM.

O agente não implementa autorização corporativa própria. A autorização é responsabilidade da ma-hr-orch.
O LLM é usado somente nos fluxos RAG_ONLY (geração de resposta informativa). Os fluxos API_ONLY
usam templates determinísticos.

---

## 2. Arquitetura POC — Fluxo Geral

```
API MARH
  └─→ InvokeFunction (AWS SDK + IAM role) [Preferencial]
      ou Function URL com AWS_IAM + SigV4 [Alternativa]
          │
          ▼
    Lambda em sa-east-1 (Python 3.12)
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  [1] Valida contexto confiável                          │
    │       company_id presente e format válido               │
    │       Empresa não pode ser alterada pelo chat           │
    │                                                         │
    │  [2] Classificador determinístico                       │
    │       Regex + keywords — sem LLM                        │
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │ CLIENT_POLICY / STATIC_RESPONSE                  │   │
    │  │   → resposta determinística sem LLM              │   │
    │  │   Intenções: INT-008-009, INT-011-018, INT-021   │   │
    │  │   Fora de escopo: INT-022-027                    │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │ API_ONLY                                         │   │
    │  │   Intenções: INT-001-005                         │   │
    │  │   [Extrai parâmetro deterministicamente]         │   │
    │  │   → ma-hr-orch (GET only)                        │   │
    │  │   → validação de schema                          │   │
    │  │   → allowlist (campos reais)                     │   │
    │  │   → sanitização complementar                     │   │
    │  │   → template determinístico                      │   │
    │  │   → resposta sem LLM                             │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │ RAG_ONLY                                         │   │
    │  │   Intenções: INT-010, INT-013, INT-019, INT-020  │   │
    │  │   → embedding In-Region (modelo confirmado)      │   │
    │  │   → S3 Vectors em sa-east-1                      │   │
    │  │   → chunks + contexto mínimo                     │   │
    │  │   → modelo de geração In-Region (uma chamada)    │   │
    │  │   → validação final sem PII                      │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                         │
    │  [3] Validação final da resposta                        │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
          │
          ▼
    Resposta à API MARH
```

---

## 3. Tabela de Componentes

| Componente Lógico | Serviço AWS | Responsabilidade | Justificativa |
|---|---|---|---|
| Entrada | InvokeFunction (AWS SDK) ou Function URL AWS_IAM | Invocação pela API MARH | Sem API Gateway — sem custo adicional |
| Runtime do Agente | AWS Lambda (Python 3.12) | Classificação, roteamento, orquestração | Serverless, pay-per-use, sem infra |
| Modelo LLM | Amazon Bedrock — PROPOSED_PENDING_ACCOUNT_VALIDATION | Geração RAG_ONLY | Somente para INT-010, INT-013, INT-019, INT-020 |
| Embedding | Amazon Bedrock — PROPOSED_PENDING_ACCOUNT_VALIDATION | Vetorização de query | Geração de embedding para RAG |
| RAG — Retrieval | Lambda → S3 Vectors direto | Consulta vetorial | Preferencial; KB gerenciada depende de confirmação |
| Vector Store | Amazon S3 Vectors (sa-east-1) | Armazenamento de embeddings | REQUIRES_ACCOUNT_VALIDATION |
| Fonte documental | Amazon S3 (KMS + Versioning) | marh_feature_knowledge.md | Versioning, criptografia, metadados |
| Segredos | AWS Secrets Manager | Token ma-hr-orch (se necessário) | Rotação, KMS |
| Criptografia | AWS KMS | S3 docs, Secrets Manager | CMK regional |
| Logs | Amazon CloudWatch Logs | Logs estruturados JSON | Nativo, retenção curta |
| Métricas | Amazon CloudWatch Metrics | Latência, erros | Nativo |
| Tracing | AWS X-Ray | Rastreamento end-to-end | Nativo Lambda |
| HTTP Client | Lambda runtime (httpx) | GET ao ma-hr-orch | Simples, sem overhead |

---

## 4. Características da POC

| Característica | Valor |
|---|---|
| Stateless | ✅ Sem DynamoDB, sem cache corporativo |
| VPC | ❌ Lambda fora de VPC |
| NAT Gateway | ❌ Sem custo de rede |
| API Gateway | ❌ API MARH invoca diretamente |
| LLM em API_ONLY | ❌ Template determinístico |
| LLM em CLIENT_POLICY | ❌ Resposta estática |
| LLM em REDIRECT | ❌ Mensagem fixa |
| LLM em RAG_ONLY | ✅ Uma chamada de geração |
| Cross-Region | ❌ Proibido — todos os serviços em sa-east-1 |
| RBAC inventado | ❌ Removido — autorização na ma-hr-orch |
| Cache de dados corporativos | ❌ Dado sempre fresco via ma-hr-orch |
| Operações de escrita | ❌ Somente GET |
| Múltiplos agentes | ❌ Single agent |

---

## 5. Decisões de Design Fundamentais

### 5.1 Classificação Determinística

Nenhuma chamada LLM para classificar a intenção. Usa regex, keywords e regras para mapear para os 27 intents definidos no catálogo real (`intents_catalog.json`).

### 5.2 PII como Parâmetro Técnico Transitório

O CPF e nome são extraídos da mensagem do usuário apenas como parâmetros técnicos transitórios para a chamada da API. CPF:
- usado como parâmetro `nameOrCpf`
- nunca logado
- nunca persistido
- nunca enviado ao modelo
- nunca aparece na resposta

### 5.3 Somente Operações GET

Nenhuma operação de escrita via ma-hr-orch. O agente é exclusivamente consultivo.

### 5.4 Mensagens de Erro do Discovery (ERR-001 a ERR-010)

Respostas de erro consistentes usando exclusivamente as mensagens definidas no catálogo de requisitos. Sem segundo catálogo com textos diferentes.

### 5.5 Sem Cache de Dados Corporativos

Cada consulta busca dados frescos do ma-hr-orch. Evita inconsistência de dados.

### 5.6 Empresa Imutável via Chat

A empresa selecionada vem do contexto confiável (payload da API MARH). O usuário não pode alterar a empresa digitando CNPJ, contrato ou nome no chat.

### 5.7 Region Lock

Todos os serviços em sa-east-1. Sem inferência cross-region. Modelo processado na região.

---

## 6. Estratégia RAG — Preferencial para POC

**Desenho preferencial (Bedrock Knowledge Bases não confirmada em sa-east-1):**

```
Lambda em sa-east-1
  → gera embedding da query (modelo In-Region confirmado)
  → consulta S3 Vectors diretamente em sa-east-1
  → recupera top-k chunks (ASSUMPTION_REQUIRES_EVALUATION)
  → monta contexto mínimo (limite de tokens)
  → chama modelo de geração In-Region (uma chamada)
  → retorna resposta
```

**Fonte da KB:** `marh_feature_knowledge.md` — indexado por seções do markdown com metadados:
- `section_id`
- `topic`
- `source_file`
- `content_version`
- `approval_status`

**Não indexar:** `agent_policy.md` — política fica no código determinístico.

**Parâmetros marcados como ASSUMPTION_REQUIRES_EVALUATION:**
- top-k inicial
- threshold de score
- limite de tokens por contexto

**Fallback quando não há evidência:** ERR-008 (sem LLM) quando score abaixo do threshold.

---

## 7. Componentes NÃO Implementar na POC

| Componente | Motivo |
|---|---|
| VPC + NAT Gateway | $105/mês, cold start adicional, desnecessário para POC |
| API Gateway | API MARH invoca direto |
| DynamoDB | POC stateless |
| OpenSearch Serverless | $700/mês mínimo |
| Multi-Agent | Desnecessário — um agente atende 27 intenções |
| Cross-Region Inference | Proibido por requisito |
| Bedrock Agents Classic | Descontinuado para novos clientes |
| ElastiCache | Sem cache de dados corporativos |
| Rate limiting in-memory global | Não confiável entre instâncias |
| Circuit breaker distribuído em memória | Não compartilhado entre instâncias |
| WAF | Produção |
| Bedrock Guardrails | Produção |
| CI/CD | Pós-POC |
| Frontend | Fora do escopo |

---

## 8. Componentes a Adicionar Posteriormente

| Componente | Quando | Motivo |
|---|---|---|
| Sessão/Histórico (DynamoDB) | Pós-POC | Contexto multi-turno |
| API Management (API Gateway) | Produção | Rate limiting, throttling, métricas |
| Proteção DDoS (WAF + Shield) | Produção | Segurança de borda |
| Guardrails nativos (Bedrock) | Produção | Proteção prompt injection nativa |
| CI/CD (CodePipeline) | Pós-POC | Automação de deploy |
| IaC (AWS CDK) | Produção | Infraestrutura como código |
| CloudTrail + Config | Produção | Compliance |
| VPC (se necessário) | Se ma-hr-orch migrar para rede privada | Isolamento de rede |
