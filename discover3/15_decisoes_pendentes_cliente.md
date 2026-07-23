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

## DP-003 — Deeplink de navegação — subdividido em DP-003-A e DP-003-B

### DP-003-A — Deeplink de colaborador

| Campo | Valor |
|---|---|
| **ID** | DP-003-A |
| **Impacto** | MELHORIA (não bloqueia POC) |
| **Responsável** | ARQUITETURA + MA_HR_ORCH |
| **Origem** | LAC-007, AMB-002, NAV-SEC-001, DP-008 |
| **Status** | **RESOLVED_NOT_SUPPORTED_CURRENTLY** |
| **O que foi resolvido** | A rota `#/employees/:id/edit` existe como rota interna mas **não é deeplink-safe**. A tela depende de `location.state` (dados passados pela listagem) — não busca dados pela API usando o `:id`. Abrir a URL diretamente quebra porque os dados esperados não estão em memória. Não existe endpoint de detalhe de beneficiário por id. `beneficiaryId` nunca deve aparecer no deeplink. |
| **Navegação segura disponível** | `#/employees` (ROUTE-003) — lista de colaboradores. Funciona sem parâmetro. |
| **Feature futura necessária** | (1) Endpoint GET de beneficiário por id; (2) Adaptação da tela para carregamento por parâmetro; (3) Validação de autorização; (4) Validação de exposição do identificador. Esta feature está fora do escopo da POC atual. |
| **Referência** | `discover3/artifacts/deeplink_routes_catalog.json` campo `collaborator_deeplink_constraints` |
| **Fonte** | Resposta técnica 2026-07-23 (Leandro → Marcelo Gorzoni da Silva) |

### DP-003-B — Deeplink de pedido

| Campo | Valor |
|---|---|
| **ID** | DP-003-B |
| **Impacto** | ~~BLOQUEADOR_PILOTO~~ → **PARTIALLY_RESOLVED_PENDING_DEFAULT_SCREEN** |
| **Responsável** | ARQUITETURA + PRODUTO |
| **Origem** | LAC-007, AMB-002, RNF-004 |
| **Status** | **PARTIALLY_RESOLVED_PENDING_DEFAULT_SCREEN** |
| **O que foi resolvido** | Formato das rotas; parâmetro `orderNumber`; diferença para `idOrder`; suporte a múltiplos números na solicitação; bases HML e PRD; template do deeplink; casing dos parâmetros; responsabilidade de montar o deeplink. |
| **Rotas confirmadas** | `#/order-detail/{orderNumber}` (ROUTE-014) — detalhe do pedido específico (PATH); `#/order-request-group?orderNumber={orderNumbers}` (ROUTE-013-V2) — detalhe da solicitação agrupadora (QUERY, máximo 2 valores). |
| **Regra crítica** | `orderNumber` ≠ `idOrder`. Nunca usar `idOrder` no path, query string ou deeplink. |
| **O que ainda está pendente** | Qual tela deve ser o destino padrão da resposta do agente ao consultar um pedido: detalhe do pedido específico (ROUTE-014) ou detalhe da solicitação agrupadora (ROUTE-013-V2)? |
| **Recomendação técnica para POC** | Consulta de pedido único → ROUTE-014. Resposta sobre solicitação agrupadora → ROUTE-013-V2. Não transformar em regra sem confirmação. |
| **Referência** | `discover3/artifacts/deeplink_routes_catalog.json`; `discover3/agent_policy.md` seção 7 |
| **Fonte** | `Rotas_hr_space.html` (2026-07-21); Resposta técnica 2026-07-23 |
| **Backlog afetado** | BL-016 (Piloto — desbloqueado para POC) |

---

## DP-008 — Confirmação de segurança para `#/employees/:id/edit` (NAV-SEC-001)

| Campo | Valor |
|---|---|
| **ID** | DP-008 |
| **Impacto** | MELHORIA (não bloqueia POC) |
| **Responsável** | ARQUITETURA + TIME DE SEGURANÇA |
| **Origem** | NAV-SEC-001, `Rotas_hr_space.html` s.4.3 e s.5 |
| **Status** | **RESOLVED_NOT_SUPPORTED** — A resposta técnica de 2026-07-23 confirmou que a rota não é deeplink-safe e não existe endpoint de detalhe por id. A questão de segurança sobre `beneficiaryId` no deeplink tornou-se secundária: o deeplink individual não é possível independentemente. |
| **Comportamento atual** | Usar `#/employees` (ROUTE-003). Não usar `#/employees/:id/edit`. Não expor `beneficiaryId` em nenhuma circunstância. |
| **Feature futura** | Deeplink individual de colaborador depende de feature futura (endpoint + adaptação da tela). Registrado em DP-003-A. |

---

## DP-004 — Mapeamento de status de pedido (inglês → português)

| Campo | Valor |
|---|---|
| **ID** | DP-004 |
| **Impacto** | ~~BLOQUEADOR_PILOTO~~ → **PARTIALLY_RESOLVED_PENDING_GAPS** |
| **Responsável** | CLIENTE |
| **Origem** | LAC-008, CF-001, TEC-022, KB-025 |
| **Status** | **PARTIALLY_RESOLVED_PENDING_GAPS** — Resposta técnica 2026-07-23 forneceu labels completed/not_completed e aliases para 10 status. |
| **O que foi resolvido** | Labels completed e not_completed para 12 status; tipos visuais (POSITIVE, NEGATIVE, INFORMATIVE, WARNING); aliases de 10 status (INVOICE e CANCEL_PROCESSING sem aliases). |
| **Gaps restantes** | (1) Aliases de INVOICE; (2) Aliases de CANCEL_PROCESSING; (3) Label e type concluído de PARTIAL_REFUNDED; (4) Contexto de uso da tabela (timeline, resumo do chat ou ambos); (5) Confirmação do label genérico "Processado" para REFUNDED. |
| **Pergunta de acompanhamento** | "Recebemos os mappings. Para fechar a tabela, poderiam confirmar: (1) quais variações de texto devem mapear para INVOICE; (2) quais variações devem mapear para CANCEL_PROCESSING; (3) qual label e tipo usar quando PARTIAL_REFUNDED estiver concluído; (4) se as colunas Concluído/Não concluído são da timeline, do resumo do chat ou de ambos; (5) se REFUNDED concluído deve permanecer como 'Processado'?" |
| **Referência** | `discover3/artifacts/order_status_catalog.json` |
| **Fonte** | Resposta técnica 2026-07-23 (Leandro → Marcelo Gorzoni da Silva) |
| **Backlog afetado** | BL-014 (Piloto — parcialmente desbloqueado) |

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
| **DP-003-B** | Qual tela padrão: pedido específico ou solicitação agrupadora? | PRODUTO |
| **DP-004** | Fechar gaps restantes de status (aliases, PARTIAL_REFUNDED, contexto da tabela) | CLIENTE |
| **DP-005** | Estratégia de paginação para filtro de status? | ARQUITETURA |

### Decisões parcialmente resolvidas

| ID | Status | Pendência restante |
|---|---|---|
| **DP-003-A** | RESOLVED_NOT_SUPPORTED_CURRENTLY | Feature futura (endpoint + tela) necessária para deeplink individual |
| **DP-003-B** | PARTIALLY_RESOLVED_PENDING_DEFAULT_SCREEN | Tela padrão do botão de navegação de pedido |
| **DP-004** | PARTIALLY_RESOLVED_PENDING_GAPS | 5 gaps listados na seção DP-004 |
| **DP-008** | RESOLVED_NOT_SUPPORTED | Deeplink individual não possível — feature futura |

### Decisões de melhoria (não bloqueiam, mas melhoram a experiência)

| ID | Pergunta central | Responsável |
|---|---|---|
| **DP-007** | GET /v1/orders suporta ordenação por data? | MA_HR_ORCH |
| **DP-008-B** | total de beneficiaries = total de cartões? | MA_HR_ORCH |

---

*Fontes: `06_analise_lacunas.md`, `01_requisitos_cliente.md`, `03_capacidades_restricoes_tecnicas.md`, `14_backlog_mvp.md` · Gerado em 2026-07-22 · Atualizado em 2026-07-23 (DP-003 subdividido em A/B; DP-004 PARTIALLY_RESOLVED; resposta técnica Leandro → Marcelo Gorzoni da Silva)*
