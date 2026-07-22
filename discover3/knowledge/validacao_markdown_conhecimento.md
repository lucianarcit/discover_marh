# Validação do Markdown Consolidado de Conhecimento MARH

> **Princípio:** Este documento registra a análise de todos os arquivos de `docs/kb` para verificar o que foi incluído, o que foi excluído e por quê, além de conflitos, lacunas e itens que precisam de validação pelo cliente.
>
> Não oculta divergências. Registra o que foi observado, não o que seria ideal.

---

## 1. Arquivos da KB analisados

| # | Arquivo | Temas encontrados |
|---|---|---|
| 1 | `1CONFIG_BENE_1.md` | Configuração de benefícios, perfis permitidos, modalidades, regras de transferência |
| 2 | `1CONFIG_BENE_REDES.md` | Redes de aceitação por modalidade (Alimentação, Refeição, Multibenefícios) |
| 3 | `2CADASTRO_INTERLO_PERFIS.md` | Quatro perfis de interlocutores, tabela de funções e responsabilidades |
| 4 | `2CADASTRO_INTERLO_EDITAR.md` | Fluxo de cadastro de interlocutor (2 etapas), edição, bloqueio, exclusão |
| 5 | `3CADASTRO_COLAB_TELA.md` | Cadastro manual de colaborador, campos obrigatórios, CPF imutável, edição e exclusão |
| 6 | `3CADASTRO_COLAB_PLANILHA.md` | Importação por planilha (.xls/.xlsx), atualização de CPF já existente, colunas do modelo |
| 7 | `3CADASTRO_COLAB_TAGS.md` | Tags de produto associadas ao colaborador ao entrar em pedido |
| 8 | `4PEDIDO_PLANILHA.md` | Pedido via planilha, 5 etapas, estrutura das colunas, alerta de validação de CPF |
| 9 | `4PEDIDO_TELA.md` | Pedido via tela, 5 etapas, seleção manual de colaboradores, regra de transferência |
| 10 | `5PAG_DISPO.md` | Forma de pagamento (boleto), disponibilização automática e agendada |
| 11 | `5PAG_DISPO_BOLETO.md` | Geração e pagamento do boleto, prazo de compensação (2 dias úteis), fluxo completo |
| 12 | `5PAG_DISPO_MODELO_COBRANCA.md` | Modelo de cobrança: tarifas no próximo boleto, exceção no 1º pedido |
| 13 | `6ACOMPA_PEDIDO_STATUS.md` | 6 status de pedidos, cancelamento automático por boleto vencido (30 dias), ações na tela |
| 14 | `6ACOMPA_PEDIDO_BOLETO_NF.md` | Boleto disponível após confirmação, NF emitida após disponibilização dos créditos |
| 15 | `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md` | Alterar data de crédito (apenas pedidos pagos, sem tarifa adicional) |
| 16 | `7RELATORIOS.md` | 4 tipos de relatórios, status dos relatórios, colunas da listagem |
| 17 | `8RASTREIO_CARTOES.md` | Rastreio de cartões no portal web, status, detalhe por AR, busca por CPF |
| 18 | `9VISUALIZAR_CONTRATOS.md` | Dados do contrato, tarifas, alteração do Interlocutor de Decisão via Central |
| 19 | `10CADASTRO_FILIAIS_TELA.md` | Cadastro de filiais via tela, 3 etapas, responsáveis por cartões e NF |
| 20 | `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md` | Postos de trabalho via planilha, limite de 15MB, atualização de CNPJ existente |
| 21 | `faturamento-descentralizado.md` | Faturamento descentralizado, mesma raiz CNPJ, boletos separados por CNPJ |
| 22 | `manual-emissao-2via.md` | 2ª via por perda ou roubo, cancelamento automático dos cartões ativos, prazo 7–10 dias úteis |

**Total analisado:** 22 arquivos

---

## 2. Temas incluídos no markdown consolidado

| Seção no markdown | Arquivos de origem | Status |
|---|---|---|
| O que é o MARH e o Espaço RH | `1CONFIG_BENE_1.md`, `2CADASTRO_INTERLO_PERFIS.md` + spec | COVERED |
| O que o agente pode e não pode fazer | `00_Agente_Consultivo_MARH.html` (seções 1, 7.3, 12) | COVERED |
| Como usar o agente | `00_Agente_Consultivo_MARH.html` (seções 5, 8.1–8.5, 10) | COVERED |
| Perfis de interlocutores | `2CADASTRO_INTERLO_PERFIS.md`, `2CADASTRO_INTERLO_EDITAR.md` | COVERED |
| Configuração de benefícios | `1CONFIG_BENE_1.md`, `1CONFIG_BENE_REDES.md` | COVERED |
| Colaboradores | `3CADASTRO_COLAB_TELA.md`, `3CADASTRO_COLAB_PLANILHA.md`, `3CADASTRO_COLAB_TAGS.md` | COVERED |
| Pedidos | `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md`, `6ACOMPA_PEDIDO_STATUS.md` | COVERED |
| Status dos pedidos | `6ACOMPA_PEDIDO_STATUS.md` | COVERED |
| Boleto e Nota Fiscal | `6ACOMPA_PEDIDO_BOLETO_NF.md`, `5PAG_DISPO_BOLETO.md` | COVERED |
| Modelo de cobrança | `5PAG_DISPO_MODELO_COBRANCA.md` | COVERED |
| Alterar data de disponibilização | `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md` | COVERED |
| Rastreamento de cartões | `8RASTREIO_CARTOES.md`, `manual-emissao-2via.md` | COVERED |
| Emissão de 2ª via | `manual-emissao-2via.md` | COVERED (informativo — agente não executa) |
| Relatórios disponíveis | `7RELATORIOS.md` | COVERED (informativo — agente não gera) |
| Contratos | `9VISUALIZAR_CONTRATOS.md`, `2CADASTRO_INTERLO_EDITAR.md` | COVERED (informativo) |
| Locais de entrega e filiais | `10CADASTRO_FILIAIS_TELA.md`, `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md`, `faturamento-descentralizado.md` | COVERED (informativo) |

---

## 3. Temas excluídos e motivo

| Tema | Arquivo de origem | Motivo da exclusão |
|---|---|---|
| Detalhes do formulário de cadastro de filial via tela (passo a passo completo) | `10CADASTRO_FILIAIS_TELA.md` | Operação transacional; o agente não cadastra filiais. O conteúdo informativo (regras de responsáveis e CNPJ) foi preservado. |
| Detalhes do formulário de cadastro de colaborador (campos de endereço residencial) | `3CADASTRO_COLAB_TELA.md` | Dados pessoais detalhados (endereço, CEP, município) — PII não necessário para fins informativos. |
| Exemplos de linhas de planilha com dados pessoais fictícios | `3CADASTRO_COLAB_PLANILHA.md`, `4PEDIDO_PLANILHA.md` | Contêm CPFs e e-mails fictícios que não devem compor o arquivo de conhecimento do agente. |
| Exemplos de colaboradores na tela com CPF visível | `3CADASTRO_COLAB_TAGS.md` | Contém CPF fictício (727.575.480-00) — removido. |
| Tabela de exemplo de reemissão com CPFs de colaboradores | `manual-emissao-2via.md` | Contém CPFs fictícios (082.154.151-32 repetido) — removidos. |
| Colunas completas da planilha de posto de trabalho (edição/exclusão passo a passo) | `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md` | Detalhes operacionais de edição e exclusão via sistema — ações transacionais, não informativas. |
| Botões de navegação e caminhos de menu detalhados | Todos os arquivos | Detalhes de UI (nomes de botões, caminhos de menu) não são necessários para respostas informativas. |
| Detalhes internos do faturamento descentralizado (campos técnicos do formulário) | `faturamento-descentralizado.md` | Detalhes de formulário técnico; apenas as regras informativas foram preservadas. |

---

## 4. Conteúdos duplicados identificados

| Conteúdo duplicado | Arquivos envolvidos | Resolução |
|---|---|---|
| Regra de não-transferência entre contas Alimentação, Refeição e Benefícios | `1CONFIG_BENE_1.md` e `4PEDIDO_TELA.md` | Consolidado uma vez na seção de Configuração de Benefícios (seção 5). |
| Fluxo de 5 etapas do pedido | `4PEDIDO_PLANILHA.md` e `4PEDIDO_TELA.md` | Unificado na seção de Pedidos (seção 7) com nota de que se aplica a ambas as formas. |
| Prazo de compensação do boleto (2 dias úteis) | `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md` e `6ACOMPA_PEDIDO_BOLETO_NF.md` | Consolidado uma vez na seção de Boleto e Nota Fiscal (seção 9). |
| Regra de cancelamento automático por boleto vencido (30 dias) | `6ACOMPA_PEDIDO_STATUS.md` (implícito em `5PAG_DISPO_BOLETO.md`) | Consolidado uma vez na seção de Pedidos (seção 7). |
| Prazo de entrega de cartões reemitidos e rastreio | `8RASTREIO_CARTOES.md` e `manual-emissao-2via.md` | Ambas as referências mantidas nas seções 12 e 13 por contextos distintos. |

---

## 5. Conflitos identificados entre arquivos da KB

### CF-KB-001 — Status dos pedidos: KB lista 6, API lista 10

| Campo | Detalhe |
|---|---|
| **Arquivos** | `6ACOMPA_PEDIDO_STATUS.md` vs. API `cardholders-hr-management/v1` (documentada em `Gestao_de_Pedidos.html`) |
| **Conflito** | A KB documenta 6 status em português: Aguardando pagamento, Pagamento confirmado, Nota Fiscal Emitida, Aguardando Disponibilização, Pedido creditado, Cancelado. A API retorna 10 status em inglês: IN_PROCESSING, PENDING, PAID, CREDITED, CANCELLED, REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED. |
| **Impacto** | O markdown foi construído com os 6 status da KB. Os status REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED e PARTIAL_REFUNDED não têm correspondência validada na KB. |
| **Status** | CONFLICTING |
| **Ação necessária** | Confirmar com o cliente quais labels em português devem ser exibidos para os 4 status adicionais da API (DP-004 no discovery). |

### CF-KB-002 — Rastreamento de cartões: KB descreve o portal web, não um endpoint de API

| Campo | Detalhe |
|---|---|
| **Arquivos** | `8RASTREIO_CARTOES.md` vs. especificação do agente (`00_Agente_Consultivo_MARH.html` seção 8.5) |
| **Conflito** | A KB descreve o rastreamento como uma funcionalidade do portal web com busca por CPF. A especificação do agente prevê rastreamento via `ma-hr-orch`, mas o endpoint não foi confirmado. |
| **Impacto** | A KB não pode ser usada como fonte de dados em tempo real para a consulta consultiva (INT-007). Para o uso informativo (INT-013), o conteúdo da KB está disponível. |
| **Status** | CONFLICTING |
| **Resolução aplicada** | O markdown usa a KB como fonte informativa (o que é rastreamento, quais status existem). Para dados em tempo real, a fonte é a API via `ma-hr-orch`. As duas fontes estão claramente separadas no markdown. |

### CF-KB-003 — Responsável pela funcionalidade de usuários responsáveis pela entrega

| Campo | Detalhe |
|---|---|
| **Arquivo** | `10CADASTRO_FILIAIS_TELA.md` |
| **Conflito** | O arquivo informa que "usuários cadastrados apenas para ser responsável pela entrega são uma funcionalidade em desenvolvimento (opção desativada temporariamente)". |
| **Impacto** | O texto sugere que a funcionalidade está incompleta. Pode desatualizar-se. |
| **Status** | POSSIBLY_OUTDATED |
| **Resolução aplicada** | Informação não incluída no markdown. Mencionada aqui para validação. |

---

## 6. Informações possivelmente desatualizadas

| Informação | Arquivo | Motivo |
|---|---|---|
| "Em breve a funcionalidade [rastreio de cartões] estará disponível também no Sistema de Pedidos Alelo." | `6ACOMPA_PEDIDO_STATUS.md` | Pode já ter sido implementada. Não incluída no markdown. |
| Funcionalidade de responsável pela entrega "desativada temporariamente" | `10CADASTRO_FILIAIS_TELA.md` | Status de desenvolvimento; pode ter mudado. |
| "A emissão de 2ª via de cartões é uma nova funcionalidade." | `manual-emissao-2via.md` | Linguagem de lançamento que pode estar desatualizada. Não incluída no markdown. |
| Datas de exemplo nos documentos (2024, 2025) | Múltiplos arquivos | Exemplos com datas específicas (ex.: "21 de Junho de 2024"). Não incluídos no markdown. |

---

## 7. Lacunas identificadas

### LAC-MD-001 — Definição formal de MARH e Espaço RH ausente na KB

| Campo | Detalhe |
|---|---|
| **Problema** | Nenhum arquivo da KB define explicitamente o que é o MARH ou o Espaço RH. A seção 1 do markdown foi construída com base no contexto implícito dos arquivos e na especificação do cliente. |
| **Status** | NEEDS_CLIENT_VALIDATION |
| **Impacto** | As intenções INT-019 e INT-020 têm cobertura parcial — o conteúdo informativo foi deduzido do contexto. |

### LAC-MD-002 — Informações sobre o app Meu Alelo ausentes na KB

| Campo | Detalhe |
|---|---|
| **Problema** | A KB descreve funcionalidades do portal web (Sistema de Pedidos). Não há descrição sobre o app Meu Alelo, suas telas ou sua navegação. |
| **Status** | NEEDS_CLIENT_VALIDATION |
| **Impacto** | Perguntas sobre "o que é o app Meu Alelo" ou "como o app funciona" não têm fonte na KB. |

### LAC-MD-003 — Tabela de mapeamento de status API→português não validada

| Campo | Detalhe |
|---|---|
| **Problema** | O markdown documenta os 6 status da KB. Os 4 status adicionais da API (REJECTED, RELEASED, IN_BILLING_PROCESSING, REFUNDED, PARTIAL_REFUNDED) não foram validados com o cliente (CF-KB-001). |
| **Status** | NEEDS_CLIENT_VALIDATION |
| **Impacto** | Intenções INT-005 e INT-003 podem exibir status incorretos ou em inglês. |

### LAC-MD-004 — Rastreamento por CPF via agente não tem confirmação técnica

| Campo | Detalhe |
|---|---|
| **Problema** | O agente prevê rastreamento por CPF, mas o endpoint não foi confirmado. O markdown informa que o agente solicitará o número do pedido nesse caso. |
| **Status** | NEEDS_CLIENT_VALIDATION |
| **Impacto** | INT-006 está coberta apenas pelo fallback (solicitar número do pedido). |

---

## 8. Itens que precisam de validação do cliente

| ID | Item | Impacto |
|---|---|---|
| VC-001 | Definição formal de MARH e Espaço RH (LAC-MD-001) | INT-019, INT-020 |
| VC-002 | Mapeamento completo de status API→português (CF-KB-001, LAC-MD-003) | INT-003, INT-005 |
| VC-003 | Confirmação técnica do endpoint de rastreamento por orderNumber (LAC-001) | INT-007 |
| VC-004 | Confirmação técnica do endpoint de rastreamento por CPF (AMB-001) | INT-006 |
| VC-005 | Funcionalidade de responsável pela entrega "desativada" — atualizar status | Seção 16 do markdown |
| VC-006 | Validação geral do conteúdo do markdown antes do uso em produção | Todos os itens do Grupo B |

---

## 9. Cobertura das intenções informativas (Grupo B)

| INT ID | Pergunta | Seção no markdown | Status | Observação |
|---|---|---|---|---|
| INT-008 | "O que posso fazer?" | Seção 2 | COVERED | Seção completa com consultas disponíveis e ações proibidas |
| INT-009 | "Quais informações posso consultar?" | Seções 2, 3 | COVERED | Consultas disponíveis e exemplos |
| INT-010 | "Como faço para fazer um pedido?" | Seção 7 | COVERED | Fluxo de 5 etapas descrito; agente orienta para o Espaço RH |
| INT-011 | "Como faço para consultar um pedido?" | Seção 3 | COVERED | Instrução clara: informar número do pedido no chat |
| INT-012 | "Como faço para consultar um colaborador?" | Seção 3 | COVERED | Instrução clara: informar nome ou CPF no chat |
| INT-013 | "Consigo rastrear cartões?" | Seção 12 | COVERED | Sim — pelo número do pedido. CPF em avaliação técnica. |
| INT-014 | "Você consegue cancelar pedido?" | Seção 2 | COVERED | Não — agente redireciona para o Espaço RH |
| INT-015 | "Você consegue alterar dados de um colaborador?" | Seção 2 | COVERED | Não — agente redireciona para o Espaço RH |
| INT-016 | "Você consulta dados de qualquer empresa?" | Seção 3 | COVERED | Apenas empresa selecionada no app |
| INT-017 | "Preciso selecionar uma empresa para usar o agente?" | Seção 3 | COVERED | Sim — contexto obrigatório |
| INT-018 | "O agente substitui o portal web?" | Seção 2 | COVERED | Não — apenas consultas; ações via portal |
| INT-019 | "O que é o MARH?" | Seção 1 | PARTIALLY_COVERED | Definição construída por contexto — sem fonte explícita na KB. Requer VC-001. |
| INT-020 | "O que é o Espaço RH?" | Seção 1 | PARTIALLY_COVERED | Idem INT-019. Requer VC-001. |
| INT-021 | "Quais tipos de pergunta posso fazer?" | Seção 2 e 3 | COVERED | Lista explícita das 5 consultas disponíveis |

**Resumo:**
- COVERED: 12 intenções (INT-008 a INT-018, INT-021)
- PARTIALLY_COVERED: 2 intenções (INT-019, INT-020)
- NOT_COVERED: 0

---

## 10. Verificações obrigatórias

| Verificação | Status | Observação |
|---|---|---|
| O markdown foi criado | ✅ | `discover3/knowledge/markdown_conhecimento_marh.md` |
| Cada conteúdo possui fonte em `docs/kb` | ✅ | Seções 1–17 com indicação de fontes |
| Nenhum conteúdo da API foi incluído como conhecimento informativo | ✅ | Endpoints, headers e tokens não estão presentes |
| Nenhuma regra de KB foi transformada em requisito do cliente | ✅ | As regras de KB são informações de domínio, não exigências do agente |
| Dados pessoais reais excluídos | ✅ | CPFs, e-mails e endereços dos exemplos da KB foram removidos |
| Conteúdo transacional indicado como redirecionamento | ✅ | Seções 2, 13, 14, 16 orientam para o Espaço RH |
| Conflitos documentados | ✅ | CF-KB-001, CF-KB-002, CF-KB-003 |
| Lacunas documentadas | ✅ | LAC-MD-001 a LAC-MD-004 |
| IDs consistentes com o catálogo de intenções | ✅ | INT-008 a INT-021 verificados |

---

*Gerado em 2026-07-22 · 22 arquivos da KB analisados*
