# 10 — Observabilidade

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Pilares de Observabilidade

| Pilar | Serviço AWS | Escopo POC | Escopo Produção |
|---|---|---|---|
| Logs | CloudWatch Logs | Structured JSON | + Log Insights queries |
| Métricas | CloudWatch Metrics | Custom metrics | + Dashboards + Alarmes |
| Tracing | AWS X-Ray | Distributed tracing | + Service Map + Analytics |
| Alertas | — | Manual | CloudWatch Alarms + SNS |

---

## 2. Logs Estruturados

### 2.1 Formato de Log

Todos os logs são em JSON estruturado para facilitar queries no CloudWatch Insights.

```json
{
  "timestamp": "2026-07-23T14:30:00.123Z",
  "level": "INFO",
  "correlation_id": "uuid-1234",
  "session_id": "uuid-5678",
  "company_id": "uuid-abcd",
  "intent": "INT-003",
  "flow": "API_ONLY",
  "stage": "ma_hr_orch_call",
  "duration_ms": 1523,
  "status": "success",
  "message": "ma-hr-orch call completed",
  "metadata": {
    "endpoint": "/orders",
    "http_status": 200,
    "retry_count": 0
  }
}
```

### 2.2 O Que Logar

| Categoria | Exemplos | Nível |
|---|---|---|
| Request recebido | correlation_id, intent classificado, flow selecionado | INFO |
| Chamada externa iniciada | target (bedrock/ma-hr-orch/kb), endpoint, timestamp | INFO |
| Chamada externa completa | duration_ms, status, retry_count | INFO |
| Classificação | intent detectado, confidence, padrão matched | INFO |
| Token usage | input_tokens, output_tokens, model_id | INFO |
| Rate limit aplicado | user_id (hash), limit_type, remaining | WARN |
| Erro tratado | error_type, error_code, fallback_used | WARN |
| Erro não esperado | stack trace (sem PII), error_type | ERROR |
| Circuit breaker mudança | old_state, new_state, failure_count | WARN |
| Cold start | init_duration_ms, runtime_version | INFO |

### 2.3 O Que NÃO Logar (NUNCA)

| Dado Proibido | Motivo | Alternativa |
|---|---|---|
| CPF, RG, CNH | PII — regulação LGPD | Não logar |
| Nome completo do usuário | PII | Hash ou user_id |
| E-mail, telefone | PII | Não logar |
| Endereço | PII | Não logar |
| Conteúdo completo da mensagem do usuário | Pode conter PII | Logar apenas intent + metadata |
| JWT / tokens de autenticação | Credencial | Não logar |
| Resposta completa do ma-hr-orch | Pode conter PII | Logar apenas status + duração |
| Prompt completo enviado ao modelo | Pode conter dados sanitizados | Logar template_id + params count |
| Resposta completa do modelo | Pode conter informação sensível | Logar tokens + duração |
| Chaves de API / secrets | Credencial | NUNCA |
| Dados financeiros específicos (saldos, valores) | Financeiro | Logar apenas "has_balance: true/false" |

### 2.4 Log Levels

| Nível | Quando Usar |
|---|---|
| DEBUG | Desenvolvimento local apenas (desabilitado em prod) |
| INFO | Operação normal, métricas operacionais |
| WARN | Situação recuperável (retry, rate limit, fallback) |
| ERROR | Falha não esperada, requer investigação |
| CRITICAL | Falha sistêmica (circuit breaker open, todas as retries falharam) |

---

## 3. Métricas Custom

### 3.1 Métricas por Rota/Intent

| Métrica | Dimensões | Unidade | Descrição |
|---|---|---|---|
| `agent/request_count` | intent, flow, status | Count | Total de requisições |
| `agent/latency` | intent, flow, stage | Milliseconds | Latência por estágio |
| `agent/error_count` | intent, error_type, error_code | Count | Erros por tipo |
| `agent/token_usage` | model_id, intent | Count | Tokens consumidos |
| `agent/cost_estimate` | model_id, intent | USD (micro) | Custo estimado por request |
| `agent/fallback_count` | intent, fallback_level | Count | Uso de fallbacks |
| `agent/circuit_breaker` | target, state | Count | Mudanças de estado |
| `agent/cold_start` | — | Count | Cold starts |
| `agent/retry_count` | target, attempt | Count | Retries realizados |

### 3.2 Métricas de Custo por Rota

```python
# Estimativa de custo por request
COST_PER_INPUT_TOKEN_HAIKU = 0.00000025   # $0.25/1M tokens
COST_PER_OUTPUT_TOKEN_HAIKU = 0.00000125  # $1.25/1M tokens

def calculate_request_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens * COST_PER_INPUT_TOKEN_HAIKU + 
            output_tokens * COST_PER_OUTPUT_TOKEN_HAIKU)

# Publicar como métrica
cloudwatch.put_metric_data(
    Namespace='MARHAgent',
    MetricData=[{
        'MetricName': 'CostPerRequest',
        'Value': cost_usd,
        'Unit': 'None',
        'Dimensions': [
            {'Name': 'Intent', 'Value': intent_id},
            {'Name': 'Flow', 'Value': flow_type},
        ]
    }]
)
```

### 3.3 Métricas Lambda (Automáticas)

| Métrica | Fonte | Uso |
|---|---|---|
| Duration | CloudWatch (auto) | Latência end-to-end |
| Invocations | CloudWatch (auto) | Volume |
| Errors | CloudWatch (auto) | Falhas não tratadas |
| Throttles | CloudWatch (auto) | Capacidade |
| ConcurrentExecutions | CloudWatch (auto) | Scaling |
| IteratorAge | CloudWatch (auto) | N/A (sem streams) |

---

## 4. Tracing Distribuído (X-Ray)

### 4.1 Configuração

```python
# Lambda com X-Ray ativo
# Variável de ambiente: AWS_XRAY_TRACING_MODE=Active

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Instrumenta automaticamente boto3, requests, httpx
patch_all()
```

### 4.2 Correlation ID

```python
import uuid

def get_correlation_id(event: dict) -> str:
    """Extrai ou gera correlation ID para rastreamento end-to-end."""
    # Tenta extrair da API MARH (header)
    headers = event.get('headers', {})
    correlation_id = headers.get('x-correlation-id') or headers.get('x-request-id')
    
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    
    # Adiciona ao X-Ray como annotation (pesquisável)
    xray_recorder.current_segment().put_annotation('correlation_id', correlation_id)
    
    return correlation_id
```

### 4.3 Subsegmentos Customizados

```python
@xray_recorder.capture('classify_intent')
def classify_intent(message: str) -> str:
    # Classificação determinística
    ...

@xray_recorder.capture('call_ma_hr_orch')
def call_ma_hr_orch(endpoint: str, params: dict) -> dict:
    # Chamada HTTP ao ma-hr-orch
    ...

@xray_recorder.capture('invoke_bedrock')
def invoke_bedrock(prompt: str) -> str:
    # Chamada ao Bedrock
    ...

@xray_recorder.capture('retrieve_knowledge_base')
def retrieve_kb(query: str) -> list:
    # RAG retrieve
    ...
```

### 4.4 Trace Completo (Exemplo)

```
[Lambda] (30ms init + 2100ms duration)
  ├── [classify_intent] 8ms
  ├── [call_ma_hr_orch] 1523ms
  │     └── [HTTP GET /orders] 1520ms
  ├── [sanitize_response] 5ms
  ├── [invoke_bedrock] 650ms
  │     └── [bedrock-runtime.InvokeModel] 645ms
  └── [validate_output] 3ms
```

---

## 5. POC vs. Produção

### 5.1 Observabilidade no POC

| Componente | Implementar | Notas |
|---|---|---|
| Logs estruturados (JSON) | ✅ Sim | Padrão desde o início |
| Métricas custom básicas | ✅ Sim | latency, error_count, token_usage |
| X-Ray tracing | ✅ Sim | Active tracing |
| Correlation ID | ✅ Sim | Propagar desde API MARH |
| Dashboard | ⏳ Não | Consultas manuais no Insights |
| Alarmes | ⏳ Não | Monitoramento manual |
| Log retention | 30 dias | Suficiente para POC |
| Métricas de custo | ✅ Sim | Validar estimativas |

### 5.2 Observabilidade em Produção (Futuro)

| Componente | Adicionar | Notas |
|---|---|---|
| CloudWatch Dashboard | ✅ | Visão real-time |
| CloudWatch Alarms | ✅ | Error rate, latency, cost |
| SNS Notifications | ✅ | Alertas para equipe |
| Log retention | 90 dias+ | Compliance |
| Log Insights queries salvas | ✅ | Troubleshooting rápido |
| Service Map (X-Ray) | ✅ | Visualização de dependências |
| X-Ray Analytics | ✅ | Análise de performance |
| Anomaly Detection | ✅ | ML-based alerting |
| Cost anomaly alerts | ✅ | Controle de gastos |
| SLA monitoring | ✅ | Uptime e latência |

---

## 6. Queries Úteis (CloudWatch Insights)

### 6.1 Latência por Intent

```
fields @timestamp, intent, flow, duration_ms
| filter level = "INFO" and stage = "complete"
| stats avg(duration_ms) as avg_latency, 
        pct(duration_ms, 95) as p95_latency,
        count() as requests
  by intent
| sort p95_latency desc
```

### 6.2 Erros por Tipo

```
fields @timestamp, error_type, error_code, intent
| filter level in ["ERROR", "CRITICAL"]
| stats count() as error_count by error_type, error_code
| sort error_count desc
```

### 6.3 Token Usage e Custo

```
fields @timestamp, intent, metadata.input_tokens, metadata.output_tokens
| filter stage = "bedrock_complete"
| stats sum(metadata.input_tokens) as total_input,
        sum(metadata.output_tokens) as total_output,
        count() as calls
  by intent
```

### 6.4 Circuit Breaker Events

```
fields @timestamp, message, metadata.old_state, metadata.new_state, metadata.failure_count
| filter event = "circuit_breaker_state_change"
| sort @timestamp desc
| limit 20
```

---

## 7. Compliance de Logs com LGPD

| Requisito | Implementação |
|---|---|
| Não logar PII | Sanitização antes de log |
| Retenção limitada | TTL de 30 dias (POC) |
| Acesso auditado | IAM + CloudTrail |
| Criptografia | CloudWatch Logs com KMS (opcional POC) |
| Direito ao esquecimento | Logs não identificam indivíduos |
