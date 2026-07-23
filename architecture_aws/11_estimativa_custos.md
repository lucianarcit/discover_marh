# 11 — Estimativa de Custos

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Fonte de Preços:** AWS Official Pricing (2026-07-23)  
**Status:** DRAFT

---

## 1. Custos Fixos (Near-Zero para POC)

| Serviço | Custo Fixo Mensal | Notas |
|---|---|---|
| Lambda | $0 (free tier: 1M requests + 400K GB-s) | POC dentro do free tier |
| S3 (documentos KB) | ~$0.50 | ~20GB storage com KMS |
| S3 Vectors | ~$5.00 | Armazenamento de embeddings |
| Secrets Manager | ~$1.20 | 3 secrets × $0.40 |
| KMS | ~$3.00 | 3 CMKs × $1.00 |
| CloudWatch Logs | ~$2.00 | ~2GB/mês de logs |
| X-Ray | ~$0.50 | Free tier 100K traces |
| Knowledge Bases | $0 | Sem custo fixo (pay per query) |
| **TOTAL FIXO** | **~$12.20/mês** | — |

---

## 2. Custos Variáveis — Fórmulas

### 2.1 Lambda

```
Custo Lambda = (invocações × $0.20/1M) + (duração_GB_s × $0.0000166667)

Onde:
- duração_GB_s = (memory_MB / 1024) × duração_s × invocações
- Memory POC: 512MB = 0.5GB
- Duração média: 3s (mix de fluxos)
```

### 2.2 Bedrock — Claude 3.5 Haiku

```
Custo Bedrock = (input_tokens × $0.00025/1K) + (output_tokens × $0.00125/1K)

Preços Claude 3.5 Haiku (sa-east-1):
- Input:  $0.25 / 1M tokens  = $0.00000025/token
- Output: $1.25 / 1M tokens  = $0.00000125/token

Estimativa por request:
- Input médio: ~1500 tokens (system + context + user)
- Output médio: ~500 tokens
- Custo por request: (1500 × 0.00025) + (500 × 0.00125) = $0.000375 + $0.000625 = $0.001
```

### 2.3 Bedrock — Claude Sonnet 4 (Alternativo)

```
Preços Claude Sonnet 4 (sa-east-1):
- Input:  $3.00 / 1M tokens  = $0.000003/token
- Output: $15.00 / 1M tokens = $0.000015/token

Custo por request: (1500 × 0.003) + (500 × 0.015) = $0.0045 + $0.0075 = $0.012
(~12x mais caro que Haiku)
```

### 2.4 Bedrock Knowledge Bases — Retrieve

```
Custo KB Retrieve = queries × $0.00 (incluso no modelo)
Nota: Custo de retrieval é cobrado via embedding model + S3 Vectors storage
```

### 2.5 S3 Vectors

```
Custo S3 Vectors = storage_GB × $0.25/GB/mês + queries × preço_por_query
Estimativa: ~20GB de vetores = ~$5/mês
```

### 2.6 CloudWatch

```
Custo CloudWatch = (logs_GB × $0.50/GB) + (métricas_custom × $0.30/métrica/mês) + (queries × $0.005/GB scanned)

Estimativa:
- Logs: ~2GB/mês = $1.00
- Métricas: 10 custom = $3.00
- Queries: ~1GB scanned = $0.005
```

---

## 3. Cenários de Custo

### 3.1 Cenário POC Pequeno — 100 req/dia (3.000 req/mês)

| Componente | Cálculo | Custo Mensal |
|---|---|---|
| Lambda | 3000 × 0.5GB × 3s = 4500 GB-s | ~$0.08 (free tier) |
| Bedrock Haiku | 3000 × $0.001 | $3.00 |
| KB Retrieve | 1200 queries (40% RAG) | incluso |
| S3 Vectors | storage | $5.00 |
| S3 (docs) | storage | $0.50 |
| Secrets Manager | 3 secrets | $1.20 |
| KMS | 3 keys + decrypt | $3.50 |
| CloudWatch | logs + metrics | $3.00 |
| X-Ray | traces | $0.50 |
| **TOTAL** | — | **~$16.78/mês** |

### 3.2 Cenário Piloto — 1.000 req/dia (30.000 req/mês)

| Componente | Cálculo | Custo Mensal |
|---|---|---|
| Lambda | 30000 × 0.5GB × 3s = 45000 GB-s | ~$0.75 |
| Bedrock Haiku | 30000 × $0.001 × 0.7 (70% usa LLM) | $21.00 |
| KB Retrieve | 12000 queries | incluso |
| S3 Vectors | storage | $5.00 |
| S3 (docs) | storage | $0.50 |
| Secrets Manager | 3 secrets | $1.20 |
| KMS | 3 keys + decrypt | $4.00 |
| CloudWatch | logs + metrics | $8.00 |
| X-Ray | traces | $2.00 |
| **TOTAL** | — | **~$42.45/mês** |

### 3.3 Cenário Produção — 10.000 req/dia (300.000 req/mês)

| Componente | Cálculo | Custo Mensal |
|---|---|---|
| Lambda | 300000 × 0.5GB × 3s = 450000 GB-s | ~$7.50 |
| Bedrock Haiku | 300000 × $0.001 × 0.7 | $210.00 |
| KB Retrieve | 120000 queries | incluso |
| S3 Vectors | storage | $5.00 |
| S3 (docs) | storage | $0.50 |
| Secrets Manager | 3 secrets | $1.20 |
| KMS | 3 keys + decrypt | $8.00 |
| CloudWatch | logs + metrics | $25.00 |
| X-Ray | traces (sampling 10%) | $5.00 |
| **TOTAL** | — | **~$262.20/mês** |

### 3.4 Cenário Alto Volume — 50.000 req/dia (1.500.000 req/mês)

| Componente | Cálculo | Custo Mensal |
|---|---|---|
| Lambda | 1.5M × 0.5GB × 3s = 2.25M GB-s | ~$37.50 |
| Bedrock Haiku | 1.5M × $0.001 × 0.7 | $1,050.00 |
| KB Retrieve | 600000 queries | incluso |
| S3 Vectors | storage (pode crescer) | $10.00 |
| S3 (docs) | storage | $0.50 |
| Secrets Manager | 3 secrets | $1.20 |
| KMS | 3 keys + decrypt | $15.00 |
| CloudWatch | logs + metrics | $60.00 |
| X-Ray | traces (sampling 5%) | $10.00 |
| Provisioned Concurrency | 20 instâncias | $50.00 |
| **TOTAL** | — | **~$1,234.20/mês** |

---

## 4. Resumo Comparativo

| Cenário | Req/dia | Custo Mensal | Custo/Request |
|---|---|---|---|
| POC Pequeno | 100 | ~$17 | $0.0056 |
| Piloto | 1.000 | ~$42 | $0.0014 |
| Produção | 10.000 | ~$262 | $0.0009 |
| Alto Volume | 50.000 | ~$1.234 | $0.0008 |

---

## 5. Comparação com Alternativas

### 5.1 Vector Store: S3 Vectors vs. OpenSearch Serverless

| Aspecto | S3 Vectors | OpenSearch Serverless |
|---|---|---|
| Custo fixo mínimo | ~$5/mês | ~$700/mês (2 OCU mínimo) |
| Custo variável | Baixo | Médio |
| Performance (P95) | ~500ms | ~200ms |
| Escalabilidade | Alta | Alta |
| Gerenciamento | Zero (serverless) | Baixo (serverless) |
| **Decisão** | ✅ **POC** | Considerar em produção se latência for crítica |

**Economia:** $700 - $5 = **$695/mês** por usar S3 Vectors

### 5.2 Runtime: Lambda vs. ECS Fargate

| Aspecto | Lambda | ECS Fargate |
|---|---|---|
| Custo (100 req/dia) | ~$0.08 | ~$35/mês (min 1 task) |
| Custo (10000 req/dia) | ~$7.50 | ~$70/mês |
| Cold start | ~300ms | 0 (always running) |
| Escalabilidade | Automática | Requer config |
| Operação | Zero | Médio |
| **Decisão** | ✅ **POC e Produção** | Apenas se cold start for inaceitável |

### 5.3 API Management: Function URL vs. API Gateway

| Aspecto | Function URL | API Gateway |
|---|---|---|
| Custo | $0 | $3.50/M requests + data transfer |
| Rate limiting | Lambda throttling | Built-in |
| Auth | IAM Auth | API Key, JWT, IAM |
| Métricas | CloudWatch | Built-in dashboard |
| WAF | Não | Sim |
| **Decisão** | ✅ **POC** | Produção |

---

## 6. Cost Drivers (Maiores Impulsionadores de Custo)

| # | Driver | % do Custo Total | Otimização |
|---|---|---|---|
| 1 | Bedrock (tokens LLM) | ~70-80% | Reduzir tokens, usar Haiku, prompts curtos |
| 2 | CloudWatch (logs) | ~5-10% | Log level INFO (não DEBUG), sampling |
| 3 | Lambda (execução) | ~3-5% | Otimizar duração, memory right-sizing |
| 4 | S3 Vectors | ~2-3% | Custo fixo baixo |
| 5 | KMS + Secrets | ~2-3% | Custo fixo baixo |

---

## 7. Estratégias de Redução de Custo

| Estratégia | Economia Estimada | Quando Implementar |
|---|---|---|
| Respostas estáticas para OUT-* (sem LLM) | ~20-30% dos tokens | ✅ POC (já planejado) |
| Prompts curtos e objetivos | ~15% dos tokens | ✅ POC |
| Cache de respostas RAG frequentes | ~10-15% das chamadas | Produção |
| Sampling de X-Ray (10% em prod) | ~80% do custo X-Ray | Produção |
| Log level INFO (sem DEBUG) | ~50% do volume de logs | ✅ POC |
| Bedrock batch API (off-peak) | ~50% do custo Bedrock | Produção (se aplicável) |
| Committed throughput (Bedrock) | ~20-30% do custo Bedrock | Alto volume |

---

## 8. Notas sobre Precificação

- Preços referência: AWS sa-east-1, data 2026-07-23
- Preços podem variar; consultar sempre a [página oficial da AWS](https://aws.amazon.com/pricing/)
- Bedrock pricing pode ter variações regionais
- Free tier Lambda: 1M requests/mês + 400K GB-s (12 meses)
- Impostos não incluídos
- Data transfer dentro da mesma região: gratuito
- Data transfer para internet: $0.09/GB (desprezível para texto)
