# 06 — Análise de Lacunas

> **Princípio:** Este documento cataloga apenas lacunas reais — ausências de informação, endpoint, dado ou decisão que impedem ou comprometem a resposta do agente. Lacunas são classificadas por severidade de impacto no MVP, piloto e produção. Conflitos entre fontes são tratados em seção separada.

---

## Legenda de classificação por momento

| Momento | Descrição |
|---|---|
| BLOQUEADOR_MVP | A POC não pode ser entregue sem resolver esta lacuna |
| NECESSARIO_PILOTO | O piloto com usuários reais pode falhar sem resolver esta lacuna |
| NECESSARIO_PRODUCAO | Necessário antes do go-live em produção |
| MELHORIA_FUTURA | Pode ser ignorado no MVP/piloto — melhora qualidade futura |

---

## Legenda de status de lacuna

| Status | Descrição |
|---|---|
| ABERTA | Lacuna identificada e ainda não resolvida |
| EM_INVESTIGACAO | Time técnico está avaliando |
| AGUARDANDO_DECISAO | Depende de decisão do cliente ou de negócio |
| RESOLVIDA | Lacuna sanada com solução documentada |

---

## L1 — Endpoint de rastreamento de cartão (via ma-hr-orch) não inventariado

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-001 |
| **Momento** | BLOQUEADOR_MVP |
| **Status** | ABERTA |
| **Afeta** | INT-007 (Rastrear por número do pedido) |
| **Descrição** | Os testes de API realizados em 2026-07-22 inventariaram os endpoints de gestão de colaboradores e gestão de pedidos. Nenhum endpoint de rastreamento de cartão foi encontrado nas APIs testadas. A especificação do cliente menciona que o rastreamento deve ser feito "quando houver fonte disponível por meio da ma-hr-orch", mas não indica qual endpoint da ma-hr-orch deve ser chamado. |
| **Impacto** | Sem este endpoint confirmado, o agente não pode responder consultas de rastreamento com dados em tempo real. A KB descreve rastreamento no portal web (KB-028, KB-029), mas isso não é equivalente a um endpoint de API. |
| **Evidências** | TEC-027; api_inventory_pedidos.md — nenhum endpoint de rastreamento inventariado |
| **Ação necessária** | Solicitar ao time da ma-hr-orch: (a) o endpoint de rastreamento por orderNumber, (b) o schema de request/response, (c) quais campos retornam e se incluem endereço de entrega (PII). |
| **Requisitos relacionados** | RF-015, TEC-027, KB-028, KB-029 |
| **Nota** | INT-006 (rastreamento por CPF) é uma lacuna adicional, mas não é bloqueadora — vide LAC-002. |

---

## L2 — Rastreamento por CPF do colaborador não confirmado

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-002 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | AGUARDANDO_DECISAO |
| **Afeta** | INT-006 (Rastrear por CPF) |
| **Descrição** | O cliente especifica que o rastreamento por CPF deve ser avaliado com o time técnico. O documento de especificação indica explicitamente: "Avaliar, junto ao time técnico, se a ma-hr-orch consegue disponibilizar uma consulta de rastreamento por CPF do colaborador." O fallback (solicitar número do pedido) está confirmado como comportamento de POC. |
| **Impacto** | Para a POC: sem impacto — fallback funciona. Para o piloto: o usuário precisará informar o número do pedido quando quiser rastrear, o que pode causar fricção. |
| **Evidências** | AMB-001; RF-016; RN-014; ERR-010 |
| **Ação necessária** | Confirmar com time técnico se ma-hr-orch pode expor rastreamento por CPF. Se sim: especificar contrato. Se não: documentar formalmente que o comportamento permanente é solicitar o orderNumber. |
| **Requisitos relacionados** | RF-016, RF-017, AMB-001, RN-014, ERR-010 |

---

## L3 — Arquivo markdown de conhecimento não criado

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-003 |
| **Momento** | BLOQUEADOR_MVP |
| **Status** | ABERTA |
| **Afeta** | INT-008 a INT-021 (todas as intenções informativas) |
| **Descrição** | A especificação define que o agente deve possuir um arquivo markdown de conhecimento carregado em tempo de execução (RF-010, RNF-002, ACE-007). Este arquivo deve conter todas as informações que o agente está autorizado a responder sobre a feature MARH. O arquivo ainda não existe — o conteúdo disponível está nos documentos da KB (`docs\kb\`) e na especificação, mas não foi consolidado no arquivo de runtime. |
| **Impacto** | Sem o markdown, as 14 intenções do Grupo B não podem ser respondidas. O agente recorreria ao ERR-008 para todas as perguntas informativas sobre o MARH. |
| **Evidências** | RF-010, RNF-002, ACE-007, ACE-008; KB-001 a KB-047 têm o conteúdo |
| **Ação necessária** | Criar o arquivo markdown de conhecimento consolidando: (a) o escopo do agente (o que pode e não pode fazer), (b) as 5 consultas disponíveis, (c) limitações conhecidas, (d) definição de MARH e Espaço RH, (e) redirecionamentos para ações transacionais. |
| **Requisitos relacionados** | RF-010, RNF-002, ACE-007, ACE-008, ERR-008 |

---

## L4 — Filtro de status de pedido não disponível no endpoint da API

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-004 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | ABERTA |
| **Afeta** | INT-005 (Consultar pedidos por status) |
| **Descrição** | O endpoint `GET /v1/orders` não possui parâmetro de filtro por status. O filtro precisa ser aplicado no agente ou na camada de orquestração sobre os resultados paginados. Para empresas com muitos pedidos, isso significa paginar múltiplas vezes para garantir que todos os pedidos com o status desejado sejam encontrados. |
| **Impacto** | Para um conjunto pequeno de pedidos: sem problema. Para empresas com dezenas ou centenas de pedidos: o agente pode retornar uma lista incompleta se apenas a primeira página for consultada. |
| **Evidências** | TEC-003, TEC-002; api_inventory_pedidos.md |
| **Ação necessária** | Definir estratégia de paginação para INT-005: (a) limitar a N páginas e informar ao usuário, (b) solicitar à ma-hr-orch que implemente filtro de status no endpoint, (c) aceitar incompletude com aviso. |
| **Requisitos relacionados** | RF-014, TEC-002, TEC-003 |

---

## L5 — Ausência de ordenação por data na consulta de último pedido

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-005 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | ABERTA |
| **Afeta** | INT-004 (Consultar último pedido) |
| **Descrição** | A API `GET /v1/orders` não garante ordenação por data. O "último pedido" retornado pode ser o primeiro da paginação padrão, que não necessariamente é o mais recente. A especificação cobre este caso com um aviso obrigatório ao usuário, mas a experiência pode ser confusa. |
| **Impacto** | Usuário pode receber um pedido antigo como "último pedido". O aviso obrigatório mitiga parcialmente, mas não resolve o problema de dados. |
| **Evidências** | TEC-003; RF-013 (aviso obrigatório definido) |
| **Ação necessária** | Verificar com o time da ma-hr-orch se é possível adicionar ordenação por `orderDate desc` no endpoint ou se há endpoint específico para "último pedido". |
| **Requisitos relacionados** | RF-013, TEC-002, TEC-003 |

---

## L6 — Sanitização de PII não implementada na camada de integração

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-006 |
| **Momento** | BLOQUEADOR_MVP |
| **Status** | ABERTA |
| **Afeta** | INT-001, INT-002 (colaboradores), INT-003, INT-004, INT-005 (pedidos) |
| **Descrição** | Os endpoints de colaboradores retornam PII (CPF, email, telefone, nome da mãe, endereço) que **não deve ir ao modelo de linguagem**. Os endpoints de pedidos retornam campos restritos (billingDocumentNumber, contractNumber, idLegalPersonBilling). A ma-hr-orch deve filtrar esses campos antes de retornar ao agente, mas não há evidência de que essa sanitização está implementada. |
| **Impacto** | Se o agente receber PII diretamente, pode expor dados sensíveis ao usuário (violação de SEG-003). Se a integração não for feita corretamente, o agente pode processar dados desnecessários, aumentando custo de tokens e risco de exposição. |
| **Evidências** | TEC-017, TEC-018, TEC-019, TEC-009; model_consumption_assessment.md; SEG-003 |
| **Ação necessária** | Confirmar com o time da ma-hr-orch que a camada de orquestração filtra: (a) CPF, email, telefone, nome da mãe e endereço dos colaboradores, (b) billingDocumentNumber, contractNumber e idLegalPersonBilling dos pedidos, (c) content (base64 do PDF) do boleto. |
| **Requisitos relacionados** | TEC-017, TEC-018, TEC-019, TEC-011, SEG-003, RN-004 |

---

## L7 — Camada responsável pela URL final da webview

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-007 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | **PARTIALLY_RESOLVED** (2026-07-23) |
| **Afeta** | RF-018 (elemento [list_navigation]) |
| **Resolução parcial** | `docs/cliente/Rotas_hr_space.html` (CLIENT_NAVIGATION_CONTRACT, 2026-07-21) confirmou: formato da URL (`{BASE_URL}/#{ROTA}`); bases HML e PRD; template do deeplink (`meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true`); casing dos parâmetros; lista de rotas autorizadas; responsabilidade de montar o deeplink atribuída ao Agente/Backend. |
| **Pendência restante** | Confirmar se há camada intermediária (BFF) para casos específicos. Para a POC, o agente monta o deeplink diretamente. |
| **Referência** | `discover3/artifacts/deeplink_routes_catalog.json`; `discover3/agent_policy.md` seção 7 |
| **Requisitos relacionados** | RF-018, RNF-003, RNF-004, AMB-002 |

---

## L8 — Mapeamento de status da API para português não especificado

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-008 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | ABERTA |
| **Afeta** | INT-003, INT-004, INT-005 |
| **Descrição** | Os status retornados pela API de pedidos são em inglês (IN_PROCESSING, PENDING, PAID, CREDITED, CANCELLED, REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED — TEC-022). A KB documenta 6 status em português (KB-025): "Aguardando pagamento", "Pagamento confirmado", "Nota Fiscal Emitida", "Aguardando Disponibilização", "Pedido creditado", "Cancelado". Há discrepância: a API tem 10 status, a KB tem 6. |
| **Impacto** | O agente pode exibir status em inglês ao usuário ou usar mapeamento incorreto (CONFLITANTE). |
| **Evidências** | TEC-022, KB-025; conflito entre lista de status da API e lista da KB |
| **Ação necessária** | Criar tabela de mapeamento completa: status da API → label em português. Definir o que exibir para status não presentes na KB (REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED). |
| **Requisitos relacionados** | TEC-022, KB-025, RF-014 |
| **Tipo** | CONFLITANTE (documentação vs. KB) |

---

## L9 — Número de cartões por pedido requer endpoint adicional

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-009 |
| **Momento** | NECESSARIO_PILOTO |
| **Status** | ABERTA |
| **Afeta** | INT-003 (Consultar pedido por número) |
| **Descrição** | A especificação define que a consulta de pedido deve exibir "quantidade de colaboradores e cartões quando disponíveis" (RF-012). O endpoint `GET /v1/orders/{orderNumber}` não retorna diretamente essas quantidades — é necessário chamar `GET /v1/orders/{orderNumber}/beneficiaries` para obter o campo `total`, que representa a quantidade de colaboradores (e presumidamente cartões) do pedido. |
| **Impacto** | O agente precisará de 2 chamadas de API para responder INT-003 completamente. Aumenta latência e complexidade. Se o campo `total` de beneficiaries não corresponder à qtd. de cartões, haverá imprecisão. |
| **Evidências** | RF-012, TEC-004, TEC-005, TEC-006 |
| **Ação necessária** | Confirmar com o time técnico: (a) se `total` de `/v1/orders/{orderNumber}/beneficiaries` representa a qtd. de cartões, (b) se há campo direto no endpoint de detalhe do pedido para essas quantidades. |
| **Requisitos relacionados** | RF-012, TEC-004, TEC-006 |

---

## L10 — rpsLink do endpoint de Nota Fiscal pode expor dados fiscais

| Campo | Valor |
|---|---|
| **LAC ID** | LAC-010 |
| **Momento** | NECESSARIO_PRODUCAO |
| **Status** | ABERTA |
| **Afeta** | Potencial exibição de link de NF ao usuário (INT-003 — detalhe de pedido) |
| **Descrição** | O endpoint `GET /v1/orders/{orderNumber}/invoice` retorna um campo `rpsLink` que pode conter CNPJ implícito na URL. O agente pode exibir este link ao usuário, mas a sanitização ainda precisa ser validada (TEC-009). Para INT-003, se o usuário perguntar sobre a NF do pedido, o agente pode retornar este link — mas somente se a URL for adequada para exibição. |
| **Impacto** | Exposição de dados fiscais sensíveis na URL se não sanitizado. |
| **Evidências** | TEC-009; model_consumption_assessment_pedidos.md — "CNPJ embutido na URL — APTO_COM_SANITIZACAO" |
| **Ação necessária** | Validar com time técnico se ma-hr-orch sanitiza a URL antes de retornar ao agente. |
| **Requisitos relacionados** | TEC-008, TEC-009, SEG-003 |

---

## Conflitos entre fontes

### CF-001 — Status de pedidos: API (10 status em inglês) vs. KB (6 status em português)

| Campo | Valor |
|---|---|
| **CF ID** | CF-001 |
| **Fontes em conflito** | `docs\cliente\Gestao_de_Pedidos.html` seção 3 (TEC-022) vs. `docs\kb\6ACOMPA_PEDIDO_STATUS.md` (KB-025) |
| **Descrição** | A API retorna 10 valores de status em inglês. A KB documenta 6 status em português. Não há mapeamento explícito entre os dois conjuntos. Quatro status da API (REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED) não aparecem na KB. |
| **Impacto** | O agente pode usar labels inconsistentes com o que o usuário vê no portal. |
| **Resolução necessária** | Criar mapeamento completo (LAC-008). Validar com cliente quais labels devem ser exibidos ao usuário. |
| **Classificação** | CONFLITANTE |

### CF-002 — Rastreamento de cartão: KB descreve portal web, não endpoint de API

| Campo | Valor |
|---|---|
| **CF ID** | CF-002 |
| **Fontes em conflito** | `docs\kb\8RASTREIO_CARTOES.md` (KB-028, KB-029) vs. ausência de endpoint de rastreamento no inventário de APIs |
| **Descrição** | A KB descreve o rastreamento como uma funcionalidade do portal web (`Menu Cartões > Rastreio de Cartões`), com busca por CPF do colaborador. A especificação do cliente define que o agente deve rastrear "quando houver fonte disponível por meio da ma-hr-orch", mas não indica qual endpoint da ma-hr-orch provê essa informação. O inventário de APIs não inclui nenhum endpoint de rastreamento. |
| **Impacto** | A KB pode induzir a crer que rastreamento por CPF é possível, quando o endpoint não foi confirmado. O agente pode tentar usar a KB como fonte para dados em tempo real — o que é incorreto. |
| **Resolução necessária** | Separar claramente: (a) KB descreve como funciona no portal web (RAG — INT-013 informativo); (b) endpoint de API é necessário para resposta em tempo real (INT-007 consultivo). |
| **Classificação** | CONFLITANTE |

### CF-003 — Número de cartões por pedido: spec vs. campos de API disponíveis

| Campo | Valor |
|---|---|
| **CF ID** | CF-003 |
| **Fontes em conflito** | `00_Agente_Consultivo_MARH.html` seção 8.2 (RF-012) vs. `gestao_pedidos_apis.json` (TEC-004) |
| **Descrição** | A especificação define que o agente deve exibir "quantidade de colaboradores e cartões". O endpoint de detalhe do pedido não retorna diretamente esses campos — eles precisam ser derivados de uma chamada adicional. Quantidade de cartões pode ser diferente de quantidade de colaboradores (um colaborador pode ter múltiplos cartões em cenários de 2ª via). |
| **Impacto** | O agente pode exibir informação incompleta ou imprecisa ao usuário. |
| **Resolução necessária** | Confirmar com time técnico o campo correto para "número de cartões" (LAC-009). |
| **Classificação** | CONFLITANTE |

---

## Resumo das lacunas por momento

### Bloqueadores do MVP (sem estes, a POC não funciona)

| LAC ID | Descrição | Ação necessária |
|---|---|---|
| LAC-001 | Endpoint de rastreamento não inventariado | Solicitar contrato do endpoint à ma-hr-orch |
| LAC-003 | Arquivo markdown de conhecimento não existe | Criar arquivo com base na KB e na especificação |
| LAC-006 | Sanitização de PII não confirmada na ma-hr-orch | Confirmar implementação da camada de filtro de dados |

### Necessários para o piloto (sem estes, usuários reais terão problemas)

| LAC ID | Descrição | Ação necessária |
|---|---|---|
| LAC-002 | Rastreamento por CPF não confirmado | Decisão técnica com time da ma-hr-orch |
| LAC-004 | Filtro de status sem suporte na API | Definir estratégia de paginação no agente |
| LAC-005 | Ordenação do último pedido não garantida | Verificar parâmetro de ordenação na ma-hr-orch |
| LAC-007 | URL da webview — **PARTIALLY_RESOLVED** | Formato, bases, deeplink e rotas confirmadas por `Rotas_hr_space.html`. Pendente: BFF intermediário. |
| LAC-008 | Mapeamento de status API→português | Criar tabela de mapeamento com validação do cliente |
| LAC-009 | Qtd. cartões requer chamada adicional | Confirmar campo correto com time técnico |

### Necessários para produção (sem estes, há risco em go-live)

| LAC ID | Descrição | Ação necessária |
|---|---|---|
| LAC-010 | rpsLink pode expor CNPJ | Validar sanitização na ma-hr-orch |

### Conflitos a resolver (impactam coerência das respostas)

| CF ID | Descrição | Ação necessária |
|---|---|---|
| CF-001 | Status API vs. KB divergem | Mapeamento completo |
| CF-002 | KB descreve portal, não API de rastreamento | Separar fontes claramente |
| CF-003 | Qtd. cartões não está no endpoint de detalhe | Confirmar campo correto |

---

## Contagem final

| Categoria | Qtd |
|---|---|
| Lacunas bloqueadoras do MVP | 3 (LAC-001, LAC-003, LAC-006) |
| Lacunas necessárias para o piloto | 6 (LAC-002, LAC-004, LAC-005, LAC-007, LAC-008, LAC-009) |
| Lacunas necessárias para produção | 1 (LAC-010) |
| Conflitos entre fontes | 3 (CF-001, CF-002, CF-003) |
| **Total** | **13** |

---

*Fontes: `01_requisitos_cliente.md`, `02_conhecimento_rag.md`, `03_capacidades_restricoes_tecnicas.md`, `03_matriz_cobertura_escopo.md`, `04_catalogo_intencoes.md`, `05_matriz_fontes_resposta.md` · Gerado em 2026-07-22 · Atualizado em 2026-07-23 (LAC-007 PARTIALLY_RESOLVED por `Rotas_hr_space.html`)*
