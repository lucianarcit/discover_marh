# 04 — Catálogo de Intenções: Agente Consultivo MARH

> **Princípio:** Este documento cataloga todas as perguntas, exemplos e intenções extraídas diretamente do documento do cliente (`docs\cliente\00_Agente_Consultivo_MARH.html`), sem adicionar intenções deduzidas ou hipotéticas. Cada item é rastreado à seção de origem.

---

## Legenda de tipo de intenção

| Tipo | Descrição |
|---|---|
| CONSULTIVA | Usuário deseja consultar dados da empresa selecionada via ma-hr-orch |
| INFORMATIVA_MARH | Usuário pergunta sobre o que o agente faz, como funciona ou quais são suas limitações |
| FORA_DO_ESCOPO | Usuário pede algo que o agente não pode fazer (ação transacional) |

---

## Grupo A — Intenções Consultivas (dados em tempo real)

Estas intenções exigem chamada à `ma-hr-orch`. Fontes: Seções 7.1, 8.1, 8.2, 8.3, 8.4, 8.5 e 10.

### A1 — Consultar colaborador por nome

| Campo | Valor |
|---|---|
| **INT ID** | INT-001 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Gestão de Colaboradores |
| **Descrição** | Usuário quer consultar dados de um colaborador buscando pelo nome |
| **Exemplos do cliente** | "Consultar colaborador Wesley Fabrete." (Seções 7.1, 8.1, 10) |
| **Variações implícitas** | "Me mostra os dados do colaborador João Silva." / "Quem é João Silva?" |
| **Dados necessários do usuário** | Nome completo ou parcial do colaborador |
| **Endpoint necessário** | `GET /v1/beneficiaries?nameOrCpf={nome}` |
| **Comportamento esperado** | Buscar na empresa selecionada; exibir dados disponíveis; se múltiplos, pedir escolha; se não encontrar, informar. Após consulta bem-sucedida, mesmo com escolha de colaborador específico, a navegação aponta para `#/employees` — não há deeplink individual disponível. |
| **Múltiplos resultados** | Solicitar que o usuário escolha. Mesmo após a escolha, permanecer em `#/employees` — deeplink individual não é suportado (DP-003-A). |
| **Resposta de fallback** | ERR-002 — "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." |
| **Navegação** | `#/employees` (ROUTE-003) — única rota segura. `#/employees/:id/edit` não é deeplink-safe (DP-003-A: depende de `location.state`, não há endpoint de detalhe por id). |
| **Proibido** | Montar `#/employees/{id}/edit`. Expor `beneficiaryId`. Tentar preencher `location.state`. Inventar deeplink de detalhe. |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html`; Resposta técnica 2026-07-23 |
| **Seção do cliente** | 8.1 e 10 |
| **Prioridade MVP** | MUST |

### A2 — Consultar colaborador por CPF

| Campo | Valor |
|---|---|
| **INT ID** | INT-002 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Gestão de Colaboradores |
| **Descrição** | Usuário quer consultar dados de um colaborador buscando pelo CPF |
| **Exemplos do cliente** | "Rastrear cartão do colaborador 123.456.789-00." (Seção 7.1 — implica consulta prévia por CPF) |
| **Variações implícitas** | "Consulta o colaborador 123.456.789-00." |
| **Dados necessários do usuário** | CPF do colaborador |
| **Endpoint necessário** | `GET /v1/beneficiaries?nameOrCpf={cpf}` |
| **Comportamento esperado** | Buscar na empresa selecionada; exibir dados disponíveis; se não encontrar, informar. Navegação disponível para `#/employees` — não há deeplink individual. |
| **Múltiplos resultados** | Solicitar que o usuário escolha. Mesmo após a escolha, permanecer em `#/employees`. |
| **Resposta de fallback** | ERR-002 — "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." |
| **Navegação** | `#/employees` (ROUTE-003) — única rota segura. Deeplink individual não suportado (DP-003-A). |
| **Proibido** | Montar `#/employees/{id}/edit`. Expor `beneficiaryId`. Inventar deeplink de detalhe. |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html`; Resposta técnica 2026-07-23 |
| **Seção do cliente** | 8.1 (implícito em 8.5) |
| **Prioridade MVP** | MUST |

### A3 — Consultar pedido por número

| Campo | Valor |
|---|---|
| **INT ID** | INT-003 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Gestão de Pedidos |
| **Descrição** | Usuário quer consultar os detalhes de um pedido específico pelo número |
| **Exemplos do cliente** | "Consultar pedido 342671." (Seções 7.1, 8.2, 10) |
| **Variações implícitas** | "Qual o status do pedido 342671?" / "Me mostra o pedido 342671." |
| **Dados necessários do usuário** | Número do pedido (`orderNumber`) |
| **Endpoint necessário** | `GET /v1/orders/{orderNumber}` |
| **Comportamento esperado** | Exibir status (label português do `order_status_catalog.json`), data, produto, valor, qtd. colaboradores, cartões e etapas quando disponíveis. Não permitir ações. |
| **Campos a exibir** | status (label PT-BR), orderDate, productInfo, totalOrder, qtd. colaboradores, qtd. cartões, steps[] |
| **Resposta de fallback** | ERR-003 — "Não encontrei o pedido informado para a empresa selecionada." |
| **Parâmetro de rota** | Usar **`orderNumber`** — nunca `idOrder`. Os dois coexistem no objeto do pedido mas são identificadores distintos. |
| **Navegação primária** | `#/order-detail/{orderNumber}` (ROUTE-014) — parâmetro no PATH |
| **Navegação auxiliar** | `#/order-detail/{orderNumber}/beneficiaries` (ROUTE-015) quando a resposta incluir colaboradores do pedido |
| **Navegação solicitação** | `#/order-request-group?orderNumber={orderNumber}` (ROUTE-013-V2) quando o contexto for a solicitação agrupadora |
| **Decisão padrão pendente** | Qual tela deve ser o botão padrão: ROUTE-014 ou ROUTE-013-V2? → DP-003-B (pendente confirmação de produto). Usar ROUTE-014 na POC. |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html`; Resposta técnica 2026-07-23 |
| **Seção do cliente** | 8.2 e 10 |
| **Prioridade MVP** | MUST |

### A4 — Consultar último pedido

| Campo | Valor |
|---|---|
| **INT ID** | INT-004 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Gestão de Pedidos |
| **Descrição** | Usuário quer saber qual foi o último pedido da empresa selecionada |
| **Exemplos do cliente** | "Qual foi o último pedido?" (Seções 7.1, 8.3, 10) |
| **Variações implícitas** | "Qual o pedido mais recente?" / "Mostra o último pedido feito." |
| **Dados necessários do usuário** | Nenhum (usa empresa do contexto) |
| **Endpoint necessário** | `GET /v1/orders` (primeiro resultado da paginação ou ordenado por data) |
| **Comportamento esperado** | Retornar pedido mais recente disponível; se ordenação incerta, avisar sobre isso |
| **Aviso obrigatório** | "Se não houver ordenação confiável nos dados, informar que está exibindo o pedido mais recente retornado pela consulta." |
| **Resposta de fallback** | ERR-007 genérico se indisponível |
| **Parâmetro de rota** | `orderNumber` do primeiro item retornado pela API — nunca `idOrder`. |
| **Navegação** | `#/order-detail/{orderNumber}` (ROUTE-014) quando `orderNumber` disponível via API; fallback: `#/orders` (ROUTE-012) |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html`; Resposta técnica 2026-07-23 |
| **Seção do cliente** | 8.3 e 10 |
| **Prioridade MVP** | MUST |

### A5 — Consultar pedidos por status

| Campo | Valor |
|---|---|
| **INT ID** | INT-005 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Gestão de Pedidos |
| **Descrição** | Usuário quer listar pedidos filtrando por um status específico |
| **Exemplos do cliente** | "Quais são os últimos pedidos com status pago?" (Seções 7.1, 8.4, 10) |
| **Variações aceitas pelo cliente** | "Quais são os últimos pedidos pendentes?" / "Mostre os últimos pedidos cancelados." / "Quais pedidos estão em processamento?" |
| **Dados necessários do usuário** | Status desejado (pago, pendente, cancelado, em processamento etc.) |
| **Endpoint necessário** | `GET /v1/orders` + filtro de status no agente |
| **Comportamento esperado** | Identificar o status; listar pedidos; se status não reconhecido, pedir esclarecimento; se não houver pedidos, responder amigavelmente |
| **Status reconhecidos pela API** | IN_PROCESSING, PENDING, PAID, CREDITED, CANCELLED, REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED |
| **Resposta de fallback** | ERR-004 — "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." |
| **Navegação** | `#/orders` (ROUTE-012) — lista de pedidos, sem parâmetro |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html` |
| **Seção do cliente** | 8.4 e 10 |
| **Prioridade MVP** | MUST |

### A6 — Rastrear cartão por CPF do colaborador

| Campo | Valor |
|---|---|
| **INT ID** | INT-006 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Rastreamento de Cartões |
| **Descrição** | Usuário solicita o rastreamento do cartão de um colaborador informando o CPF |
| **Exemplos do cliente** | "Rastrear cartão do colaborador 123.456.789-00." (Seções 7.1, 8.5, 10) |
| **Dados necessários do usuário** | CPF do colaborador |
| **Endpoint necessário** | Endpoint de rastreamento por CPF via ma-hr-orch — **NÃO CONFIRMADO** (TEC-027, AMB-001) |
| **Comportamento esperado (fallback confirmado)** | Solicitar número do pedido ao usuário para continuar o rastreamento |
| **Resposta obrigatória de fallback** | "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." |
| **Status** | AMBIGUOUS — depende de validação técnica com o time |
| **Navegação (fallback informativo)** | `#/card-tracking` (ROUTE-024) — rota frontend CONFIRMADA; backend NOT_VALIDATED |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html` |
| **Separação rota/API** | Existência da rota de frontend NÃO confirma endpoint de backend (LAC-002, DP-002 permanecem abertos) |
| **Seção do cliente** | 8.5 e 10 |
| **Prioridade MVP** | MUST (com fallback) |

### A7 — Rastrear cartão por número do pedido

| Campo | Valor |
|---|---|
| **INT ID** | INT-007 |
| **Tipo** | CONSULTIVA |
| **Grupo** | Rastreamento de Cartões |
| **Descrição** | Usuário solicita o rastreamento do cartão informando o número do pedido (caminho confirmado) |
| **Exemplos do cliente** | Resposta esperada na seção 8.5 usa pedido 342671 como exemplo |
| **Dados necessários do usuário** | Número do pedido |
| **Endpoint necessário** | Endpoint de rastreamento por orderNumber via ma-hr-orch |
| **Comportamento esperado** | Exibir status, data da última atualização, código de rastreio. Não inventar prazo, transportadora ou status. |
| **Campos a exibir** | status, data última atualização, endereço de entrega, código de rastreio |
| **Resposta de fallback** | ERR-007 se indisponível |
| **Status** | CONFIRMED (única rota confirmada para rastreamento) |
| **Navegação** | `#/card-tracking/:orderNumber` (ROUTE-025); com arNumber: `#/card-tracking/:orderNumber/:arNumber` (ROUTE-026); fallback: `#/card-tracking` (ROUTE-024) |
| **navigation_source** | `docs/cliente/Rotas_hr_space.html` |
| **frontend_route_status** | CONFIRMED |
| **backend_api_status** | NOT_VALIDATED (LAC-001, DP-001 permanecem abertos) |
| **Seção do cliente** | 8.5 |
| **Prioridade MVP** | MUST |

---

## Grupo B — Intenções Informativas sobre a feature MARH

Estas intenções não exigem chamada à `ma-hr-orch` — são respondidas via markdown de conhecimento. Fontes: Seções 6, 7.2 e 10.

| INT ID | Pergunta do cliente | Origem | Prioridade |
|---|---|---|---|
| INT-008 | "O que posso fazer?" | Seções 6 e 7.2 | MUST |
| INT-009 | "Quais informações posso consultar?" | Seção 6 | MUST |
| INT-010 | "Como faço para fazer um pedido?" | Seções 6 e 7.2 | MUST |
| INT-011 | "Como faço para consultar um pedido?" | Seção 6 | MUST |
| INT-012 | "Como faço para consultar um colaborador?" | Seções 6 e 10 | MUST |
| INT-013 | "Consigo rastrear cartões?" | Seções 6 e 10 | MUST |
| INT-014 | "Você consegue cancelar pedido?" | Seções 6, 7.2 e 10 | MUST |
| INT-015 | "Você consegue alterar dados de um colaborador?" | Seções 6 e 7.2 | MUST |
| INT-016 | "Você consulta dados de qualquer empresa?" | Seções 6 e 7.2 | MUST |
| INT-017 | "Preciso selecionar uma empresa para usar o agente?" | Seção 6 | MUST |
| INT-018 | "O agente substitui o portal web?" | Seção 6 | MUST |
| INT-019 | "O que é o MARH?" | Seção 6 | MUST |
| INT-020 | "O que é o Espaço RH?" | Seção 6 | MUST |
| INT-021 | "Quais tipos de pergunta posso fazer?" | Seções 6 e 7.2 / "Quais perguntas posso fazer?" | MUST |

---

## Grupo C — Intenções Fora do Escopo

Estas intenções recebem redirecionamento para o Espaço RH. Fontes: Seções 7.3 e 12.

| INT ID | Exemplo do cliente | Ação proibida | Origem |
|---|---|---|---|
| INT-022 | "Cancela o pedido 342671." | Cancelar pedido (FORA-002) | Seção 7.3 |
| INT-023 | "Altera o endereço do colaborador." | Alterar endereço de entrega (FORA-006) | Seção 7.3 |
| INT-024 | "Cria um novo pedido." | Criar pedido (FORA-001) | Seção 7.3 |
| INT-025 | "Remove esse colaborador." | Excluir colaborador (FORA-005) | Seção 7.3 |
| INT-026 | "Paga o pedido." | Realizar pagamento (FORA-010) | Seção 7.3 |
| INT-027 | "Emite um novo cartão." | Solicitar segunda via / reemitir (FORA-007, FORA-008) | Seção 7.3 |

**Resposta esperada para todas:** "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH."

---

## Resumo do catálogo

| Grupo | Tipo | Qtd | Exemplos principais |
|---|---|---|---|
| A | CONSULTIVA | 7 (INT-001 a INT-007) | Colaborador por nome/CPF, pedido por número, último pedido, pedidos por status, rastreamento por CPF/pedido |
| B | INFORMATIVA_MARH | 14 (INT-008 a INT-021) | O que posso fazer?, Quais perguntas posso fazer?, O que é MARH? |
| C | FORA_DO_ESCOPO | 6 (INT-022 a INT-027) | Cancelar pedido, alterar endereço, criar pedido, excluir colaborador, pagar, emitir cartão |
| **Total** | | **27** | |

---

## Observações

1. **INT-006 (rastreamento por CPF)** é marcada AMBIGUOUS porque o endpoint via ma-hr-orch não foi confirmado. O comportamento de fallback (pedir número do pedido) é a única rota CONFIRMED para a POC.
2. **INT-007 (rastreamento por número do pedido)** é a rota confirmada e obrigatória para rastreamento.
3. As intenções do Grupo B são respondidas exclusivamente pelo markdown de conhecimento — o agente não deve chamar a `ma-hr-orch` para essas perguntas.
4. As intenções do Grupo C não devem ser executadas. O agente deve apenas orientar o usuário a acessar o Espaço RH.

---

## Navegação por intenção — resumo

> **Fonte:** `docs/cliente/Rotas_hr_space.html` (CLIENT_NAVIGATION_CONTRACT, 2026-07-21)
>
> A existência de uma rota de frontend **não comprova** endpoint de backend. Rotas e APIs são conceitos separados.

| INT ID | Rota de navegação | Requer parâmetro | Parâmetro | Status da rota |
|---|---|---|---|---|
| INT-001 | `#/employees` | Não | — | CONFIRMED |
| INT-002 | `#/employees` | Não | — | CONFIRMED |
| INT-003 | `#/order-detail/{orderNumber}` | Sim | orderNumber (usuário) — nunca idOrder | CONFIRMED |
| INT-003 | `#/order-detail/{orderNumber}/beneficiaries` | Sim | orderNumber (usuário) | CONFIRMED |
| INT-003 | `#/order-request-group?orderNumber={...}` | Sim | orderNumber (API) — contexto de solicitação agrupadora | CONFIRMED (decisão padrão pendente — DP-003-B) |
| INT-004 | `#/order-detail/{orderNumber}` (se disponível via API) | Sim | orderNumber (API) — nunca idOrder | CONFIRMED |
| INT-004 | `#/orders` (fallback) | Não | — | CONFIRMED |
| INT-005 | `#/orders` | Não | — | CONFIRMED |
| INT-006 | `#/card-tracking` (fallback informativo) | Não | — | CONFIRMED (frontend); backend NOT_VALIDATED |
| INT-007 | `#/card-tracking/:orderNumber` | Sim | orderNumber (usuário) | CONFIRMED (frontend); backend NOT_VALIDATED |
| INT-007 | `#/card-tracking/:orderNumber/:arNumber` | Sim | orderNumber + arNumber (API) | CONFIRMED (frontend); backend NOT_VALIDATED |
| INT-010 | `#/new-order/products` (redirect apenas) | Não | — | CONFIRMED |
| INT-024 | `#/new-order/products` (redirect apenas) | Não | — | CONFIRMED |

**Rota de colaborador individual (DP-003-A):** `#/employees/:id/edit` — **NÃO SUPORTADA COMO DEEPLINK**. A tela depende de `location.state` e não existe endpoint de detalhe por id. Nenhuma resposta do agente deve referenciar esta rota. Usar `#/employees`. Feature futura necessária.

**Regra `orderNumber` vs. `idOrder`:** Os dois campos coexistem no objeto de pedido mas são identificadores distintos. Sempre usar `orderNumber` nas rotas. `idOrder` é proibido em path, query string e deeplink.

**Status de pedido:** Labels de exibição ao usuário definidos em `discover3/artifacts/order_status_catalog.json`. Não usar valores canônicos da API diretamente ao usuário.

---

*Fontes: `docs\cliente\00_Agente_Consultivo_MARH.html` (seções 6, 7.1, 7.2, 7.3, 8.1–8.5, 10) · `docs/cliente/Rotas_hr_space.html` (navegação) · Resposta técnica 2026-07-23 (Leandro → Marcelo Gorzoni da Silva) · Atualizado em 2026-07-23*
