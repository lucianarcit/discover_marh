# Documentação — Índice da Fase 3 RAG

Índice cronológico dos documentos da Fase 3 do Agente Consultivo MARH.

---

## Fase 3 — RAG (Retrieval-Augmented Generation)

| # | Documento | Status | Resultado principal |
|---|---|---|---|
| Plano | [fase-3-plano.md](fase-3-plano.md) | Aprovado | Arquitetura RAG, ADR-001, dataset de avaliação |
| Passo 2 | *(config.py — sem doc separado)* | Concluído | `DATA_SOURCE_MODE`, `KNOWLEDGE_MODE`, `RETRIEVAL_SCORE_THRESHOLD` |
| Passo 3 | [fase-3-step-3-rag-interfaces.md](fase-3-step-3-rag-interfaces.md) | Concluído | `Retriever`, `LanguageModelClient`, `RetrievedChunk`, `GenerationResult` |
| Passo 4 | [fase-3-step-4-bedrock-rag-knowledge-client.md](fase-3-step-4-bedrock-rag-knowledge-client.md) | Concluído | `BedrockRagKnowledgeClient` com fakes — 14 tópicos, threshold, fallback |
| Passo 5 | [fase-3-step-5-bedrock-knowledge-base-retriever.md](fase-3-step-5-bedrock-knowledge-base-retriever.md) | Concluído | `BedrockKnowledgeBaseRetriever` — Retrieve real via Bedrock |
| Passo 6 | [fase-3-step-6-bedrock-language-model-client.md](fase-3-step-6-bedrock-language-model-client.md) | Concluído | `BedrockLanguageModelClient` — Converse real via Bedrock |
| Passo 7 | [fase-3-step-7-composition-root.md](fase-3-step-7-composition-root.md) | Concluído | Factory por `KNOWLEDGE_MODE` — pipeline wired, MOCK preservado |
| Passo 8A | [fase-3-step-8-gate-end-to-end.md](fase-3-step-8-gate-end-to-end.md) | **Concluído** — GO_PHASE_3_INFRA_WITH_CONDITIONS | Gate descartável: ingestão, Retrieve, análise threshold, smoke |
| Passo 8B | [fase-3-step-8b-notebook-validacao-demo.md](fase-3-step-8b-notebook-validacao-demo.md) | Implementado — revisão visual pendente | Notebook + HTML de demonstração para cliente |
| Passo 9 | *(a criar)* | Pendente | Terraform RAG HML permanente |
| Passo 10 | *(a criar)* | Pendente | Dataset de avaliação, threshold definitivo, modelo definitivo |
| Passo 11 | *(a criar)* | Pendente | Deploy RAG HML |
| Passo 12 | *(a criar)* | Pendente | Frontend com badge AWS RAG HML |

---

## Resultados do Gate (Passo 8A)

| Componente | Status |
|---|---|
| Knowledge Base + S3 Vectors em sa-east-1 | VALIDATED |
| `metadataConfiguration` (nonFilterableMetadataKeys) | VALIDATED |
| Ingestão do corpus | COMPLETE — 1 doc, 0 falhas |
| Retrieve — 14 tópicos oficiais | Executado |
| Threshold recomendado | **0.65** (provisório) — `USE_0_65_PROVISIONALLY` |
| Threshold rejeitado | **0.70** — causava FN=8 (57% dos tópicos bloqueados) |
| Smoke — 3 casos | PASSARAM |
| Teardown | COMPLETE — residual=0 |
| **Decisão** | **GO_PHASE_3_INFRA_WITH_CONDITIONS** |

---

## Artefatos do Gate

```
phase_3_e2e_gate/artifacts/
  ├── gate_summary.json
  ├── vector_index_validation.json
  ├── ingestion_result.json
  ├── retrieve_scores.json
  ├── threshold_analysis_query_level.json
  ├── threshold_comparison_chunk_level.json
  ├── pipeline_smoke.json
  └── teardown_verification.json
```

---

## Relatórios

```
reports/
  ├── phase3_rag_validation_demo.html   ← apresentação ao cliente
  └── threshold_metrics.png             ← gráfico de métricas
```

---

## Documentação de Fase 1 e Fase 2

| Documento | Conteúdo |
|---|---|
| [fase-1-completa.md](fase-1-completa.md) | Entrega completa da Fase 1 — ambiente MOCK |
| [fase-1-roteiro-testes.md](fase-1-roteiro-testes.md) | 145 validações da Fase 1 |
| [fase-2-plano.md](fase-2-plano.md) | Plano de integração com ma-hr-orch real |
| [fase-2-step-0-auth.md](fase-2-step-0-auth.md) | Autenticação e probe da Fase 2 |
| [fase-2-existing-probe-audit.md](fase-2-existing-probe-audit.md) | Auditoria do probe existente |
| [procedimento-atualizar-access-token.md](procedimento-atualizar-access-token.md) | Como renovar token AWS/Alelo |

---

## Próximo passo

**Passo 9 — Terraform do ambiente RAG HML**

```
PASSO_8A = CONCLUÍDO
PASSO_8B = IMPLEMENTADO_PENDING_FINAL_VISUAL_REVIEW
GATE_DECISION = GO_PHASE_3_INFRA_WITH_CONDITIONS
NEXT_STEP = PHASE_3_STEP_9_TERRAFORM_RAG_HML
```
