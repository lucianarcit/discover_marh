# Relatório de Testes de API - Gestão de Pedidos

**Gerado em:** 2026-07-22 13:38
**Execução:** `20260722_133814`
**Ambiente:** homologacao (UAT)
**Autenticação:** Bearer token (app portador, 5min TTL)

---

## Resumo por Categoria

| Categoria | Total | Sucesso | Falha | Bloqueado | Ignorado |
|-----------|-------|---------|-------|-----------|----------|
| Testes unitários | 64 | 64 | 0 | 0 | 0 |
| Integração GET (Pedidos) | 8 | 7 | 1 | 0 | 0 |
| Operações POST | 3 | 0 | 0 | 0 | 3 (removidas) |

---

## Resultado das APIs Executadas

| # | Operação | Status HTTP | Resultado | Duração | Observação |
|---|----------|-------------|-----------|---------|------------|
| 1 | Consulta de Pedidos | 200 | ✅ SUCCESS | 782ms | 32 pedidos, paginado |
| 2 | Consulta dos Produtos | 200 | ✅ SUCCESS | 520ms | 1 produto |
| 3 | Consulta dos Benefícios | 200 | ✅ SUCCESS | 368ms | benefits + orderRules |
| 4 | Dias para Crédito | 200 | ✅ SUCCESS | 319ms | minDate, maxDate, feriados |
| 5 | Nota Fiscal | 422 | ⚠️ Esperado | 306ms | Pedido sem NF emitida |
| 6 | Colaboradores do Pedido | 200 | ✅ SUCCESS | 188ms | 1 colaborador |
| 7 | Detalhes do Pedido | 200 | ✅ SUCCESS | 256ms | Pedido 356145 |
| 8 | Boleto | 200 | ✅ SUCCESS | 723ms | fileName + barCodeLine |

---

## Dados Observados na Resposta Real

### GET /v1/orders (200)
```json
{
  "total": 32,
  "content": [...],
  "pageable": {"page": 0, "size": 10}
}
```
Campos por pedido: `orderNumber`, `status`, `totalOrder`, `paymentMethod`, `steps[]`, `productInfo`, `statusHistory[]`

### GET /v1/products (200)
```json
{
  "total": 1,
  "content": [...],
  "pageable": {...}
}
```

### GET /v1/benefits (200)
```json
{
  "benefits": [...],
  "orderRules": {...}
}
```

### GET /v1/availability-dates-for-credit (200)
```json
{
  "minDate": "...",
  "maxDate": "...",
  "holidaysList": [...]
}
```

### GET /v1/orders/{id}/beneficiaries (200)
```json
{
  "total": 1,
  "content": [...],
  "pageable": {...}
}
```

### GET /v1/orders/{id} (200)
Campos: `orderNumber`, `collectNumber`, `idOrder`, `orderDate`, `orderDateCreated`, ...

### GET /v1/orders/{id}/bank-ticket (200)
```json
{
  "fileName": "...",
  "content": "...",
  "barCodeLine": "..."
}
```

### GET /v1/orders/{id}/invoice (422)
```json
{
  "statusCode": 422,
  "message": "A nota fiscal não foi encontrada (Pedido 356145)."
}
```

---

## Encadeamento Executado

1. `GET /v1/orders` → extraiu `orderNumber: 356145`
2. Usado em: `/orders/356145`, `/orders/356145/beneficiaries`, `/orders/356145/invoice`, `/orders/356145/bank-ticket`

---

## Localização dos Artefatos

- Inventário JSON: `artifacts/api_inventory/gestao_pedidos_apis.json`
- Resumo execução: `artifacts/api_runs/20260722_133814/execution_summary.json`
- Respostas sanitizadas: `artifacts/api_runs/20260722_133814/sanitized_responses.json`
- Individual: `artifacts/api_runs/20260722_133814/individual/`
