# Fase 3 — Passo 9A: Terraform do Ambiente RAG HML

**Data:** 2026-07-24
**Status:** ARQUITETURA CRIADA — terraform fmt ✅ | terraform validate ✅ | terraform plan ✅ | terraform apply PENDENTE
**STEP_9A_COMPONENT=TERRAFORM_RAG_HML**
**AWS_REGION=sa-east-1**
**TERRAFORM_PROVIDER_AWS=6.56.0 (recursos nativos S3 Vectors e Knowledge Base)**
**TERRAFORM_APPLY=NOT_EXECUTED — aguarda autorização**

---

## 1. Arquitetura proposta

```
Corpus (S3)
  └── marh_feature_knowledge.md (único arquivo aprovado)
        │
        ▼
Knowledge Base (Bedrock)   ←── IAM role menor privilégio
  embedding: Titan Embed Text v2 (1024 dim, cosine, float32)
  storage:   S3 Vectors
        │
        ▼
  S3 Vector bucket + index
  metadataConfiguration:
    nonFilterableMetadataKeys:
      - AMAZON_BEDROCK_TEXT
      - AMAZON_BEDROCK_METADATA
        │
   Retrieve (separado da geração)
   NÃO usa RetrieveAndGenerate
        │
        ▼
Lambda RAG HML
  DATA_SOURCE_MODE=MOCK
  KNOWLEDGE_MODE=BEDROCK_RAG
  RETRIEVAL_SCORE_THRESHOLD=0.65
        │
        ▼
API Gateway HTTP v2
  POST /chat
  GET  /health
```

---

## 2. Arquivos Terraform criados

| Arquivo | Responsabilidade |
|---|---|
| `infra-rag/main.tf` | Provider AWS, null, archive; backend remoto comentado |
| `infra-rag/locals.tf` | Prefixo, configuração do índice, ARN do embedding |
| `infra-rag/variables.tf` | Todas as variáveis com validações; proíbe modelos excluídos |
| `infra-rag/s3_corpus.tf` | Bucket S3 do corpus, upload do arquivo aprovado |
| `infra-rag/s3_vectors.tf` | Vector bucket e index via `null_resource + local-exec` (ver limitação) |
| `infra-rag/iam_knowledge_base.tf` | Role da KB: menor privilégio (S3, S3Vectors, Bedrock embed) |
| `infra-rag/knowledge_base.tf` | Knowledge Base + Data Source via `null_resource + local-exec` (ver limitação) |
| `infra-rag/secrets.tf` | Secret com configuração RAG (modelo, threshold, KB ID placeholder) |
| `infra-rag/lambda.tf` | IAM da Lambda, CloudWatch, Layer, Function |
| `infra-rag/api_gateway.tf` | API Gateway HTTP v2, rotas `/chat` e `/health`, logs |
| `infra-rag/outputs.tf` | Outputs seguros (KB ID marcado como sensitive) |
| `infra-rag/terraform.tfvars.example` | Template de variáveis (nunca versionar o `.tfvars` real) |
| `infra-rag/.gitignore` | State, `.tfvars`, `.build/` |

---

## 3. Variáveis

| Variável | Padrão | Observação |
|---|---|---|
| `aws_region` | `sa-east-1` | Validação: apenas sa-east-1 permitido |
| `environment` | `HML` | HML ou PRD |
| `bedrock_model_id` | — | **Obrigatório, sem padrão** — seleção no Passo 10 |
| `retrieval_score_threshold` | `0.65` | Provisório — calibrar no Passo 10 |
| `retrieval_top_k` | `5` | Chunks por consulta |
| `lambda_memory_size` | `512` | MB |
| `lambda_timeout` | `60` | Segundos (maior que MOCK por causa do RAG) |
| `knowledge_base_chunking_parent_tokens` | `500` | Validado no gate |
| `knowledge_base_chunking_child_tokens` | `200` | Validado no gate |
| `knowledge_base_chunking_overlap_tokens` | `50` | Validado no gate |

---

## 4. Outputs

| Output | Sensitive | Descrição |
|---|---|---|
| `api_base_url` | não | URL do API Gateway |
| `health_check_url` | não | `<api_base_url>/health` |
| `lambda_function_name` | não | Nome da Lambda |
| `model_id` | não | Modelo configurado |
| `region` | não | sa-east-1 |
| `score_threshold` | não | Threshold configurado |
| `corpus_bucket_name` | **sim** | Bucket S3 do corpus |
| `vector_bucket_name` | não | Nome do S3 Vector bucket |
| `vector_index_name` | não | Nome do S3 Vector index |
| `rag_config_secret_arn` | **sim** | ARN do secret RAG |
| `knowledge_base_id_note` | não | Instrução pós-apply |

---

## 5. IAM (menor privilégio)

### Role da Knowledge Base

| Permissão | Recurso |
|---|---|
| `s3:GetObject`, `s3:ListBucket` | Somente o bucket do corpus |
| `s3vectors:PutVectors`, `GetVectors`, `DeleteVectors`, `QueryVectors`, `ListVectors` | Somente o index do projeto |
| `bedrock:InvokeModel` | Somente `amazon.titan-embed-text-v2:0` |

### Role da Lambda

| Permissão | Recurso |
|---|---|
| `AWSLambdaBasicExecutionRole` | Managed policy (logs CloudWatch) |
| `AWSXRayDaemonWriteAccess` | Managed policy (tracing) |
| `bedrock-agent-runtime:Retrieve` | Qualquer KB do account (estreitar após apply) |
| `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` | Somente o modelo configurado |
| `secretsmanager:GetSecretValue` | Somente o secret RAG deste ambiente |

---

## 6. Decisão do provider — migração para v6.56

**Avaliação realizada no Passo 9A.1:**

| Item | v5.100 | v6.56 |
|---|---|---|
| `aws_s3vectors_vector_bucket` | ❌ ausente | ✅ nativo |
| `aws_s3vectors_index` com `metadata_configuration` | ❌ ausente | ✅ nativo |
| `storage_configuration.s3_vectors_configuration` em KB | ❌ ausente | ✅ nativo |
| `null_resource + local-exec` necessário | Sim | **Não** |
| Idempotência garantida | Parcial (CLI) | Total (state) |
| Detecção de drift | Não | Sim |
| `terraform destroy` remove todos os recursos | Não | Sim |

**Decisão:** migrar para `hashicorp/aws ~> 6.56`. Todos os workarounds `null_resource` e `local-exec` foram removidos. Recursos nativos utilizados: `aws_s3vectors_vector_bucket`, `aws_s3vectors_index`, `aws_bedrockagent_knowledge_base` com `s3_vectors_configuration`.

**Provider null removido** — não é mais necessário.

---

## 7. Resultado do plan (após migração para v6.56)

```
terraform fmt      → OK
terraform validate → Success! The configuration is valid.
terraform plan -var="bedrock_model_id=mistral.magistral-small-2509"
  Plan: 28 to add, 0 to change, 0 to destroy.
  null_resource: 0
  local-exec: 0
```

Recursos que serão criados (28 — todos nativos):

| # | Tipo | Nome |
|---|---|---|
| 1 | `aws_s3_bucket` | corpus |
| 2 | `aws_s3_bucket_versioning` | corpus |
| 3 | `aws_s3_bucket_server_side_encryption_configuration` | corpus |
| 4 | `aws_s3_bucket_public_access_block` | corpus |
| 5 | `aws_s3_bucket_policy` | corpus |
| 6 | `aws_s3_object` | corpus_knowledge |
| 7 | `aws_iam_role` | knowledge_base |
| 8 | `aws_iam_role_policy` | knowledge_base_permissions |
| 9 | **`aws_s3vectors_vector_bucket`** | rag |
| 10 | **`aws_s3vectors_index`** | rag |
| 11 | **`aws_bedrockagent_knowledge_base`** | rag |
| 12 | **`aws_bedrockagent_data_source`** | corpus |
| 13 | `aws_secretsmanager_secret` | rag_config |
| 14 | `aws_secretsmanager_secret_version` | rag_config |
| 15 | `aws_iam_role` | lambda |
| 16 | `aws_iam_role_policy_attachment` | lambda_basic |
| 17 | `aws_iam_role_policy_attachment` | lambda_xray |
| 18 | `aws_iam_role_policy` | lambda_rag |
| 19 | `aws_cloudwatch_log_group` | lambda |
| 20 | `aws_lambda_layer_version` | deps |
| 21 | `aws_lambda_function` | agent |
| 22 | `aws_apigatewayv2_api` | agent |
| 23 | `aws_apigatewayv2_stage` | default |
| 24 | `aws_cloudwatch_log_group` | api_gateway |
| 25 | `aws_apigatewayv2_integration` | lambda |
| 26 | `aws_apigatewayv2_route` | chat |
| 27 | `aws_apigatewayv2_route` | health |
| 28 | `aws_lambda_permission` | api_gateway |

---

## 8. Riscos e custos

| Item | Detalhe |
|---|---|
| S3 Vectors | Sem custo fixo de OCU (diferença do OpenSearch Serverless) |
| Knowledge Base | Cobrança por query Retrieve |
| Titan Embed Text v2 | Cobrança por tokenização na ingestão e por query |
| Lambda | Cobrança por invocação e tempo de execução |
| API Gateway | Cobrança por request |
| CloudWatch | Cobrança por ingestão de logs |
| Modelo de geração | Cobrança por token (modelo a definir no Passo 10) |
| `COST_ESTIMATE_STATUS` | `PENDING_MODEL_AND_PERMANENT_INFRA_SELECTION` |

---

## 9. Pré-requisitos para apply

Antes de executar `terraform apply`:

1. Criar arquivo `infra-rag/terraform.tfvars` (não versionar):

```hcl
bedrock_model_id = "<modelo selecionado no Passo 10>"
retrieval_score_threshold = 0.65
```

2. Construir o layer de dependências Python:

```powershell
cd C:\proj\discover_alelo\infra-rag
# Criar .build/layer.zip com boto3, pydantic, etc.
# Script: bash scripts/build_layer.sh (a criar no Passo 9B)
```

3. Credencial AWS válida com AdministratorAccess ou policy mínima equivalente.

---

## 10. Comandos para revisão

```powershell
# Revisar o plan salvo
cd C:\proj\discover_alelo\infra-rag
terraform show tfplan

# Revisar arquivos
Get-ChildItem C:\proj\discover_alelo\infra-rag\ | Select-Object Name

# Revisar variáveis
Get-Content .\variables.tf

# Revisar IAM
Get-Content .\iam_knowledge_base.tf
Get-Content .\lambda.tf | Select-String "statement|actions|resources" -Context 0,2

# Quando autorizar apply:
# terraform apply tfplan
```

---

## 11. Próximas subetapas

| Subetapa | Atividade |
|---|---|
| **9B** | Construir layer, executar `terraform apply`, ingestão, validar KB ACTIVE |
| **9C** | Criar `notebooks/phase3_rag_live_validation.ipynb` com LIVE_HML |
| **9D** | Smoke via API HML, dataset live, relatório HTML, evidências sanitizadas |
