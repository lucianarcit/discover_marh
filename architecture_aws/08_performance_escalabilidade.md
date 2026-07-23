# 08 — Performance e Escalabilidade

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Budget de Latência por Estágio

### 1.1 Tabela Consolidada

| Estágio | P50 | P95 | Timeout | Notas |
|---|---|---|---|---|
| Recepção + Parse | 5ms | 10ms | — | JSON parse + validação |
| Classificação determinística | 5ms | 15ms | — | Regex + keyword match |
| Bedrock KB Retrieve | 400ms | 1.5s | 5s | top-k=5, score threshold |
| Bedrock LLM Generate (Haiku) | 600ms | 2s | 8s | ~500 tokens output |
| ma-hr-orch GET | 1.5s | 3.3s | 10s | Latência medida: P95=3275ms |
| Sanitização PII | 3ms | 10ms | — | Regex sobre payload |
| Validação de output | 2ms | 5ms | — | Re-scan + URL check |
| Serialização + Response | 3ms | 8ms | — | JSON serialize |

### 1.2 Latência Total por Fluxo

| Fluxo | P50 | P95 | Timeout Total |
|---|---|---|---|
| STATIC_RESPONSE | 15ms | 40ms | 1s |
| REDIRECT | 15ms | 40ms | 1s |
| RAG_ONLY | 1.1s | 3.5s | 10s |
| API_ONLY | 2.1s | 5.3s | 15s |
| HYBRID_RAG_API (paralelo) | 2.1s | 5.3s | 15s |
| REQUIRES_CLARIFICATION | 50ms | 1.5s | 8s |

---

## 2. Cenários de Carga

### 2.1 Cenário POC: 100 Usuários Simultâneos

| Métrica | Valor | Status |
|---|---|---|
| Requisições/segundo (pico) | ~10 req/s | ✅ Confortável |
| Lambda concurrency necessário | 10-15 | ✅ Dentro do default (1000) |
| Bedrock tokens/minuto | ~50K | ✅ Dentro da quota |
| ma-hr-orch chamadas/min | ~70 | ⚠️ Verificar capacidade |
| Custo estimado/hora | ~$0.50 | ✅ Aceitável |

### 2.2 Cenário Piloto: 1.000 Usuários Simultâneos

| Métrica | Valor | Status |
|---|---|---|
| Requisições/segundo (pico) | ~100 req/s | ✅ Viável |
| Lambda concurrency necessário | 100-150 | ✅ Dentro do default (1000) |
| Bedrock tokens/minuto | ~500K | ⚠️ Verificar quota sa-east-1 |
| ma-hr-orch chamadas/min | ~700 | ⚠️ Rate limit do serviço |
| Custo estimado/hora | ~$5 | ✅ Aceitável |

### 2.3 Cenário Produção: 10.000 Usuários Simultâneos

| Métrica | Valor | Status |
|---|---|---|
| Requisições/segundo (pico) | ~1000 req/s | ⚠️ Requer planejamento |
| Lambda concurrency necessário | 1000-1500 | ⚠️ Requer aumento de quota |
| Bedrock tokens/minuto | ~5M | ❌ Provavelmente excede quota regional |
| ma-hr-orch chamadas/min | ~7000 | ❌ Requer validação |
| Custo estimado/hora | ~$50 | ⚠️ Monitorar |

**Ações para 10K usuários:**
- Solicitar aumento de quota Bedrock
- Implementar cache (ElastiCache)
- Validar capacidade do ma-hr-orch
- Considerar provisioned concurrency

---

## 3. Gargalos Identificados

### 3.1 Ranking de Gargalos

| # | Gargalo | Impacto | Probabilidade | Mitigação |
|---|---|---|---|---|
| 1 | ma-hr-orch latência (P95=3275ms) | Alto | Alta | Timeout agressivo, fallback |
| 2 | Bedrock quotas sa-east-1 | Alto | Média | Monitorar, solicitar aumento |
| 3 | Lambda concurrency (default=1000) | Médio | Baixa (POC) | Reserved concurrency |
| 4 | Cold start (~300ms) | Baixo | Alta | Provisioned concurrency |
| 5 | S3 Vectors retrieval | Baixo | Baixa | Otimizar chunks |

### 3.2 ma-hr-orch — Principal Gargalo

**Dados observados:**
- P50: 1500ms
- P75: 2200ms  
- P95: 3275ms
- P99: 4500ms
- Timeout recomendado: 10s

**Estratégia:**
```
┌─────────────────────────────────────┐
│ 1. Timeout: 10s                     │
│ 2. Se timeout → mensagem padrão    │
│ 3. Não fazer retry de timeout       │
│ 4. Circuit breaker: 5 falhas → open│
│ 5. Fallback: "tente novamente"      │
└─────────────────────────────────────┘
```

### 3.3 Bedrock Quotas (sa-east-1)

| Quota | Valor Esperado | Nota |
|---|---|---|
| InvokeModel RPM | ~100 RPM (Haiku) | Verificar quota real |
| InvokeModel TPM | ~100K TPM | Pode ser menor em sa-east-1 |
| KB Retrieve RPM | ~100 RPM | Verificar quota real |
| On-demand throughput | Variável | Sujeito a disponibilidade |

⚠️ **RISCO:** Quotas em sa-east-1 podem ser menores que us-east-1. Verificar antes do POC.

---

## 4. Autoscaling

### 4.1 Lambda Autoscaling (Nativo)

| Configuração | Valor POC | Valor Produção |
|---|---|---|
| Reserved concurrency | 100 | 500 |
| Provisioned concurrency | 0 (POC) | 10-50 |
| Burst limit | 500 (padrão sa-east-1) | 500 |
| Scale rate | 500/min | 500/min |
| Memory | 512MB | 1024MB |
| Timeout | 30s | 30s |

### 4.2 Nenhum Outro Autoscaling Necessário

- Bedrock: gerenciado (on-demand)
- S3: sem limite prático
- S3 Vectors: gerenciado
- Knowledge Bases: gerenciado
- Secrets Manager: gerenciado
- CloudWatch: gerenciado

---

## 5. Mitigação de Cold Start

### 5.1 Estratégias

| Estratégia | Implementação POC | Impacto |
|---|---|---|
| Provisioned concurrency | Não (custo) | Elimina cold start |
| Manter Lambda warm (ping) | Sim (CloudWatch Events 5min) | Reduz frequência |
| Minimizar pacote | Sim (apenas deps necessárias) | Reduz init time |
| Lazy loading de SDK clients | Sim (inicializar fora do handler) | Reduz cold start |
| Python 3.12 (mais rápido que 3.9) | Sim | ~10% redução |
| SnapStart | Não disponível para Python | — |

### 5.2 Inicialização Otimizada

```python
# FORA do handler (executado no cold start, reutilizado em warm)
import boto3

bedrock_client = boto3.client('bedrock-runtime', region_name='sa-east-1')
secrets_client = boto3.client('secretsmanager', region_name='sa-east-1')
kb_client = boto3.client('bedrock-agent-runtime', region_name='sa-east-1')

# Pré-carregar secrets (cache em memória durante lifecycle da instância)
_secrets_cache = {}

def get_secret(name: str) -> str:
    if name not in _secrets_cache:
        response = secrets_client.get_secret_value(SecretId=name)
        _secrets_cache[name] = response['SecretString']
    return _secrets_cache[name]

# Handler
def lambda_handler(event, context):
    # clients já inicializados, secrets em cache
    ...
```

---

## 6. Rate Limiting por Usuário/Empresa

### 6.1 Limites Propostos (POC)

| Escopo | Limite | Janela | Ação |
|---|---|---|---|
| Por usuário | 10 requisições | 1 minuto | HTTP 429 + mensagem amigável |
| Por usuário | 100 requisições | 1 hora | HTTP 429 + cooldown |
| Por empresa | 100 requisições | 1 minuto | HTTP 429 |
| Por empresa | 5000 requisições | 1 hora | HTTP 429 + alerta |
| Global | 1000 concorrentes | — | Lambda throttling |

### 6.2 Implementação (POC — In-Memory)

```python
# POC: rate limiting simples em memória (reseta a cada cold start)
# PRODUÇÃO: migrar para DynamoDB ou ElastiCache
from collections import defaultdict
from time import time

_rate_limits = defaultdict(list)

def check_rate_limit(user_id: str, limit: int = 10, window: int = 60) -> bool:
    now = time()
    _rate_limits[user_id] = [t for t in _rate_limits[user_id] if now - t < window]
    if len(_rate_limits[user_id]) >= limit:
        return False  # Rate limited
    _rate_limits[user_id].append(now)
    return True
```

**Limitação POC:** Rate limiting em memória não é distribuído. Cada instância Lambda tem seu próprio contador. Aceitável para POC com baixo volume.

---

## 7. Plano de Teste de Carga

### 7.1 Objetivo

Validar que a arquitetura suporta o cenário POC (100 req/day a 1000 req/day) com latências dentro do budget.

### 7.2 Ferramenta

- **Locust** (Python) ou **Artillery** (Node.js)
- Executar a partir de máquina local ou EC2 em sa-east-1

### 7.3 Cenários de Teste

| # | Cenário | Duração | Carga | Métrica Alvo |
|---|---|---|---|---|
| 1 | Warm-up | 2min | 1 req/s | Baseline de latência |
| 2 | Carga normal | 5min | 5 req/s | P95 < 6s |
| 3 | Pico | 2min | 20 req/s | P95 < 8s, 0 erros |
| 4 | Sustentado | 10min | 10 req/s | Sem degradação |
| 5 | Recovery | 2min | 1 req/s | Volta ao baseline |

### 7.4 Dados de Teste

- **Dados sintéticos** — NUNCA usar dados reais de clientes
- Mix de intents: 30% static, 40% RAG, 25% API, 5% hybrid
- Payloads variados (curtos e longos)
- Incluir cenários de erro (timeout do ma-hr-orch simulado)

### 7.5 Métricas a Coletar

| Métrica | Fonte | Alerta se |
|---|---|---|
| Latência P50/P95/P99 | X-Ray + Locust | P95 > 6s |
| Error rate | CloudWatch | > 1% |
| Lambda duration | CloudWatch | P95 > 15s |
| Lambda throttles | CloudWatch | > 0 |
| Bedrock throttles | CloudWatch | > 0 |
| Cold starts | CloudWatch | > 10% das invocações |

### 7.6 Status

⏳ **NÃO EXECUTAR AGORA** — Plano definido para execução após implementação do POC.
