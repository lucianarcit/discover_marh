# Quality Gate — Correções Aplicadas
**Data:** 2026-07-23

Todas as correções foram validadas com re-execução completa da suíte de testes (57/57 ✅).

---

## Correção 1 — Bug de classificação: "cancelados" → INT-022

**Finding:** F-001 (BLOCKER)  
**Arquivo:** `poc_marh_agent/backend/src/marh_agent/classification/intent_classifier.py`

**Antes:**
```python
_TRANSACTIONAL_PATTERNS = [
    (r"cancel[ae]", "INT-022"),  # capturava "cancelados"
    ...
]
```

**Depois:**
```python
_TRANSACTIONAL_PATTERNS = [
    # Cancelamento: exige forma verbal imperativa/infinitiva
    # "cancelados" (particípio = status) não é capturado
    (r"\bcancelar?\b|\bcancele\b", "INT-022"),
    ...
]
```

**Testes adicionados:**
- `test_cancelled_status_query_not_transactional` — "Pedidos cancelados" → INT-005
- `test_cancelled_alias_anulado` — "Pedidos anulados" → INT-005
- `test_cancel_imperative_triggers_int022` — "Cancele o pedido" → INT-022 (comportamento preservado)
- `test_cancellation_word_not_transactional` — "Pedidos em cancelamento" → não transacional
- `test_cancelled_orders_query_not_transactional` (integração) — idem

---

## Correção 2 — LookupError não capturada no router

**Finding:** F-004 (HIGH)  
**Arquivo:** `poc_marh_agent/backend/src/marh_agent/application/router.py`

**Adicionado:**
```python
except LookupError:
    # 404 do backend — recurso não encontrado
    return ChatResponse(
        correlation_id=correlation_id,
        intent_id=intent_id,
        flow="API_ONLY",
        message=ERROR_CATALOG["ERR-003"],
        error_code="ERR-003",
        metadata=metadata,
    )
```

**Teste adicionado:**
- `test_lookup_error_handled_gracefully` — `simulate_error=404` retorna ERR-003 sem lançar exceção

---

## Correção 3 — `get_display_label()` não expõe api_status ao usuário

**Finding:** F-005 (MEDIUM)  
**Arquivo:** `poc_marh_agent/backend/src/marh_agent/classification/status_mapper.py`

**Antes:**
```python
def get_display_label(api_status: str) -> str:
    for entry in _STATUS_ENTRIES:
        if entry.api_status == api_status:
            return entry.label_completed or entry.api_status  # expunha api_status
    return api_status  # expunha api_status desconhecido
```

**Depois:**
```python
def get_display_label(api_status: str) -> str:
    for entry in _STATUS_ENTRIES:
        if entry.api_status == api_status:
            return entry.label_completed if entry.label_completed else "Status não disponível"
    return "Status desconhecido"
```

**Testes adicionados:**
- `test_unknown_status_display_label` — status desconhecido retorna genérico
- `test_partial_refunded_no_technical_label` — PARTIAL_REFUNDED não retorna "PARTIAL_REFUNDED"

---

## Correção 4 — Dead code `_CATALOG_PATH` removido

**Finding:** F-007 (MEDIUM)  
**Arquivo:** `poc_marh_agent/backend/src/marh_agent/classification/status_mapper.py`

Removidas as linhas:
```python
import json
from pathlib import Path
...
_CATALOG_PATH = (
    Path(__file__).resolve().parents[4]
    / "fixtures"
    / "order_status_catalog.json"
)
```

Adicionado comentário explícito sobre o catálogo inline.

---

## Correção 5 — Import inline `extract_name` movido para topo

**Finding:** F-008 (MEDIUM)  
**Arquivo:** `poc_marh_agent/backend/src/marh_agent/classification/intent_classifier.py`

**Antes:** `from marh_agent.classification.entity_extractor import extract_name` dentro de `classify()`.  
**Depois:** Import no topo do arquivo junto com os demais imports.

---

## Correção 6 — 15 testes críticos adicionados

**Finding:** Testes ausentes identificados no F-001, F-004, F-005 e outros.

**Novos testes em `test_orchestrator.py` (10):**
- `test_cancelled_status_query_not_transactional`
- `test_cancelled_alias_anulado`
- `test_lookup_error_handled_gracefully`
- `test_unknown_status_display_label`
- `test_partial_refunded_no_technical_label`
- `test_steps_do_not_leak_restricted_fields`
- `test_id_order_never_in_full_response`
- `test_prd_environment_uses_prd_base`
- `test_cancel_imperative_triggers_int022`
- `test_cancellation_word_not_transactional`

**Novos testes em `test_api.py` (5):**
- `test_id_order_never_in_response`
- `test_invalid_json_body`
- `test_missing_message_field`
- `test_cancelled_orders_query_not_transactional`
- `test_deeplink_no_sensitive_ids`

---

## Resultado da Reexecução

```
57 passed in 0.49s
EXIT_CODE: 0
```

Nenhum teste introduzido pela correção falhou. Nenhum teste preexistente foi quebrado.
