# Probe — 11. Go / No-Go

**Decisão:** `GO_PHASE_3_CODE_IMPLEMENTATION`
**Data:** 2026-07-23
**Região validada:** sa-east-1

## Escopo da decisão

`GO_PHASE_3_CODE_IMPLEMENTATION` — autoriza implementação de código (Passos 2 a 7 do plano). **Não** autoriza criação de recursos AWS, Terraform nem deploy.

Um gate adicional (`GO_PHASE_3_INFRA`) será emitido após o probe end-to-end do Passo 8.

## Critérios e resultado

| Critério | Requerido | Resultado |
|---|---|---|
| Modelo de embedding ACTIVE em sa-east-1 | Sim | **ATENDIDO** — `amazon.titan-embed-text-v2:0` invocado |
| Modelo de geração ACTIVE em sa-east-1 | Sim | **ATENDIDO** — 11 candidatos na shortlist com Converse ativo |
| Geração funciona sem cross-region | Sim | **ATENDIDO** — todos os candidatos em sa-east-1 direto |
| `bedrock:InvokeModel` (Converse) funcional | Sim | **ATENDIDO** — confirmado por chamadas reais |
| Serviço Knowledge Bases alcançável em sa-east-1 | Sim | **ATENDIDO** — `KNOWLEDGE_BASE_SERVICE_REACHABLE=CONFIRMED` |
| S3 Vectors alcançável em sa-east-1 | Sim | **ATENDIDO** — `list_vector_buckets` acessível |
| Nenhuma dependência exige cross-region | Sim | **ATENDIDO** — zero cross-region detectado |

## Itens ainda abertos (não bloqueantes para código)

| Item | Status |
|---|---|
| Modelo de geração definitivo | `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION` |
| Threshold de recuperação | `0.70_PROPOSED_PENDING_EVALUATION` |
| Estimativa de custo | `PENDING_MODEL_AND_VECTOR_STORE_SELECTION` |
| Knowledge Base end-to-end | `KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED` |
| ADR-001 definitivo | Provisório — confirmar no gate do Passo 8 |
| IAM da Lambda RAG HML | A criar no Passo 8 |

## ADR-001 (provisório)

**Knowledge Bases + S3 Vectors** — ver `09_adr_001_vector_retrieval.md`.

## Embedding confirmado

`amazon.titan-embed-text-v2:0` — ACTIVE, ON_DEMAND, 1024 dim, invocado com sucesso em sa-east-1.

## Gate do Passo 8 (antes de Terraform)

Antes de criar infra definitiva:
1. Criar KB temporária com S3 Vectors
2. Ingerir corpus
3. Executar Retrieve real
4. Validar chunks e scores
5. Destruir recursos
6. Emitir `GO_PHASE_3_INFRA` ou revisar ADR-001

## Próximo passo autorizado

**Passo 2 — Adicionar `DATA_SOURCE_MODE`, `KNOWLEDGE_MODE` e `RETRIEVAL_SCORE_THRESHOLD` ao `config.py`**

Nenhum recurso AWS criado. Nenhum ambiente alterado. Nenhum commit ou push realizado.
