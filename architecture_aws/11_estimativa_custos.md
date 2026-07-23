# 11 — Estimativa de Custos

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1
**Status:** DRAFT

---

## Premissas Gerais

| Premissa | Valor |
|---|---|
| Modelo LLM | PROPOSED_PENDING_ACCOUNT_VALIDATION — preços marcados como PRICE_REQUIRES_VALIDATION |
| Modelo de embedding | PROPOSED_PENDING_ACCOUNT_VALIDATION |
| Bedrock Knowledge Bases | Não confirmada em sa-east-1 — usando S3 Vectors direto |
| LLM em API_ONLY | ❌ Removido — template determinístico |
| LLM em CLIENT_POLICY/REDIRECT | ❌ Removido — resposta estática |
| LLM em RAG_ONLY | ✅ Uma chamada por request (INT-010, INT-013, INT-019, INT-020) |
| Corpus da KB | `marh_feature_knowledge.md` — arquivo real, estimado < 200 KB |
| Vetores estimados | Baseado em tamanho real — não assumir 20 GB |

---

## 1. Custos Fixos

| Serviço | Custo Fixo Mensal | Notas |
|---|---|---|
| Lambda | $0 (free tier: 1M requests + 400K GB-s) | POC dentro do free tier |
| S3 (documentos KB) | < $0.01 | Corpus real < 200 KB |
| S3 Vectors | PRICE_REQUIRES_VALIDATION | Depende de confirmação disponibilidade e preço em sa-east-1 |
| Secrets Manager | ~$0.40–0.80 | 1–2 secrets × $0.40 |
| KMS | ~$2.00 | 2 CMKs × $1.00 |
| CloudWatch Logs | ~$1.00–3.00 | Retenção curta (~30 dias) |
| X-Ray | ~$0 | Free tier 100K traces |
| **TOTAL FIXO (sem Bedrock, sem S3 Vectors)** | **~$4–6/mês** | Significativamente menor que versão anterior |

---

## 2. Corpus Real — Tamanho

| Arquivo | Tamanho estimado |
|---|---|
| `marh_feature_knowledge.md` | < 200 KB |
| Chunks estimados (512 tokens) | < 50 chunks |
| Vetores estimados | < 50 vetores |

**A versão anterior assumia 20 GB de corpus. O corpus real é < 200 KB. O custo de storage vetorial é desprezível.**

---

## 3. Custos Variáveis

### 3.1 Lambda

```
Custo Lambda = (invocações × $0.20/1M) + (duração_GB_s × $0.0000166667)

POC (100 req/dia = 3.000 req/mês):
  Invocações: $0.0006 (free tier cobre)
  Duração: 3.000 × 0.5GB × 3s = 4.500 GB-s → $0.075 (free tier cobre)
  Total Lambda POC: ~$0 (dentro do free tier)
```

### 3.2 Bedrock — LLM (RAG_ONLY apenas)

**Status:** PRICE_REQUIRES_VALIDATION (modelo não confirmado)

**Estimativa com referência provisória** (verificar preços reais em sa-east-1 após confirmar modelo):

```
Mix de intenções POC (hipótese):
  ~30% RAG_ONLY (INT-010, INT-013, INT-019, INT-020)
  ~40% API_ONLY (sem LLM)
  ~30% CLIENT_POLICY / REDIRECT (sem LLM)

3.000 req/mês × 30% RAG = 900 requests com LLM

Estimativa (modelo a confirmar):
  Input médio RAG: ~800 tokens (contexto + query)
  Output médio RAG: ~300 tokens
  Custo por request: PRICE_REQUIRES_VALIDATION

Impacto da remoção do LLM de API_ONLY:
  Versão anterior: 3.000 × 70% × $0.001 = $2.10/mês
  Versão corrigida: 900 × PRICE_REQUIRES_VALIDATION
  Redução estimada: ~70% menos chamadas ao LLM
```

### 3.3 Bedrock — Embedding (RAG_ONLY)

```
Embedding gerado uma vez por query RAG:
  900 queries/mês × ~50 tokens/query = 45.000 tokens/mês
  Custo: PRICE_REQUIRES_VALIDATION

Indexação (rara — só ao atualizar marh_feature_knowledge.md):
  < 50 chunks × ~300 tokens = ~15.000 tokens
  Custo: PRICE_REQUIRES_VALIDATION (desprezível)
```

### 3.4 S3 Vectors

```
Storage: < 50 vetores
Queries: ~900/mês (apenas RAG_ONLY)
Custo: PRICE_REQUIRES_VALIDATION (provavelmente < $1/mês para esse volume)
```

---

## 4. Cenário POC Pequeno — 100 req/dia (3.000 req/mês)

| Componente | Fórmula | Custo Mensal | Status |
|---|---|---|---|
| Lambda | free tier | $0 | |
| S3 (docs) | < 200 KB storage | < $0.01 | |
| S3 Vectors | < 50 vetores + 900 queries | PRICE_REQUIRES_VALIDATION | |
| Bedrock (LLM RAG) | 900 × custo/req | PRICE_REQUIRES_VALIDATION | |
| Bedrock (embedding) | 900 × 50 tokens | PRICE_REQUIRES_VALIDATION | |
| Secrets Manager | 2 secrets | ~$0.80 | |
| KMS | 2 CMKs | ~$2.00 | |
| CloudWatch | ~1 GB logs/mês | ~$1.00 | |
| X-Ray | ~3.000 traces | $0 (free tier) | |
| **TOTAL ESTIMADO** | | **< $5 fixo + PRICE_REQUIRES_VALIDATION** | |

**Redução vs. versão anterior:** Remoção do LLM de API_ONLY reduz em ~70% as chamadas ao modelo.

---

## 5. Registros de Preço

| Item | Preço | Unidade | Região | Fonte | Data | Status |
|---|---|---|---|---|---|---|
| Lambda invocações | $0.20 | por 1M requests | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| Lambda duração | $0.0000166667 | por GB-s | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| S3 storage | $0.023 | por GB/mês | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| KMS CMK | $1.00 | por chave/mês | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| Secrets Manager | $0.40 | por secret/mês | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| CloudWatch Logs ingest | $0.50 | por GB | sa-east-1 | AWS oficial | 2026-07-23 | CONFIRMED |
| Bedrock (modelo LLM) | TBD | por token | sa-east-1 | PRICE_REQUIRES_VALIDATION | — | PENDING |
| Bedrock (embedding) | TBD | por token | sa-east-1 | PRICE_REQUIRES_VALIDATION | — | PENDING |
| S3 Vectors storage | TBD | — | sa-east-1 | PRICE_REQUIRES_VALIDATION | — | PENDING |
| S3 Vectors queries | TBD | — | sa-east-1 | PRICE_REQUIRES_VALIDATION | — | PENDING |

---

## 6. Cost Drivers

| # | Driver | % estimado (após correção) | Otimização |
|---|---|---|---|
| 1 | Bedrock (tokens LLM — RAG_ONLY) | ~60–70% | Reduzido vs. versão anterior (LLM removido de API_ONLY) |
| 2 | KMS + Secrets | ~20% | Custo fixo baixo |
| 3 | CloudWatch | ~10% | Retenção curta |
| 4 | Lambda | ~5% | Free tier para POC |
| 5 | S3 Vectors | < 5% | Volume mínimo |

---

## 7. Estratégias de Redução

| Estratégia | Economia estimada | Status |
|---|---|---|
| LLM somente em RAG_ONLY (já implementado) | ~70% menos chamadas ao modelo | ✅ POC |
| Respostas estáticas para CLIENT_POLICY (já implementado) | Sem custo de tokens | ✅ POC |
| Corpus mínimo real (não 20 GB) | Storage desprezível | ✅ POC |
| Log level INFO (sem DEBUG) | ~50% volume de logs | ✅ POC |
| Retenção de logs 30 dias | Reduz custo de storage | ✅ POC |
| Prompts curtos e objetivos | ~15% dos tokens RAG | ✅ POC |

---

## 8. Free Tier — Nota

Não declarar free tier como garantia de custo zero. Free tier:
- É limitado a 12 meses em alguns serviços
- Tem limites de uso
- Pode não se aplicar à conta alvo

O free tier de Lambda (1M requests + 400K GB-s) cobre a POC, mas não é garantia para produção.
