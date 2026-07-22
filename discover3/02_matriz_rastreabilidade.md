# 02 — Matriz de Rastreabilidade

> Relaciona cada requisito às suas fontes documentais. Uma fonte marcada como "primária" é onde o requisito aparece como declaração explícita do cliente. Uma fonte "secundária" confirma ou complementa o requisito.

---

## Legenda de fontes

| Código | Arquivo |
|---|---|
| F01 | `docs/cliente/00_Agente_Consultivo_MARH.html` |
| F02 | `docs/cliente/Gestao_de_Colaboradores.html` |
| F03 | `docs/cliente/Gestao_de_Pedidos.html` |
| F04 | `docs/kb/1CONFIG_BENE_1.md` |
| F05 | `docs/kb/1CONFIG_BENE_REDES.md` |
| F06 | `docs/kb/2CADASTRO_INTERLO_EDITAR.md` |
| F07 | `docs/kb/2CADASTRO_INTERLO_PERFIS.md` |
| F08 | `docs/kb/3CADASTRO_COLAB_PLANILHA.md` |
| F09 | `docs/kb/3CADASTRO_COLAB_TAGS.md` |
| F10 | `docs/kb/3CADASTRO_COLAB_TELA.md` |
| F11 | `docs/kb/4PEDIDO_PLANILHA.md` |
| F12 | `docs/kb/4PEDIDO_TELA.md` |
| F13 | `docs/kb/5PAG_DISPO.md` |
| F14 | `docs/kb/5PAG_DISPO_BOLETO.md` |
| F15 | `docs/kb/5PAG_DISPO_MODELO_COBRANCA.md` |
| F16 | `docs/kb/6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md` |
| F17 | `docs/kb/6ACOMPA_PEDIDO_BOLETO_NF.md` |
| F18 | `docs/kb/6ACOMPA_PEDIDO_STATUS.md` |
| F19 | `docs/kb/7RELATORIOS.md` |
| F20 | `docs/kb/8RASTREIO_CARTOES.md` |
| F21 | `docs/kb/9VISUALIZAR_CONTRATOS.md` |
| F22 | `docs/kb/10CADASTRO_FILIAIS_TELA.md` |
| F23 | `docs/kb/10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md` |
| F24 | `docs/kb/faturamento-descentralizado.md` |
| F25 | `docs/kb/manual-emissao-2via.md` |
| F26 | `docs/reports/api_inventory.md` |
| F27 | `docs/reports/api_inventory_pedidos.md` |
| F28 | `docs/reports/api_test_report.md` |
| F29 | `docs/reports/api_test_report_pedidos.md` |
| F30 | `docs/reports/model_consumption_assessment.md` |
| F31 | `docs/reports/model_consumption_assessment_pedidos.md` |
| F32 | `artifacts/api_inventory/gestao_colaboradores_apis.json` |
| F33 | `artifacts/api_inventory/gestao_pedidos_apis.json` |
| F34 | `artifacts/api_inventory/model_data_catalog.json` |
| F35 | `artifacts/api_inventory/model_data_catalog_pedidos.json` |

---

## Requisitos Funcionais (RF)

| ID | Título Curto | Fonte Primária | Fontes Secundárias | Status |
|---|---|---|---|---|
| RF-001 | Consultar colaborador por nome ou CPF | F01 (seções 1, 8.1) | F02, F32 | CONFIRMED |
| RF-002 | Consultar pedido por número | F01 (seção 8.2) | F03, F33 | CONFIRMED |
| RF-003 | Consultar último pedido | F01 (seção 8.3) | F03, F33 | CONFIRMED |
| RF-004 | Consultar pedidos por status | F01 (seção 8.4) | F03, F27, F33 | CONFIRMED |
| RF-005 | Rastrear cartão de colaborador | F01 (seção 8.5) | F20, F33 | AMBIGUOUS |
| RF-006 | Classificar intenção da mensagem | F01 (seção 7) | — | CONFIRMED |
| RF-007 | Chamar ma-hr-orch para intenção consultiva | F01 (seções 7.1, 3) | — | CONFIRMED |
| RF-008 | Responder dúvidas MARH via markdown | F01 (seções 6, 7.2) | — | CONFIRMED |
| RF-009 | Disponibilizar agente via API REST | F01 (seção 3) | — | CONFIRMED |
| RF-010 | Retornar elemento de navegação [list_navigation] | F01 (seção 9) | — | CONFIRMED |
| RF-011 | Usar empresa selecionada como contexto obrigatório | F01 (seção 5) | — | CONFIRMED |
| RF-012 | API MARH envia contexto da empresa ao agente | F01 (seção 5) | — | CONFIRMED |
| RF-013 | Repassar contexto da empresa à ma-hr-orch | F01 (seção 5) | — | CONFIRMED |
| RF-014 | Distinguir consulta de dados vs. resposta informativa | F01 (seção 3) | — | CONFIRMED |
| RF-015 | Pedir escolha quando múltiplos colaboradores | F01 (seção 8.1) | — | CONFIRMED |
| RF-016 | Pedir esclarecimento de status não reconhecido | F01 (seção 8.4) | — | CONFIRMED |
| RF-017 | Avisar sobre ordenação incerta no último pedido | F01 (seção 8.3) | — | CONFIRMED |
| RF-018 | Versionar e revisar markdown de conhecimento | F01 (seção 6) | — | CONFIRMED |
| RF-019 | Exibir campos do pedido quando disponíveis | F01 (seção 8.2) | F03, F27, F33 | CONFIRMED |
| RF-020 | Exibir campos de rastreamento quando disponíveis | F01 (seção 8.5) | F20, F33 | CONFIRMED |

---

## Regras de Negócio (RN)

| ID | Título Curto | Fonte Primária | Fontes Secundárias | Status |
|---|---|---|---|---|
| RN-001 | Agente não executa ações transacionais | F01 (seções 1, 7.1, 8.2, 12) | — | CONFIRMED |
| RN-002 | Agente não inventa capacidades | F01 (seção 6) | — | CONFIRMED |
| RN-003 | Agente não inventa dados de rastreamento | F01 (seção 8.5) | — | CONFIRMED |
| RN-004 | Autorização/token é responsabilidade da ma-hr-orch | F01 (seção 4) | — | CONFIRMED |
| RN-005 | Elemento de navegação só quando há relação e identificador | F01 (seção 9) | — | CONFIRMED |
| RN-006 | Elemento de navegação não aciona transações | F01 (seção 9) | — | CONFIRMED |
| RN-007 | Resposta compreensível sem renderização do componente | F01 (seção 9) | — | CONFIRMED |
| RN-008 | Links de jornada não executam ação automaticamente | F01 (seção 9) | — | CONFIRMED |
| RN-009 | Configuração de benefícios: Decisão ou Gerenciamento | F04 | F07 | CONFIRMED |
| RN-010 | Sem transferência entre contas Alimentação/Refeição/Benefícios | F04, F12 | F05 | CONFIRMED |
| RN-011 | Cancelamento automático por boleto não pago em 30 dias | F18 | — | CONFIRMED |
| RN-012 | Tarifas cobradas no próximo boleto | F15 | — | CONFIRMED |
| RN-013 | 2ª via: cancela cartões ativos e não pode ser desfeita | F25 | — | CONFIRMED |
| RN-014 | CPF de colaborador não pode ser alterado após cadastro | F10 | — | CONFIRMED |
| RN-015 | Reimportar CPF atualiza dados, não duplica | F08 | — | CONFIRMED |
| RN-016 | Faturamento descentralizado: mesma raiz CNPJ, todos boletos | F24 | — | CONFIRMED |
| RN-017 | NF emitida somente após disponibilização dos créditos | F17 | F14 | CONFIRMED |
| RN-018 | API GBA não filtra pedidos por data | F03 (seção 3) | F27 | CONFIRMED |

---

## Requisitos Não Funcionais (RNF)

| ID | Título Curto | Fonte Primária | Fontes Secundárias | Status |
|---|---|---|---|---|
| RNF-001 | Agente disponível via API REST | F01 (seções 3, 14) | — | CONFIRMED |
| RNF-002 | Markdown contém todas as informações autorizadas | F01 (seção 6) | — | CONFIRMED |
| RNF-003 | URL da webview em formato URL encoded | F01 (seção 9) | — | CONFIRMED |
| RNF-004 | Quem define a URL final da webview (indefinido) | F01 (seção 9) | — | AMBIGUOUS |
| RNF-005 | Planilha de postos de trabalho: .xls/.xlsx até 15MB | F23 | — | CONFIRMED |

---

## Segurança (SEG)

| ID | Título Curto | Fonte Primária | Fontes Secundárias | Status |
|---|---|---|---|---|
| SEG-001 | ma-hr-orch valida token, interlocutor, FNP, prova de vida | F01 (seção 4) | F02, F03, F26, F27 | CONFIRMED |
| SEG-002 | Agente não permite troca de empresa pelo usuário | F01 (seções 5, 11) | — | CONFIRMED |
| SEG-003 | Agente não expõe dados técnicos sensíveis | F01 (seção 11) | — | CONFIRMED |
| SEG-004 | Elemento de navegação apenas para telas do Espaço RH | F01 (seções 11, 9) | — | CONFIRMED |
| SEG-005 | Deeplink exige usuário autenticado (authRequired=true) | F01 (seção 9) | — | CONFIRMED |
| SEG-006 | Todos endpoints exigem token OAuth2, FNP ativo, prova de vida | F02, F03 | F26, F27, F28, F29 | CONFIRMED |
| SEG-007 | Perfil Decisão definido no contrato, não no sistema | F07 | F06 | CONFIRMED |
| SEG-008 | Trocar Interlocutor de Decisão requer Central de Atendimento | F21 | — | CONFIRMED |
| SEG-009 | Agente consulta apenas dados da empresa selecionada | F01 (seção 11) | — | CONFIRMED |

---

## Tratamento de Erros (ERR)

| ID | Mensagem-chave | Fonte Primária | Seção | Status |
|---|---|---|---|---|
| ERR-001 | Empresa não identificada → selecionar no Espaço RH | F01 | Seções 5 e 13 | CONFIRMED |
| ERR-002 | Colaborador não encontrado | F01 | Seção 13 | CONFIRMED |
| ERR-003 | Pedido não encontrado | F01 | Seção 13 | CONFIRMED |
| ERR-004 | Status não reconhecido | F01 | Seções 8.4 e 13 | CONFIRMED |
| ERR-005 | Sem permissão para consultar empresa | F01 | Seção 13 | CONFIRMED |
| ERR-006 | Validação de segurança não concluída | F01 | Seção 13 | CONFIRMED |
| ERR-007 | Consulta indisponível no momento | F01 | Seção 13 | CONFIRMED |
| ERR-008 | Informação não disponível no markdown | F01 | Seções 6 e 13 | CONFIRMED |
| ERR-009 | Atalho de navegação não pôde ser gerado | F01 | Seção 13 | CONFIRMED |

---

## Critérios de Aceite (ACE)

| ID | Título Curto | Fonte Primária | Status |
|---|---|---|---|
| ACE-001 | Agente disponível via API REST | F01 seção 14 | CONFIRMED |
| ACE-002 | App consome agente via API MARH | F01 seção 14 | CONFIRMED |
| ACE-003 | API MARH envia empresa selecionada | F01 seção 14 | CONFIRMED |
| ACE-004 | Empresa selecionada como contexto obrigatório | F01 seção 14 | CONFIRMED |
| ACE-005 | Agente consulta via ma-hr-orch | F01 seção 14 | CONFIRMED |
| ACE-006 | ma-hr-orch responsável por validações de segurança | F01 seção 14 | CONFIRMED |
| ACE-007 | Agente possui markdown de conhecimento | F01 seção 14 | CONFIRMED |
| ACE-008 | Agente responde dúvidas MARH via markdown | F01 seção 14 | CONFIRMED |
| ACE-009 | Agente classifica intenção do usuário | F01 seção 14 | CONFIRMED |
| ACE-010 | Consulta colaborador por nome ou CPF | F01 seção 14 | CONFIRMED |
| ACE-011 | Consulta pedido por número | F01 seção 14 | CONFIRMED |
| ACE-012 | Retorna último pedido disponível | F01 seção 14 | CONFIRMED |
| ACE-013 | Lista pedidos por status | F01 seção 14 | CONFIRMED |
| ACE-014 | Trata status inválido | F01 seção 14 | CONFIRMED |
| ACE-015 | Informa quando não encontra dados | F01 seção 14 | CONFIRMED |
| ACE-016 | Não executa ações transacionais | F01 seção 14 | CONFIRMED |
| ACE-017 | Avalia rastreamento por CPF (pendente técnico) | F01 seção 14 | AMBIGUOUS |
| ACE-018 | Pode retornar elemento de navegação | F01 seção 14 | CONFIRMED |
| ACE-019 | Frontend interpreta [list_navigation] e abre deeplink | F01 seção 14 | CONFIRMED |
| ACE-020 | Elemento de navegação não aciona transações | F01 seção 14 | CONFIRMED |

---

## Fora do Escopo (FORA)

| ID | Ação proibida | Fonte Primária | Status |
|---|---|---|---|
| FORA-001 | Criar pedido | F01 seção 12 | CONFIRMED |
| FORA-002 | Cancelar pedido | F01 seção 12 | CONFIRMED |
| FORA-003 | Alterar pedido | F01 seção 12 | CONFIRMED |
| FORA-004 | Editar colaborador | F01 seção 12 | CONFIRMED |
| FORA-005 | Excluir colaborador | F01 seção 12 | CONFIRMED |
| FORA-006 | Alterar endereço de entrega | F01 seção 12 | CONFIRMED |
| FORA-007 | Solicitar 2ª via de cartão | F01 seção 12 | CONFIRMED |
| FORA-008 | Reemitir cartão | F01 seção 12 | CONFIRMED |
| FORA-009 | Alterar status de pedido/entrega | F01 seção 12 | CONFIRMED |
| FORA-010 | Realizar pagamento | F01 seção 12 | CONFIRMED |
| FORA-011 | Consultar empresa sem permissão | F01 seção 12 | CONFIRMED |
| FORA-012 | Responder capacidades não previstas no markdown | F01 seção 12 | CONFIRMED |
| FORA-013 | Retornar links fora do contexto do Espaço RH | F01 seção 12 | CONFIRMED |

---

## Ambiguidades e Pendências (AMB)

| ID | Descrição Resumida | Fontes Envolvidas | Bloqueador? |
|---|---|---|---|
| AMB-001 | Rastreamento por CPF depende de avaliação técnica da ma-hr-orch | F01 seção 8.5, F33 | Parcial — MVP pode funcionar sem este caminho |
| AMB-002 | Quem define a URL final da webview: API MARH, frontend ou outra camada | F01 seção 9 | Sim — necessário definir antes da implementação do elemento de navegação |
| AMB-003 | benefits-order-management sem endpoint para cadastro individual de colaborador | F02 seção 2 | Não afeta o agente diretamente (escopo consulta) |
| AMB-004 | benefits-order-management sem endpoint para exclusão de colaborador | F02 seção 4 | Não afeta o agente diretamente (escopo consulta) |
| AMB-005 | Como o agente obtém orderNumber para rastreamento iniciado por CPF | F01 seção 8.5, F27 | Sim — pode exigir lógica adicional no agente |

---

## Resumo de cobertura por fonte

| Fonte | # Requisitos rastreados | Categorias |
|---|---|---|
| F01 (Agente MARH) | 73 | RF, RN (parcial), RNF, SEG, ERR, ACE, FORA, AMB |
| F02 (Gestão Colaboradores) | 6 | RF, SEG, AMB |
| F03 (Gestão Pedidos) | 5 | RF, RN |
| F04–F25 (KB) | 12 | RN, RNF |
| F26–F31 (Reports) | 8 | SEG, RN (confirmação) |
| F32–F35 (Artifacts) | 6 | RF, SEG (confirmação) |

---

*Gerado em 2026-07-22*
