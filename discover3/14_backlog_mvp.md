# 14 — Backlog do MVP

> **Princípio:** Itens derivados dos requisitos confirmados do cliente (`01_requisitos_cliente.md`) e das lacunas identificadas (`06_analise_lacunas.md`). Cada item é rastreável a pelo menos um requisito ou lacuna. Recomendações técnicas que não têm origem em requisito do cliente estão marcadas como COULD ou LATER.

---

## Legenda de prioridade

| Prioridade | Significado |
|---|---|
| MUST | Obrigatório — sem este item o MVP não pode ser entregue |
| SHOULD | Importante para o piloto — sem este item a experiência do usuário é comprometida |
| COULD | Agrega valor mas não é bloqueador |
| LATER | Evolução futura — não deve ser priorizado nas primeiras entregas |

## Legenda de fase

| Fase | Descrição |
|---|---|
| MVP | Deve estar presente na POC de demonstração |
| PILOTO | Necessário para o piloto com usuários reais |
| PRODUCAO | Necessário antes do go-live em produção |
| FUTURO | Evolução após produção estável |

---

## Fase MVP — O mínimo para demonstrar o agente funcionando

### BL-001 — Configurar agente com endpoint REST

| Campo | Valor |
|---|---|
| **ID** | BL-001 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Disponibilizar o agente via API REST para ser consumido pela API MARH |
| **Critérios de aceite** | CA-001 |
| **Requisitos** | RF-006, RNF-001, ACE-001 |
| **Dependências** | Nenhuma |

### BL-002 — Implementar recebimento e validação do contexto de empresa

| Campo | Valor |
|---|---|
| **ID** | BL-002 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | O agente deve receber o contexto da empresa selecionada via API MARH e retornar ERR-001 quando ausente |
| **Critérios de aceite** | CA-002, CA-027 |
| **Requisitos** | RF-007, RF-008, RF-009, RN-011, ERR-001 |
| **Dependências** | BL-001 |

### BL-003 — Implementar classificador de intenção

| Campo | Valor |
|---|---|
| **ID** | BL-003 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | O agente deve classificar cada mensagem em: CONSULTIVA, INFORMATIVA_MARH ou FORA_DO_ESCOPO antes de responder |
| **Critérios de aceite** | CA-003, CA-004, CA-005 |
| **Requisitos** | RF-002, ACE-009 |
| **Dependências** | BL-001, BL-004 (markdown), BL-005 (ma-hr-orch) |

### BL-004 — Criar arquivo markdown de conhecimento

| Campo | Valor |
|---|---|
| **ID** | BL-004 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Criar o arquivo markdown de conhecimento consolidando: escopo do agente, as 5 consultas disponíveis, limitações, definição de MARH e Espaço RH, e ações que o agente não executa |
| **Critérios de aceite** | CA-004, CA-018, CA-019, CA-020 |
| **Requisitos** | RF-004, RF-010, RNF-002, ACE-007, ACE-008 |
| **Lacunas** | LAC-003 |
| **Dependências** | Nenhuma — pode ser feito em paralelo |
| **Fontes de conteúdo** | `docs/kb/` + `01_requisitos_cliente.md` seções 1, 6, 8.1–8.5, 12 |

### BL-005 — Integrar com ma-hr-orch: consulta de colaboradores

| Campo | Valor |
|---|---|
| **ID** | BL-005 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar chamada a `GET /v1/beneficiaries` via ma-hr-orch, com filtragem de PII antes de enviar ao modelo |
| **Critérios de aceite** | CA-006, CA-007, CA-008, CA-009 |
| **Requisitos** | RF-011, ACE-010 |
| **Lacunas** | LAC-006 |
| **Dependências** | BL-002 |
| **Nota técnica** | Campos a filtrar: documentNumber, email, phoneNumber, motherName, address (TEC-017) |

### BL-006 — Integrar com ma-hr-orch: consulta de pedido por número

| Campo | Valor |
|---|---|
| **ID** | BL-006 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar chamada a `GET /v1/orders/{orderNumber}` com filtragem de campos restritos |
| **Critérios de aceite** | CA-010, CA-011, CA-015 |
| **Requisitos** | RF-012, ACE-011 |
| **Lacunas** | LAC-006 |
| **Dependências** | BL-002 |
| **Nota técnica** | Campos a filtrar: billingDocumentNumber, contractNumber, idLegalPersonBilling (TEC-019) |

### BL-007 — Integrar com ma-hr-orch: consulta de último pedido

| Campo | Valor |
|---|---|
| **ID** | BL-007 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar chamada a `GET /v1/orders` para retornar o pedido mais recente, com aviso de ordenação incerta |
| **Critérios de aceite** | CA-012 |
| **Requisitos** | RF-013, ACE-012 |
| **Lacunas** | LAC-005 |
| **Dependências** | BL-002 |

### BL-008 — Integrar com ma-hr-orch: consulta de pedidos por status

| Campo | Valor |
|---|---|
| **ID** | BL-008 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar filtro de status sobre `GET /v1/orders` com mapeamento inglês→português e tratamento de status não reconhecido |
| **Critérios de aceite** | CA-013, CA-014 |
| **Requisitos** | RF-014, ACE-013, ACE-014, ERR-004 |
| **Lacunas** | LAC-004, LAC-008 |
| **Dependências** | BL-002 |
| **Nota técnica** | Mapeamento de status necessário — CF-001 |

### BL-009 — Implementar fallback de rastreamento por CPF

| Campo | Valor |
|---|---|
| **ID** | BL-009 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Quando o usuário solicitar rastreamento por CPF, o agente deve solicitar o número do pedido com a mensagem ERR-010 |
| **Critérios de aceite** | CA-016 |
| **Requisitos** | RF-017, RN-014, ERR-010, ACE-017 |
| **Dependências** | BL-003 |

### BL-010 — Implementar tratamento de todos os erros definidos

| Campo | Valor |
|---|---|
| **ID** | BL-010 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar as 10 mensagens de erro padronizadas (ERR-001 a ERR-010) com os textos exatos definidos na seção 13 da especificação |
| **Critérios de aceite** | CA-002, CA-008, CA-011, CA-014, CA-016, CA-022, CA-023, CA-026, CA-027 |
| **Requisitos** | ERR-001 a ERR-010, RN-010 |
| **Dependências** | BL-005, BL-006, BL-007, BL-008 |

### BL-011 — Implementar regras de segurança do agente

| Campo | Valor |
|---|---|
| **ID** | BL-011 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Implementar: (1) bloquear troca de empresa pelo chat, (2) não expor tokens/dados técnicos, (3) não inventar capacidades, (4) não executar ações transacionais |
| **Critérios de aceite** | CA-021, CA-024, CA-025, CA-031, CA-032, CA-033 |
| **Requisitos** | SEG-002, SEG-003, SEG-006, RN-001, RN-002 |
| **Dependências** | BL-003 |

### BL-012 — Implementar resposta para intenções fora do escopo

| Campo | Valor |
|---|---|
| **ID** | BL-012 |
| **Fase** | MVP |
| **Prioridade** | MUST |
| **Descrição** | Para qualquer ação transacional, retornar: "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH." |
| **Critérios de aceite** | CA-005 |
| **Requisitos** | RF-005, FORA-001 a FORA-013 |
| **Dependências** | BL-003 |

---

## Fase PILOTO — Necessário para usuários reais

### BL-013 — Confirmar e integrar endpoint de rastreamento por orderNumber

| Campo | Valor |
|---|---|
| **ID** | BL-013 |
| **Fase** | PILOTO |
| **Prioridade** | MUST |
| **Descrição** | Inventariar o endpoint de rastreamento via ma-hr-orch, implementar chamada e filtrar campo de endereço (PII) |
| **Critérios de aceite** | CA-017 |
| **Requisitos** | RF-015, RN-003 |
| **Lacunas** | LAC-001 (bloqueador do MVP para rastreamento real) |
| **Dependências** | BL-002, decisão técnica da ma-hr-orch |

### BL-014 — Implementar mapeamento completo de status de pedidos

| Campo | Valor |
|---|---|
| **ID** | BL-014 |
| **Fase** | PILOTO |
| **Prioridade** | MUST |
| **Descrição** | Criar tabela de mapeamento validada com o cliente para todos os 10 status da API (inglês) → labels em português, incluindo os status sem correspondência na KB |
| **Critérios de aceite** | CA-013 |
| **Requisitos** | TEC-022, RF-014 |
| **Lacunas** | LAC-008, CF-001 |
| **Dependências** | Validação com cliente |

### BL-015 — Implementar estratégia de paginação para filtro de status

| Campo | Valor |
|---|---|
| **ID** | BL-015 |
| **Fase** | PILOTO |
| **Prioridade** | SHOULD |
| **Descrição** | Definir e implementar estratégia de paginação ao filtrar pedidos por status (quantas páginas consultar, como informar ao usuário se lista pode estar incompleta) |
| **Critérios de aceite** | CA-013 |
| **Requisitos** | RF-014, TEC-002, TEC-003 |
| **Lacunas** | LAC-004 |
| **Dependências** | BL-008 |

### BL-016 — Implementar elemento de navegação [list_navigation]

| Campo | Valor |
|---|---|
| **ID** | BL-016 |
| **Fase** | PILOTO |
| **Prioridade** | SHOULD |
| **Descrição** | Implementar geração do elemento [list_navigation] com deeplink `meualelo://app/webview`, somente quando o identificador estiver disponível |
| **Critérios de aceite** | CA-028, CA-029, CA-030 |
| **Requisitos** | RF-018, RN-005, RN-006, RN-007, SEG-004, SEG-005 |
| **Lacunas** | LAC-007 (URL final da webview — aguarda decisão de arquitetura) |
| **Dependências** | Decisão arquitetural AMB-002 |

### BL-017 — Confirmar sanitização de rpsLink da Nota Fiscal

| Campo | Valor |
|---|---|
| **ID** | BL-017 |
| **Fase** | PILOTO |
| **Prioridade** | SHOULD |
| **Descrição** | Validar com a ma-hr-orch que a URL do rpsLink não expõe CNPJ ou dados fiscais antes de exibir ao usuário |
| **Critérios de aceite** | CA-037 |
| **Requisitos** | TEC-009, SEG-003 |
| **Lacunas** | LAC-010 |
| **Dependências** | BL-006 |

### BL-018 — Implementar continuidade de conversa com manutenção de contexto

| Campo | Valor |
|---|---|
| **ID** | BL-018 |
| **Fase** | PILOTO |
| **Prioridade** | SHOULD |
| **Descrição** | O agente deve manter o contexto da empresa selecionada e referências a colaboradores/pedidos ao longo de uma conversa multi-turno |
| **Critérios de aceite** | CA-034 |
| **Requisitos** | RF-007, RF-009 |
| **Dependências** | BL-002, BL-003 |

---

## Fase PRODUÇÃO — Necessário antes do go-live

### BL-019 — Validar e certificar sanitização de PII na ma-hr-orch

| Campo | Valor |
|---|---|
| **ID** | BL-019 |
| **Fase** | PRODUCAO |
| **Prioridade** | MUST |
| **Descrição** | Confirmar formalmente (com teste de integração documentado) que a camada ma-hr-orch filtra CPF, email, telefone, nome da mãe, endereço e campos fiscais antes de retornar ao agente |
| **Critérios de aceite** | CA-009, CA-015, CA-036 |
| **Requisitos** | SEG-003, TEC-017, TEC-018, TEC-019, TEC-011 |
| **Lacunas** | LAC-006 |

### BL-020 — Auditoria de segurança: prompt injection e adversarial inputs

| Campo | Valor |
|---|---|
| **ID** | BL-020 |
| **Fase** | PRODUCAO |
| **Prioridade** | MUST |
| **Descrição** | Executar bateria de testes adversariais (prompt injection, extração de dados técnicos, tentativa de bypass de autorização) antes do go-live |
| **Critérios de aceite** | CA-024, CA-025 |
| **Requisitos** | SEG-003, RN-002 |
| **Dependências** | BL-011 concluído e em produção |

### BL-021 — Implementar monitoramento e alertas de erros do agente

| Campo | Valor |
|---|---|
| **ID** | BL-021 |
| **Fase** | PRODUCAO |
| **Prioridade** | SHOULD |
| **Descrição** | Logging estruturado de: erros de classificação, chamadas com falha à ma-hr-orch, taxa de ERR-007, incidentes de possível PII na resposta |
| **Critérios de aceite** | — (não derivado de requisito do cliente — decisão técnica) |
| **Requisitos** | — |
| **Nota** | Este item é uma recomendação técnica, não um requisito do cliente |

### BL-022 — Versionamento e processo de atualização do markdown de conhecimento

| Campo | Valor |
|---|---|
| **ID** | BL-022 |
| **Fase** | PRODUCAO |
| **Prioridade** | MUST |
| **Descrição** | Definir processo formal de atualização do markdown de conhecimento a cada evolução do escopo do agente, conforme exigido pelo cliente |
| **Critérios de aceite** | — |
| **Requisitos** | RF-010, RNF-002 |
| **Dependências** | BL-004 |

---

## Fase FUTURO — Evolução após produção estável

### BL-023 — Rastreamento direto por CPF do colaborador

| Campo | Valor |
|---|---|
| **ID** | BL-023 |
| **Fase** | FUTURO |
| **Prioridade** | LATER |
| **Descrição** | Implementar rastreamento por CPF quando a ma-hr-orch confirmar a existência e o contrato do endpoint |
| **Requisitos** | RF-016, AMB-001 |
| **Lacunas** | LAC-002 |
| **Dependências** | Validação técnica da ma-hr-orch |

### BL-024 — Filtro de pedidos por data

| Campo | Valor |
|---|---|
| **ID** | BL-024 |
| **Fase** | FUTURO |
| **Prioridade** | LATER |
| **Descrição** | Solicitar à ma-hr-orch implementação de filtro por data no endpoint `GET /v1/orders` para suportar consultas como "pedidos dos últimos 30 dias" |
| **Requisitos** | TEC-003 |
| **Lacunas** | LAC-005 |
| **Nota** | Limitação da API documentada em TEC-003 — necessita mudança no endpoint |

### BL-025 — Expansão do escopo consultivo (novos dados)

| Campo | Valor |
|---|---|
| **ID** | BL-025 |
| **Fase** | FUTURO |
| **Prioridade** | LATER |
| **Descrição** | Avaliar expansão do escopo para incluir: consulta de contratos, relatórios, saldo de disponibilização |
| **Requisitos** | — (não há requisito atual para estes temas) |
| **Nota** | Expansão de escopo requer nova especificação do cliente |

### BL-026 — Capacidades transacionais (criação e alteração)

| Campo | Valor |
|---|---|
| **ID** | BL-026 |
| **Fase** | FUTURO |
| **Prioridade** | LATER |
| **Descrição** | Avaliar extensão do agente para suportar ações transacionais (criação de pedido, edição de colaborador) em versão futura do produto |
| **Requisitos** | — (explicitamente fora do escopo atual — FORA-001 a FORA-013) |
| **Nota** | Requer nova especificação do cliente e revisão completa das regras de segurança |

---

## Resumo por fase e prioridade

### MVP

| ID | Prioridade | Descrição |
|---|---|---|
| BL-001 | MUST | Endpoint REST do agente |
| BL-002 | MUST | Contexto de empresa |
| BL-003 | MUST | Classificador de intenção |
| BL-004 | MUST | Markdown de conhecimento |
| BL-005 | MUST | Integração colaboradores |
| BL-006 | MUST | Integração pedido por número |
| BL-007 | MUST | Integração último pedido |
| BL-008 | MUST | Integração pedidos por status |
| BL-009 | MUST | Fallback rastreamento por CPF |
| BL-010 | MUST | Tratamento de erros (10 mensagens) |
| BL-011 | MUST | Regras de segurança |
| BL-012 | MUST | Resposta para fora do escopo |

**Total MVP:** 12 itens MUST

### Piloto

| ID | Prioridade | Descrição |
|---|---|---|
| BL-013 | MUST | Rastreamento por orderNumber (endpoint real) |
| BL-014 | MUST | Mapeamento de status validado |
| BL-015 | SHOULD | Paginação para filtro de status |
| BL-016 | SHOULD | Elemento [list_navigation] |
| BL-017 | SHOULD | Sanitização rpsLink NF |
| BL-018 | SHOULD | Continuidade de conversa |

**Total Piloto:** 2 MUST, 4 SHOULD

### Produção

| ID | Prioridade | Descrição |
|---|---|---|
| BL-019 | MUST | Certificação de sanitização PII |
| BL-020 | MUST | Auditoria adversarial |
| BL-021 | SHOULD | Monitoramento |
| BL-022 | MUST | Versionamento do markdown |

**Total Produção:** 3 MUST, 1 SHOULD

### Futuro

| ID | Prioridade | Descrição |
|---|---|---|
| BL-023 | LATER | Rastreamento por CPF |
| BL-024 | LATER | Filtro por data |
| BL-025 | LATER | Expansão do escopo |
| BL-026 | LATER | Capacidades transacionais |

---

*Fontes: `01_requisitos_cliente.md`, `06_analise_lacunas.md`, `12_criterios_aceite.md` · Gerado em 2026-07-22*
