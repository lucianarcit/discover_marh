# Regional Capability Probe — Fase 3 MARH Agent

**Data:** 2026-07-23
**Região:** sa-east-1 (exclusiva — cross-region proibido)
**Decisão:** `GO_PHASE_3_CODE_IMPLEMENTATION`
**Bloqueadores críticos:** 0

---

## Resultado por componente

| Componente | Status | Evidência |
|---|---|---|
| Identidade AWS | OK | SSO federado, sa-east-1 |
| Foundation models listados | 55 modelos | `list_foundation_models` sem erro |
| Embedding candidato primário | **CONFIRMADO** | `amazon.titan-embed-text-v2:0` — invocado, 1024 dim, 233ms |
| `bedrock:InvokeModel` (Converse) | **11 modelos ativos** | Todos sem cross-region |
| Bedrock Knowledge Bases | **REACHABLE** | `KNOWLEDGE_BASE_SERVICE_REACHABLE=CONFIRMED` |
| Knowledge Bases end-to-end | **NÃO VALIDADO** | `KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED` — gate do Passo 8 |
| S3 Vectors | **DISPONÍVEL** | `list_vector_buckets` acessível em sa-east-1 |
| Permissões IAM do probe | **CONFIRMADAS** | Chamadas reais bem-sucedidas |
| Cross-region detectado | Nenhum | — |

---

## Decisões tomadas

| Decisão | Resultado |
|---|---|
| ADR-001 — Vector store | **Knowledge Bases + S3 Vectors** (provisório — confirmar no Passo 8) |
| Embedding model | **`amazon.titan-embed-text-v2:0`** (confirmado) |
| Modelo de geração | `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION` |
| Threshold de recuperação | `0.70 — PROPOSED_PENDING_EVALUATION` |
| Estimativa de custo | `PENDING_MODEL_AND_VECTOR_STORE_SELECTION` |
| `RetrieveAndGenerate` | **PROIBIDO** — usar sempre Retrieve + LLM separados |

---

## Shortlist de geração para Passo 10

Filtro: `modelLifecycle.status = ACTIVE`, `ON_DEMAND`, `CONVERSE_ACTIVE_IN_REGION`, sem risco de ciclo de vida curto.

| Candidato | Provider | Latência |
|---|---|---|
| `mistral.mistral-large-2402-v1:0` | Mistral | 402ms |
| `mistral.magistral-small-2509` | Mistral | 283ms |
| `mistral.ministral-3-14b-instruct` | Mistral | 259ms |
| `google.gemma-3-27b-it` | Google | 226ms |
| `qwen.qwen3-32b-v1:0` | Qwen | 200ms |

Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`) removido da shortlist por risco de ciclo de vida — lifecycle `ACTIVE` confirmado na API, mas modelo de 2024 sem EOL declarado; priorizar modelos mais recentes.

---

## Gate futuro — antes do Passo 8

Antes de criar Terraform definitivo:
1. Criar KB temporária com S3 Vectors em sa-east-1
2. Ingerir corpus `marh_feature_knowledge.md`
3. Executar `Retrieve` real com queries do `topic_to_query`
4. Validar chunks e scores (calibrar threshold)
5. Destruir todos os recursos do probe
6. Emitir `GO_PHASE_3_INFRA` ou revisar ADR-001

---

## Correções aplicadas nesta versão

1. ADR-001 expandido com três opções (KB+S3V, KB+OpenSearch, Retriever próprio+S3V)
2. `KNOWLEDGE_BASE_SERVICE_REACHABLE=CONFIRMED` e `KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED` separados
3. Decisão go/no-go corrigida para `GO_PHASE_3_CODE_IMPLEMENTATION`
4. Gate end-to-end criado para antes do Passo 8
5. Permissões IAM corrigidas: removido `bedrock:Converse`; adicionado `bedrock:InvokeModel` com nota explicativa
6. Claude 3 Sonnet removido da shortlist por risco de ciclo de vida
7. Justificativa Gemma corrigida: removida inferência por nome; mantida avaliação pendente do Passo 10
8. Identidade, UserId, ARN e e-mail mascarados em `01_aws_identity_region.md`

---

## Artefatos gerados

```
phase_3_probe/
├── 00_executive_summary.md
├── 01_aws_identity_region.md
├── 02_foundation_models_inventory.md
├── 03_embedding_models.md
├── 04_generation_models.md
├── 05_converse_validation.md
├── 06_knowledge_bases_availability.md
├── 07_s3_vectors_availability.md
├── 08_iam_permissions.md
├── 09_adr_001_vector_retrieval.md
├── 10_blockers.md
├── 11_go_no_go.md
└── artifacts/
    ├── 01_identity.json
    ├── 02_all_models_inventory.json
    ├── 03_embedding_models.json
    ├── 04_generation_models.json
    ├── 05_embedding_invocation_results.json
    ├── 06_generation_converse_results.json
    ├── 07_knowledge_bases_availability.json
    ├── 08_s3_vectors_availability.json
    ├── 09_iam_findings.json
    ├── 10_adr_001_vector_retrieval.json
    ├── 11_blockers.json
    └── 12_go_no_go.json
```

---

## Próximo passo autorizado

**Passo 2 — Adicionar `DATA_SOURCE_MODE`, `KNOWLEDGE_MODE` e `RETRIEVAL_SCORE_THRESHOLD` ao `config.py`**

Nenhum recurso AWS criado. Nenhum ambiente MOCK ou Fase 2 alterado.
