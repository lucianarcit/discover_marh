# Roteiro de Testes — Fase 1

**Objetivo:** Validar que a infraestrutura AWS está funcionando corretamente e o agente responde como esperado.

---

## 1. Testes Automatizados (Local)

```powershell
cd poc_marh_agent/backend
python -m pytest -v
```

**Esperado:** 107 testes passando, 0 falhas.

---

## 2. Validação do Lambda Handler (Local)

```powershell
cd poc_marh_agent/backend
python scripts/validate_lambda.py
```

**Esperado:** 11/11 mensagens passando.

---

## 3. Health Check (AWS)

```powershell
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/health"
```

**Esperado:**
```json
{
  "status": "ok",
  "mode": "MOCK_LOCAL",
  "environment": "HML",
  "dependencies": {
    "ma_hr_orch": "MOCK",
    "bedrock_classifier": "DISABLED",
    "bedrock_rag": "DISABLED"
  }
}
```

---

## 4. Testes Funcionais na API (AWS)

Executar cada mensagem via terminal e validar a resposta:

### 4.1 — O que posso fazer? (INT-008)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"O que posso fazer?","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-008`
- `flow` = `RAG_ONLY`
- `presentation.variant` = `capabilities_list`
- `message` presente e não vazio

---

### 4.2 — Consultar colaborador por nome (INT-001)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Consultar colaborador Pessoa Colaboradora A","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-001`
- `flow` = `API_ONLY`
- `presentation.variant` = `collaborator_summary`
- Campos do colaborador presentes (nome, status)
- **CPF NÃO aparece** nos campos de presentation

---

### 4.3 — Consultar colaborador por CPF (INT-002)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Consultar CPF 000.000.000-00","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-002`
- `presentation.variant` = `collaborator_summary`
- CPF mascarado na mensagem (se mencionado)

---

### 4.4 — Consultar pedido por número (INT-003)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Consultar pedido 342671","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-003`
- `presentation.variant` = `order_summary`
- `navigation` presente com deeplink
- **idOrder NÃO aparece** no deeplink nem na resposta

---

### 4.5 — Último pedido (INT-004)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Qual foi o ultimo pedido?","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-004`
- `presentation.variant` = `order_summary`
- Retorna o pedido com maior número

---

### 4.6 — Pedidos por status (INT-005)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Pedidos com status pago","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-005`
- `presentation.variant` = `order_list`
- `presentation.items` é lista com pedidos

---

### 4.7 — Rastreamento por CPF (INT-006)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Rastrear cartões pelo CPF","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-006`
- `flow` = `REQUIRES_CLARIFICATION`
- `presentation.variant` = `clarification`

---

### 4.8 — Rastreamento por pedido (INT-007)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Rastrear pedido 342671","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-007`
- `presentation.variant` = `warning_notice`
- `navigation` presente (Ver rastreamento)

---

### 4.9 — Ação transacional bloqueada (INT-022)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Cancele o pedido 342671","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-022`
- `flow` = `REDIRECT_TO_OFFICIAL_JOURNEY`
- `presentation.variant` = `transactional_redirect`
- Mensagem orienta a usar o portal

---

### 4.10 — Troca de empresa (COMPANY_SWITCH)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"Troque para outra empresa","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `null` (router retorna null para COMPANY_SWITCH)
- `flow` = `STATIC_RESPONSE`
- `presentation.variant` = `informational_notice`

---

### 4.11 — Pergunta informativa (INT-019)

```powershell
$body = '{"company_id":"emp-001","user_id":"usr-001","session_id":"sess-001","message":"O que é o MARH?","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Validar:**
- `intent_id` = `INT-019`
- `flow` = `RAG_ONLY`
- `presentation.variant` = `knowledge_answer`

---

## 5. Testes de Segurança (AWS)

### 5.1 — Request sem company_id

```powershell
$body = '{"user_id":"usr-001","session_id":"sess-001","message":"Oi","environment":"HML"}'
Invoke-RestMethod -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body $body -ContentType "application/json"
```

**Esperado:** `error_code` = `ERR-VALIDATION`, status 422

---

### 5.2 — Request com body inválido

```powershell
Invoke-WebRequest -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method POST -Body "isso não é json" -ContentType "application/json" -UseBasicParsing
```

**Esperado:** `error_code` = `ERR-PARSE`, status 400

---

### 5.3 — CORS bloqueado (origem não autorizada)

```powershell
$r = Invoke-WebRequest -Uri "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat" -Method OPTIONS -Headers @{Origin="https://evil.com"; "Access-Control-Request-Method"="POST"} -UseBasicParsing
$r.Headers["access-control-allow-origin"]
```

**Esperado:** Header `access-control-allow-origin` **ausente** ou não contém `evil.com`

---

## 6. Testes no Frontend (Browser)

Abrir: **https://d1vtu9x0di76z9.cloudfront.net**

### Checklist visual

| # | Teste | Esperado |
|---|-------|----------|
| 1 | Página carrega | Home do Espaço RH aparece |
| 2 | Badge de ambiente | Mostra "AWS HML" |
| 3 | Abrir chat | Tela de conversa carrega |
| 4 | Enviar "O que posso fazer?" | Card `capabilities_list` renderiza com 6 itens |
| 5 | Enviar "Consultar pedido 342671" | Card `order_summary` com dados do pedido |
| 6 | Enviar "Cancele o pedido" | Card `transactional_redirect` com botão de ação |
| 7 | Clicar em link de navigation | Deeplink válido (não contém CPF nem idOrder) |
| 8 | Enviar mensagem vazia | Não quebra (botão desabilitado ou mensagem de erro) |
| 9 | DevTools → Network | Requests vão para `pzn843po3h.execute-api...` |
| 10 | DevTools → Console | Nenhum erro de CORS ou CSP |

---

## 7. Testes de Infraestrutura

### 7.1 — Terraform state consistente

```powershell
cd infra
terraform plan
```

**Esperado:** `No changes. Your infrastructure matches the configuration.`

---

### 7.2 — Logs chegando no CloudWatch

```powershell
aws logs tail /aws/lambda/marh-agent-hml --since 5m --format short
```

**Esperado:** Logs de `request_processed` com `intent_id` e `duration_ms`

---

### 7.3 — X-Ray traces

Verificar no console AWS: **X-Ray → Traces** — devem aparecer traces da Lambda.

---

## Resultado Esperado

| Categoria | Total | Passando |
|-----------|:---:|:---:|
| Testes automatizados | 107 | 107 |
| Validação Lambda local | 11 | 11 |
| Testes funcionais AWS | 11 | 11 |
| Testes de segurança | 3 | 3 |
| Testes no browser | 10 | 10 |
| Testes de infra | 3 | 3 |
| **Total** | **145** | **145** |
