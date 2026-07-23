# 09 — Resiliência e Tratamento de Erros

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Princípios de Resiliência

1. **Fail gracefully** — Sempre retornar uma resposta ao usuário, mesmo em falha
2. **Retry only transient** — Apenas erros transitórios merecem retry (429, 500, 502, 503, 504)
3. **Never retry client errors** — 400, 401, 403, 404, 422 não recebem retry
4. **Timeout everything** — Nenhuma chamada externa sem timeout explícito
5. **Circuit breaker** — Proteger contra cascata de falhas
6. **Fallback chain** — Degradação graciosa com respostas padronizadas

---

## 2. Integração ma-hr-orch

### 2.1 Configuração de Timeout

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Connect timeout | 3s | Tempo máximo para estabelecer conexão TCP |
| Read timeout | 10s | P99 do ma-hr-orch é ~4.5s; margem de 2x |
| Total timeout | 12s | Connect + Read + overhead |
| Pool connections | 10 | Reuso de conexões HTTP |
| Pool maxsize | 10 | Máximo de conexões simultâneas |

### 2.2 Política de Retry

```python
RETRY_CONFIG = {
    "max_retries": 2,           # Máximo de tentativas adicionais
    "retry_on": [429, 500, 502, 503, 504],  # Apenas transitórios
    "no_retry_on": [400, 401, 403, 404, 422],  # Client errors = não retry
    "backoff_base": 0.5,        # Base do backoff exponencial (segundos)
    "backoff_max": 4.0,         # Máximo de espera entre retries
    "jitter": True,             # Adicionar randomização para evitar thundering herd
}
```

### 2.3 Backoff com Jitter

```python
import random
import time

def calculate_backoff(attempt: int, base: float = 0.5, max_wait: float = 4.0) -> float:
    """Exponential backoff with full jitter."""
    exponential = min(base * (2 ** attempt), max_wait)
    jitter = random.uniform(0, exponential)
    return jitter

# Exemplo:
# Attempt 0: wait 0-0.5s
# Attempt 1: wait 0-1.0s
# Attempt 2: wait 0-2.0s (não excede max_wait)
```

### 2.4 Circuit Breaker

```python
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,     # Falhas consecutivas para abrir
    "success_threshold": 2,     # Sucessos para fechar (half-open → closed)
    "timeout": 30,              # Segundos em estado OPEN antes de tentar half-open
    "monitored_errors": [500, 502, 503, 504, "timeout"],
}
```

**Estados:**

```
CLOSED ──(5 falhas)──▶ OPEN ──(30s)──▶ HALF-OPEN
   ▲                                        │
   └────────(2 sucessos)────────────────────┘
                                            │
                         (1 falha)──▶ OPEN ──┘
```

**Comportamento por estado:**

| Estado | Ação | Resposta ao Usuário |
|---|---|---|
| CLOSED | Permite todas as chamadas | Normal |
| OPEN | Bloqueia chamadas ao ma-hr-orch | Mensagem padronizada: "Sistema temporariamente indisponível" |
| HALF-OPEN | Permite 1 chamada de teste | Normal se sucesso; volta a OPEN se falha |

---

## 3. Mapeamento de Erros HTTP

### 3.1 Erros do ma-hr-orch

| HTTP Status | Categoria | Retry? | Mensagem ao Usuário (ID) | Ação Interna |
|---|---|---|---|---|
| 400 Bad Request | Client Error | ❌ NÃO | ERR-001: "Não entendi sua solicitação" | Log warn, verificar request |
| 401 Unauthorized | Auth Error | ❌ NÃO | ERR-002: "Sessão expirada, faça login novamente" | Log error, alerta |
| 403 Forbidden | Auth Error | ❌ NÃO | ERR-003: "Você não tem permissão para esta consulta" | Log warn |
| 404 Not Found | Client Error | ❌ NÃO | ERR-004: "Não encontrei o recurso solicitado" | Log info |
| 422 Unprocessable | Client Error | ❌ NÃO | ERR-005: "Dados insuficientes para completar a consulta" | Log warn |
| 429 Too Many Requests | Throttle | ✅ SIM (com backoff) | ERR-006: "Sistema ocupado, aguarde um momento" | Retry 2x, log warn |
| 500 Internal Server Error | Server Error | ✅ SIM (1x) | ERR-007: "Erro temporário, tente novamente" | Retry 1x, log error |
| 502 Bad Gateway | Server Error | ✅ SIM (2x) | ERR-007: "Erro temporário, tente novamente" | Retry 2x, log error |
| 503 Service Unavailable | Server Error | ✅ SIM (2x) | ERR-008: "Serviço em manutenção" | Retry 2x, circuit breaker |
| 504 Gateway Timeout | Timeout | ✅ SIM (1x) | ERR-009: "Consulta demorou demais, tente novamente" | Retry 1x, log warn |
| Timeout (connect/read) | Timeout | ✅ SIM (1x) | ERR-009: "Consulta demorou demais" | Retry 1x, circuit breaker |
| Connection Error | Network | ✅ SIM (2x) | ERR-010: "Não foi possível conectar ao serviço" | Retry 2x, circuit breaker |

### 3.2 As 10 Mensagens Padronizadas de Erro

| ID | Mensagem | Quando |
|---|---|---|
| ERR-001 | "Desculpe, não entendi sua solicitação. Pode reformular?" | 400, parsing error |
| ERR-002 | "Sua sessão expirou. Por favor, faça login novamente no app." | 401 |
| ERR-003 | "Você não tem permissão para acessar essa informação." | 403 |
| ERR-004 | "Não encontrei o que você está procurando. Verifique os dados informados." | 404 |
| ERR-005 | "Preciso de mais informações para completar sua consulta." | 422, parâmetros faltantes |
| ERR-006 | "O sistema está muito ocupado agora. Tente novamente em alguns segundos." | 429, rate limit |
| ERR-007 | "Ocorreu um erro temporário. Tente novamente em instantes." | 500, 502 |
| ERR-008 | "O serviço está em manutenção. Tente novamente em alguns minutos." | 503 |
| ERR-009 | "A consulta está demorando mais que o esperado. Tente novamente." | 504, timeout |
| ERR-010 | "Não foi possível conectar ao serviço no momento. Tente mais tarde." | Connection error, circuit open |

---

## 4. Falhas do Bedrock

### 4.1 Cenários de Falha

| Erro Bedrock | Retry? | Fallback |
|---|---|---|
| ThrottlingException | ✅ SIM (3x, backoff) | Resposta genérica sem LLM |
| ModelTimeoutException | ✅ SIM (1x) | Resposta genérica sem LLM |
| ModelNotReadyException | ✅ SIM (2x, 5s wait) | Resposta genérica sem LLM |
| ValidationException | ❌ NÃO | Log error, resposta genérica |
| AccessDeniedException | ❌ NÃO | Log critical, alerta, resposta de erro |
| ServiceUnavailableException | ✅ SIM (2x) | Resposta genérica sem LLM |
| InternalServerException | ✅ SIM (2x) | Resposta genérica sem LLM |

### 4.2 Fallback sem LLM

Quando o Bedrock está indisponível e o fluxo é:
- **RAG_ONLY** → Retorna: "Não consegui processar sua pergunta no momento. Tente novamente."
- **API_ONLY** → Se dados da API já foram obtidos, retorna dados brutos formatados (sem LLM)
- **HYBRID** → Retorna parcial (apenas a parte que funcionou) + disclaimer

---

## 5. Falhas do RAG (Knowledge Bases)

### 5.1 Cenários

| Falha | Retry? | Fallback |
|---|---|---|
| KB Retrieve timeout | ✅ SIM (1x) | Resposta genérica |
| Nenhum chunk relevante (score < 0.7) | ❌ NÃO | "Não encontrei informação sobre isso nos nossos documentos." |
| KB indisponível | ✅ SIM (1x) | Resposta genérica |
| Erro de indexação | ❌ NÃO | Log error, resposta genérica |

### 5.2 Qualidade dos Chunks

```python
def evaluate_retrieval(chunks: list, threshold: float = 0.7) -> tuple:
    relevant = [c for c in chunks if c.score >= threshold]
    if not relevant:
        return None, "NO_RELEVANT_CHUNKS"
    return relevant[:5], "OK"
```

---

## 6. Cadeia de Fallback

### 6.1 Fluxo de Degradação

```
Fluxo Normal
    │
    ▼ Falha?
Retry (se transitório)
    │
    ▼ Falha novamente?
Fallback específico do fluxo
    │
    ▼ Fallback também falha?
Mensagem padronizada de erro (ERR-001 a ERR-010)
    │
    ▼ Sempre retorna algo
Resposta ao usuário (NUNCA deixa sem resposta)
```

### 6.2 Fallback por Fluxo

| Fluxo | Fallback Nível 1 | Fallback Nível 2 | Fallback Nível 3 |
|---|---|---|---|
| STATIC_RESPONSE | — (nunca falha) | — | — |
| RAG_ONLY | Retry KB | "Não encontrei informação" | ERR-007 |
| API_ONLY | Retry ma-hr-orch | Dados brutos sem LLM | ERR-009 |
| HYBRID | Parcial (só parte que funcionou) | Retry individual | ERR-007 |
| CLARIFICATION | Pergunta genérica determinística | ERR-001 | — |

---

## 7. Implementação de Referência

### 7.1 HTTP Client Resiliente

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception

TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}

class MaHrOrchClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(connect=3.0, read=10.0, pool=5.0),
            headers={"Authorization": f"Bearer {api_key}"},
        )
        self._circuit_state = "CLOSED"
        self._failure_count = 0
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=0.5, max=4.0),
        retry=retry_if_exception(lambda e: _is_transient(e)),
    )
    def get(self, endpoint: str, params: dict = None) -> dict:
        if self._circuit_state == "OPEN":
            raise CircuitOpenError("Circuit breaker is OPEN")
        
        response = self.client.get(endpoint, params=params)
        
        if response.status_code in TRANSIENT_STATUS_CODES:
            self._record_failure()
            raise TransientError(f"HTTP {response.status_code}")
        
        if response.status_code >= 400:
            raise ClientError(response.status_code, response.json())
        
        self._record_success()
        return response.json()
```

### 7.2 Timeout Global

```python
import asyncio

async def handle_request_with_timeout(request, timeout=15.0):
    """Garante que NENHUMA requisição exceda o timeout global."""
    try:
        result = await asyncio.wait_for(
            process_request(request),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return error_response("ERR-009")
```

---

## 8. Monitoramento de Resiliência

### 8.1 Métricas de Resiliência

| Métrica | Alerta se | Ação |
|---|---|---|
| Circuit breaker state | OPEN > 2min | Investigar ma-hr-orch |
| Retry rate | > 10% das requests | Verificar saúde dos serviços |
| Fallback rate | > 5% das requests | Verificar Bedrock/KB |
| Error rate (4xx) | > 5% | Verificar classificação/validação |
| Error rate (5xx) | > 1% | Alerta imediato |
| Timeout rate | > 3% | Verificar ma-hr-orch latência |

### 8.2 Logs de Resiliência

```json
{
  "event": "retry_attempted",
  "attempt": 2,
  "reason": "HTTP 503",
  "target": "ma-hr-orch",
  "endpoint": "/orders",
  "wait_time_ms": 1200,
  "correlation_id": "uuid",
  "timestamp": "2026-07-23T10:30:00Z"
}
```
