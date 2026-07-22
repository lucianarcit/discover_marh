# 00 — Resumo Executivo: Discovery do Agente Consultivo MARH

> **Data do discovery:** 2026-07-22  
> **Versão:** 1.0  
> **Decisão de GO/NO-GO:** **GO_COM_RESSALVAS** — sustentado por evidências documentadas neste relatório

---

## 1. Fontes analisadas

| # | Tipo | Arquivo | Status |
|---|---|---|---|
| F01 | Especificação do cliente | `docs/cliente/00_Agente_Consultivo_MARH.html` | Lido integralmente (14 seções) |
| F02 | Documentação técnica de API | `docs/cliente/Gestao_de_Colaboradores.html` | Lido integralmente |
| F03 | Documentação técnica de API | `docs/cliente/Gestao_de_Pedidos.html` | Lido com apoio dos relatórios de inventário |
| F04–F25 | Base de conhecimento (KB) | `docs/kb/` — 22 arquivos Markdown | Todos lidos |
| F26–F29 | Relatórios de inventário e testes | `docs/reports/` | Todos lidos |
| F30–F35 | Catálogos de dados e schemas de API | `artifacts/api_inventory/` | Todos lidos |

**Total de fontes analisadas:** 36 (35 legíveis, 1 pasta sem extensão identificável)

Testes reais de integração foram executados em 2026-07-22 no ambiente de homologação (UAT), confirmando HTTP 200 para `GET /v1/beneficiaries` (3.275ms) e para `GET /v1/orders` (782ms).

---

## 2. Requisitos identificados

| Categoria | Prefixo | Qtd |
|---|---|---|
| Requisitos Funcionais | RF | 18 |
| Regras de Negócio | RN | 14 |
| Requisitos Não Funcionais | RNF | 4 |
| Segurança | SEG | 7 |
| Tratamento de Erros | ERR | 10 |
| Critérios de Aceite (cliente) | ACE | 20 |
| Fora do Escopo | FORA | 13 |
| Ambiguidades | AMB | 2 |
| **Total** | | **88** |

Todos os requisitos são rastreáveis ao documento `docs/cliente/00_Agente_Consultivo_MARH.html`. Nenhum requisito foi inferido.

---

## 3. Intenções do usuário identificadas

**Total: 27 intenções**, distribuídas em 3 grupos:

| Grupo | Tipo | Qtd | Exemplos do cliente |
|---|---|---|---|
| A | CONSULTIVA (dados em tempo real) | 7 | Consultar colaborador, pedido, último pedido, pedidos por status, rastrear cartão |
| B | INFORMATIVA_MARH (markdown) | 14 | "O que posso fazer?", "O que é o MARH?", "Você cancela pedido?" |
| C | FORA_DO_ESCOPO | 6 | Cancelar pedido, criar pedido, alterar endereço |

Todas as intenções foram extraídas diretamente das seções 6, 7.1, 7.2, 7.3, 8.1–8.5 e 10 da especificação do cliente.

---

## 4. Cobertura atual das intenções

| Cobertura | Qtd | Detalhes |
|---|---|---|
| **COBERTO** | 6 | INT-022 a INT-027 — fora do escopo (respostas estáticas definidas) |
| **PARCIALMENTE_COBERTO** | 19 | Grupos A e B — APIs confirmadas mas com lacunas em sanitização, mapeamento de status ou markdown não criado |
| **NÃO_VALIDADO** | 1 | INT-006 — rastreamento por CPF depende de validação técnica |
| **NÃO_COBERTO** | 0 | Nenhuma intenção sem qualquer caminho de resposta |

**Cobertura plena (COBERTO):** 22% das intenções  
**Com lacunas resolvíveis (PARCIALMENTE_COBERTO):** 70%  
**Aguardando validação técnica:** 4% (INT-006 — não bloqueia o MVP)

---

## 5. APIs disponíveis e confirmadas

| Endpoint | Status | Latência | Uso no agente |
|---|---|---|---|
| `GET /v1/beneficiaries` | CONFIRMADO | 3.275ms (UAT) | INT-001, INT-002 |
| `GET /v1/orders` | CONFIRMADO | 782ms (UAT) | INT-004, INT-005 |
| `GET /v1/orders/{orderNumber}` | CONFIRMADO | — | INT-003 |
| `GET /v1/orders/{orderNumber}/beneficiaries` | CONFIRMADO | — | INT-003 (qtd. colaboradores) |
| `GET /v1/orders/{orderNumber}/invoice` | CONFIRMADO (422 esperado) | — | INT-003 (NF) |
| `GET /v1/orders/{orderNumber}/bank-ticket` | CONFIRMADO | — | INT-003 (boleto) |
| `GET /v1/products` | CONFIRMADO (candidato RAG) | — | INT-008/009 |
| `GET /v1/benefits` | CONFIRMADO (candidato RAG) | — | INT-008/009 |
| Endpoint de rastreamento por orderNumber | **NÃO INVENTARIADO** | — | INT-007 — LAC-001 |
| Endpoint de rastreamento por CPF | **NÃO CONFIRMADO** | — | INT-006 — AMB-001 |

Limitações técnicas críticas confirmadas:
- `GET /v1/orders` **não filtra por data** (TEC-003) — impacta INT-004 e INT-005
- `GET /v1/orders` **não filtra por status no servidor** — filtro deve ser feito no agente (LAC-004)
- Resposta de colaboradores contém PII que não pode chegar ao modelo (TEC-017)

---

## 6. Capacidade RAG identificada

**47 itens de KB** analisados de 22 arquivos Markdown em `docs/kb/`:

| Status | Qtd | Observação |
|---|---|---|
| AVAILABLE_FOR_RAG | 35 | Prontos para consolidação no markdown de conhecimento |
| PARTIALLY_AVAILABLE | 3 | Conteúdo informativo disponível, mas requer aviso de que agente não executa a ação |
| OUT_OF_AGENT_SCOPE | 5 | Descrevem ações transacionais — agente informa mas não executa |
| CONFLICTING | 2 | KB-025 (status da KB vs. API) e KB-028 (rastreamento portal vs. API) |

**Lacuna crítica:** O arquivo markdown de conhecimento de runtime (RF-010, RNF-002) **ainda não foi criado**. O conteúdo existe na KB, mas o arquivo de runtime está ausente — LAC-003 (BLOQUEADOR_MVP).

---

## 7. Lacunas identificadas

| ID | Momento | Descrição | Impacto |
|---|---|---|---|
| **LAC-001** | BLOQUEADOR_MVP | Endpoint de rastreamento por orderNumber não inventariado | Rastreamento real não implementável |
| **LAC-003** | BLOQUEADOR_MVP | Arquivo markdown de conhecimento não criado | 14 intenções informativas retornariam ERR-008 |
| **LAC-006** | BLOQUEADOR_MVP | Sanitização de PII na ma-hr-orch não confirmada | PII pode chegar ao modelo e ao usuário |
| LAC-002 | BLOQUEADOR_PILOTO | Rastreamento por CPF não confirmado | Fricção no piloto — fallback disponível |
| LAC-004 | BLOQUEADOR_PILOTO | Filtro de status sem suporte no endpoint | Lista de pedidos pode ser incompleta |
| LAC-005 | BLOQUEADOR_PILOTO | Ordenação de último pedido não garantida | "Último pedido" pode não ser o mais recente |
| LAC-007 | BLOQUEADOR_PILOTO | URL da webview ([list_navigation]) sem responsável definido | Componente de navegação não implementável |
| LAC-008 | BLOQUEADOR_PILOTO | Mapeamento de status API→português incompleto | Exibição incorreta de status ao usuário |
| LAC-009 | BLOQUEADOR_PILOTO | Qtd. de cartões requer chamada adicional | Campo pode ser omitido ou impreciso |
| LAC-010 | BLOQUEADOR_PRODUCAO | rpsLink pode expor CNPJ na URL | Exposição de dado fiscal |

**Total de lacunas:** 10 (3 bloqueadoras do MVP, 6 do piloto, 1 da produção)

---

## 8. Conflitos entre fontes

| ID | Fontes | Descrição | Classificação |
|---|---|---|---|
| **CF-001** | API (Gestao_de_Pedidos.html) vs. KB (6ACOMPA_PEDIDO_STATUS.md) | API retorna 10 status em inglês; KB documenta 6 em português — 4 sem mapeamento validado | CONFLITANTE |
| **CF-002** | KB (8RASTREIO_CARTOES.md) vs. ausência de endpoint de API | KB descreve rastreamento no portal web; spec fala em endpoint de API — fontes descrevem coisas diferentes | CONFLITANTE |
| **CF-003** | Spec (RF-012) vs. campos disponíveis na API | Spec exige qtd. de cartões, mas endpoint de detalhe do pedido não tem esse campo | CONFLITANTE |

---

## 9. Riscos identificados

| Risco | Severidade | Mitigação disponível |
|---|---|---|
| PII chega ao modelo de linguagem se sanitização não estiver implementada | ALTO | Confirmar com ma-hr-orch (DP-006) antes do build |
| Prompt injection contorna restrições de escopo | ALTO | Testes adversariais obrigatórios (BL-020) |
| Agente exibe dados de rastreamento inventados | ALTO | Instrução RN-003 + CA-017 + EV-012 |
| Endpoint de rastreamento não existe na ma-hr-orch | MÉDIO | Fallback (solicitar orderNumber) cobre MVP |
| Lista de pedidos por status incompleta sem paginação correta | MÉDIO | Definir estratégia de paginação (DP-005) |
| Status de pedido exibido em inglês ao usuário | MÉDIO | Mapeamento completo com cliente (DP-004) |
| Agente afirma ser o "último pedido" sem garantia de ordenação | BAIXO | Aviso obrigatório definido na spec (RF-013) |

---

## 10. Decisões pendentes do cliente

| ID | Impacto | Pergunta central | Responsável |
|---|---|---|---|
| **DP-006** | BLOQUEADOR_MVP | ma-hr-orch filtra PII antes de retornar ao agente? | MA_HR_ORCH |
| **DP-001** | BLOQUEADOR_PILOTO | Endpoint de rastreamento por orderNumber existe? | MA_HR_ORCH |
| **DP-002** | BLOQUEADOR_PILOTO | Rastreamento por CPF é viável? | MA_HR_ORCH |
| **DP-003** | BLOQUEADOR_PILOTO | Quem monta a URL da webview? | ARQUITETURA |
| **DP-004** | BLOQUEADOR_PILOTO | Labels em português para os 10 status da API? | CLIENTE |
| **DP-005** | BLOQUEADOR_PILOTO | Estratégia de paginação para filtro de status? | ARQUITETURA |
| DP-007 | MELHORIA | GET /v1/orders suporta ordenação por data? | MA_HR_ORCH |
| DP-008 | MELHORIA | total de beneficiaries = total de cartões? | MA_HR_ORCH |

**Total:** 8 decisões pendentes — 1 bloqueadora do MVP, 5 bloqueadoras do piloto, 2 de melhoria.

---

## 11. Backlog resumido

| Fase | MUST | SHOULD | Total |
|---|---|---|---|
| **MVP** | 12 itens | 0 | 12 |
| **Piloto** | 2 itens | 4 itens | 6 |
| **Produção** | 3 itens | 1 item | 4 |
| **Futuro** | 0 | 0 | 4 (LATER) |

**Itens MVP obrigatórios:** BL-001 a BL-012 — todos rastreáveis à especificação do cliente.

---

## 12. Critérios de aceite e avaliação

**Critérios de aceite definidos:** 37 (35 MUST, 2 SHOULD)  
**Casos de avaliação:** 50, cobrindo 12 categorias:

| Categoria | Qtd |
|---|---|
| Pergunta simples | 5 |
| Pergunta ambígua | 4 |
| Informação ausente | 5 |
| API indisponível | 3 |
| Usuário sem permissão | 3 |
| Tentativa de outra empresa | 3 |
| Identificador inválido | 4 |
| Conflito RAG vs. API | 3 |
| Tentativa de dados sensíveis | 5 |
| Prompt injection | 4 |
| Continuidade de conversa | 5 |
| Fora do escopo | 6 |

**Limiar de aprovação:** 100% dos critérios MUST + ≥90% dos 50 casos + zero PII exposto + zero alucinações em dados ausentes.

---

## 13. Recomendação de MVP

### O que está confirmado e pode ser construído

Com base no discovery realizado, os seguintes itens têm requisitos claros, APIs testadas e comportamento definido na especificação:

1. Agente disponível via API REST com classificação de intenção (BL-001, BL-003)
2. Consulta de colaborador por nome ou CPF (BL-005) — API confirmada, PII filtrado
3. Consulta de pedido por número (BL-006) — API confirmada, campos restritos filtrados
4. Consulta do último pedido com aviso de ordenação (BL-007)
5. Consulta de pedidos por status com mapeamento (BL-008)
6. Fallback de rastreamento por CPF → solicitar orderNumber (BL-009)
7. Tratamento de todos os erros definidos na seção 13 (BL-010)
8. Regras de segurança e proteção contra troca de empresa (BL-011)
9. Resposta estática para ações fora do escopo (BL-012)
10. Markdown de conhecimento (BL-004) — conteúdo existe na KB, arquivo precisa ser criado

### O que NÃO deve estar no MVP sem resolução prévia

- Rastreamento de cartão em tempo real (LAC-001 — endpoint não inventariado)
- Elemento [list_navigation] (LAC-007 — responsável pela URL indefinido)
- Mapeamento completo de status em português (LAC-008 — sem validação do cliente)

---

## 14. Condições para iniciar o Build

Para que o build do MVP possa ser iniciado com segurança, as seguintes condições devem ser atendidas:

| # | Condição | Status atual | Responsável |
|---|---|---|---|
| 1 | Confirmar que ma-hr-orch filtra PII antes de retornar ao agente (DP-006) | **PENDENTE** | MA_HR_ORCH |
| 2 | Criar o arquivo markdown de conhecimento (LAC-003, BL-004) | **PENDENTE** | Time de build |
| 3 | Definir contrato da API de rastreamento por orderNumber (DP-001) | **PENDENTE** | MA_HR_ORCH |
| 4 | Aprovar mapeamento de status inglês→português (DP-004) | **PENDENTE** | CLIENTE |

Condições 1 e 2 são pré-requisito para iniciar o build. Condição 3 pode ser resolvida em paralelo (o fallback de solicitar orderNumber está disponível). Condição 4 é necessária antes da validação de INT-005.

---

## 15. Decisão Final

### **GO_COM_RESSALVAS**

**Evidências que sustentam o GO:**

1. O escopo do agente está completamente especificado no documento do cliente — 88 itens rastreáveis, zero inferências.
2. As APIs de colaboradores e pedidos foram testadas com sucesso em ambiente de homologação (HTTP 200 em 2026-07-22).
3. Os comportamentos de erro, segurança e fora do escopo estão totalmente definidos com mensagens exatas.
4. O fallback de rastreamento por CPF está confirmado como comportamento válido para o MVP.
5. 35 dos 47 itens de KB estão disponíveis para o markdown de conhecimento.
6. Nenhuma intenção do catálogo é classificada como NÃO_COBERTO — todas têm pelo menos um caminho de resposta.

**Ressalvas que impedem um GO limpo:**

1. **LAC-006/DP-006 (CRÍTICO):** Sanitização de PII pela ma-hr-orch não confirmada. Sem isso, CPF, email e dados fiscais podem chegar ao modelo de linguagem — risco de violação de SEG-003.
2. **LAC-001/DP-001:** Endpoint de rastreamento não inventariado — rastreamento em tempo real não pode ser implementado no MVP sem esta informação.
3. **LAC-003:** Markdown de conhecimento não criado — 14 intenções informativas retornarão ERR-008 até que o arquivo exista.

**O que NÃO é GO:**

- O build não deve ser iniciado antes de DP-006 ser respondida afirmativamente com evidência (confirmação técnica de que a ma-hr-orch filtra PII).
- Se DP-006 for negativa (ma-hr-orch não filtra PII), o build deve incluir a camada de sanitização como pré-requisito obrigatório antes de qualquer chamada ao modelo de linguagem.

---

## Localização dos documentos

| Documento | Caminho |
|---|---|
| **Este resumo executivo** | `discover3/00_resumo_executivo.md` |
| Requisitos do cliente | `discover3/01_requisitos_cliente.md` |
| Conhecimento RAG | `discover3/02_conhecimento_rag.md` |
| Capacidades técnicas das APIs | `discover3/03_capacidades_restricoes_tecnicas.md` |
| Matriz de cobertura de escopo | `discover3/03_matriz_cobertura_escopo.md` |
| Catálogo de intenções | `discover3/04_catalogo_intencoes.md` |
| Matriz de fontes de resposta | `discover3/05_matriz_fontes_resposta.md` |
| Análise de lacunas | `discover3/06_analise_lacunas.md` |
| Critérios de aceite | `discover3/12_criterios_aceite.md` |
| Plano de avaliação | `discover3/13_plano_avaliacao.md` |
| **Backlog do MVP** | `discover3/14_backlog_mvp.md` |
| **Decisões pendentes** | `discover3/15_decisoes_pendentes_cliente.md` |
| JSON: intenções | `discover3/artifacts/intents_catalog.json` |
| JSON: cobertura | `discover3/artifacts/scope_coverage_matrix.json` |
| JSON: mapa RAG | `discover3/artifacts/rag_knowledge_map.json` |
| JSON: capacidades API | `discover3/artifacts/api_capability_map.json` |
| JSON: testes de aceite | `discover3/artifacts/acceptance_tests.json` |
| JSON: dataset de avaliação | `discover3/artifacts/evaluation_dataset.json` |

---

*Discovery concluído em 2026-07-22 · Fontes: 36 arquivos analisados · Versão 1.0*
