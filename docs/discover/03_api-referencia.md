# Referência de API — cardholders-hr-management

**Base path:** `/cardholders-hr-management/v1`
**Base URL HML:** `https://api-ma.homologacaoalelo.com.br/alelo/uat/cardholders-hr-management/v1`
**Versão:** 1
**Contato:** casiqueira@alelo.com.br (Lego)

> API de gerenciamento de colaboradores, benefícios, locais de entrega dos cartões e criação de pedidos de compra por interlocutores — usada pelo app Meu Alelo.

---

## Headers obrigatórios em todos os endpoints

| Header | Obrigatório | Descrição |
|---|---|---|
| `x-basic-authorization` | Sim | Token Sensedia (Basic base64 do CLIENT_ID:CLIENT_SECRET) |
| `Authorization` | Sim | `Bearer <accessToken>` (JWT WSO2 B2C) |
| `APP_VERSION` | Sim | Versão do app nativo |
| `FNP` | Sim | Fingerprint do dispositivo |
| `PLATFORM` | Sim | `ANDROID` ou `IOS` |
| `USER_ID` | Não | ID do usuário (fallback) |

> O header `x-document-number` (CPF do interlocutor) é injetado automaticamente pelo gateway a partir do JWT — não precisa ser enviado pelo cliente.

---

## Recursos

### 1. Beneficiaries — Colaboradores

#### `GET /beneficiaries`
Lista os colaboradores da empresa do interlocutor logado.

**Query params:**
| Param | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `nameOrCpf` | string | Não | Filtro por nome ou CPF |
| `page` | integer | Não | Número da página |

**Response 200:**
```json
{
  "content": [
    {
      "beneficiaryId": "string",
      "documentNumber": "CPF do colaborador",
      "name": "string",
      "email": "string",
      "phoneNumber": "string",
      "motherName": "string",
      "isHomeDelivery": true,
      "placeName": "string",
      "shippingAddressName": "string",
      "shippingAddressWorkplaceCode": "string",
      "subtype": "BRANCH | WORKPLACE",
      "address": { "street": "", "number": "", "complement": "", "neighborhood": "", "city": "", "state": "", "postalCode": "" },
      "products": [{ "productCode": "700", "tagName": "Alelo Pod" }]
    }
  ],
  "pageable": { "page": 0, "size": 20, "sort": { "direction": "ASC", "property": "beneficiary.name" } },
  "total": 100
}
```

**Erros:** 400, 403, 422

---

#### `POST /beneficiaries`
Cadastra um novo colaborador.

**Body:**
```json
{
  "name": "string",
  "birthDate": "yyyy-mm-dd",
  "email": "string",
  "phoneNumber": "string (sem caracteres especiais)",
  "motherName": "string",
  "isHomeDelivery": false,
  "placeDocumentNumber": "CNPJ do local de entrega",
  "placeType": "BRANCH | WORKPLACE",
  "placeCode": "código do local (quando placeType=WORKPLACE)",
  "address": { "street": "", "number": "", "complement": "", "neighborhood": "", "city": "", "state": "", "postalCode": "" }
}
```

**Response:** 201 Created | 400 | 403 | 422

---

#### `PUT /beneficiaries/{beneficiaryId}`
Atualiza os dados de um colaborador. Body igual ao POST.

**Response:** 204 No Content | 400 | 403 | 422

---

#### `DELETE /beneficiaries/{beneficiaryId}`
Exclui um colaborador.

**Response:** 204 No Content | 400 | 403 | 422

---

### 2. Benefits — Benefícios

#### `GET /benefits`
Lista os benefícios das empresas do interlocutor/portador.

**Response 200:** Array de:
```json
{
  "benefitCode": 1,
  "benefitName": "string",
  "enabled": true,
  "iconPath": "string",
  "isCustomBenefit": false,
  "partnerCode": "string",
  "productContractId": 123,
  "productIconCode": "string"
}
```

**Erros:** 204 (sem conteúdo), 403

---

### 3. Companies — Empresas

#### `GET /companies`
Lista as empresas pelas quais o interlocutor é responsável.

**Response 200:**
```json
{
  "contractees": [
    {
      "documentNumber": "CNPJ",
      "name": "Nome da empresa",
      "default": true
    }
  ]
}
```

**Erros:** 204, 403

---

#### `PUT /default-company`
Define a empresa padrão do interlocutor.

**Body:**
```json
{ "companyId": "string" }
```

**Response:** 200 | 403 | 422

---

### 4. Orders — Pedidos

#### `GET /orders`
Lista os pedidos do interlocutor.

**Query params:**
| Param | Tipo | Descrição |
|---|---|---|
| `page` | number | Número da página |
| `size` | number | Tamanho da página |
| `orderNumber` | number | Filtro por número do pedido |

**Response 200:**
```json
{
  "content": [
    {
      "orderNumberGroup": 123,
      "orderDateCreated": "string",
      "billingDocumentNumber": 12345678000199,
      "total": 500.00,
      "orders": [
        {
          "idOrder": 1,
          "orderNumber": 1001,
          "orderType": 1,
          "contractNumber": 100,
          "status": "string",
          "orderDate": "2026-12-31",
          "availabilityDate": "string",
          "paymentMethod": "string",
          "paymentDate": "string",
          "totalOrder": 500.00,
          "feesAmount": 10.00,
          "countBeneficiaries": 5,
          "countCard": 5,
          "trackingStatus": "string",
          "steps": [{ "label": "", "status": "", "completed": true, "date": "" }],
          "warnings": [],
          "productInfo": { "productCode": "", "productName": "", "benefits": [] }
        }
      ]
    }
  ],
  "pageable": { "page": 0, "size": 10 },
  "total": 50
}
```

**Erros:** 204, 403

---

#### `POST /orders`
Cria um novo pedido.

**Body:**
```json
{
  "contractNumber": 100,
  "orderType": "string",
  "paymentMethod": "string",
  "availabilityDate": "yyyy-mm-dd",
  "isImmediateAvailability": false,
  "beneficiaries": [
    {
      "beneficiaryId": "string",
      "balances": [
        { "benefitCode": "string", "value": 100.00 }
      ]
    }
  ]
}
```

**Response 200:**
```json
{
  "orderNumberGroup": 123,
  "orders": [
    {
      "id": 1,
      "orderNumber": 1001,
      "orderNumberGroup": 123,
      "contractNumber": 100,
      "status": "string",
      "paymentMethod": "string",
      "paymentType": "string",
      "billingDocumentNumber": "string",
      "idLegalPersonBilling": 1,
      "providerId": 1
    }
  ]
}
```

**Erros:** 403, 422

---

#### `GET /orders/{orderNumber}`
Detalhes de um pedido específico.

**Response 200:** `OrderDetailsResponse` — inclui todos os campos de `OrderResponse` mais:
- `billings` (taxas detalhadas)
- `invoiceDetail` (endereço da nota fiscal)
- `responsibleName` / `responsibleDocumentNumber`
- `loadDate`, `paymentDate`
- `orderChargebackFeeStatus`

**Erros:** 403, 422

---

#### `GET /orders/{orderNumber}/beneficiaries`
Lista os colaboradores de um pedido específico.

**Response 200:**
```json
{
  "content": [
    {
      "name": "string",
      "documentNumber": "CPF",
      "amount": 100.00,
      "placeType": "string",
      "placeName": "string",
      "address": { ... },
      "homeAddress": { ... },
      "benefits": [
        { "benefitName": "", "creditedValue": 50.00, "externalCode": "", "idProductCategory": 1 }
      ],
      "reasonCode": 1,
      "reasonName": "string"
    }
  ],
  "pageable": { ... },
  "total": 5
}
```

**Erros:** 403, 422

---

#### `GET /orders/{orderNumber}/bank-ticket`
Retorna o boleto em Base64.

**Response 200:**
```json
{
  "content": "base64...",
  "fileName": "boleto.pdf"
}
```

**Erros:** 403, 422

---

#### `GET /orders/{orderNumber}/invoice`
Retorna o link para download da nota fiscal.

**Response 200:**
```json
{ "rpsLink": "https://..." }
```

**Erros:** 403, 422

---

#### `POST /orders/{orderNumber}/cancel`
Cancela um pedido.

**Body:**
```json
{ "reason": "Motivo do cancelamento" }
```

**Response:** 204 No Content | 403 | 422

---

#### `POST /simulate-order`
Simula a criação de um pedido (calcula taxas e totais sem confirmar).

**Body:**
```json
{
  "contractNumber": "string",
  "orderType": "string",
  "beneficiaries": [
    { "documentNumber": "CPF", "deliveryType": "string", "benefits": [1, 2] }
  ],
  "products": [
    { "code": 700, "total": 500.00 }
  ]
}
```

**Response 200:** Retorna `providers` com taxas, contagem de cartões e opções de pagamento.

**Erros:** 403

---

### 5. Places — Locais de Entrega

#### `GET /places`
Lista os locais de entrega de uma empresa.

**Query params:**
| Param | Tipo | Descrição |
|---|---|---|
| `placeType` | string | `BRANCH` ou `WORKPLACE` |
| `page` | integer | Número da página |
| `status` | boolean | Ativo/inativo |

**Response 200:** Array de `PlaceResponse`:
```json
{
  "content": [
    {
      "id": "string",
      "name": "string",
      "placeCode": "string",
      "placeType": "BRANCH | WORKPLACE",
      "placeDocumentNumber": "CNPJ",
      "billingDocumentNumber": "CNPJ de faturamento",
      "street": "", "numberHouse": "", "placeComplement": "",
      "placeZipCode": "", "cityName": "", "state": "",
      "status": true,
      "mainPlace": false
    }
  ],
  "pageable": { ... },
  "total": 10
}
```

**Erros:** 204, 403

---

### 6. Products — Produtos

#### `GET /products`
Lista os produtos vinculados às empresas do interlocutor.

**Response 200:**
```json
{
  "content": [
    {
      "contractId": 1,
      "contractNumber": 100,
      "productCode": 700,
      "productName": "string"
    }
  ],
  "pageable": { ... },
  "total": 3
}
```

**Erros:** 204, 403

---

### 7. Profile — Perfil do Usuário

#### `GET /profile`
Retorna os dados do responsável/interlocutor logado.

**Response 200:**
```json
{
  "idResponsible": 1,
  "documentNumber": "CPF",
  "name": "string",
  "email": "string",
  "brithDate": "1980-12-31",
  "nameDepartment": "string",
  "primaryPhone": {
    "areaCode": "11",
    "phoneNumber": "999999999",
    "type": 1
  },
  "functions": [
    { "functionType": "DECISAO | GERENCIAMENTO | OPERACAO | FINANCEIRO", "responsibleProfileId": 1 }
  ]
}
```

> **Atenção:** O campo `functions[].functionType` é a fonte de verdade para o perfil do usuário — usar para guardrails do bot.

**Erros:** 204

---

### 8. Tracking — Rastreio de Cartões

#### `GET /tracking`
Lista todos os pedidos em rastreio da empresa.

**Query params:** `page`, `size`

**Response 200:**
```json
{
  "content": [
    {
      "orderNumber": "string",
      "orderDate": "string",
      "orderType": "string",
      "contractNumber": "string",
      "contractCardType": "string",
      "deliveryType": "string",
      "emittedCards": 5,
      "numberOfTrackingCodes": 5,
      "statusLabel": "string",
      "statusType": "string",
      "trackingOrderStatus": "string",
      "productInfo": { "productCode": "", "productName": "" }
    }
  ],
  "pageable": { "page": 0, "size": 10 },
  "total": 20
}
```

**Erros:** 400, 403, 422

---

#### `GET /orders/{orderNumber}/tracking`
Rastreio dos cartões de um pedido específico.

**Response 200:**
```json
{
  "content": [
    {
      "arMaster": "código AR",
      "address": "string",
      "currentTrackingStatus": "string",
      "deliveryDate": "string",
      "deliveryResponsible": ["string"],
      "events": [
        { "date": "", "description": "", "detail": "", "eventType": 1, "status": "" }
      ],
      "steps": [
        { "label": "", "status": "", "statusLabel": "", "statusType": "", "completed": true, "date": "" }
      ]
    }
  ],
  "pageable": { ... },
  "total": 5
}
```

**Erros:** 400, 403, 422

---

#### `GET /orders/{orderNumber}/tracking/{arNumber}/detail`
Detalhes de um AR (aviso de recebimento) específico.

**Response 200:**
```json
{
  "content": [
    {
      "arNumber": "string",
      "status": "string",
      "statusLabel": "string",
      "statusType": "string",
      "statusOccurredAt": "string",
      "address": { "street": "", "number": "", "complement": "", "neighborhood": "", "city": "", "state": "", "zipcode": "" },
      "beneficiaries": [
        { "documentNumber": "CPF", "name": "string" }
      ]
    }
  ],
  "pageable": { ... },
  "total": 1
}
```

**Erros:** 400, 403, 422

---

### 9. Availability Dates for Credit

#### `GET /availability-dates-for-credit`
Consulta os dias disponíveis para crédito dos valores do pedido.

**Response 200:**
```json
{
  "minDate": "yyyy-mm-dd",
  "maxDate": "yyyy-mm-dd",
  "holidaysList": ["yyyy-mm-dd", "yyyy-mm-dd"]
}
```

**Erros:** 403

---

## Mapa de Métodos por Recurso

| Recurso | GET | POST | PUT | DELETE |
|---|---|---|---|---|
| `/beneficiaries` | ✅ Lista | ✅ Cadastra | — | — |
| `/beneficiaries/{id}` | — | — | ✅ Atualiza | ✅ Exclui |
| `/benefits` | ✅ Lista | — | — | — |
| `/companies` | ✅ Lista | — | — | — |
| `/default-company` | — | — | ✅ Define padrão | — |
| `/orders` | ✅ Lista | ✅ Cria | — | — |
| `/orders/{n}` | ✅ Detalhe | — | — | — |
| `/orders/{n}/beneficiaries` | ✅ Lista | — | — | — |
| `/orders/{n}/bank-ticket` | ✅ Boleto (base64) | — | — | — |
| `/orders/{n}/invoice` | ✅ Link NF | — | — | — |
| `/orders/{n}/cancel` | — | ✅ Cancela | — | — |
| `/orders/{n}/tracking` | ✅ Rastreio | — | — | — |
| `/orders/{n}/tracking/{ar}/detail` | ✅ Detalhe AR | — | — | — |
| `/simulate-order` | — | ✅ Simula | — | — |
| `/places` | ✅ Lista | — | — | — |
| `/products` | ✅ Lista | — | — | — |
| `/profile` | ✅ Perfil | — | — | — |
| `/tracking` | ✅ Lista geral | — | — | — |
| `/availability-dates-for-credit` | ✅ Datas | — | — | — |

---

## Descobertas Relevantes para o Bot

### 1. A API não é somente leitura
Ao contrário do levantado anteriormente, a API possui operações de **escrita**:
- Criar pedidos (`POST /orders`)
- Cancelar pedidos (`POST /orders/{n}/cancel`)
- Simular pedidos (`POST /simulate-order`)
- Cadastrar, atualizar e excluir colaboradores
- Definir empresa padrão

O bot precisa ter **guardrails explícitos** para definir quais dessas ações ele pode ou não iniciar.

### 2. Perfil do usuário via `GET /profile`
O campo `functions[].functionType` retorna o perfil real do interlocutor (`DECISAO`, `GERENCIAMENTO`, `OPERACAO`, `FINANCEIRO`). É a fonte que o bot deve usar para aplicar as restrições de acesso.

### 3. Identificação do usuário pelo gateway
O CPF do interlocutor (`x-document-number`) é extraído automaticamente do JWT pelo gateway Sensedia — o bot não precisa enviá-lo manualmente, apenas o `Authorization: Bearer <token>`.

### 4. `GET /companies` como ponto de entrada
Para saber a qual empresa o usuário pertence e quais contratos existem, o bot deve chamar `/companies` logo após obter o perfil.
