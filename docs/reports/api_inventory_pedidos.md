# Inventário de APIs - Gestão de Pedidos

**Gerado em:** 2026-07-22
**Fonte:** `docs/cliente/Gestao_de_Pedidos.html`
**Total de operações GET:** 8
**Operações POST ignoradas:** 3 (simulate-order, orders, cancel)

---

## Operações GET Identificadas

| # | Operação | Método | Endpoint | Parâmetros | Depende de | Resultado Real |
|---|----------|--------|----------|-----------|------------|----------------|
| 1 | Consulta de Pedidos | `GET` | `/v1/orders` | page, size, orderNumber | — | ✅ 200 (32 pedidos) |
| 2 | Consulta dos Produtos | `GET` | `/v1/products` | — | — | ✅ 200 (1 produto) |
| 3 | Consulta dos Benefícios | `GET` | `/v1/benefits` | — | — | ✅ 200 |
| 4 | Consulta dos Dias para Crédito | `GET` | `/v1/availability-dates-for-credit` | — | — | ✅ 200 |
| 5 | Download da Nota Fiscal | `GET` | `/v1/orders/{orderNumber}/invoice` | — | orderNumber | 422 (sem NF) |
| 6 | Colaboradores do Pedido | `GET` | `/v1/orders/{orderNumber}/beneficiaries` | page, size | orderNumber | ✅ 200 (1 colab) |
| 7 | Detalhes de um Pedido | `GET` | `/v1/orders/{orderNumber}` | — | orderNumber | ✅ 200 |
| 8 | Visualizar Boleto | `GET` | `/v1/orders/{orderNumber}/bank-ticket` | — | orderNumber | ✅ 200 (boleto) |

---

## Operações POST (Ignoradas — fora do escopo)

| Operação | Método | Endpoint | Motivo |
|----------|--------|----------|--------|
| Simulação do Pedido | POST | `/v1/simulate-order` | Mutável |
| Criação de Pedido | POST | `/v1/orders` | Mutável |
| Cancelamento de Pedido | POST | `/v1/orders/{orderNumber}/cancel` | Mutável |

---

## Detalhes por Operação

### 1. Consulta de Pedidos

- **Path:** `cardholders-hr-management/v1/orders`
- **Query Params:** `page`, `size`, `orderNumber`
- **Status codes:** 200 (Success), 204 (No Content), 403 (FNP/prova de vida NOK)
- **Observação:** Não permite filtrar por data
- **Campos principais da resposta:**
  - `total` — quantidade total de pedidos
  - `content[].orders[].orderNumber` — número do pedido
  - `content[].orders[].status` — status (PENDING, PAID, CREDITED, CANCELLED, etc.)
  - `content[].orders[].totalOrder` — valor total
  - `content[].orders[].paymentMethod` — método de pagamento
  - `content[].orders[].steps[]` — etapas do pedido
  - `content[].orders[].productInfo` — produto e benefícios
  - `pageable` — paginação

### 2. Consulta dos Produtos

- **Path:** `cardholders-hr-management/v1/products`
- **Status codes:** 200, 403
- **Campos observados:** `total`, `content`, `pageable`

### 3. Consulta dos Benefícios

- **Path:** `cardholders-hr-management/v1/benefits`
- **Status codes:** 200, 403
- **Campos observados:** `benefits`, `orderRules`

### 4. Consulta dos Dias para Crédito

- **Path:** `cardholders-hr-management/v1/availability-dates-for-credit`
- **Status codes:** 200, 403
- **Campos observados:** `minDate`, `maxDate`, `holidaysList`

### 5. Download da Nota Fiscal

- **Path:** `cardholders-hr-management/v1/orders/{orderNumber}/invoice`
- **Path params:** `orderNumber`
- **Status codes:** 200, 403, 422
- **Resposta 200:** `{ "rpsLink": "url_da_nota" }`
- **Observação:** 422 quando o pedido não tem NF emitida

### 6. Colaboradores do Pedido

- **Path:** `cardholders-hr-management/v1/orders/{orderNumber}/beneficiaries`
- **Path params:** `orderNumber`
- **Query params:** `page`, `size`
- **Status codes:** 200, 204, 403
- **Campos:** `total`, `content[].name`, `content[].documentNumber`, `content[].benefits[]`

### 7. Detalhes de um Pedido

- **Path:** `cardholders-hr-management/v1/orders/{orderNumber}`
- **Path params:** `orderNumber`
- **Status codes:** 200, 403
- **Campos observados:** `orderNumber`, `collectNumber`, `idOrder`, `orderDate`, `orderDateCreated`

### 8. Visualizar Boleto

- **Path:** `cardholders-hr-management/v1/orders/{orderNumber}/bank-ticket`
- **Path params:** `orderNumber`
- **Status codes:** 200, 403
- **Campos observados:** `fileName`, `content`, `barCodeLine`

---

## Encadeamento

Endpoints 5, 6, 7 e 8 dependem de um `orderNumber` válido. O fluxo é:

1. `GET /v1/orders` → retorna lista com `orders[].orderNumber`
2. Usa o `orderNumber` extraído nas chamadas dependentes

---

## Status Possíveis de Pedido (documentados)

- `IN_PROCESSING`
- `PENDING`
- `PAID`
- `CREDITED`
- `CANCELLED`
- `REJECTED`
- `RELEASED`
- `IN_BILLING_PROCESSING`
- `REFUNDED`
- `PARTIAL_REFUNDED`
