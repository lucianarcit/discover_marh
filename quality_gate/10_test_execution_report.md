# Quality Gate — Relatório de Execução de Testes
**Data:** 2026-07-23

---

## Antes das Correções — 42 testes

```
42 passed in 0.45s
```

Todos os 42 testes preexistentes passaram. Nenhuma falha antes das correções.

---

## Após as Correções — 57 testes

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1
collected 57 items

tests/integration/test_api.py::test_health PASSED
tests/integration/test_api.py::test_chat_order_specific PASSED
tests/integration/test_api.py::test_chat_last_order PASSED
tests/integration/test_api.py::test_chat_orders_paid PASSED
tests/integration/test_api.py::test_chat_collaborator_by_name PASSED
tests/integration/test_api.py::test_chat_collaborator_by_cpf PASSED
tests/integration/test_api.py::test_chat_tracking_by_cpf PASSED
tests/integration/test_api.py::test_chat_transactional_action PASSED
tests/integration/test_api.py::test_chat_company_switch PASSED
tests/integration/test_api.py::test_cors_localhost_accepted PASSED
tests/integration/test_api.py::test_cors_unauthorized_origin PASSED
tests/integration/test_api.py::test_response_contract PASSED
tests/integration/test_api.py::test_id_order_never_in_response PASSED        [NOVO]
tests/integration/test_api.py::test_invalid_json_body PASSED                  [NOVO]
tests/integration/test_api.py::test_missing_message_field PASSED              [NOVO]
tests/integration/test_api.py::test_cancelled_orders_query_not_transactional PASSED [NOVO]
tests/integration/test_api.py::test_deeplink_no_sensitive_ids PASSED          [NOVO]
tests/unit/test_orchestrator.py::test_valid_request PASSED
... (30 testes preexistentes passando)
tests/unit/test_orchestrator.py::test_cancelled_status_query_not_transactional PASSED [NOVO - valida F-001]
tests/unit/test_orchestrator.py::test_cancelled_alias_anulado PASSED          [NOVO]
tests/unit/test_orchestrator.py::test_lookup_error_handled_gracefully PASSED  [NOVO - valida F-004]
tests/unit/test_orchestrator.py::test_unknown_status_display_label PASSED     [NOVO - valida F-005]
tests/unit/test_orchestrator.py::test_partial_refunded_no_technical_label PASSED [NOVO]
tests/unit/test_orchestrator.py::test_steps_do_not_leak_restricted_fields PASSED [NOVO - documenta F-002]
tests/unit/test_orchestrator.py::test_id_order_never_in_full_response PASSED  [NOVO]
tests/unit/test_orchestrator.py::test_prd_environment_uses_prd_base PASSED    [NOVO]
tests/unit/test_orchestrator.py::test_cancel_imperative_triggers_int022 PASSED [NOVO]
tests/unit/test_orchestrator.py::test_cancellation_word_not_transactional PASSED [NOVO]

57 passed in 0.49s
```

---

## Distribuição de Testes por Dimensão

| Dimensão | Cobertura | Testes |
|---|---|---|
| Classificação de intenção | INT-001 a INT-007, Grupo B, Grupo C | 15 |
| Allowlist / PII | Colaborador, Pedido, Campos restritos | 6 |
| Deeplinks | HML, PRD, casing, path traversal, idOrder | 7 |
| Erros | ERR-001 a ERR-010 | 8 |
| CORS | localhost aceito, externo rejeitado | 2 |
| Contrato de API | Request/Response, campos obrigatórios | 4 |
| Segurança | CPF na resposta, empresa imutável, troca bloqueada | 5 |
| Rastreamento | INT-006 (CPF), INT-007 (pedido) | 2 |
| Lógica de classificação | cancelados/anulados, verbo imperativo | 4 |
| Resiliência | LookupError, timeout, 403, 500 | 2 |
| **Total** | | **57** |

---

## Ferramentas de Qualidade Estática — Não Configuradas

| Ferramenta | Status |
|---|---|
| `ruff` (linter) | Não configurado |
| `mypy` (type check) | Não configurado |
| `bandit` (security analysis) | Não configurado |
| `coverage` (cobertura) | Não configurado |

**Recomendação:** Adicionar ao `pyproject.toml` antes da integração real.

---

## Comando de Reprodução

```bash
cd C:\proj\discover_alelo\poc_marh_agent\backend
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```
