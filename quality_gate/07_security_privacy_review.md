# Quality Gate — Revisão de Segurança e Privacidade
**Data:** 2026-07-23

---

## 1. Arquivos .env — Credenciais

| Arquivo | Conteúdo | Commitado? | Risco |
|---|---|---|---|
| `.env` (raiz) | Credenciais HML reais: `ALELO_CLIENT_ID`, `ALELO_CLIENT_SECRET`, `ALELO_ACCESS_TOKEN`, `ALELO_REFRESH_TOKEN`, `ALELO_FNP`, `ALELO_USER_ID` | **NÃO** (coberto pelo `.gitignore` linha 2) | Baixo — não versionado. Recomendado rotacionar tokens após o Discovery. |
| `docs/_referencia_alelo_faq_ciandt/.env` | Não auditado — diretório coberto pelo `.gitignore` | **NÃO** | Coberto |
| `docs/_referencia_alelo_faq_ciandt/api/.env` | Idem | **NÃO** | Coberto |

**Verificação:** `git check-ignore -v .env` → confirmou que `.env` está coberto. Nenhum `.env` aparece em `git status`.

---

## 2. Scan de Padrões Sensíveis no Código

### 2.1 CPF / CNPJ

| Ocorrência | Arquivo | Classificação |
|---|---|---|
| `000.000.000-00` | `fixtures/collaborators.json` | SYNTHETIC_OK — CPF nitidamente inválido (zeros) |
| `111.111.111-11`, `222.222.222-22` | `fixtures/collaborators.json` | SYNTHETIC_OK — CPFs nitidamente inválidos |
| `000.000.000-00` | `tests/unit/test_orchestrator.py` | SYNTHETIC_OK — dado de teste documentado |
| `CPF-SINTETICO-001` | `artifacts/intents_catalog.json` | SYNTHETIC_OK — marcador explícito |

Nenhum CPF com formato válido encontrado no código ou fixtures.

### 2.2 Tokens / Secrets

| Termo buscado | Ocorrências | Classificação |
|---|---|---|
| `secret` | `.env.example` (placeholder), comentários | DOCUMENTATION_OK |
| `token` | `.env.example` (placeholder), comentários explicativos | DOCUMENTATION_OK |
| `bearer` | `docs/tests/apis/.env.example` (placeholder) | DOCUMENTATION_OK |
| `access_key` | Nenhuma | — |
| `api_key` | Nenhuma em código fonte | — |
| `password` | Nenhuma | — |

### 2.3 PII em Código Executável

| Padrão | Arquivo | Status |
|---|---|---|
| `email` | `security/allowlists.py` — na lista de campos **bloqueados** | DOCUMENTATION_OK |
| `motherName` | `security/allowlists.py` — na lista de campos **bloqueados** | DOCUMENTATION_OK |
| `beneficiaryId` | `security/allowlists.py` — na lista de campos **bloqueados** | DOCUMENTATION_OK |
| `billingDocumentNumber` | `security/allowlists.py` — na lista de campos **bloqueados** | DOCUMENTATION_OK |
| `documentNumber` | `security/allowlists.py` — na lista de campos **bloqueados** | DOCUMENTATION_OK |

Todos os campos PII mencionados no código executável estão **exclusivamente** nas allowlists de bloqueio, nunca em campos permitidos.

### 2.4 idOrder

| Ocorrência | Arquivo | Status |
|---|---|---|
| `"idOrder"` | `fixtures/orders.json` | SYNTHETIC_OK — presente para testar remoção pela allowlist |
| `"idOrder"` | `security/allowlists.py` — **não** está em `ORDER_ALLOWED_FIELDS` | Correto — removido |
| `"idOrder"` | `tests/unit/test_orchestrator.py` — verificando ausência | DOCUMENTATION_OK |

---

## 3. Frontend — Verificações de Segurança

| Verificação | Status | Evidência |
|---|---|---|
| Nenhum `eval()` | ✅ | Grep: nenhuma ocorrência em JS |
| Mensagens renderizadas com `textContent` | ✅ | `chat.js` linha 160, `_formatMessageText()` usa `createTextNode` |
| `innerHTML` apenas com dados estáticos ou escapados | ✅ | `chat.js:298` — SVG hardcoded. `home.js:61,88` — dados sintéticos com `_escText()` |
| Nenhum token em localStorage | ✅ | Grep: nenhuma ocorrência de `localStorage.set` com token/secret |
| Nenhum endpoint interno exposto | ✅ | `config.js` usa `http://localhost:8000` (local) como placeholder |
| Nenhum `console.log` com PII | ✅ | Grep: nenhum log com CPF, nome, empresa no código |
| CSP via meta tag | ✅ | Ambos HTMLs com `Content-Security-Policy` meta |
| Timeout implementado | ✅ | `api-client.js` usa `AbortController` com `CONFIG.REQUEST_TIMEOUT_MS` |
| Loading sempre encerrado | ✅ | `finally { isLoading = false; _hideTyping(); }` em `chat.js:107` |
| Botão send desabilitado quando vazio | ✅ | `sendBtn.disabled = inputField.value.trim().length === 0` |
| Allowlist de hosts no navigation builder | ✅ | `isAllowedWebviewUrl()` em `api-client.js` |
| Scripts remotos | ✅ | Nenhum `<script src="http...">` nos HTMLs |
| `USE_MOCK_AGENT=true` → sem POST | ✅ | `if (CONFIG.USE_MOCK_AGENT) return MockAgent.sendMessage(payload)` — sem fetch |

---

## 4. Backend — Verificações de Segurança

| Verificação | Status |
|---|---|
| Nenhum secret hardcoded | ✅ |
| Nenhum CPF em logs | ✅ — `_log()` só loga `correlation_id`, `intent_id`, `flow`, `error_code`, `duration_ms` |
| Nenhum nome em logs | ✅ |
| CORS restrito | ✅ — somente `localhost:8080` e `127.0.0.1:8080` |
| Validação Pydantic no request | ✅ |
| Limite de tamanho da mensagem | ✅ — `MAX_MESSAGE_LENGTH = 2000` |
| Campos restritos removidos | ✅ — allowlists funcionando (57 testes) |
| `authRequired=true` obrigatório nos deeplinks | ✅ |

---

## 5. Risco Residual Documentado

| Risco | Severidade | Ação Necessária Antes de Produção |
|---|---|---|
| `steps` sem sub-filtro (F-002) | HIGH | Definir campos seguros de `steps` |
| `sanitize_response_text()` não chamada (F-003) | HIGH | Conectar ao pipeline antes de usar LLM |
| Tokens no `.env` raiz não rotacionados | INFO | Rotacionar credenciais de HML após o Discovery |
