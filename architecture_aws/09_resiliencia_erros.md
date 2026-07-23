# 09 — Resiliência e Tratamento de Erros

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1

---

## 1. Princípios de Resiliência

1. **Fail gracefully** — Sempre retornar uma resposta ao usuário, mesmo em falha
2. **Retry only transient** — Apenas 429, 500, 502, 503, 504 e falhas transitórias de rede recebem retry
3. **Never retry client errors** — 400, 401, 403, 404, 422 **nunca** recebem retry
4. **Timeout everything** — Nenhuma chamada externa sem timeout explícito
5. **Sem circuit breaker distribuído em memória** — Memória da Lambda não é compartilhada
6. **Fallback determinístico** — ERR-001 a ERR-010 do Discovery

---

## 2. Política de Retry — POC

### 2.1 Regras

| Código HTTP | Retry? | Motivo |
|---|---|---|
| 400 | ❌ NUNCA | Erro de cliente — não vai mudar |
| 401 | ❌ NUNCA | Autenticação — não vai mudar sem nova auth |
| 403 | ❌ NUNCA | Autorização — não vai mudar |
| 404 | ❌ NUNCA | Recurso não existe |
| 422 | ❌ NUNCA | Dado inválido — não vai mudar |
| 429 | ✅ Máximo 1 retry | Transitório — com jitter, se idempotente e cabe no budget |
| 500 | ✅ Máximo 1 retry | Transitório — com jitter, se idempotente e cabe no budget |
| 502 | ✅ Máximo 1 retry | Transitório |
| 503 | ✅ Máximo 1 retry | Transitório |
| 504 | ✅ Máximo 1 retry | Transitório |
| Falha de rede/conexão | ✅ Máximo 1 retry | Transitório |

### 2.2 Condições para Retry

Retry somente quando:
1. A operação é idempotente (GET — sempre verdade aqui)
2. Ainda existe orçamento de latência disponível
3. O timeout global não será ultrapassado

### 2.3 Timeout e Retry Coerentes

```
Budget total: 15s (timeout global Lambda)

Fluxo API_ONLY:
  connect_timeout:  3s
  read_timeout:     8s
  (não usar 10s — ultrapassaria o budget com 1 retry)
  
  1ª tentativa:     3s + 8s = 11s máximo
  jitter:           ~0.5s
  1 retry:          3s + 8s = 11s máximo
  Total máximo:     ~23s — EXCEDE o global de 15s

  → Portanto, retry só se a 1ª tentativa completar em < 5s
  → Implementar: verificar tempo decorrido antes de tentar retry
```

**Nota:** A combinação `connect=3s + read=10s + 2 retries + geração de modelo` pode ultrapassar
o timeout global de 15s. Calcular o orçamento antes de configurar retries.

### 2.4 Backoff com Jitter

```python
import random

def calculate_backoff(attempt: int, base: float = 0.3, max_wait: float = 1.0) -> float:
    """Exponential backoff with full jitter — POC budget limitado."""
    exponential = min(base * (2 ** attempt), max_wait)
    return random.uniform(0, exponential)
# Attempt 0: wait 0–0.3s
# Attempt 1: wait 0–0.6s
```

---

## 3. Sem Circuit Breaker Distribuído em Memória

A memória de uma instância Lambda:
- Não é compartilhada entre instâncias concorrentes
- Pode desaparecer a qualquer momento (cold start)
- Não pode armazenar estado de segurança entre usuários
- Não é um controle global confiável

### Alternativas para a POC

**Opção 1 — Sem circuit breaker (preferencial para POC):**
- Retry máximo 1x para transitórios
- Timeout global de 15s
- Fallback determinístico (ERR-007)

**Opção 2 — DynamoDB para estado compartilhado (somente se houver justificativa):**
- Somente se volume e falhas recorrentes justificarem
- Fora do escopo da POC mínima

**Decisão POC:** Opção 1 — sem circuit breaker distribuído.

---

## 4. Timeouts Configurados

| Chamada | connect_timeout | read_timeout | Justificativa |
|---|---|---|---|
| ma-hr-orch GET | 3s | 8s | 3+8=11s; deixa margem para overhead |
| Bedrock InvokeModel (RAG) | N/A (SDK gerencia) | 8s | Budget RAG_ONLY |
| S3 Vectors query | N/A (SDK gerencia) | 5s | Retrieval é rápido |
| Timeout global Lambda | — | — | 30s (configurado na Lambda) |

---

## 5. Mapeamento de Erros — Mensagens do Discovery

Usar **exclusivamente** as mensagens ERR-001 a ERR-010 definidas no catálogo de requisitos.
Não criar mensagens alternativas.

| Código/Situação | Mensagem Discovery |
|---|---|
| Empresa ausente / HTTP 422 | **ERR-001**: "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente." |
| Colaborador não encontrado / HTTP 404 | **ERR-002**: "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." |
| Pedido não encontrado / HTTP 404 | **ERR-003**: "Não encontrei o pedido informado para a empresa selecionada." |
| Status não reconhecido | **ERR-004**: "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." |
| HTTP 403 — sem permissão | **ERR-005**: "Você não tem permissão para consultar informações dessa empresa no Espaço RH." |
| HTTP 403 — validação de segurança | **ERR-006**: "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente." |
| HTTP 5xx / timeout / indisponível | **ERR-007**: "Não consegui consultar essa informação agora. Tente novamente em alguns instantes." |
| KB sem resultado (RAG) | **ERR-008**: "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões." |
| [list_navigation] falhou | **ERR-009**: "Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela." |
| CPF insuficiente para rastreamento | **ERR-010**: "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." |

---

## 6. Falhas do Bedrock (RAG_ONLY)

| Erro Bedrock | Retry? | Fallback |
|---|---|---|
| ThrottlingException | ✅ 1x com backoff | ERR-008 se falhar novamente |
| ModelTimeoutException | ✅ 1x | ERR-008 |
| ValidationException | ❌ NÃO | Log error + ERR-008 |
| AccessDeniedException | ❌ NÃO | Log critical + alerta + ERR-007 |
| ServiceUnavailableException | ✅ 1x | ERR-008 |

---

## 7. Falhas de Retrieval (S3 Vectors)

| Falha | Retry? | Fallback |
|---|---|---|
| Timeout de retrieval | ✅ 1x | ERR-008 |
| Nenhum chunk relevante (score < threshold) | ❌ NÃO | ERR-008 sem LLM |
| S3 Vectors indisponível | ✅ 1x | ERR-008 |

---

## 8. Cadeia de Fallback Simplificada

```
Fluxo Normal
    │
    ▼ Erro transitório?
Retry (máximo 1x, se cabe no budget)
    │
    ▼ Falha novamente?
Mensagem padronizada ERR-001 a ERR-010
    │
    ▼ Sempre retorna algo
Resposta ao usuário
```

| Fluxo | Fallback |
|---|---|
| STATIC_RESPONSE | — (não falha) |
| REDIRECT | — (não falha) |
| API_ONLY | ERR-002/003/004/005/006/007 conforme código HTTP |
| RAG_ONLY | ERR-008 (sem resultado) ou ERR-007 (indisponível) |
| REQUIRES_CLARIFICATION | ERR-010 (determinístico) |

---

## 9. Monitoramento de Resiliência

| Métrica | Alerta se | Ação |
|---|---|---|
| Retry rate | > 10% | Verificar saúde dos serviços |
| Error rate (4xx) | > 5% | Verificar classificação/validação |
| Error rate (5xx) | > 1% | Alerta imediato |
| Timeout rate | > 3% | Verificar latência ma-hr-orch |
| Lambda throttles | > 0 | Verificar reserved concurrency |
