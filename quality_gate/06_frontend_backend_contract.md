# Quality Gate — Contrato Frontend ↔ Backend
**Data:** 2026-07-23

---

## 1. Request — Comparação Campo a Campo

| Campo | Frontend (`config.js`) | Backend (`requests.py`) | Compatível? |
|---|---|---|---|
| `company_id` | `CONFIG.SYNTHETIC_COMPANY_ID = "empresa-sintetica-001"` | `company_id: str = Field(default="")` | ✅ |
| `user_id` | `CONFIG.SYNTHETIC_USER_ID = "usuario-sintetico-001"` | `user_id: str = Field(default="")` | ✅ |
| `session_id` | `CONFIG.SYNTHETIC_SESSION_ID = "sessao-sintetica-001"` | `session_id: str = Field(default="")` | ✅ |
| `message` | `String(userMessage).slice(0, 2000)` | `message: str = Field(..., min_length=1)` + `validate_message_length` (trunca em 2000) | ✅ |
| `environment` | `CONFIG.ENVIRONMENT = "HML"` | `environment: Literal["HML", "PRD"] = "HML"` | ✅ |
| `correlation_id` | Não enviado | `correlation_id: str | None = None` (opcional, gerado no orchestrator) | ✅ |

---

## 2. Response — Comparação Campo a Campo

| Campo | Backend (`responses.py`) | Frontend (`chat.js` / `api-client.js`) | Compatível? |
|---|---|---|---|
| `correlation_id` | `str` obrigatório | Verificado em `_validateResponse`: campo `message` obrigatório (correlation_id não verificado pelo frontend, mas presente) | ✅ |
| `intent_id` | `str | None` | Consumido em logs internos, não renderizado | ✅ |
| `flow` | `str` | Consumido para routing no frontend | ✅ |
| `message` | `str` obrigatório | Verificado: `typeof data.message !== "string"` → rejeita | ✅ |
| `navigation` | `NavigationResponse | None` | Verificado: `if (response.navigation && response.navigation.type === "list_navigation")` | ✅ |
| `navigation.type` | `"list_navigation"` (hardcoded) | Verificado: `response.navigation.type === "list_navigation"` | ✅ |
| `navigation.route_id` | `str` | Usado em `buildWebviewUrl(nav.route_id, ...)` | ✅ |
| `navigation.label` | `str` | Renderizado como `textContent` | ✅ |
| `navigation.deeplink` | `str` | Guardado em `card.dataset.deeplink` | ✅ |
| `navigation.webview_url` | `str` | Usado como fallback se `buildWebviewUrl` retornar null | ✅ |
| `error_code` | `str | None` | Não renderizado diretamente — presente na resposta | ✅ |
| `metadata` | `dict` | Verificado em testes: `data["metadata"]["mode"] == "MOCK_LOCAL"` | ✅ |
| `metadata.mode` | `"MOCK_LOCAL"` | Badge de ambiente no frontend usa `CONFIG.ENV_LABEL`, não o metadata | ✅ |
| `metadata.data_classification` | `"SYNTHETIC_TEST_DATA"` | Presente no response, não renderizado ao usuário | ✅ |

**Divergência encontrada:** O frontend `api-client.js` tem campos extras no erro interno (`_error`, `_code`) que não existem no contrato do backend. Estes são campos **privados do frontend** para tratamento de erros de rede/timeout, nunca enviados ao usuário. Não é incompatibilidade — são dois contratos: backend→frontend (JSON da API) e frontend→DOM (renderização). ✅

---

## 3. Modo Mock vs. Modo Backend

### USE_MOCK_AGENT = true (padrão)

- Frontend chama `MockAgent.sendMessage(payload)` — sem HTTP
- MockAgent segue o mesmo contrato de response do backend
- Verificado: nenhum `fetch()` é chamado ✅

### USE_MOCK_AGENT = false

- Frontend chama `_sendToBackend(payload)` via `fetch POST`
- Backend recebe e valida com Pydantic
- CORS configurado para `localhost:8080`
- Timeout: 30 segundos (`AbortController`)
- Erros HTTP (400, 401, 403, 404, 422, 429, 5xx) tratados com mensagem amigável

---

## 4. Indicador de Ambiente

| Modo | Badge exibida | Classe CSS |
|---|---|---|
| `USE_MOCK_AGENT = true` | **MOCK LOCAL** | `env-badge--mock` (laranja) |
| `USE_MOCK_AGENT = false` + localhost | **BACKEND LOCAL** | `env-badge--local` (verde) |
| `USE_MOCK_AGENT = false` + AWS URL | **AWS HML** | `env-badge--hml` (azul) |

O indicador reflete o modo real (derivado de `CONFIG.ENV_LABEL`). ✅

---

## 5. Cenários de Teste End-to-End (manual)

| Cenário | Comportamento Esperado | Comportamento Real |
|---|---|---|
| "O que posso fazer?" | Resposta informativa, sem API call | ✅ `flow: RAG_ONLY`, mensagem de capacidades |
| "Consultar pedido 342671" | Detalhes do pedido 342671, deeplink ROUTE-014 | ✅ `intent_id: INT-003`, deeplink com orderNumber |
| "Qual foi o último pedido?" | Pedido 342671 (mais recente na fixture) | ✅ `intent_id: INT-004` |
| "Pedidos pagos" | Lista com 342671 e 342674 | ✅ `intent_id: INT-005` |
| "Consultar colaborador Pessoa Colaboradora A" | Dados filtrados (sem CPF/email) | ✅ `intent_id: INT-001`, sem PII |
| "Consultar CPF 000.000.000-00" | Colaborador encontrado, CPF não na resposta | ✅ `intent_id: INT-002` |
| "Rastrear cartões pelo CPF" | ERR-010, solicita orderNumber | ✅ `intent_id: INT-006` |
| "Rastrear pedido 342671" | Informativo: validação pendente + deeplink card-tracking | ✅ `intent_id: INT-007` |
| "Cancele o pedido 342671" | Redirect: acesse o Espaço RH | ✅ `flow: REDIRECT_TO_OFFICIAL_JOURNEY` |
| "Troque para outra empresa" | Empresa imutável: use o app | ✅ mensagem de bloqueio |
| "Pedidos cancelados" | Lista de pedidos CANCELLED | ✅ `intent_id: INT-005` (após correção F-001) |
| Body JSON inválido | HTTP 400, `error_code: ERR-PARSE` | ✅ (teste automatizado) |
| Message ausente | HTTP 422, `error_code: ERR-VALIDATION` | ✅ (teste automatizado) |
