# Arquitetura AWS — POC do Agente Consultivo MARH

> **Versão:** 2.0 (revisão corretiva)
> **Data:** 2026-07-23
> **Região exclusiva:** `sa-east-1` (South America — São Paulo)
> **Status:** Desenho arquitetural — nenhum recurso criado

---

## Objetivo

Desenho da arquitetura AWS para a POC do Agente Consultivo MARH, um agente de IA conversacional
exclusivamente consultivo que responde perguntas sobre colaboradores, pedidos, rastreamento de cartões
e dúvidas sobre a feature MARH no app Meu Alelo.

## Decisão Arquitetural

**Alternativa recomendada: B — Lambda com orquestração própria**

Justificativa resumida:
- Menor custo fixo (zero quando inativo)
- Menor complexidade operacional
- Latência controlável
- Totalmente disponível em `sa-east-1`
- Controle total sobre sanitização de PII e classificação determinística

## Correções Aplicadas nesta Versão

| Área | Correção |
|---|---|
| Modelo | Claude 3.5 Haiku removido da seleção automática. Status `PROPOSED_PENDING_ACCOUNT_VALIDATION` até validação em conta real. |
| RAG | Bedrock Knowledge Bases não confirmada em sa-east-1. Desenho preferencial: Lambda → embedding → S3 Vectors direto. |
| Intenções | Mapeamento reconstruído a partir de `intents_catalog.json` real. IDs e nomes corretos. |
| LLM em API_ONLY | Removido. Templates determinísticos para INT-001 a INT-005. |
| Sanitização | CPF e nome como parâmetros técnicos transitórios — nunca no contexto do LLM. 4 camadas. |
| RBAC | Papéis `admin/rh/colaborador` removidos. Autorização delegada à ma-hr-orch. |
| Autenticação entrada | `shared secret` removido. InvokeFunction SDK (preferencial) ou Function URL AWS_IAM. |
| Rate limiting | Dicionário in-memory removido como controle global. Throttling na API MARH. |
| Circuit breaker | Distribuído in-memory removido. Retry máx 1x + fallback determinístico. |
| Campos inventados | `order_id, created_at, total_value, balance, expiry_date` etc. removidos. Apenas campos reais inventariados. |
| Performance | 3275ms classificado como `single_observed_sample_ms`. P50/P95 não derivados de uma amostra. |
| Custos | Recalculados após remoção de LLM de API_ONLY (~70% menos chamadas ao modelo). |
| Cenários POC | 12 → 16 cenários. Alinhados com catálogo real de intenções. |
| ADRs | ADR-002 (modelo), ADR-003 (RAG), ADR-015 (entrada) reabertos. ADR-014 e ADR-016 novos. |

## Estrutura dos documentos

| Documento | Conteúdo |
|---|---|
| `00_resumo_decisao.md` | Decisão final com justificativa e bloqueadores |
| `01_requisitos_arquiteturais.md` | Requisitos derivados do discovery |
| `02_disponibilidade_sa_east_1.md` | Matriz de disponibilidade regional |
| `03_alternativas_arquitetura.md` | Comparação das alternativas |
| `04_arquitetura_recomendada.md` | Arquitetura detalhada da POC |
| `05_fluxos_por_intencao.md` | Fluxos completos com 27 intenções reais |
| `06_seguranca.md` | Segurança em camadas — sem RBAC inventado |
| `07_rede_conectividade.md` | Rede e conectividade |
| `08_performance_escalabilidade.md` | Performance com premissas explícitas |
| `09_resiliencia_erros.md` | Resiliência — 1 retry máx, sem circuit breaker in-memory |
| `10_observabilidade.md` | Observabilidade e monitoramento |
| `11_estimativa_custos.md` | Custos recalculados pós-correção |
| `12_plano_poc.md` | Plano — 16 cenários, 18 dias, KB já existe |
| `13_riscos_pendencias.md` | Riscos e pendências atualizados |
| `14_adrs.md` | ADRs — 3 reabertos, 2 novos |

### Artefatos (`artifacts/`)

| Arquivo | Conteúdo |
|---|---|
| `service_region_matrix.json` | Disponibilidade de serviços em sa-east-1 |
| `latency_budget.json` | Orçamentos de latência por fluxo |
| `capacity_scenarios.json` | Cenários de carga com premissas |
| `cost_assumptions.json` | Premissas de custo |
| `security_controls.json` | Controles de segurança por camada |
| `poc_scope.json` | Escopo da POC — 16 cenários |
| `architecture_decision_matrix.json` | Matriz de decisão das alternativas |

## Restrições

- Todos os recursos em `sa-east-1`
- Sem cross-Region inference
- Sem inference profile que roteia para outra região
- Apenas operações consultivas GET
- PII como parâmetro técnico transitório — nunca no contexto do LLM
- Empresa selecionada imutável pelo chat
- Autorização delegada à ma-hr-orch — sem RBAC próprio no agente
- Modelo somente após validação ACTIVE In-Region no console da conta

## Bloqueadores Ativos

| # | Bloqueador | Prioridade |
|---|---|---|
| 1 | Conta AWS e permissões (DP-005) | P0 CRÍTICO |
| 2 | Modelo ACTIVE In-Region sa-east-1 (DP-002) | P0 CRÍTICO |
| 3 | Formato de invocação — hospedagem da API MARH (DP-001) | P0 |
| 4 | S3 Vectors em sa-east-1 (DP-003) | P1 |
| 5 | Aprovação de marh_feature_knowledge.md (DP-007) | P1 |
| 6 | Sandbox ma-hr-orch (DP-006) | P1 |

---

*Fontes: `discover3/` — Discovery concluído em 2026-07-22 · Revisão corretiva: 2026-07-23*
