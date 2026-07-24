# Fase 3 — Passo 8A: Gate End-to-End Descartável

**Data:** 2026-07-24
**Status:** EM ANDAMENTO — gate interrompido por falha de validação IAM; correção aplicada; re-execução pendente
**Testes:** 399/399 aprovados (380 anteriores + 19 novos — correção do Router)
**STEP_8A_COMPONENT=E2E_GATE_DESCARTAVEL**
**AWS_REGION=sa-east-1**
**CROSS_REGION=PROHIBITED**
**RETRIEVE_AND_GENERATE=PROHIBITED**
**KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED**
**GATE_DECISION=PENDING**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `tests/unit/test_router_flow_detail.py` | 19 testes da correção do Router |
| `phase_3_e2e_gate/gate_runner.py` | Script do gate: preflight → recursos → ingestão → Retrieve → análise → smoke → teardown |
| `phase_3_e2e_gate/requirements.txt` | Dependências do gate para Python do sistema (`boto3`) |
| `phase_3_e2e_gate/resource_manifest.json` | Manifesto progressivo dos recursos criados no gate |

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

### Execução 3 — resultado pendente

> **Instrução de atualização:** quando o gate terminar com sucesso, substituir este bloco pelos dados reais. Preservar integralmente as execuções 1 e 2.
>
> Registrar (sem IDs completos, ARNs, bucket names, Account ID ou respostas brutas):
> - Knowledge Base: status ACTIVE, duração
> - Ingestão: status COMPLETE, docs processados, docs falhos, duração
> - Retrieve: scores por tópico (min/max/mediana), scores das queries negativas, duração
> - Análise de threshold: tabela comparativa 0.50–0.80, recomendação, status (KEEP_0_70 / ADJUST_THRESHOLD)
> - Smoke: found, flow_detail, data_classification, content_len, duração por caso
> - Teardown: actions, errors, residual=0
> - Decisão: GO_PHASE_3_INFRA ou GO_PHASE_3_INFRA_WITH_CONDITIONS
>
> Atualizar cabeçalho (Status, KNOWLEDGE_BASE_END_TO_END, GATE_DECISION) e seções 7, 9 e 10.
>
> Não marcar GO_PHASE_3_INFRA enquanto ingestão, Retrieve, smoke e teardown não estiverem todos comprovados.

---

## 7. Arquitetura do gate

```
gate_runner.py
  │
  ├─ 1. Preflight
  │    aws sts, corpus SHA-256, 6 clientes boto3
  │
  ├─ 2. S3 bucket (corpus)
  │    bloqueio público + criptografia AES256
  │    upload: knowledge/marh_feature_knowledge.md
  │
  ├─ 3. S3 Vectors
  │    vector bucket + vector index (1024 dim, cosine, float32)
  │
  ├─ 4. IAM temporário (menor privilégio)
  │    trust: bedrock.amazonaws.com
  │    permissões: s3:GetObject, s3vectors:*, bedrock:InvokeModel (embed)
  │
  ├─ 5. Knowledge Base
  │    embedding: amazon.titan-embed-text-v2:0
  │    storage: S3_VECTORS
  │    aguarda status ACTIVE
  │
  ├─ 6. Data source + ingestão
  │    chunking HIERARCHICAL: parent=500t, child=200t, overlap=50t
  │    polling com timeout; estado COMPLETE obrigatório
  │
  ├─ 7. Retrieve real (BedrockKnowledgeBaseRetriever)
  │    14 queries dos tópicos oficiais + 3 negativas
  │    coleta scores para análise de threshold
  │
  ├─ 8. Análise de threshold
  │    compara: 0.50 / 0.60 / 0.65 / 0.70 / 0.75 / 0.80
  │    produz recomendação
  │
  ├─ 9. Smoke pipeline completo (3 chamadas)
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
| Preflight PASSED | ✅ (execução 2) |
| S3 + S3 Vectors funcionais em sa-east-1 | ✅ (execução 2 — criados e destruídos) |
| IAM role criada sem erro | ⏸ correção aplicada, re-execução pendente |
| Knowledge Base criada | ⏸ pendente |
| Ingestão COMPLETE | ⏸ pendente |
| Retrieve real funcionando | ⏸ pendente |
| Threshold analisado | ⏸ pendente |
| Pipeline smoke positivo | ⏸ pendente |
| Teardown COMPLETE | ✅ (execução 2 — residual=0) |

---

## 11. Limitações registradas

- `KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED` — ainda não validado
- Modelo de geração definitivo: `PROPOSED_PENDING_DATASET_EVALUATION`
- Threshold 0.70: `PROPOSED_PENDING_EVALUATION`
- `COST_ESTIMATE_STATUS=PENDING_MODEL_AND_VECTOR_STORE_SELECTION`

---

## 12. Próximo passo após gate aprovado

**Passo 9 — Terraform do ambiente RAG HML**

- Lambda `marh-agent-rag-hml`
- Knowledge Base permanente com S3 Vectors em sa-east-1
- API Gateway, CloudFront, badge `AWS RAG HML`
- Secrets Manager para `BEDROCK_KNOWLEDGE_BASE_ID` e `BEDROCK_MODEL_ID`
- Logs e métricas separados do ambiente MOCK
