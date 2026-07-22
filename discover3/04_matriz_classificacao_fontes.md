# 04 — Matriz de Separação das Fontes

> Este documento mapeia cada informação relevante do projeto à sua fonte real, ao tipo de fonte e ao documento de destino correto. Serve de referência para garantir que requisitos, fatos de domínio e capacidades técnicas estejam nos lugares certos.

---

## Legenda de tipos de fonte

| Tipo | Descrição |
|---|---|
| CLIENT_SPECIFICATION | Documento de especificação fornecido pelo cliente |
| RAG_KNOWLEDGE | Base de conhecimento para RAG — procedimentos, fatos de domínio |
| API_DOCUMENTATION | Documentação técnica de API (contratos, schemas) |
| API_REAL_RESPONSE | Dados reais obtidos em testes executados |
| TECHNICAL_REPORT | Relatórios de inventário, consumo e testes |
| TEST_RESULT | Resultado de execução de testes |

## Legenda de classificações

| Classificação | Descrição |
|---|---|
| CLIENT_REQUIREMENT | Exigência do cliente sobre o comportamento do agente |
| KNOWLEDGE_FACT | Fato de domínio ou procedimento disponível para RAG |
| TECHNICAL_CAPABILITY | Capacidade técnica confirmada da API |
| TECHNICAL_LIMITATION | Limitação técnica confirmada da API |
| OBSERVED_BEHAVIOR | Comportamento observado em testes reais |
| RECOMMENDATION | Recomendação técnica (não exigência do cliente) |
| GAP | Lacuna — informação necessária mas ausente nas fontes |
| CONFLICT | Contradição entre fontes |

---

## Matriz

| Informação | Fonte | Tipo da fonte | Classificação correta | Documento de destino |
|---|---|---|---|---|
| Agente deve responder perguntas consultivas sobre colaboradores, pedidos, rastreamento e dúvidas MARH | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 1 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-001) |
| Agente não deve criar, alterar, cancelar ou executar ações transacionais | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 1 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RN-001) |
| Agente deve classificar intenção da mensagem antes de responder | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 7 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-002) |
| Para intenção consultiva, chamar ma-hr-orch e responder com base nos dados | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 7.1 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-003) |
| Para intenção informativa MARH, responder exclusivamente pelo markdown | docs\cliente\00_Agente_Consultivo_MARH.html — Seções 6 e 7.2 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-004) |
| Para intenção fora do escopo, orientar o usuário para o Espaço RH | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 7.3 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-005) |
| Agente disponível via API REST no Espaço RH | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 3 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-006, RNF-001) |
| Empresa selecionada é contexto obrigatório em todas as consultas | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 5 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-007) |
| API MARH envia contexto da empresa ao agente (parâmetros esperados) | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 5 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-008) |
| Agente repassa contexto da empresa à ma-hr-orch | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 5 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-009) |
| Markdown de conhecimento deve ser versionado e revisado a cada alteração | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 6 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-010) |
| Consulta de colaborador por nome ou CPF, múltiplos resultados pede escolha | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.1 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-011) |
| Consulta de pedido por número, exibir campos disponíveis, sem ações | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.2 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-012) |
| Consulta do último pedido com aviso sobre ordenação incerta | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.3 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-013) |
| Consulta de pedidos por status, pedir esclarecimento se não reconhecido | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.4 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-014) |
| Rastreamento de cartão — exibir campos disponíveis, não inventar | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.5 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-015) |
| Elemento de navegação [list_navigation] com deeplink | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 9 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RF-016) |
| URL da webview em formato URL encoded | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 9 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (RNF-003) |
| Quem define a URL final da webview — indefinido | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 9 | CLIENT_SPECIFICATION | GAP | 01_requisitos_cliente.md (RNF-004, AMB-002) |
| ma-hr-orch valida token, interlocutor, FNP, prova de vida | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 4 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-001) |
| Agente não permite troca de empresa pelo chat | docs\cliente\00_Agente_Consultivo_MARH.html — Seções 5 e 11 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-002) |
| Agente não expõe tokens, integrações ou dados sensíveis | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 11 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-003) |
| Elemento de navegação apenas para telas do Espaço RH | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 11 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-004) |
| Deeplink exige authRequired=true | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 9 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-005) |
| Agente consulta apenas dados da empresa selecionada via ma-hr-orch | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 11 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (SEG-006) |
| 9 mensagens de erro padronizadas + mensagem para CPF insuficiente no rastreio | docs\cliente\00_Agente_Consultivo_MARH.html — Seções 5, 6, 8.5, 13 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (ERR-001 a ERR-010) |
| 20 critérios de aceite explícitos na seção 14 | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 14 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (ACE-001 a ACE-020) |
| 13 ações fora do escopo explicitadas na seção 12 | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 12 | CLIENT_SPECIFICATION | CLIENT_REQUIREMENT | 01_requisitos_cliente.md (FORA-001 a FORA-013) |
| Rastreamento por CPF depende de avaliação técnica com o time | docs\cliente\00_Agente_Consultivo_MARH.html — Seção 8.5 | CLIENT_SPECIFICATION | GAP | 01_requisitos_cliente.md (AMB-001) |
| Somente perfil Decisão ou Gerenciamento pode configurar benefícios | docs\kb\1CONFIG_BENE_1.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-001) |
| Não é permitida transferência entre contas Alimentação, Refeição e Benefícios | docs\kb\1CONFIG_BENE_REDES.md e docs\kb\4PEDIDO_TELA.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-006) |
| CPF de colaborador não pode ser alterado após o cadastro | docs\kb\3CADASTRO_COLAB_TELA.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-013) |
| Reimportar planilha com CPF já cadastrado atualiza dados (não duplica) | docs\kb\3CADASTRO_COLAB_PLANILHA.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-014) |
| Cancelamento automático de pedido: boleto não pago em 30 dias | docs\kb\6ACOMPA_PEDIDO_STATUS.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-026) |
| Tarifas do pedido cobradas no próximo boleto (exceto 1º pedido) | docs\kb\5PAG_DISPO_MODELO_COBRANCA.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-022) |
| Reemissão de 2ª via cancela cartões ativos e é irreversível | docs\kb\manual-emissao-2via.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-037) |
| NF emitida somente após disponibilização dos créditos | docs\kb\6ACOMPA_PEDIDO_BOLETO_NF.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-024) |
| Perfil Decisão definido no contrato — não pode ser atribuído pelo sistema | docs\kb\2CADASTRO_INTERLO_PERFIS.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-007) |
| Para alterar Interlocutor de Decisão, acionar Central de Atendimento | docs\kb\9VISUALIZAR_CONTRATOS.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-011) |
| Faturamento descentralizado: mesma raiz de CNPJ | docs\kb\faturamento-descentralizado.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-034) |
| Planilha de postos de trabalho: .xls/.xlsx até 15MB | docs\kb\10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md | RAG_KNOWLEDGE | KNOWLEDGE_FACT | 02_conhecimento_rag.md (KB-033) |
| GET /v1/beneficiaries aceita filtro por nome ou CPF e retorna lista paginada | docs\cliente\Gestao_de_Colaboradores.html seção 1; gestao_colaboradores_apis.json | API_DOCUMENTATION | TECHNICAL_CAPABILITY | 03_capacidades_restricoes_tecnicas.md (TEC-001) |
| GET /v1/orders não permite filtro por data | docs\cliente\Gestao_de_Pedidos.html seção 3; api_inventory_pedidos.md | API_DOCUMENTATION | TECHNICAL_LIMITATION | 03_capacidades_restricoes_tecnicas.md (TEC-003) |
| Endpoints /v1/orders/{orderNumber}/* dependem de orderNumber prévio | api_inventory_pedidos.md; api_test_report_pedidos.md | TECHNICAL_REPORT | TECHNICAL_CAPABILITY | 03_capacidades_restricoes_tecnicas.md (TEC-005) |
| GET /v1/orders/{orderNumber}/invoice retorna 422 quando sem NF | api_test_report_pedidos.md | TEST_RESULT | OBSERVED_BEHAVIOR | 03_capacidades_restricoes_tecnicas.md (TEC-007) |
| Campo content do boleto é base64 do PDF — não deve ir ao modelo | model_consumption_assessment_pedidos.md; model_data_catalog_pedidos.json | TECHNICAL_REPORT | RECOMMENDATION | 03_capacidades_restricoes_tecnicas.md (TEC-011) |
| GET /v1/products e /v1/benefits são candidatos a RAG (sem PII) | model_consumption_assessment_pedidos.md | TECHNICAL_REPORT | RECOMMENDATION | 03_capacidades_restricoes_tecnicas.md (TEC-012, TEC-013) |
| Todos os endpoints exigem Authorization, APP_VERSION, client_id, FNP, PLATFORM, Content-Type, X-BASIC-AUTHORIZATION, USER_ID | Gestao_de_Colaboradores.html; gestao_colaboradores_apis.json | API_DOCUMENTATION | TECHNICAL_CAPABILITY | 03_capacidades_restricoes_tecnicas.md (TEC-015) |
| Endpoints retornam 403 (sem permissão, FNP/prova de vida NOK) e 422 (empresa inválida) | Gestao_de_Colaboradores.html; Gestao_de_Pedidos.html | API_DOCUMENTATION | TECHNICAL_CAPABILITY | 03_capacidades_restricoes_tecnicas.md (TEC-016) |
| Resposta de GET /v1/beneficiaries contém PII (CPF, email, telefone, nome da mãe) | model_consumption_assessment.md; model_data_catalog.json | TECHNICAL_REPORT | RECOMMENDATION | 03_capacidades_restricoes_tecnicas.md (TEC-017) |
| POST/PUT/DELETE de colaboradores existem mas não foram testados (SKIPPED_SAFETY) | api_inventory.md; api_test_report.md | TECHNICAL_REPORT | OBSERVED_BEHAVIOR | 03_capacidades_restricoes_tecnicas.md (TEC-021) |
| Status possíveis em pedidos: IN_PROCESSING, PENDING, PAID, CREDITED, CANCELLED, REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED | Gestao_de_Pedidos.html seção 3 | API_DOCUMENTATION | DOCUMENTED_BEHAVIOR | 03_capacidades_restricoes_tecnicas.md (TEC-022) |
| benefits-order-management não possui endpoint para cadastro individual de colaborador — débito técnico | Gestao_de_Colaboradores.html seção 2 | API_DOCUMENTATION | CONFLICT | 03_capacidades_restricoes_tecnicas.md (TEC-025) |
| benefits-order-management não possui endpoint para exclusão de colaborador — débito técnico | Gestao_de_Colaboradores.html seção 4 | API_DOCUMENTATION | CONFLICT | 03_capacidades_restricoes_tecnicas.md (TEC-026) |
| Rastreamento por CPF via ma-hr-orch — sem evidência técnica de existência do endpoint | 00_Agente_Consultivo_MARH.html seção 8.5; api_inventory_pedidos.md | API_DOCUMENTATION | GAP | 03_capacidades_restricoes_tecnicas.md (TEC-027) |
| GET /v1/beneficiaries retornou HTTP 200 em 3.275ms em teste real (2026-07-22) | api_test_report.md | TEST_RESULT | OBSERVED_BEHAVIOR | 03_capacidades_restricoes_tecnicas.md (TEC-024) |
| GET /v1/orders retornou HTTP 200 em 782ms em teste real (2026-07-22) | api_test_report_pedidos.md | TEST_RESULT | OBSERVED_BEHAVIOR | 03_capacidades_restricoes_tecnicas.md (TEC-024) |

---

## Resumo de distribuição

| Tipo de informação | Qtd | Documento de destino |
|---|---|---|
| CLIENT_REQUIREMENT | 86 itens | 01_requisitos_cliente.md |
| KNOWLEDGE_FACT | 39 itens (KB-001 a KB-039, KB-040 a KB-047) | 02_conhecimento_rag.md |
| TECHNICAL_CAPABILITY / LIMITATION / OBSERVED / DOCUMENTED | 27 itens (TEC-001 a TEC-027) | 03_capacidades_restricoes_tecnicas.md |
| GAP / CONFLICT | 5 itens | Identificados nos documentos respectivos |

---

*Gerado em 2026-07-22*
