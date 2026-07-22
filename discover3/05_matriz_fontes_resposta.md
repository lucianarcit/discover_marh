# 05 — Matriz de Fontes de Resposta

> **Princípio:** Para cada intenção catalogada em `04_catalogo_intencoes.md`, este documento mapeia a fonte concreta de resposta, a estratégia, os campos, as restrições e o status de validação.
>
> **Separação de fontes obrigatória:**
> - `00_Agente_Consultivo_MARH.html` → define escopo, erros e respostas estáticas
> - `discover3/knowledge/markdown_conhecimento_marh.md` → fonte informativa em runtime (consolidado da KB)
> - APIs via `ma-hr-orch` → dados em tempo real

---

## Legenda de estratégia

| Estratégia | Descrição |
|---|---|
| RAG_ONLY | Respondida exclusivamente pelo markdown de conhecimento em runtime |
| API_ONLY | Respondida por chamada à ma-hr-orch, sem necessidade de conteúdo informativo |
| HYBRID_RAG_API | Dado atual vem da API; explicação necessária sustentada no markdown consolidado |
| STATIC_RESPONSE | Mensagem fixa definida pelo cliente em `00_Agente_Consultivo_MARH.html` |
| REDIRECT_TO_OFFICIAL_JOURNEY | Ação transacional — redirecionamento para o Espaço RH |
| REQUIRES_CLARIFICATION | Agente precisa de dado adicional do usuário antes de responder |
| NEEDS_CLIENT_VALIDATION | Depende de decisão técnica ou aprovação do cliente |
| OUT_OF_SCOPE | Fora do escopo — ação proibida ao agente |

## Legenda de cobertura

| Valor | Descrição |
|---|---|
| COVERED | Todos os 7 critérios atendidos (fonte, seção, conteúdo, escopo, segurança, fallback, dependência técnica) |
| PARTIALLY_COVERED | Fonte identificada com lacunas específicas |
| NOT_COVERED | Sem fonte de resposta disponível |
| CONFLICTING | Fontes divergem — requer resolução |
| NOT_VALIDATED | Depende de validação técnica ainda não realizada |

## Legenda de status da fonte

| Valor | Significado |
|---|---|
| API_TESTED | Endpoint testado com sucesso em UAT (2026-07-22) |
| API_DOCUMENTED_ONLY | Endpoint documentado, não testado |
| API_NOT_FOUND | Endpoint não localizado no inventário |
| PENDING_CLIENT_APPROVAL | Conteúdo rastreado à KB; aguarda aprovação humana antes de produção |
| STATIC_CLIENT_DEFINED | Mensagem exata definida pelo cliente na especificação |

---

## Tabela principal

| ID | Intenção | Grupo | Estratégia | Fonte primária | Seção | Evidências originais | API/Operação | Campos permitidos | Campos restritos | Sanitização | Tempo real | Fallback | Cobertura | Status da fonte |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INT-001 | Consultar colaborador por nome | A | API_ONLY | ma-hr-orch | — | `Gestao_de_Colaboradores.html` s.1; `gestao_colaboradores_apis.json` | GET /v1/beneficiaries?nameOrCpf={nome} | name, placeName, subtype, isHomeDelivery, products[] | documentNumber, email, phoneNumber, motherName, beneficiaryId, address | Filtrar PII antes de enviar ao modelo | Sim | ERR-002 se total=0; ERR-005/ERR-006 se 403; ERR-001 se 422 | PARTIALLY_COVERED | API_TESTED |
| INT-002 | Consultar colaborador por CPF | A | API_ONLY | ma-hr-orch | — | `Gestao_de_Colaboradores.html` s.1; `gestao_colaboradores_apis.json` | GET /v1/beneficiaries?nameOrCpf={cpf} | name, placeName, subtype, isHomeDelivery, products[] | documentNumber, email, phoneNumber, motherName, beneficiaryId, address | Filtrar PII antes de enviar ao modelo | Sim | ERR-002 se total=0 | PARTIALLY_COVERED | API_TESTED |
| INT-003 | Consultar pedido por número | A | API_ONLY | ma-hr-orch | — | `Gestao_de_Pedidos.html` s.4; `gestao_pedidos_apis.json` | GET /v1/orders/{orderNumber}; GET /v1/orders/{orderNumber}/beneficiaries (qtd.) | status, orderDate, totalOrder, productInfo.productName, paymentMethod, steps[] | billingDocumentNumber, contractNumber, idLegalPersonBilling | Filtrar campos fiscais restritos | Sim | ERR-003 se 404; ERR-005/ERR-006 se 403 | PARTIALLY_COVERED | API_TESTED |
| INT-004 | Consultar último pedido | A | API_ONLY | ma-hr-orch | — | `Gestao_de_Pedidos.html` s.3; `gestao_pedidos_apis.json` | GET /v1/orders?page=0&size=1 | status, orderDate, totalOrder, productInfo.productName | billingDocumentNumber, contractNumber, idLegalPersonBilling | Filtrar campos fiscais restritos | Sim | Aviso de ordenação incerta obrigatório (RF-013); ERR-007 se indisponível | PARTIALLY_COVERED | API_TESTED |
| INT-005 | Consultar pedidos por status | A | API_ONLY | ma-hr-orch | — | `Gestao_de_Pedidos.html` s.3; `gestao_pedidos_apis.json` | GET /v1/orders (filtro de status na camada de orquestração) | status, orderDate, totalOrder, productInfo.productName | billingDocumentNumber, contractNumber, idLegalPersonBilling | Filtrar campos fiscais restritos | Sim | ERR-004 se status não reconhecido; resposta amigável se lista vazia | PARTIALLY_COVERED | API_TESTED |
| INT-006 | Rastrear cartão por CPF do colaborador | A | REQUIRES_CLARIFICATION | 00_Agente_Consultivo_MARH.html | Seção 8.5 | `00_Agente_Consultivo_MARH.html` s.8.5; `TEC-027` | Endpoint de rastreamento por CPF via ma-hr-orch — NÃO ENCONTRADO | — | — | — | Não aplicável | Solicitar número do pedido (ERR-010): "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." | NOT_VALIDATED | API_NOT_FOUND |
| INT-007 | Rastrear cartão por número do pedido | A | API_ONLY | ma-hr-orch | — | `8RASTREIO_CARTOES.md` (portal); `00_Agente_Consultivo_MARH.html` s.8.5 | Endpoint de rastreamento por orderNumber via ma-hr-orch — NÃO INVENTARIADO | status rastreio, data última atualização, código de rastreio | endereço de entrega (PII) | Filtrar endereço de entrega antes de enviar ao modelo | Sim | ERR-007 se indisponível; nunca inventar prazo, transportadora ou status (RN-003) | PARTIALLY_COVERED | API_NOT_FOUND |
| INT-008 | "O que posso fazer?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 2 — O que o Agente Consultivo MARH pode fazer | `1CONFIG_BENE_1.md`; `00_Agente_Consultivo_MARH.html` s.1, s.7.3, s.12 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-009 | "Quais informações posso consultar?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seções 2 e 3 — O que pode fazer + Como usar | `4PEDIDO_PLANILHA.md`; `4PEDIDO_TELA.md`; `00_Agente_Consultivo_MARH.html` s.8.1–8.5 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-010 | "Como faço para fazer um pedido?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 7 — Pedidos | `4PEDIDO_PLANILHA.md`; `4PEDIDO_TELA.md`; `5PAG_DISPO.md` | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-011 | "Como faço para consultar um pedido?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 3 — Como usar o agente | `00_Agente_Consultivo_MARH.html` s.8.2 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-012 | "Como faço para consultar um colaborador?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 3 — Como usar o agente | `00_Agente_Consultivo_MARH.html` s.8.1 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-013 | "Consigo rastrear cartões?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 12 — Rastreamento de cartões | `8RASTREIO_CARTOES.md`; `manual-emissao-2via.md` | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-014 | "Você consegue cancelar pedido?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 2 — O que o agente não faz | `00_Agente_Consultivo_MARH.html` s.12 (FORA-002) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-015 | "Você consegue alterar dados de um colaborador?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 2 — O que o agente não faz | `00_Agente_Consultivo_MARH.html` s.12 (FORA-004) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-016 | "Você consulta dados de qualquer empresa?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 3 — Como usar o agente | `00_Agente_Consultivo_MARH.html` s.5 (RF-007) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-017 | "Preciso selecionar uma empresa para usar o agente?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 3 — Como usar o agente | `00_Agente_Consultivo_MARH.html` s.5 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-018 | "O agente substitui o portal web?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 2 — O que o agente não faz | `00_Agente_Consultivo_MARH.html` s.1 (RN-001) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-019 | "O que é o MARH?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 1 — O que é o MARH e o Espaço RH | `1CONFIG_BENE_1.md`; `2CADASTRO_INTERLO_PERFIS.md` (contexto implícito) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | PARTIALLY_COVERED | PENDING_CLIENT_APPROVAL |
| INT-020 | "O que é o Espaço RH?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seção 1 — O que é o MARH e o Espaço RH | `1CONFIG_BENE_1.md`; `2CADASTRO_INTERLO_PERFIS.md` (contexto implícito) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | PARTIALLY_COVERED | PENDING_CLIENT_APPROVAL |
| INT-021 | "Quais tipos de pergunta posso fazer?" | B | RAG_ONLY | discover3/knowledge/markdown_conhecimento_marh.md | Seções 2 e 3 — O que pode fazer + Como usar | `00_Agente_Consultivo_MARH.html` s.10 | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | ERR-008 se seção não encontrada | COVERED | PENDING_CLIENT_APPROVAL |
| INT-022 | "Cancela o pedido 342671." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-002) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Resposta estática: "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH." | COVERED | STATIC_CLIENT_DEFINED |
| INT-023 | "Altera o endereço do colaborador." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-006) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Idem INT-022 | COVERED | STATIC_CLIENT_DEFINED |
| INT-024 | "Cria um novo pedido." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-001) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Idem INT-022 | COVERED | STATIC_CLIENT_DEFINED |
| INT-025 | "Remove esse colaborador." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-005) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Idem INT-022 | COVERED | STATIC_CLIENT_DEFINED |
| INT-026 | "Paga o pedido." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-010) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Idem INT-022 | COVERED | STATIC_CLIENT_DEFINED |
| INT-027 | "Emite um novo cartão." | C | REDIRECT_TO_OFFICIAL_JOURNEY | 00_Agente_Consultivo_MARH.html | Seção 7.3 e Seção 12 | `00_Agente_Consultivo_MARH.html` s.7.3, s.12 (FORA-007, FORA-008) | Não aplicável | Não aplicável | Não aplicável | Nenhum | Não | Idem INT-022 | COVERED | STATIC_CLIENT_DEFINED |

---

## Detalhamento — Grupo A (Intenções Consultivas)

### INT-001 / INT-002 — Consultar colaborador (por nome ou CPF)

| Campo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Operação técnica** | GET /v1/beneficiaries?nameOrCpf={nome_ou_cpf}&page={n} |
| **Parâmetros obrigatórios** | nameOrCpf (obrigatório), page (paginação) |
| **Parâmetros de contexto** | empresa_selecionada (obrigatório, fornecido pela API MARH) |
| **Dependências** | Nenhuma chamada prévia necessária |
| **Campos permitidos ao modelo** | name, placeName, subtype (WORKPLACE/HOME_DELIVERY/BRANCH), isHomeDelivery, products[] |
| **Campos restritos** | documentNumber (CPF), email, phoneNumber, motherName, beneficiaryId, address |
| **Sanitização** | Filtrar todos os campos restritos antes de enviar ao modelo de linguagem |
| **Múltiplos resultados** | Campo total > 1 → apresentar lista e pedir escolha ao usuário |
| **Ausência de dados** | total: 0 → ERR-002 |
| **Erro de acesso** | HTTP 403 → ERR-005 (permissão) ou ERR-006 (FNP/prova de vida) |
| **Empresa inválida** | HTTP 422 → ERR-001 |
| **Status técnico** | API_TESTED (HTTP 200, 3.275ms, UAT 2026-07-22) |
| **Fonte de documentação** | `Gestao_de_Colaboradores.html` s.1; `gestao_colaboradores_apis.json` |

**Fluxo:**
```
Usuário informa nome ou CPF
  → Agente não inventa o identificador
  → ma-hr-orch recebe {empresa_selecionada, nameOrCpf}
  → Filtra campos PII da resposta
  → Envia ao modelo: name, placeName, subtype, products[]
  → Se total > 1: apresentar lista, pedir escolha
  → Se total = 0: ERR-002
```

---

### INT-003 — Consultar pedido por número

| Campo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Operação técnica principal** | GET /v1/orders/{orderNumber} |
| **Operação técnica auxiliar** | GET /v1/orders/{orderNumber}/beneficiaries (qtd. colaboradores/cartões) |
| **Parâmetros obrigatórios** | orderNumber (fornecido pelo usuário — nunca inventado pelo modelo) |
| **Campos permitidos** | status (traduzido), orderDate, totalOrder, productInfo.productName, paymentMethod, steps[] |
| **Campos restritos** | billingDocumentNumber, contractNumber, idLegalPersonBilling |
| **Mapeamento de status** | PAID→"Pago", PENDING→"Aguardando pagamento", CREDITED→"Pedido creditado", CANCELLED→"Cancelado", IN_PROCESSING→"Em processamento", RELEASED→"Liberado", REJECTED→"Rejeitado", IN_BILLING_PROCESSING→"Em processamento de faturamento", REFUNDED→"Estornado", PARTIAL_REFUNDED→"Parcialmente estornado" |
| **Conflito de status** | 4 status sem mapeamento validado pela KB (CF-KB-001) — requer DP-004 |
| **Qtd. colaboradores/cartões** | Campo total de /beneficiaries — requer chamada adicional (LAC-009) |
| **Ausência de dados** | HTTP 404 → ERR-003 |
| **Status técnico** | API_TESTED |

---

### INT-004 — Consultar último pedido

| Campo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Operação técnica** | GET /v1/orders?page=0&size=1 |
| **Limitação técnica** | API não filtra por data (TEC-003) — "último" = primeiro resultado da paginação padrão |
| **Aviso obrigatório** | Se ordenação não garantida: "Estou exibindo o pedido mais recente retornado pela consulta." |
| **Campos permitidos** | status (traduzido), orderDate, totalOrder, productInfo.productName |
| **Campos restritos** | billingDocumentNumber, contractNumber, idLegalPersonBilling |
| **Status técnico** | API_TESTED |

---

### INT-005 — Consultar pedidos por status

| Campo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Operação técnica** | GET /v1/orders (filtro de status aplicado na camada de orquestração) |
| **Limitação técnica** | Sem parâmetro de filtro por status no endpoint — filtro client-side (LAC-004) |
| **Mapeamento de status** | Idem INT-003 — 4 status sem validação do cliente (CF-KB-001) |
| **Status não reconhecido** | ERR-004 |
| **Lista vazia** | Resposta amigável sem inventar pedidos |
| **Status técnico** | API_TESTED |

---

### INT-006 — Rastrear cartão por CPF do colaborador

| Campo | Valor |
|---|---|
| **Estratégia** | REQUIRES_CLARIFICATION |
| **Razão** | Endpoint de rastreamento por CPF via ma-hr-orch não foi encontrado no inventário de APIs |
| **Comportamento confirmado** | Solicitar número do pedido com a mensagem ERR-010 |
| **Mensagem obrigatória** | "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." |
| **Fonte do comportamento** | `00_Agente_Consultivo_MARH.html` s.8.5 (RF-017, RN-014, ERR-010) |
| **Validação técnica** | DP-002 — aguardando confirmação da ma-hr-orch |
| **Status técnico** | API_NOT_FOUND |

---

### INT-007 — Rastrear cartão por número do pedido

| Campo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Operação técnica** | Endpoint de rastreamento por orderNumber via ma-hr-orch — contrato não inventariado |
| **Parâmetros obrigatórios** | orderNumber (fornecido pelo usuário — nunca inventado pelo modelo) |
| **Campos permitidos** | status de rastreio, data da última atualização, código de rastreio |
| **Campos restritos** | endereço de entrega (PII) |
| **Sanitização** | Filtrar endereço de entrega antes de enviar ao modelo |
| **Regra de não invenção** | Nunca inventar prazo, transportadora ou status (RN-003) |
| **Ausência de dados** | Informar sem inventar — ERR-007 se indisponível |
| **Observação KB** | `8RASTREIO_CARTOES.md` descreve rastreamento no portal web — **não é fonte de dados em tempo real** |
| **Status técnico** | API_NOT_FOUND — bloqueador do MVP (LAC-001) |

---

## Detalhamento — Grupo B (Intenções Informativas)

Para todas as intenções do Grupo B:

- **Estratégia:** RAG_ONLY
- **Fonte primária:** `discover3/knowledge/markdown_conhecimento_marh.md`
- **Status da fonte:** PENDING_CLIENT_APPROVAL
- **Tempo real:** Não
- **Sanitização:** Nenhuma (sem PII no markdown)
- **Fallback:** ERR-008 se a seção não for encontrada no markdown

### Rastreabilidade das intenções informativas

| INT ID | Intenção | Seção no markdown | Arquivos KB de origem da seção |
|---|---|---|---|
| INT-008 | "O que posso fazer?" | Seção 2 — O que o Agente pode fazer | Spec seções 1, 7.3, 12 |
| INT-009 | "Quais informações posso consultar?" | Seções 2 e 3 | Spec seções 8.1–8.5, 10 |
| INT-010 | "Como faço para fazer um pedido?" | Seção 7 — Pedidos | `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md` |
| INT-011 | "Como faço para consultar um pedido?" | Seção 3 — Como usar o agente | Spec seção 8.2 |
| INT-012 | "Como faço para consultar um colaborador?" | Seção 3 — Como usar o agente | Spec seção 8.1 |
| INT-013 | "Consigo rastrear cartões?" | Seção 12 — Rastreamento de cartões | `8RASTREIO_CARTOES.md`, `manual-emissao-2via.md` |
| INT-014 | "Você consegue cancelar pedido?" | Seção 2 — O que o agente não faz | Spec seção 12 (FORA-002) |
| INT-015 | "Você consegue alterar dados de um colaborador?" | Seção 2 — O que o agente não faz | Spec seção 12 (FORA-004) |
| INT-016 | "Você consulta dados de qualquer empresa?" | Seção 3 — Como usar o agente | Spec seção 5 (RF-007) |
| INT-017 | "Preciso selecionar uma empresa para usar o agente?" | Seção 3 — Como usar o agente | Spec seção 5 |
| INT-018 | "O agente substitui o portal web?" | Seção 2 — O que o agente não faz | Spec seção 1 (RN-001) |
| INT-019 | "O que é o MARH?" | Seção 1 — O que é o MARH e o Espaço RH | `1CONFIG_BENE_1.md`, `2CADASTRO_INTERLO_PERFIS.md` (contexto implícito) |
| INT-020 | "O que é o Espaço RH?" | Seção 1 — O que é o MARH e o Espaço RH | Idem INT-019 — PARTIALLY_COVERED (LAC-MD-001) |
| INT-021 | "Quais tipos de pergunta posso fazer?" | Seções 2 e 3 | Spec seção 10 |

---

## Detalhamento — Grupo C (Intenções Fora do Escopo)

Para todas as intenções do Grupo C:

- **Estratégia:** REDIRECT_TO_OFFICIAL_JOURNEY
- **Fonte:** `00_Agente_Consultivo_MARH.html` seções 7.3 e 12
- **Mensagem estática:** "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH."
- **Status da fonte:** STATIC_CLIENT_DEFINED
- **Cobertura:** COVERED
- **Observação:** O elemento `[list_navigation]` é desejável para redirecionar para a jornada oficial, mas depende de identificador válido e decisão técnica sobre a URL da webview (AMB-002, DP-003).

---

## Respostas estáticas de erro (não RAG, não API)

Estas respostas são derivadas exclusivamente de `00_Agente_Consultivo_MARH.html` e não devem ser tratadas como conteúdo RAG:

| Código | Disparado quando | Mensagem |
|---|---|---|
| ERR-001 | Empresa selecionada ausente ou inválida (HTTP 422) | "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente." |
| ERR-002 | Colaborador não encontrado | "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." |
| ERR-003 | Pedido não encontrado | "Não encontrei o pedido informado para a empresa selecionada." |
| ERR-004 | Status não reconhecido | "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." |
| ERR-005 | Sem permissão (HTTP 403 — permissão) | "Você não tem permissão para consultar informações dessa empresa no Espaço RH." |
| ERR-006 | Validação de segurança não concluída (HTTP 403 — FNP/prova de vida) | "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente." |
| ERR-007 | API indisponível | "Não consegui consultar essa informação agora. Tente novamente em alguns instantes." |
| ERR-008 | Informação não disponível no markdown | "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões." |
| ERR-009 | Elemento [list_navigation] não pôde ser gerado | "Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela." |
| ERR-010 | CPF insuficiente para rastreamento | "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." |

**Fonte:** `00_Agente_Consultivo_MARH.html` seção 13 (STATIC_CLIENT_DEFINED)

---

## Verificações de consistência com o catálogo de intenções

| Verificação | Resultado |
|---|---|
| Todas as 27 intenções do catálogo estão na matriz | ✅ INT-001 a INT-027 presentes |
| Nenhuma intenção extra na matriz | ✅ |
| IDs idênticos entre catálogo e matriz | ✅ |
| Grupos idênticos (A, B, C) | ✅ |
| Estratégias coerentes com o tipo de intenção | ✅ |
| Intenções informativas apontam para seções concretas do markdown | ✅ |
| Intenções consultivas apontam para operações técnicas concretas | ✅ |
| Respostas estáticas apontam para a especificação do cliente | ✅ |
| Operações transacionais usam REDIRECT_TO_OFFICIAL_JOURNEY | ✅ |
| Nenhuma intenção marcada COVERED sem evidência | ✅ |
| A matriz não afirma mais que o markdown ainda precisa ser criado | ✅ — markdown criado em `discover3/knowledge/markdown_conhecimento_marh.md` |

---

*Fontes: `04_catalogo_intencoes.md`, `discover3/knowledge/markdown_conhecimento_marh.md`, `discover3/knowledge/validacao_markdown_conhecimento.md`, `Gestao_de_Colaboradores.html`, `Gestao_de_Pedidos.html`, `00_Agente_Consultivo_MARH.html` · Atualizado em 2026-07-22*
