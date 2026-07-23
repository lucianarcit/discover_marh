# 15 — Decisões Pendentes do Cliente

> **Princípio:** Este documento lista exclusivamente as decisões que dependem do cliente, do time técnico da Alelo ou de validações que bloqueiam o avanço do projeto. Não são recomendações técnicas internas — são perguntas abertas que precisam de resposta antes de prosseguir com a implementação dos itens afetados.

---

## Legenda de impacto

| Impacto | Descrição |
|---|---|
| BLOQUEADOR_MVP | A POC não pode ser entregue sem esta decisão |
| BLOQUEADOR_PILOTO | O piloto não pode ser iniciado sem esta decisão |
| BLOQUEADOR_PRODUCAO | Necessário antes do go-live |
| MELHORIA | Não bloqueia — melhora qualidade ou experiência |

## Legenda de responsável

| Responsável | Descrição |
|---|---|
| CLIENTE | Decisão de negócio — apenas o cliente pode decidir |
| MA_HR_ORCH | Decisão técnica — time responsável pela ma-hr-orch |
| FRONTEND | Decisão de frontend/mobile |
| ARQUITETURA | Decisão de arquitetura de sistema (envolve múltiplos times) |

---

## DP-001 — Endpoint de rastreamento de cartão por orderNumber

| Campo | Valor |
|---|---|
| **ID** | DP-001 |
| **Impacto** | BLOQUEADOR_MVP (para rastreamento real) |
| **Responsável** | MA_HR_ORCH |
| **Origem** | LAC-001, TEC-027, RF-015 |
| **Pergunta** | A ma-hr-orch possui (ou pode disponibilizar) um endpoint de rastreamento de cartão por número de pedido (`orderNumber`)? |
| **Contexto** | O cliente especifica que o agente deve rastrear cartões "quando houver fonte disponível por meio da ma-hr-orch" (RF-015). Nenhum endpoint de rastreamento foi encontrado no inventário de APIs testado em 2026-07-22. A KB descreve rastreamento no portal web, mas não via API. |
| **O que é necessário** | (a) Confirmação de que o endpoint existe ou pode ser criado; (b) URL, método e schema de request/response; (c) se o campo de endereço de entrega está presente e como será sanitizado (PII). |
| **Impacto se não respondida** | O agente não pode oferecer rastreamento em tempo real. Na POC, o comportamento será: "ainda não consigo rastrear" + ERR-007. |
| **Backlog afetado** | BL-013 (Piloto) |

---

## DP-002 — Endpoint de rastreamento de cartão por CPF do colaborador

| Campo | Valor |
|---|---|
| **ID** | DP-002 |
| **Impacto** | BLOQUEADOR_PILOTO |
| **Responsável** | MA_HR_ORCH |
| **Origem** | LAC-002, AMB-001, RF-016 |
| **Pergunta** | A ma-hr-orch consegue (ou poderá) disponibilizar uma consulta de rastreamento por CPF do colaborador? |
| **Contexto** | O documento do cliente (seção 8.5) indica explicitamente: "Avaliar, junto ao time técnico, se a ma-hr-orch consegue disponibilizar uma consulta de rastreamento por CPF do colaborador." Esta avaliação ainda não foi realizada. |
| **O que é necessário** | Resposta binária: SIM ou NÃO. Se SIM: schema do endpoint. Se NÃO: formalizar que o fallback (solicitar número do pedido) é o comportamento permanente. |
| **Impacto se não respondida** | O agente sempre solicitará o número do pedido ao usuário — pode causar fricção no piloto. |
| **Backlog afetado** | BL-023 (Futuro) |

---

## DP-003 — Camada responsável pela URL final da webview ([list_navigation])

| Campo | Valor |
|---|---|
| **ID** | DP-003 |
| **Impacto** | ~~BLOQUEADOR_PILOTO~~ → **PARTIALLY_RESOLVED** |
| **Responsável** | ARQUITETURA (API MARH + Frontend) |
| **Origem** | LAC-007, AMB-002, RNF-004 |
| **Status** | **PARTIALLY_RESOLVED** — `Rotas_hr_space.html` (2026-07-21) confirmou formato, bases por ambiente, deeplink e parâmetros. |
| **O que foi resolvido** | Formato da URL (`{BASE_URL}/#{ROTA}`); bases HML e PRD; template do deeplink; casing dos parâmetros (`isModal`, `showNavbar`, `authRequired`); rotas autorizadas; responsabilidade de montar o deeplink atribuída ao Agente/Backend; Frontend identifica `[list_navigation]` e abre o deeplink. |
| **O que ainda está em aberto** | Se há camada intermediária (BFF) entre o Agente e o Frontend para casos específicos. Para a POC, o agente monta o deeplink diretamente. |
| **Referência** | `discover3/artifacts/deeplink_routes_catalog.json`; `discover3/agent_policy.md` seção 7 |
| **Backlog afetado** | BL-016 (Piloto — desbloqueado para POC) |

---

## DP-008 — Confirmação de segurança para `#/employees/:id/edit` (NAV-SEC-001)

| Campo | Valor |
|---|---|
| **ID** | DP-008 |
| **Impacto** | MELHORIA (não bloqueia POC) |
| **Responsável** | ARQUITETURA + TIME DE SEGURANÇA |
| **Origem** | NAV-SEC-001, `Rotas_hr_space.html` s.4.3 e s.5 |
| **Pergunta** | O identificador do colaborador (`beneficiaryId` / `:id`) pode ser incluído no deeplink retornado ao frontend pelo agente? |
| **Contexto** | O documento `Rotas_hr_space.html` menciona `#/employees/:id/edit` como opção quando houver identificador disponível. Porém, `beneficiaryId` é campo restrito no contrato da API (TEC-017, TEC-018) — não deve ir ao modelo de linguagem. Incluí-lo no deeplink pode representar exposição de dado restrito ao frontend, ao app e potencialmente ao usuário. |
| **O que é necessário** | Confirmação do time de segurança se `beneficiaryId` pode aparecer no deeplink ou se deve ser substituído por outro identificador não restrito. |
| **Comportamento atual** | Usar `#/employees` (ROUTE-003) enquanto não houver aprovação. Não usar `#/employees/:id/edit`. |
| **Impacto se não respondida** | O agente continua funcionando com `#/employees`. Navegação para colaborador individual não será implementada até resolução. |
| **Backlog afetado** | BL-novo (Piloto — desejável) |

---

## DP-004 — Mapeamento de status de pedido (inglês → português)

| Campo | Valor |
|---|---|
| **ID** | DP-004 |
| **Impacto** | BLOQUEADOR_PILOTO |
| **Responsável** | CLIENTE |
| **Origem** | LAC-008, CF-001, TEC-022, KB-025 |
| **Pergunta** | Quais são os labels em português a serem exibidos ao usuário para cada status retornado pela API? |
| **Contexto** | A API retorna 10 status em inglês. A KB documenta 6 status em português, mas há discrepância — 4 status da API (REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED) não têm correspondência validada na KB. O status "Nota Fiscal Emitida" e "Aguardando Disponibilização" da KB não têm correspondência clara na API. |
| **O que é necessário** | Tabela de mapeamento completa validada pelo cliente: status API → label exibido ao usuário. |
| **Impacto se não respondida** | O agente pode exibir status em inglês ou usar labels incorretos que não correspondem ao que o usuário vê no portal. |
| **Backlog afetado** | BL-014 (Piloto) |

---

## DP-005 — Estratégia de paginação para consulta de pedidos por status

| Campo | Valor |
|---|---|
| **ID** | DP-005 |
| **Impacto** | BLOQUEADOR_PILOTO |
| **Responsável** | ARQUITETURA |
| **Origem** | LAC-004, TEC-002, TEC-003 |
| **Pergunta** | Quantas páginas de pedidos o agente deve consultar ao filtrar por status? Como informar ao usuário se a lista pode estar incompleta? |
| **Contexto** | O endpoint `GET /v1/orders` não tem filtro de status — o filtro deve ser feito pela camada de orquestração sobre os resultados paginados. Para empresas com muitos pedidos, consultar apenas a primeira página pode retornar lista incompleta. |
| **Opções** | (a) Consultar até N páginas (ex.: N=3) e informar ao usuário; (b) Solicitar à ma-hr-orch que implemente filtro server-side; (c) Exibir apenas os mais recentes com aviso de incompletude. |
| **O que é necessário** | Decisão de quantas páginas consultar + texto do aviso ao usuário quando a lista for incompleta. |
| **Impacto se não respondida** | Usuários de empresas com muitos pedidos podem receber lista incompleta sem aviso. |
| **Backlog afetado** | BL-015 (Piloto) |

---

## DP-006 — Confirmação de sanitização de PII na camada ma-hr-orch

| Campo | Valor |
|---|---|
| **ID** | DP-006 |
| **Impacto** | BLOQUEADOR_MVP |
| **Responsável** | MA_HR_ORCH |
| **Origem** | LAC-006, TEC-017, TEC-018, TEC-019, SEG-003 |
| **Pergunta** | A camada ma-hr-orch filtra os seguintes campos antes de retornar ao agente: CPF, email, telefone, nome da mãe, endereço (colaboradores), billingDocumentNumber, contractNumber, idLegalPersonBilling (pedidos), content base64 (boleto)? |
| **Contexto** | Os testes de integração (TEC-017, TEC-019, TEC-011) identificaram campos PII e restritos nas respostas brutas das APIs. A especificação define que esses dados não devem chegar ao modelo de linguagem (SEG-003). Não há evidência de que a sanitização está implementada na ma-hr-orch. |
| **O que é necessário** | Confirmação técnica (com evidência — ex.: log de chamada mostrando que os campos não passam para o agente) de que a sanitização está implementada. |
| **Impacto se não respondida** | PII pode chegar ao modelo de linguagem e ser exposto ao usuário — violação de SEG-003. |
| **Backlog afetado** | BL-019 (Produção), impacta BL-005, BL-006 (MVP) |

---

## DP-007 — Ordenação da consulta de último pedido

| Campo | Valor |
|---|---|
| **ID** | DP-007 |
| **Impacto** | MELHORIA |
| **Responsável** | MA_HR_ORCH |
| **Origem** | LAC-005, TEC-002, TEC-003 |
| **Pergunta** | O endpoint `GET /v1/orders` suporta ordenação por data (`orderDate desc`)? Se não, a ma-hr-orch pode expor um parâmetro de ordenação? |
| **Contexto** | Sem ordenação confirmada, o "último pedido" retornado é o primeiro na paginação padrão, que pode não ser o mais recente cronologicamente. O cliente exige que o agente avise quando a ordenação não for confiável. |
| **O que é necessário** | Confirmação de parâmetro de ordenação (ex.: `sort=orderDate,desc`) ou instrução formal de que o aviso de ordenação incerta é o comportamento permanente. |
| **Impacto se não respondida** | Agente sempre exibe aviso de ordenação incerta — experiência subótima mas funcional. |
| **Backlog afetado** | BL-007 (MVP — mitigado pelo aviso obrigatório) |

---

## DP-008 — Quantidade de cartões por pedido

| Campo | Valor |
|---|---|
| **ID** | DP-008 |
| **Impacto** | MELHORIA |
| **Responsável** | MA_HR_ORCH |
| **Origem** | LAC-009, CF-003, RF-012 |
| **Pergunta** | O campo `total` do endpoint `GET /v1/orders/{orderNumber}/beneficiaries` corresponde à quantidade de cartões do pedido? Há diferença entre quantidade de colaboradores e quantidade de cartões? |
| **Contexto** | A especificação define que o agente deve exibir "quantidade de colaboradores e cartões quando disponíveis". O endpoint de detalhe do pedido não tem esses campos diretamente — seria necessário uma chamada extra a `/beneficiaries`. Em cenários de 2ª via, um colaborador pode ter mais de um cartão ativo. |
| **O que é necessário** | Confirmação de qual campo/endpoint retorna a quantidade correta de cartões por pedido. |
| **Impacto se não respondida** | Agente pode omitir a quantidade ou exibir dado impreciso. O campo "cartões" será omitido até confirmação. |
| **Backlog afetado** | BL-006 (MVP — campo pode ser omitido enquanto não confirmado) |

---

## Resumo e priorização

### Decisões que bloqueiam o MVP (devem ser resolvidas antes de iniciar o build)

| ID | Pergunta central | Responsável |
|---|---|---|
| **DP-006** | ma-hr-orch filtra PII antes de retornar ao agente? | MA_HR_ORCH |

### Decisões que bloqueiam o piloto (devem ser resolvidas antes de colocar usuários reais)

| ID | Pergunta central | Responsável |
|---|---|---|
| **DP-001** | Endpoint de rastreamento por orderNumber existe? | MA_HR_ORCH |
| **DP-002** | Rastreamento por CPF é viável na ma-hr-orch? | MA_HR_ORCH |
| **DP-003** | Quem monta a URL da webview para [list_navigation]? | ARQUITETURA |
| **DP-004** | Quais labels em português para cada status da API? | CLIENTE |
| **DP-005** | Estratégia de paginação para filtro de status? | ARQUITETURA |

### Decisões de melhoria (não bloqueiam, mas melhoram a experiência)

| ID | Pergunta central | Responsável |
|---|---|---|
| **DP-007** | GET /v1/orders suporta ordenação por data? | MA_HR_ORCH |
| **DP-008** | total de beneficiaries = total de cartões? | MA_HR_ORCH |

---

*Fontes: `06_analise_lacunas.md`, `01_requisitos_cliente.md`, `03_capacidades_restricoes_tecnicas.md`, `14_backlog_mvp.md` · Gerado em 2026-07-22*
