# 08 — Performance e Escalabilidade

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1

---

## 1. Budget de Latência por Fluxo

### 1.1 Definições

- Valores de P50/P95 marcados como **ASSUMPTION_REQUIRES_LOAD_TEST** onde não há medição real
- `single_observed_sample_ms`: valor observado em uma única chamada — não representa percentil
- Apenas a amostra de `GET /v1/beneficiaries` (3275ms) em 2026-07-22 é dado real

### 1.2 Budget por Etapa

| Etapa | Estimativa | Tipo | Timeout |
|---|---|---|---|
| Recepção + parse | ~10ms | Estimativa | — |
| Classificação determinística | ~10ms | Estimativa | — |
| ma-hr-orch GET | single_observed_sample: 3275ms (beneficiaries), 782ms (orders) | Amostra real | 10s |
| Embedding + S3 Vectors (RAG) | ASSUMPTION_REQUIRES_LOAD_TEST | — | 5s |
| Modelo de geração (RAG_ONLY) | ASSUMPTION_REQUIRES_LOAD_TEST | — | 8s |
| Schema + allowlist + sanitização | ~20ms | Estimativa | — |
| Template determinístico | ~10ms | Estimativa | — |
| Validação de output | ~5ms | Estimativa | — |

### 1.3 Latência Total por Fluxo

| Fluxo | Componentes | P95 estimado | Timeout Global | Marcação |
|---|---|---|---|---|
| STATIC_RESPONSE | Classificação + template | < 100ms | 1s | |
| REDIRECT | Classificação + template | < 100ms | 1s | |
| API_ONLY (sem LLM) | Classificação + ma-hr-orch + schema + allowlist + template | < 11s | 15s | ASSUMPTION_REQUIRES_LOAD_TEST |
| RAG_ONLY | Classificação + embedding + S3 Vectors + geração | — | 12s | ASSUMPTION_REQUIRES_LOAD_TEST |
| REQUIRES_CLARIFICATION | Template determinístico | < 100ms | 1s | |

**Nota sobre 3275ms:** É uma `single_observed_sample_ms` de uma chamada a `GET /v1/beneficiaries`
em 2026-07-22. Não representa P50, P75, P95 ou P99. Não usar para derivar estatísticas.

**Budget API_ONLY coerente (sem LLM):**

| Etapa | Orçamento |
|---|---|
| Parse + classificação | ≤ 20ms |
| ma-hr-orch GET | ≤ 10s (timeout) |
| Schema + allowlist + template | ≤ 30ms |
| Timeout global | 15s |

A combinação `connect_timeout=3s + read_timeout=10s` já soma 13s, mais overhead, dentro do global de 15s.
Não adicionar retry dentro desse orçamento sem calcular se cabe.

---

## 2. Cenários de Carga (Premissas Explícitas)

### Fórmula de Concorrência

```
concorrência ≈ RPS × duração_média_em_segundos
```

### 2.1 Cenário POC — Demonstração

| Premissa | Valor |
|---|---|
| Usuários ativos | 5–10 simultâneos |
| RPS pico | ~1–2 req/s |
| Mix de rotas | 40% STATIC, 30% API_ONLY, 30% RAG_ONLY |
| Duração média estimada | ~3s (API_ONLY sem LLM) |
| Concorrência necessária | ~3–6 instâncias |

| Métrica | Valor | Status |
|---|---|---|
| Lambda concurrency necessário | ~5–10 | ✅ Dentro do default (1.000) |
| Bedrock TPM necessário | ASSUMPTION_REQUIRES_LOAD_TEST | REQUIRES_VALIDATION |
| ma-hr-orch chamadas/min | ~10–20 | Validar capacidade |

### 2.2 Cenário Piloto

| Premissa | Valor |
|---|---|
| Usuários ativos | ~50 simultâneos |
| RPS pico | ~20 req/s |
| Duração média estimada | ~3s |
| Concorrência necessária | ~60 instâncias |

| Métrica | Valor | Status |
|---|---|---|
| Lambda concurrency | ~60 | ✅ Dentro do default |
| Bedrock TPM | ASSUMPTION_REQUIRES_LOAD_TEST | REQUIRES_VALIDATION |

**Nota:** Valores de TPM disponíveis em sa-east-1 devem ser verificados no console antes de dimensionar.

---

## 3. Gargalos Identificados

| # | Gargalo | Impacto | Probabilidade | Mitigação |
|---|---|---|---|---|
| 1 | ma-hr-orch latência (3275ms observado — amostra) | Alto | Alta | Timeout máximo 10s; fallback ERR-007 |
| 2 | Bedrock quotas sa-east-1 (desconhecidas) | Alto | Média | Verificar no console; solicitar aumento antes do POC |
| 3 | Lambda concurrency (default=1.000) | Médio | Baixa (POC) | Reserved concurrency |
| 4 | Cold start (~300ms Python) | Baixo | Alta | Warm-up via CloudWatch Events |
| 5 | S3 Vectors retrieval (ASSUMPTION) | Desconhecido | Desconhecido | ASSUMPTION_REQUIRES_LOAD_TEST |

---

## 4. Autoscaling

### 4.1 Lambda

| Configuração | Valor POC | Valor Produção |
|---|---|---|
| Reserved concurrency | 50 | A definir pós-load test |
| Provisioned concurrency | 0 (POC) | Avaliar pós-POC |
| Memory | 512MB | 512MB (ajustar pós-teste) |
| Timeout | 30s | 30s |

---

## 5. Rate Limiting na POC

Rate limiting por usuário e empresa é responsabilidade da **API MARH**.

Na Lambda:
- Reserved concurrency protege contra sobrecarga
- Cada request possui timeout global de 30s
- Retries limitados a 1 tentativa por falha transitória

**Sem rate limiting in-memory:** dicionário em memória da Lambda não é compartilhado entre instâncias. Não implementar como controle de segurança.

---

## 6. Plano de Teste de Carga

**Status:** NÃO EXECUTAR AGORA — executar após implementação do POC.

**Premissas a medir:**

| Métrica | Alvo | Notas |
|---|---|---|
| Latência P95 API_ONLY (sem LLM) | < 11s | Validar após integração real |
| Latência P95 RAG_ONLY | < 12s | ASSUMPTION_REQUIRES_LOAD_TEST |
| Latência P95 STATIC | < 100ms | Esperado |
| Error rate | < 1% | Alvo |
| Lambda throttles | 0 | Alerta |
| Bedrock throttles | 0 | Alerta — verificar quota antes |

**Cenários de teste:**

| # | Cenário | Duração | Carga |
|---|---|---|---|
| 1 | Warm-up | 2min | 1 req/s |
| 2 | Carga normal | 5min | 5 req/s |
| 3 | Pico | 2min | 20 req/s |
| 4 | Sustentado | 10min | 10 req/s |

**Dados de teste:** Sintéticos. NUNCA usar dados reais.
