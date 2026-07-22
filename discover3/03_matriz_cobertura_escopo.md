# 03 — Matriz de Cobertura de Escopo

> **Princípio:** Para cada intenção identificada no `04_catalogo_intencoes.md`, esta matriz verifica se a intenção pode ser respondida, por qual estratégia, e com qual nível de cobertura. Uma intenção só é marcada como **COBERTO** quando os 7 critérios abaixo são satisfeitos simultaneamente:
>
> 1. Existência da informação (dado existe em alguma fonte)
> 2. Fonte concreta (fonte identificada e acessível)
> 3. Atualidade (dado é retornado em tempo real ou está atualizado na KB)
> 4. Autorização (acesso autenticado e validado pela ma-hr-orch)
> 5. Campos necessários (todos os campos para resposta estão disponíveis)
> 6. Sanitização (PII e dados sensíveis tratados antes de chegar ao modelo)
> 7. Tratamento de ausência ou erro (mensagem de fallback definida)

---

## Legenda de estratégia

| Estratégia | Descrição |
|---|---|
| RAG_ONLY | Respondida exclusivamente pelo markdown de conhecimento (KB) |
| API_ONLY | Respondida por chamada à ma-hr-orch, sem necessidade de KB |
| HYBRID_RAG_API | Requer combinação de dados da API com contexto do KB |
| STATIC_RESPONSE | Resposta fixa definida no sistema (ex.: mensagem de erro padronizada) |
| REQUIRES_HUMAN | Precisa de atendimento humano — o agente deve redirecionar |
| OUT_OF_SCOPE | Fora do escopo do agente — ação transacional proibida |
| NOT_COVERED | Intenção sem fonte de resposta disponível |
| NEEDS_CLIENT_VALIDATION | Depende de decisão ou validação técnica do cliente |

## Legenda de cobertura

| Cobertura | Descrição |
|---|---|
| COBERTO | Todos os 7 critérios atendidos |
| PARCIALMENTE_COBERTO | Alguns critérios atendidos, mas há lacunas identificadas |
| NÃO_COBERTO | Critérios não atendidos — intenção não pode ser respondida adequadamente |
| CONFLITANTE | Fontes divergem sobre o comportamento ou os dados |
| NÃO_VALIDADO | Depende de validação técnica ainda não realizada |

---

## Grupo A — Intenções Consultivas (dados em tempo real)

### INT-001 — Consultar colaborador por nome

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | API `GET /v1/beneficiaries?nameOrCpf={nome}` confirmada (TEC-001) |
| Fonte concreta | ✅ | Endpoint documentado e testado com HTTP 200 (TEC-024) |
| Atualidade | ✅ | Dado em tempo real via API |
| Autorização | ✅ | Validada pela ma-hr-orch (SEG-001, TEC-015) |
| Campos necessários | ✅ | name, placeName, subtype, products disponíveis (TEC-017) |
| Sanitização | ⚠️ | CPF, email, telefone, nome da mãe e endereço devem ser filtrados antes de ir ao modelo (TEC-017) |
| Tratamento de ausência/erro | ✅ | ERR-002 definido; 403 e 422 tratados (TEC-016) |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | Sanitização de PII ainda depende de implementação na camada de integração (ma-hr-orch). Sem sanitização, campo não vai ao modelo. |
| **Requisitos relacionados** | RF-011, TEC-001, TEC-017, ERR-002 |

---

### INT-002 — Consultar colaborador por CPF

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | Mesmo endpoint `GET /v1/beneficiaries?nameOrCpf={cpf}` (TEC-001) |
| Fonte concreta | ✅ | Confirmado — parâmetro `nameOrCpf` aceita CPF |
| Atualidade | ✅ | Tempo real |
| Autorização | ✅ | Validada pela ma-hr-orch |
| Campos necessários | ✅ | Mesmos campos de INT-001 |
| Sanitização | ⚠️ | Mesmos problemas de PII de INT-001 (TEC-017) |
| Tratamento de ausência/erro | ✅ | ERR-002 definido |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | Sanitização de PII não implementada — deve ser garantida na camada de orquestração |
| **Requisitos relacionados** | RF-011, TEC-001, TEC-017, ERR-002 |

---

### INT-003 — Consultar pedido por número

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | `GET /v1/orders/{orderNumber}` confirmado (TEC-004) |
| Fonte concreta | ✅ | Endpoint testado com HTTP 200 (TEC-024) |
| Atualidade | ✅ | Tempo real |
| Autorização | ✅ | Validada pela ma-hr-orch |
| Campos necessários | ✅ | status, orderDate, totalOrder, productInfo, steps[] disponíveis (TEC-004, TEC-019) |
| Sanitização | ⚠️ | billingDocumentNumber, contractNumber, idLegalPersonBilling devem ser filtrados (TEC-019) |
| Tratamento de ausência/erro | ✅ | ERR-003 definido; 422 para empresa inválida tratado |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | Sanitização de campos restritos depende de implementação. Qtd. de colaboradores e cartões: derivar de `GET /v1/orders/{orderNumber}/beneficiaries` — endpoint extra necessário |
| **Requisitos relacionados** | RF-012, TEC-004, TEC-005, TEC-019, ERR-003 |

---

### INT-004 — Consultar último pedido

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | `GET /v1/orders` retorna lista paginada (TEC-002) |
| Fonte concreta | ✅ | Endpoint confirmado |
| Atualidade | ✅ | Tempo real |
| Autorização | ✅ | Validada pela ma-hr-orch |
| Campos necessários | ⚠️ | Lista retorna pedidos, mas **não há garantia de ordenação por data** (TEC-003, TEC-002) |
| Sanitização | ⚠️ | billingDocumentNumber, contractNumber devem ser filtrados (TEC-019) |
| Tratamento de ausência/erro | ✅ | Comportamento definido: avisar sobre ordenação incerta (RF-013) |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | A API não permite filtrar por data (TEC-003). Não há campo de ordenação confirmado. O agente deve avisar que está exibindo o pedido mais recente retornado — o que pode não ser o último cronologicamente. |
| **Requisitos relacionados** | RF-013, TEC-002, TEC-003, TEC-019 |

---

### INT-005 — Consultar pedidos por status

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | `GET /v1/orders` retorna lista com campo `status` (TEC-002) |
| Fonte concreta | ✅ | Confirmado — campo `status` presente na resposta |
| Atualidade | ✅ | Tempo real |
| Autorização | ✅ | Validada pela ma-hr-orch |
| Campos necessários | ⚠️ | A API não tem parâmetro de filtro por status no endpoint — filtro deve ser feito no agente/orquestrador sobre os resultados paginados |
| Sanitização | ⚠️ | Mesmos campos restritos de INT-003/INT-004 |
| Tratamento de ausência/erro | ✅ | ERR-004 para status não reconhecido; lista vazia tratada com resposta amigável |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | Filtro por status não está no endpoint — deve ser implementado na camada de orquestração. Para listas grandes, pode ser necessário paginar múltiplas vezes para garantir completude. Status da API são em inglês (PAID, PENDING etc.) — necessário mapeamento para português. |
| **Requisitos relacionados** | RF-014, TEC-002, TEC-022, ERR-004 |

---

### INT-006 — Rastrear cartão por CPF do colaborador

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ❌ | Endpoint de rastreamento por CPF **não foi confirmado** (TEC-027) |
| Fonte concreta | ❌ | Não há fonte técnica confirmada |
| Atualidade | N/A | — |
| Autorização | N/A | — |
| Campos necessários | N/A | — |
| Sanitização | N/A | — |
| Tratamento de ausência/erro | ✅ | Fallback confirmado: solicitar número do pedido (ERR-010, RF-017) |

| Atributo | Valor |
|---|---|
| **Estratégia** | NEEDS_CLIENT_VALIDATION |
| **Cobertura** | NÃO_VALIDADO |
| **Lacuna** | Endpoint de rastreamento por CPF não existe ou não foi confirmado na ma-hr-orch. Fallback por orderNumber é a única rota CONFIRMED (INT-007). |
| **Bloqueador MVP** | NÃO — fallback INT-007 é suficiente para a POC |
| **Requisitos relacionados** | RF-016, RF-017, AMB-001, TEC-027, ERR-010 |

---

### INT-007 — Rastrear cartão por número do pedido

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ⚠️ | Endpoint de rastreamento via ma-hr-orch mencionado, mas não inventariado diretamente nas APIs testadas |
| Fonte concreta | ⚠️ | KB confirma rastreamento (KB-028, KB-029), mas não há endpoint de API testado para rastreamento |
| Atualidade | ⚠️ | Dado deve ser em tempo real |
| Autorização | ✅ | Validada pela ma-hr-orch (presumida) |
| Campos necessários | ⚠️ | Campos definidos pelo cliente (status, data atualização, código rastreio, endereço) — não confirmados em esquema de API |
| Sanitização | ⚠️ | Endereço de entrega é PII — deve ser filtrado |
| Tratamento de ausência/erro | ✅ | ERR-007 para indisponibilidade; RN-003 proíbe inventar dados |

| Atributo | Valor |
|---|---|
| **Estratégia** | API_ONLY |
| **Cobertura** | PARCIALMENTE_COBERTO |
| **Lacuna** | Endpoint de rastreamento não foi inventariado nos testes realizados. A KB descreve a funcionalidade no portal, mas não via API. É necessário validar o contrato da API de rastreamento na ma-hr-orch. |
| **Bloqueador MVP** | SIM — endpoint precisa ser confirmado antes da implementação |
| **Requisitos relacionados** | RF-015, TEC-027, KB-028, KB-029, ERR-007 |

---

## Grupo B — Intenções Informativas sobre a feature MARH

Todas as intenções do Grupo B têm a mesma estrutura de análise:

| Critério | Status | Observação |
|---|---|---|
| Existência da informação | ✅ | KB contém informações sobre o funcionamento do MARH (KB-001 a KB-047) |
| Fonte concreta | ⚠️ | O arquivo markdown de conhecimento **ainda não existe** — deve ser criado com base na KB |
| Atualidade | ✅ | Estático — atualizado a cada evolução do escopo (RF-010, RNF-002) |
| Autorização | ✅ | Não requer chamada à ma-hr-orch |
| Campos necessários | ⚠️ | Depende do conteúdo do markdown ainda a ser criado |
| Sanitização | ✅ | Não há PII neste grupo |
| Tratamento de ausência/erro | ✅ | ERR-008 definido para informações não presentes no markdown |

| INT ID | Pergunta | Cobertura | Lacuna |
|---|---|---|---|
| INT-008 | "O que posso fazer?" | PARCIALMENTE_COBERTO | Markdown não criado; KB tem conteúdo suficiente para elaborar |
| INT-009 | "Quais informações posso consultar?" | PARCIALMENTE_COBERTO | Idem |
| INT-010 | "Como faço para fazer um pedido?" | PARCIALMENTE_COBERTO | KB tem procedimento (KB-017, KB-018), mas agente deve redirecionar — não executar |
| INT-011 | "Como faço para consultar um pedido?" | PARCIALMENTE_COBERTO | Markdown deve descrever o uso do agente consultivo, não o portal |
| INT-012 | "Como faço para consultar um colaborador?" | PARCIALMENTE_COBERTO | Idem |
| INT-013 | "Consigo rastrear cartões?" | PARCIALMENTE_COBERTO | Deve incluir aviso sobre limitação de rastreamento por CPF (AMB-001) |
| INT-014 | "Você consegue cancelar pedido?" | PARCIALMENTE_COBERTO | Resposta negativa — deve orientar para o Espaço RH |
| INT-015 | "Você consegue alterar dados de um colaborador?" | PARCIALMENTE_COBERTO | Idem |
| INT-016 | "Você consulta dados de qualquer empresa?" | PARCIALMENTE_COBERTO | Deve explicar contexto de empresa selecionada (RF-007) |
| INT-017 | "Preciso selecionar uma empresa para usar o agente?" | PARCIALMENTE_COBERTO | Idem |
| INT-018 | "O agente substitui o portal web?" | PARCIALMENTE_COBERTO | Scope explicito: apenas consultivo, não transacional |
| INT-019 | "O que é o MARH?" | PARCIALMENTE_COBERTO | KB e especificação têm definição — markdown deve consolidar |
| INT-020 | "O que é o Espaço RH?" | PARCIALMENTE_COBERTO | Idem |
| INT-021 | "Quais tipos de pergunta posso fazer?" | PARCIALMENTE_COBERTO | Markdown deve listar explicitamente as 7 intenções do Grupo A |

**Estratégia para todo o Grupo B:** RAG_ONLY  
**Cobertura geral do Grupo B:** PARCIALMENTE_COBERTO  
**Lacuna principal:** O arquivo markdown de conhecimento (RF-010, RNF-002) ainda precisa ser criado. A KB tem o conteúdo necessário, mas o arquivo de runtime ainda não existe.

---

## Grupo C — Intenções Fora do Escopo

Todas as intenções do Grupo C têm o mesmo tratamento:

| INT ID | Exemplo | Estratégia | Cobertura | Resposta |
|---|---|---|---|---|
| INT-022 | "Cancela o pedido 342671." | OUT_OF_SCOPE | COBERTO | "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH." |
| INT-023 | "Altera o endereço do colaborador." | OUT_OF_SCOPE | COBERTO | Idem |
| INT-024 | "Cria um novo pedido." | OUT_OF_SCOPE | COBERTO | Idem |
| INT-025 | "Remove esse colaborador." | OUT_OF_SCOPE | COBERTO | Idem |
| INT-026 | "Paga o pedido." | OUT_OF_SCOPE | COBERTO | Idem |
| INT-027 | "Emite um novo cartão." | OUT_OF_SCOPE | COBERTO | Idem |

**Observação:** Estas intenções estão COBERTO porque o comportamento está definido, as mensagens são estáticas, não requerem dados externos e não há lacunas de implementação.

---

## Resumo de cobertura

| Cobertura | Intenções | IDs |
|---|---|---|
| COBERTO | 6 | INT-022 a INT-027 |
| PARCIALMENTE_COBERTO | 19 | INT-001 a INT-005, INT-007, INT-008 a INT-021 |
| NÃO_COBERTO | 0 | — |
| NÃO_VALIDADO | 1 | INT-006 |
| CONFLITANTE | 0 | — |
| **Total** | **26** (INT-006 = NÃO_VALIDADO) | |

> **Nota:** INT-007 aparece em PARCIALMENTE_COBERTO porque, embora o comportamento seja definido, o endpoint de rastreamento via ma-hr-orch ainda não foi inventariado nos testes.

---

## Estratégias por intenção

| Estratégia | Intenções | IDs |
|---|---|---|
| API_ONLY | 5 | INT-001 a INT-005, INT-007 |
| RAG_ONLY | 14 | INT-008 a INT-021 |
| OUT_OF_SCOPE | 6 | INT-022 a INT-027 |
| NEEDS_CLIENT_VALIDATION | 1 | INT-006 |

---

*Fontes: `04_catalogo_intencoes.md`, `02_conhecimento_rag.md`, `03_capacidades_restricoes_tecnicas.md`, `01_requisitos_cliente.md` · Gerado em 2026-07-22*
