# Avaliação de Consumo pelo Modelo de IA — Gestão de Pedidos

**Gerado em:** 2026-07-22
**APIs analisadas:** 8 GET

---

## Matriz Consolidada

| API | Intenção possível | Dados úteis | Dados sensíveis | Estratégia | Recomendação |
|-----|------------------|-------------|-----------------|-----------|--------------|
| Consulta de Pedidos | Listar pedidos, ver status | status, valor, data, produto | documentNumber, CNPJ billing | Tool call + sanitização | APTO_SOMENTE_COM_TOOL_CALL |
| Consulta dos Produtos | Ver produtos disponíveis | nome, código, descrição | — | RAG ou tool call | APTO_PARA_MODELO |
| Consulta dos Benefícios | Ver benefícios e regras | nomes, códigos, regras | — | RAG ou tool call | APTO_PARA_MODELO |
| Dias para Crédito | Consultar datas de crédito | minDate, maxDate, feriados | — | Tool call | APTO_PARA_MODELO |
| Nota Fiscal | Baixar NF | link da NF | CNPJ na URL | Tool call | APTO_COM_SANITIZACAO |
| Colaboradores do Pedido | Ver quem está no pedido | nome, benefícios, valor | CPF, endereço | Tool call + sanitização | APTO_SOMENTE_COM_TOOL_CALL |
| Detalhes do Pedido | Ver detalhes do pedido | status, valores, datas | contractNumber | Tool call | APTO_SOMENTE_COM_TOOL_CALL |
| Boleto | Ver/baixar boleto | fileName, barCodeLine | conteúdo base64 | Tool call | APTO_SOMENTE_COM_TOOL_CALL |

---

## Avaliação Detalhada

### 1. Consulta de Pedidos (`/v1/orders`)

1. **Finalidade:** Listar pedidos com status, valores e tracking
2. **Dados de entrada:** page, size (paginação)
3. **Dados retornados:** Lista de pedidos com status, valores, datas, produto, histórico
4. **Campos úteis para o modelo:** `status`, `totalOrder`, `orderDate`, `paymentMethod`, `steps`, `productInfo.productName`
5. **Campos que NÃO devem ir ao modelo:** `billingDocumentNumber`, `contractNumber`, `idLegalPersonBilling`
6. **Dados pessoais/sensíveis:** CNPJ da empresa (billingDocumentNumber)
7. **Necessidade de anonimização:** Sim — remover CNPJ e IDs internos
8. **Intenções de usuário atendidas:** "Quais meus pedidos?", "Status do pedido?", "Quanto devo?"
9. **Determinística e factual:** Sim
10. **Requer consulta em tempo real:** Sim
11. **RAG candidate:** Não (dados mudam frequentemente)
12. **Tool call candidate:** Sim
13. **Recomendação:** `APTO_SOMENTE_COM_TOOL_CALL`

### 2. Consulta dos Produtos (`/v1/products`)

1. **Finalidade:** Catálogo de produtos disponíveis
2. **Dados de entrada:** Nenhum
3. **Dados retornados:** Lista de produtos com código e nome
4. **Campos úteis:** Todos (catálogo público)
5. **Campos restritos:** Nenhum
6. **PII:** Não contém
7. **Intenções:** "Quais produtos posso pedir?", "O que é Alelo Pod?"
8. **Determinística:** Sim (catálogo estável)
9. **RAG candidate:** Sim (muda raramente)
10. **Tool call candidate:** Sim
11. **Recomendação:** `APTO_PARA_MODELO`

### 3. Consulta dos Benefícios (`/v1/benefits`)

1. **Finalidade:** Listar benefícios e regras de pedido
2. **Dados retornados:** `benefits[]` (nome, código) + `orderRules`
3. **Campos úteis:** Todos
4. **PII:** Não contém
5. **Intenções:** "Quais benefícios posso incluir?", "Quais as regras?"
6. **RAG candidate:** Sim
7. **Recomendação:** `APTO_PARA_MODELO`

### 4. Dias para Crédito (`/v1/availability-dates-for-credit`)

1. **Finalidade:** Datas disponíveis para disponibilização de crédito
2. **Dados retornados:** `minDate`, `maxDate`, `holidaysList`
3. **PII:** Não contém
4. **Intenções:** "Quando posso agendar o crédito?", "Quais feriados?"
5. **Requer tempo real:** Sim (datas mudam)
6. **Recomendação:** `APTO_PARA_MODELO`

### 5. Download da Nota Fiscal (`/v1/orders/{id}/invoice`)

1. **Finalidade:** Obter link da NF
2. **Dados retornados:** `rpsLink` (URL da prefeitura)
3. **Campos sensíveis:** CNPJ embutido na URL
4. **Intenções:** "Preciso da nota fiscal do pedido X"
5. **Recomendação:** `APTO_COM_SANITIZACAO`

### 6. Colaboradores do Pedido (`/v1/orders/{id}/beneficiaries`)

1. **Finalidade:** Ver colaboradores incluídos em um pedido
2. **Dados retornados:** nome, CPF, endereço, benefícios, valores
3. **PII:** CPF (`documentNumber`), endereço completo
4. **Necessidade de sanitização:** Alta
5. **Intenções:** "Quem está no pedido X?", "Quanto cada um vai receber?"
6. **Recomendação:** `APTO_SOMENTE_COM_TOOL_CALL`

### 7. Detalhes do Pedido (`/v1/orders/{id}`)

1. **Finalidade:** Informações completas de um pedido
2. **Dados retornados:** orderNumber, status, valores, datas, tracking
3. **Campos sensíveis:** `contractNumber`
4. **Intenções:** "Detalhes do pedido X", "Qual o status?"
5. **Recomendação:** `APTO_SOMENTE_COM_TOOL_CALL`

### 8. Boleto (`/v1/orders/{id}/bank-ticket`)

1. **Finalidade:** Obter boleto para pagamento
2. **Dados retornados:** `fileName`, `content` (base64 do PDF), `barCodeLine`
3. **Campos sensíveis:** conteúdo do boleto (valores, CNPJ)
4. **Intenções:** "Preciso do boleto do pedido X", "Qual a linha digitável?"
5. **Recomendação:** `APTO_SOMENTE_COM_TOOL_CALL`

---

## Resumo de Recomendações

| Recomendação | APIs |
|-------------|------|
| `APTO_PARA_MODELO` | products, benefits, availability-dates-for-credit |
| `APTO_COM_SANITIZACAO` | invoice |
| `APTO_SOMENTE_COM_TOOL_CALL` | orders, orders/{id}, orders/{id}/beneficiaries, bank-ticket |
