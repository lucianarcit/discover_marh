# Quality Gate — Revisão de Deeplinks
**Data:** 2026-07-23

---

## 1. Formato do Deeplink

**Esperado (Discovery):**
```
meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true
```

**Implementado (navigation/builder.py):**
```python
deeplink = (
    f"meualelo://app/webview?url={encoded_url}"
    f"&isModal=false&showNavbar=false&authRequired=true"
)
```

✅ **Formato correto.**

---

## 2. Casing dos Parâmetros

| Parâmetro | Esperado | Implementado | Status |
|---|---|---|---|
| `isModal` | `isModal=false` | `isModal=false` | ✅ |
| `showNavbar` | `showNavbar=false` | `showNavbar=false` | ✅ |
| `authRequired` | `authRequired=true` | `authRequired=true` | ✅ |

Teste `test_deeplink_casing` confirma: ✅

---

## 3. Bases por Ambiente

| Ambiente | Esperado | Implementado | Teste |
|---|---|---|---|
| HML | `https://meualelo-webviews-hml.siteteste.inf.br/` | `WEBVIEW_BASE_URLS["HML"]` = mesmo valor | `test_deeplink_hml` ✅ |
| PRD | `https://meualelo-webviews.alelo.com.br/` | `WEBVIEW_BASE_URLS["PRD"]` = mesmo valor | `test_deeplink_prd` ✅ |

---

## 4. Catálogo de Rotas — Backend (builder.py)

| Route ID | Padrão | Permitido para Agente | Status |
|---|---|---|---|
| ROUTE-003 | `#/employees` | ✅ SIM | Implementado |
| ROUTE-012 | `#/orders` | ✅ SIM | Implementado |
| ROUTE-014 | `#/order-detail/{orderNumber}` | ✅ SIM | Implementado |
| ROUTE-015 | `#/order-detail/{orderNumber}/beneficiaries` | ✅ SIM | No catálogo, não chamado no router (LOW F-014) |
| ROUTE-017 | `#/new-order/products` | ✅ SIM (redirect only) | Implementado |
| ROUTE-024 | `#/card-tracking` | ✅ SIM | Implementado |
| ROUTE-025 | `#/card-tracking/{orderNumber}` | ✅ SIM | Implementado |
| ROUTE-008 | `#/employees/:id/edit` | ❌ NÃO | **Ausente do catálogo do builder** — correto |
| ROUTE-013-V2 | `#/order-request-group?orderNumber=...` | ✅ SIM (Discovery) | **Ausente do builder** — INFO (não implementado na POC) |
| ROUTE-026 | `#/card-tracking/:orderNumber/:arNumber` | ✅ SIM (Discovery) | **Ausente do builder** — INFO (arNumber não disponível via mock) |

---

## 5. Validações de Segurança no Builder

| Validação | Implementada | Teste |
|---|---|---|
| `orderNumber` apenas dígitos (1-10) | ✅ `_ORDER_NUMBER_VALID = re.compile(r"^\d{1,10}$")` | `test_path_traversal_blocked` ✅ |
| Path traversal rejeitado (`..`, `%2F`, `/`) | ✅ `_PATH_TRAVERSAL` regex | `test_path_traversal_blocked` ✅ |
| `idOrder` rejeitado | ✅ Parâmetro aceito é `order_number`, nunca `id_order` | `test_id_order_never_in_deeplink` ✅ |
| `beneficiaryId` ausente do deeplink | ✅ ROUTE-003 sem parâmetro de id | `test_cpf_not_in_deeplink` ✅, `test_deeplink_no_sensitive_ids` ✅ |
| Rota não autorizada bloqueada | ✅ `if route_id not in ALLOWED_ROUTES: return None` | — |
| URL externa bloqueada | ✅ Base sempre de `WEBVIEW_BASE_URLS` | — |
| `authRequired=true` obrigatório | ✅ Hardcoded no template | `test_deeplink_casing` ✅ |

---

## 6. Navigation Builder no Frontend

| Validação | Implementada | Evidência |
|---|---|---|
| Allowlist de hosts (`isAllowedWebviewUrl`) | ✅ | `api-client.js` linha 154-158 |
| Rejeição de URL não permitida | ✅ | `chat.js:264` — `if (!AgentApiClient.isAllowedWebviewUrl(resolvedUrl)) return null` |
| Deeplink no `data-deeplink` (para app nativo) | ✅ | `chat.js:272` — `card.dataset.deeplink = nav.deeplink` |
| Desktop abre webview em nova aba | ✅ | `card.target = "_blank"; card.rel = "noopener noreferrer"` |
| Validação de suffix numérico | ✅ | `buildWebviewUrl()` rejeita não-dígitos com `/^\d{1,20}$/` |

---

## 7. Conformidade com Discovery (deeplink_routes_catalog.json)

| Regra | Status |
|---|---|
| Base URL definida por configuração, nunca pelo modelo | ✅ |
| Base URL nunca vem da mensagem do usuário | ✅ |
| HML não aparece em resposta de PRD | ✅ (definido por env var `ENVIRONMENT`) |
| `orderNumber` validado antes de inserir na rota | ✅ |
| `arNumber` exclusivamente de fonte confiável (API) | ✅ (não implementado no mock — arNumber ausente) |
| Rota de colaborador individual não suportada | ✅ |
| Deeplink sem CPF, CNPJ, token | ✅ |

---

## 8. Gaps Documentados (não bloqueadores)

- **ROUTE-013-V2** (`#/order-request-group?orderNumber=...`) não está implementada no backend — será necessária quando DP-003-B for resolvido.
- **ROUTE-026** (`#/card-tracking/:orderNumber/:arNumber`) não está implementada — `arNumber` só disponível via API real de rastreamento (DP-001).
