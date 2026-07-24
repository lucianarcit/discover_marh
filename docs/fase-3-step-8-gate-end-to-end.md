# Fase 3 — Passo 8A: Gate End-to-End Descartável

**Data:** 2026-07-24
**Status:** CONCLUÍDO — gate end-to-end aprovado com condições
**Testes:** 399/399 aprovados (380 anteriores + 19 novos — correção do Router)
**STEP_8A_COMPONENT=E2E_GATE_DESCARTAVEL**
**AWS_REGION=sa-east-1**
**CROSS_REGION=PROHIBITED**
**RETRIEVE_AND_GENERATE=PROHIBITED**
**KNOWLEDGE_BASE_END_TO_END=VALIDATED**
**GATE_DECISION=GO_PHASE_3_INFRA_WITH_CONDITIONS**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `tests/unit/test_router_flow_detail.py` | 19 testes da correção do Router |
| `phase_3_e2e_gate/gate_runner.py` | Script do gate: preflight → recursos → ingestão → Retrieve → análise → smoke → teardown |
| `phase_3_e2e_gate/requirements.txt` | Dependências do gate para Python do sistema (`boto3`) |
| `phase_3_e2e_gate/resource_manifest.json` | Manifesto progressivo dos recursos criados no gate |
| `phase_3_e2e_gate/test_gate_helpers.py` | 13 testes do helper S3 Vectors (ARNs, payload KB) |
| `phase_3_e2e_gate/test_ingestion_helpers.py` | 18 testes de ingestão (sanitização, artefato antes da exceção) |
| `phase_3_e2e_gate/test_vector_index.py` | 13 testes de validação do metadataConfiguration |
| `phase_3_e2e_gate/test_threshold_analysis.py` | 19 testes da análise query-level |

## 2. Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `application/router.py` | Correção: `flow_detail` lido dinamicamente do KnowledgeClient |
| `poc_marh_agent/backend/pyproject.toml` | Grupo `[rag]` adicionado com `boto3>=1.43.0` como dependência opcional |

---

## 3. Correção do Router (pré-requisito do gate)

**Problema registrado no Passo 7:** o Router hardcodava `flow_detail="MOCK_KNOWLEDGE"` para qualquer `found=True`, independente da implementação de `KnowledgeClient` usada.

**Correção aplicada em `application/router.py`:**

```python
# Antes (hardcoded):
"flow_detail": "MOCK_KNOWLEDGE"

# Depois (dinâmico):
_kr_meta = knowledge_result.get("metadata") or {}
_flow_detail = _kr_meta.get("flow_detail") or "MOCK_KNOWLEDGE"
```

**Campos seguros propagados do resultado do KnowledgeClient:**

| Campo | Propagado |
|---|---|
| `flow_detail` | Sim — lido da metadata do resultado |
| `data_classification` | Sim |
| `retrieved_chunks` | Sim |
| `approved_chunks` | Sim |
| `score_threshold` | Sim |

**Campos proibidos — nunca propagados:**

| Campo | Motivo |
|---|---|
| `intent_id` | Controlado exclusivamente pelo classificador |
| `authorization` | Controlado pela camada de segurança |
| `navigation_override` | Controlado pelo Router e NavigationBuilder |

**Retrocompatibilidade:** `MockKnowledgeClient` não retorna `metadata` → fallback `"MOCK_KNOWLEDGE"` preservado. Todos os 380 testes anteriores continuam passando.

---

## 4. Testes da correção (19)

| Grupo | Quantidade |
|---|---|
| MockKnowledgeClient — mantém MOCK_KNOWLEDGE | 3 |
| BedrockRagKnowledgeClient fake — usa BEDROCK_RAG | 8 |
| Not-found — fallback estático | 2 |
| Metadata perigosa — não propagada | 4 |
| Intenções fora do RAG — não afetadas | 3 |
| **Total** | **19** |

---

## 5. Dependências corrigidas

**Problema:** `gate_runner.py` usa o Python do sistema, que não tinha `boto3`.

**Correção:**
- `boto3 1.43.55` instalado no Python do sistema via `pip install boto3`
- `phase_3_e2e_gate/requirements.txt` criado
- `pyproject.toml` do backend atualizado com grupo opcional `[rag]`

```toml
[project.optional-dependencies]
rag = [
    "boto3>=1.43.0",
]
```

---

## 6. Execuções do gate

### Execução 1 — falha: `ExpiredToken`

- Credencial temporária AWS expirada antes da execução
- Nenhum recurso criado
- Teardown: nada a destruir

---

### Execução 2 — falha: `ValidationError` IAM

**Preflight:** PASSED — todos os 6 clientes boto3 acessíveis em sa-east-1

**Progresso:**
- S3 bucket criado (prefixo `marh-rag-e2e-07241445`)
- Corpus enviado: `knowledge/marh_feature_knowledge.md` (11.751 bytes, sha256=`5f7b9dfa...`)
- S3 Vector bucket criado (1024 dim, cosine, float32)
- S3 Vector index criado
- **IAM role — FALHOU:** `ValidationError` — caracteres acentuados (`ó`, `á`, `—`) não são aceitos no campo `description` da AWS

**Teardown:** COMPLETE — residual=0

```json
"teardown": {
  "actions": ["vector_index_deleted", "vector_bucket_deleted", "s3_object_deleted", "s3_bucket_deleted"],
  "errors": [],
  "residual": 0,
  "status": "COMPLETE"
}
```

**Correção aplicada:** descrições IAM alteradas para ASCII puro.

---

### Execução 3 — falha: `GATE_EXECUTION_FAILED_PARAMETER_VALIDATION` (payload KB)

**Preflight:** PASSED

**Progresso:**
- S3 bucket, vector bucket e vector index criados
- IAM role e policy criadas
- **Knowledge Base — FALHOU:** `ValidationException: Unknown parameter in storageConfiguration.s3VectorsConfiguration: "vectorBucketName"` — a API `bedrock-agent:CreateKnowledgeBase` exige `vectorBucketArn` e `indexArn`, não `vectorBucketName`

**Teardown:** COMPLETE — residual=0

**Correção aplicada:**
- `create_s3_vectors()` captura `vectorBucketArn` e `indexArn` dos retornos
- `_build_s3_vectors_storage_configuration(vector_bucket_arn, index_arn)` criado como helper testável
- 13 testes Stubber verificando o payload

---

### Execução 4 — falha: `GATE_EXECUTION_FAILED_INGESTION`

**Preflight:** PASSED

**Progresso:**
- Todos os recursos criados com sucesso
- Knowledge Base ACTIVE
- **Ingestão — FALHOU:** `Filterable metadata must have at most 2048 bytes` — chaves Bedrock (`AMAZON_BEDROCK_TEXT`, `AMAZON_BEDROCK_METADATA`) precisavam ser declaradas como `nonFilterableMetadataKeys` no índice S3 Vectors

**Teardown:** COMPLETE — residual=0

**Correção aplicada:**
- `create_index()` agora inclui `metadataConfiguration={"nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]}`
- Após `create_index`, executa `get_index` e valida a configuração antes de criar a KB
- Salva `vector_index_validation.json` em caso de sucesso ou falha
- 13 testes Stubber da validação

---

### Execução 5 — falha: `AssertionError` no smoke (threshold 0.70 bloqueava tópicos)

**Preflight:** PASSED — sha256 do gate_runner registrado

**Ingestão:** COMPLETE — 1 documento indexado, 0 falhas

**Retrieve:** 14 consultas positivas + 3 negativas executadas com sucesso

**Threshold (chunk-level, código antigo):** análise por chunk recomendou 0.70 — KEEP_0_70

**Smoke:** FALHOU — `AssertionError: Caso 1: esperava found=True`
- `MARH_OVERVIEW` tem `max_score=0.6759`, bloqueado por threshold 0.70

**Teardown:** COMPLETE — residual=0

**Correções aplicadas:**
- Análise de threshold convertida para query-level (top_score por consulta)
- Smoke passa a usar o threshold recomendado pela análise (sem hardcode)
- Adicionados campos de auditoria nas queries negativas (`query_text`, `would_reach_rag_in_real_flow`)
- 19 testes da análise query-level

---

### Execução 6 — SUCESSO: `GO_PHASE_3_INFRA_WITH_CONDITIONS`

**Preflight:** PASSED — região sa-east-1, 6 clientes boto3, corpus sha256=`5f7b9dfa...`

**S3 Vectors:**
- Vector bucket e index criados (1024 dim, cosine, float32)
- `metadataConfiguration` com `AMAZON_BEDROCK_TEXT` e `AMAZON_BEDROCK_METADATA`
- `vector_index_validation.json`: **VALIDATED**

**Knowledge Base:** ACTIVE

**Ingestão:** COMPLETE
- Documentos escaneados: 1
- Documentos indexados: 1
- Documentos com falha: 0

**Retrieve real (14 positivos + 3 negativos):**
- Fonte: `marh_feature_knowledge.md` — todos os casos positivos
- Scores positivos: min=0.573, max=0.773
- NEG-001: max_score=0.575 — abaixo de 0.65
- NEG-002: max_score=0.621 — abaixo de 0.65
- NEG-003: max_score=0.724 — acima de 0.65 (FP no Retrieve isolado — bloqueado pelo Router no fluxo real)

**Análise de threshold (query-level, top_score por consulta):**

| threshold | TP | FN | TN | FP | recall | F1 | balanced_acc |
|---|---|---|---|---|---|---|---|
| 0.50 | 14 | 0 | 0 | 3 | 1.0 | 0.903 | 0.500 |
| 0.60 | 14 | 0 | 1 | 2 | 1.0 | 0.933 | 0.667 |
| **0.65** | **14** | **0** | **2** | **1** | **1.0** | **0.966** | **0.833** |
| 0.70 | 6 | 8 | 2 | 1 | 0.429 | 0.571 | 0.548 |
| 0.75 | 2 | 12 | 3 | 0 | 0.143 | 0.250 | 0.571 |
| 0.80 | 0 | 14 | 3 | 0 | 0.000 | 0.000 | 0.500 |

**0.70 rejeitado:** causava `FN=8` — 8 dos 14 tópicos positivos bloqueados, inaceitável para POC de validação.

**Recomendação:** `RETRIEVAL_SCORE_THRESHOLD=0.65 — USE_0_65_PROVISIONALLY`

**Smoke (threshold=0.65, modelo temporário):**

| Caso | Resultado |
|---|---|
| `MARH_OVERVIEW` | `found=True`, `flow_detail=BEDROCK_RAG`, `approved_chunks>=1` |
| Tópico desconhecido | `found=False`, `reason=topic_unknown`, `content=None` |
| `ORDER_PROCESS` | `found=True`, `approved_chunks>=1` |

Validações PASSED.

**Teardown:** COMPLETE — residual=0

```json
"teardown": {
  "actions": [
    "data_source_deleted", "knowledge_base_deleted",
    "vector_index_deleted", "vector_bucket_deleted",
    "s3_object_deleted", "s3_bucket_deleted",
    "iam_policy_deleted", "iam_role_deleted"
  ],
  "errors": [],
  "residual": 0,
  "status": "COMPLETE"
}
```

**Decisão:** `GO_PHASE_3_INFRA_WITH_CONDITIONS`

---

## 7. Arquitetura do gate

```
gate_runner.py
  │
  ├─ 1. Preflight
  │    aws sts, corpus SHA-256, SHA-256 do gate_runner, 6 clientes boto3
  │
  ├─ 2. S3 bucket (corpus)
  │    bloqueio público + criptografia AES256
  │    upload: knowledge/marh_feature_knowledge.md
  │
  ├─ 3. S3 Vectors
  │    vector bucket + vector index (1024 dim, cosine, float32)
  │    metadataConfiguration: nonFilterableMetadataKeys obrigatórias
  │    get_index() valida configuração → salva vector_index_validation.json
  │
  ├─ 4. IAM temporário (menor privilégio)
  │    trust: bedrock.amazonaws.com
  │    permissões: s3:GetObject, s3vectors:*, bedrock:InvokeModel (embed)
  │
  ├─ 5. Knowledge Base
  │    embedding: amazon.titan-embed-text-v2:0
  │    storage: S3_VECTORS (vectorBucketArn + indexArn)
  │    aguarda status ACTIVE
  │
  ├─ 6. Data source + ingestão
  │    chunking HIERARCHICAL: parent=500t, child=200t, overlap=50t
  │    polling com timeout; salva ingestion_result.json antes de qualquer exceção
  │
  ├─ 7. Retrieve real (BedrockKnowledgeBaseRetriever)
  │    14 queries dos tópicos oficiais + 3 negativas com campos de auditoria
  │    campos: query_text, would_reach_rag_in_real_flow, retrieved_source
  │
  ├─ 8. Análise de threshold (query-level)
  │    top_score = max(scores) por consulta
  │    TP/FN/TN/FP + precision/recall/F1/balanced_accuracy
  │    salva threshold_analysis_query_level.json
  │
  ├─ 9. Smoke pipeline completo (3 chamadas)
  │    threshold = valor recomendado pela análise (sem hardcode)
  │    caso com evidência + sem evidência + múltiplos chunks
  │    usa TEMPORARY_GATE_MODEL (não é o definitivo)
  │
  └─ finally: TEARDOWN (mesmo em caso de erro)
       data source → KB → vector index → vector bucket
       → objeto S3 → bucket S3 → policy IAM → role IAM
```

**Tags aplicadas em todos os recursos:**

```
Project=marh-agent
Environment=e2e-probe
Purpose=phase-3-gate
Temporary=true
```

---

## 8. Por que script Python e não Terraform

O gate é descartável e operacional — não apenas declarativo:

- Polling condicional (status ACTIVE, COMPLETE) é natural em Python e trabalhoso em Terraform
- Bloco `finally` garante teardown mesmo com erro, sem estado residual
- Manifesto `resource_manifest.json` rastreia exatamente o que foi criado — Terraform precisaria de backend remoto (S3 + DynamoDB) para recurso de minutos de vida
- O ambiente **definitivo** (Passo 9) usará Terraform

---

## 9. Como executar

```powershell
cd C:\proj\discover_alelo
python phase_3_e2e_gate/gate_runner.py
```

Modelo temporário customizável:

```powershell
$env:GATE_MODEL_ID = "mistral.magistral-small-2509"
python phase_3_e2e_gate/gate_runner.py
```

---

## 10. Critérios para GO_PHASE_3_INFRA

| Critério | Status |
|---|---|
| Correção do Router aprovada | ✅ 19 testes passando |
| boto3 instalado no sistema | ✅ |
| Preflight PASSED | ✅ (execução 6) |
| S3 + S3 Vectors funcionais em sa-east-1 | ✅ (execução 6 — criados e destruídos) |
| metadataConfiguration VALIDATED (nonFilterableMetadataKeys) | ✅ (execução 6) |
| IAM role criada sem erro | ✅ (execução 6) |
| Knowledge Base criada (ACTIVE) | ✅ (execução 6) |
| Ingestão COMPLETE | ✅ (execução 6 — 1 doc indexado, 0 falhas) |
| Retrieve real funcionando (14+3 consultas) | ✅ (execução 6) |
| Threshold analisado (query-level) | ✅ (execução 6 — recomendação 0.65) |
| Pipeline smoke positivo | ✅ (execução 6 — 3 casos validados) |
| Teardown COMPLETE | ✅ (execução 6 — residual=0, 8 recursos destruídos) |

**Decisão:** `GO_PHASE_3_INFRA_WITH_CONDITIONS`

---

## 11. Limitações e condições

- `RETRIEVAL_SCORE_THRESHOLD=0.65`
- `THRESHOLD_STATUS=PROVISIONAL_PENDING_DATASET_EVALUATION` — calibrar com dataset completo de 20 casos no Passo 10
- `MODEL_STATUS=PROPOSED_PENDING_DATASET_EVALUATION` — modelo temporário usado no smoke; seleção definitiva no Passo 10
- `NEG_003_STATUS=FALSE_POSITIVE_IN_ISOLATED_RETRIEVE_BLOCKED_BY_ROUTER` — score 0.724 acima de 0.65, mas a pergunta "Qual o CNPJ da Alelo?" não é roteada como `RAG_ONLY` pelo Router (retorna `ERR-008`); o KnowledgeClient nunca seria consultado no fluxo real
- `COST_ESTIMATE_STATUS=PENDING_MODEL_AND_PERMANENT_INFRA_SELECTION`
- `0.70_REJEITADO` — threshold 0.70 causava `FN=8` (8 dos 14 tópicos bloqueados por recall=0.43); inaceitável para POC de validação

---

## 12. Análise de threshold — registro definitivo

**Metodologia:** query-level — `top_score = max(scores)` por consulta. Unidade é a consulta, não o chunk.

**Dataset:** 14 consultas positivas (tópicos oficiais INT-008 a INT-021), 3 consultas negativas.

**Resultado em 0.65:**

| Métrica | Valor |
|---|---|
| TP | 14 |
| FN | 0 |
| TN | 2 |
| FP | 1 (NEG-003 — inativo no pipeline real) |
| recall | 1.0 |
| precision | 0.933 |
| F1 | 0.966 |
| balanced_accuracy | 0.833 |

**Artefatos:** `threshold_analysis_query_level.json`, `threshold_comparison_chunk_level.json` (histórico chunk-level preservado)

---

## 13. Próximo passo

**Passo 9 — Terraform do ambiente RAG HML**

- Lambda `marh-agent-rag-hml`
- Knowledge Base permanente com S3 Vectors em sa-east-1
- API Gateway, CloudFront, badge `AWS RAG HML`
- Secrets Manager para `BEDROCK_KNOWLEDGE_BASE_ID` e `BEDROCK_MODEL_ID`
- Logs e métricas separados do ambiente MOCK
- `RETRIEVAL_SCORE_THRESHOLD=0.65` configurado como variável de ambiente
