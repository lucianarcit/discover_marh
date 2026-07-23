# 14 — Architecture Decision Records (ADRs)

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1

Status permitidos: ACCEPTED | PROPOSED | PROPOSED_PENDING_VALIDATION | REJECTED | SUPERSEDED

---

## ADR-001: Runtime Choice — AWS Lambda

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

Utilizar **AWS Lambda (Python 3.12)** como runtime do agente.

### Consequências

- ✅ Zero custo fixo (pay per invocation)
- ✅ Auto-scaling nativo
- ✅ Sem gestão de infraestrutura
- ✅ Integração nativa com CloudWatch e X-Ray
- ⚠️ Cold start (~300ms) aceitável para o caso de uso

---

## ADR-002: Model Choice

| Campo | Valor |
|---|---|
| **Status** | PROPOSED_PENDING_VALIDATION |
| **Data** | 2026-07-23 |
| **Reaberto em** | 2026-07-23 (revisão corretiva) |

### Contexto

Claude 3.5 Haiku (`anthropic.claude-3-5-haiku-20241022-v1:0`) foi removido como seleção automática.
Status ACTIVE In-Region em `sa-east-1` não confirmado por evidência direta. A escolha do modelo
principal depende de verificação em conta real.

### Decisão

Nenhum modelo declarado como ACCEPTED. Seleção pendente de validação em conta.

**Critérios para seleção (pós-validação):**
- Status: ACTIVE
- Inferência: In-Region em sa-east-1 (não cross-region, não inference profile)
- Suporte a português brasileiro
- Tool use (para classificação futura se necessário)
- Baixa latência
- Custo compatível com POC
- Contexto suficiente (≥ 8K tokens)
- Disponibilidade on-demand

**Candidatos a verificar no console:**
- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-3-5-sonnet-20241022-v2:0`

**Uso:** LLM somente em RAG_ONLY (INT-010, INT-013, INT-019, INT-020).
API_ONLY usa templates determinísticos — sem chamada ao modelo.

**Procedimento:** `aws bedrock list-foundation-models --region sa-east-1 --by-inference-type ON_DEMAND`

---

## ADR-003: RAG Strategy

| Campo | Valor |
|---|---|
| **Status** | PROPOSED_PENDING_VALIDATION |
| **Data** | 2026-07-23 |
| **Reaberto em** | 2026-07-23 (revisão corretiva) |

### Contexto

Bedrock Knowledge Bases em `sa-east-1` não está confirmada com evidência oficial específica.
Integração Knowledge Bases + S3 Vectors requer validação separada.

### Decisão

**Desenho preferencial para POC:**

```
Lambda (sa-east-1)
  → embedding do query (modelo In-Region confirmado)
  → consulta direta a S3 Vectors em sa-east-1
  → recuperação de chunks
  → montagem de contexto mínimo
  → modelo de geração In-Region
```

**Fonte:** `marh_feature_knowledge.md` indexado por seções com metadados:
- `section_id`, `topic`, `source_file`, `content_version`, `approval_status`

**Não indexar:** `agent_policy.md` — fica no código determinístico.

**Parâmetros:** ASSUMPTION_REQUIRES_EVALUATION (top-k, threshold, limite de tokens).

**Fallback:** ERR-008 sem LLM quando score < threshold.

Bedrock Knowledge Bases gerenciada considerada apenas se confirmada com evidência documental oficial em sa-east-1.

---

## ADR-004: Vector Store — S3 Vectors

| Campo | Valor |
|---|---|
| **Status** | PROPOSED_PENDING_VALIDATION |
| **Data** | 2026-07-23 |

### Decisão

Utilizar **S3 Vectors** como vector store — verificar disponibilidade em sa-east-1 na conta alvo.

**Alternativa se S3 Vectors não disponível:** FAISS em Lambda layer (sem custo de serviço, mas requer gerenciamento de índice).

### Consequências

- ✅ Custo mínimo (corpus < 200 KB, < 50 vetores)
- ✅ Zero gerenciamento
- ⚠️ Serviço requer validação de disponibilidade em sa-east-1

---

## ADR-005: No VPC

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

Lambda executará **fora de VPC** no POC.

### Consequências

- ✅ Zero custo de rede
- ✅ Sem impacto em cold start
- ✅ Simplicidade operacional
- ⚠️ Migrar para VPC se ma-hr-orch migrar para rede privada ou se compliance exigir

---

## ADR-006: No NAT Gateway

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

**Não utilizar NAT Gateway.** Decorrência do ADR-005.

### Consequências

- ✅ Economia de $45/mês
- ✅ Sem ponto de falha adicional

---

## ADR-007: Session State — Stateless

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

POC será **stateless**. Cada requisição é processada independentemente.

### Consequências

- ✅ Simplicidade máxima
- ✅ Zero custo de storage
- ⚠️ Sem contexto de conversa — aceitável para POC

---

## ADR-008: Respostas Determinísticas (sem LLM)

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

Os seguintes fluxos utilizam respostas determinísticas sem LLM:
- **CLIENT_POLICY_RESPONSE:** INT-008, INT-009, INT-011–018, INT-021
- **REDIRECT_TO_OFFICIAL_JOURNEY:** INT-022–027
- **API_ONLY:** INT-001–005 — template determinístico após allowlist
- **REQUIRES_CLARIFICATION:** ERR-010 (INT-006)

LLM usado somente em **RAG_ONLY:** INT-010, INT-013, INT-019, INT-020.

### Consequências

- ✅ ~70% das requests sem custo de tokens
- ✅ Latência < 100ms para fluxos estáticos
- ✅ Respostas 100% previsíveis e controladas
- ✅ Sem risco de alucinação nos fluxos API e política

---

## ADR-009: Sem Cache de Dados Corporativos

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

**Não cachear dados corporativos** no POC. Cada consulta busca dados frescos da ma-hr-orch.

### Consequências

- ✅ Dados sempre atualizados
- ✅ Sem complexidade de invalidação
- ⚠️ Maior latência (sempre chama ma-hr-orch) — aceitável

---

## ADR-010: Observabilidade — CloudWatch + X-Ray

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

Utilizar **CloudWatch** (logs + metrics) + **AWS X-Ray** (tracing).

### Consequências

- ✅ Nativo AWS, zero setup adicional
- ✅ Logs JSON estruturados sem PII
- ✅ Custo ~$1–5/mês para POC

---

## ADR-011: Region Restriction — sa-east-1 Only

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

Todos os serviços AWS operam **exclusivamente em sa-east-1**.

### Restrições

- Sem cross-region inference
- Sem inference profile que roteia para outra região
- Sem armazenamento vetorial fora de sa-east-1
- Sem logs, backups ou documentos fora de sa-east-1
- Sem fallback silencioso para us-east-1

---

## ADR-012: No Cross-Region Inference

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

**Não utilizar cross-region inference.** Todas as inferências em sa-east-1.

### Consequências

- ✅ Dados nunca saem do Brasil
- ⚠️ Throughput limitado à capacidade regional — monitorar quotas

---

## ADR-013: Bedrock Agents Classic — Rejected

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Decisão

**Rejeitar Bedrock Agents Classic.** Descontinuado para novos clientes a partir de 30/07/2026.
Usar Lambda com orquestração própria.

---

## ADR-014: Sem RBAC Inventado — Autorização na ma-hr-orch

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Contexto

A versão anterior da arquitetura definia papéis `admin`, `rh`, `colaborador` no agente,
com uma tabela de permissões por papel sem fonte no cliente. Isso contradiz os requisitos
do Discovery (RN-004, SEG-001).

### Decisão

O agente **não implementa** autorização corporativa própria.

- Papéis `admin`, `rh`, `colaborador` removidos da arquitetura
- Sem tabela de permissões por papel no agente
- Sem `user_role` derivado do chat
- A ma-hr-orch é responsável por validar token, interlocutor, FNP, prova de vida
- O agente valida apenas presença/formato do company_id e impede troca pelo chat

### Consequências

- ✅ Alinhado com RN-004, SEG-001, ACE-004, ACE-006
- ✅ Autorização centralizada na ma-hr-orch
- ✅ Sem matriz de permissões a manter no agente

---

## ADR-015: Entrada da Lambda

| Campo | Valor |
|---|---|
| **Status** | PROPOSED_PENDING_VALIDATION |
| **Data** | 2026-07-23 |
| **Reaberto em** | 2026-07-23 (revisão corretiva) |

### Contexto

A versão anterior incluía `shared secret` como alternativa de autenticação. Shared secret
foi removido — não oferece garantias de segurança equivalentes ao IAM.

### Decisão

**Opção preferencial:**
```
API MARH → InvokeFunction (AWS SDK) → IAM role + resource-based policy da Lambda
```
Usar quando a API MARH estiver em ambiente AWS e puder assumir uma role.

**Alternativa:**
```
API MARH → Function URL com AWS_IAM → SigV4
```
- Sem autenticação anônima (AuthType=NONE proibido)
- Sem shared secret
- Requisição assinada com SigV4

Aguardando confirmação sobre hospedagem da API MARH (DP-001).

---

## ADR-016: Sem Circuit Breaker Distribuído em Memória

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |

### Contexto

A versão anterior descrevia um circuit breaker implementado em dicionário Python em memória da Lambda,
descrito como controle de resiliência. Memória da Lambda não é compartilhada entre instâncias — esse
padrão não funciona como controle global.

### Decisão

**Sem circuit breaker distribuído em memória na POC.**

Estratégia de resiliência:
- Máximo 1 retry para falhas transitórias (quando cabe no budget)
- Backoff com jitter
- Timeout global de 30s na Lambda
- Fallback determinístico (ERR-007)
- Reserved concurrency como proteção global da Lambda
- Throttling por usuário/empresa na API MARH

DynamoDB como alternativa para estado compartilhado apenas se houver justificativa explícita.

### Consequências

- ✅ Sem estado de segurança compartilhado em memória efêmera
- ✅ Arquitetura mais simples
- ⚠️ Sem proteção cascata entre instâncias — aceitável para POC
