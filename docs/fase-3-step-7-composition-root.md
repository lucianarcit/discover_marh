# Fase 3 — Passo 7: Composition Root / Factory do KnowledgeClient

**Data:** 2026-07-23
**Status:** CONCLUÍDO
**Testes:** 380/380 aprovados (352 anteriores + 28 novos)
**STEP_7_COMPONENT=COMPOSITION_ROOT**
**DEFAULT_KNOWLEDGE_MODE=MOCK**
**RAG_PIPELINE_WIRED=true**
**AWS_CALLS_DURING_TESTS=ZERO**
**MOCK_BEHAVIOR_PRESERVED=true**
**KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `application/knowledge_client_factory.py` | Único ponto de composição do pipeline RAG |
| `tests/unit/test_knowledge_client_factory.py` | 28 testes: factory, integração local com fakes |

## 2. Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `api/lambda_handler.py` | Usa `build_knowledge_client()` e `DATA_SOURCE_MODE` |
| `api/local_api.py` | Usa `build_knowledge_client()` e `DATA_SOURCE_MODE` |
| `.env.example` | Atualizado com os dois eixos, BEDROCK_REGION=sa-east-1, sem valores Haiku |

---

## 3. Factory criada

```python
# application/knowledge_client_factory.py

def build_knowledge_client() -> KnowledgeClient:
    """Lê KNOWLEDGE_MODE e instancia a implementação correta."""
    ...
```

Funções internas:
- `_build_mock()` — instancia `MockKnowledgeClient` sem nenhuma dependência AWS
- `_build_bedrock_rag()` — valida config, instancia pipeline completo
- `_require_config(name, value)` — valida var obrigatória sem expor o valor

---

## 4. Comportamento em KNOWLEDGE_MODE=MOCK

- Instancia `MockKnowledgeClient`
- Não cria nenhum cliente boto3
- Não exige `BEDROCK_KNOWLEDGE_BASE_ID`
- Não exige `BEDROCK_MODEL_ID`
- Não instancia `BedrockKnowledgeBaseRetriever`
- Não instancia `BedrockLanguageModelClient`
- Não instancia `BedrockRagKnowledgeClient`
- Comportamento atual dos 352 testes preservado

---

## 5. Comportamento em KNOWLEDGE_MODE=BEDROCK_RAG

Valida antes de construir qualquer objeto:

```
BEDROCK_KNOWLEDGE_BASE_ID  — obrigatório, não vazio
BEDROCK_MODEL_ID           — obrigatório, não vazio
```

Depois instancia o pipeline na ordem:

```python
retriever = BedrockKnowledgeBaseRetriever(
    knowledge_base_id=BEDROCK_KNOWLEDGE_BASE_ID,
    region_name=BEDROCK_REGION,         # sa-east-1
)

llm = BedrockLanguageModelClient(
    model_id=BEDROCK_MODEL_ID,
    region_name=BEDROCK_REGION,
)

knowledge_client = BedrockRagKnowledgeClient(
    retriever=retriever,
    language_model_client=llm,
    score_threshold=RETRIEVAL_SCORE_THRESHOLD,  # 0.70 padrão
    top_k=5,
)
```

---

## 6. Validações obrigatórias

| Variável | Quando obrigatória | Erro |
|---|---|---|
| `BEDROCK_KNOWLEDGE_BASE_ID` | `KNOWLEDGE_MODE=BEDROCK_RAG` | `ValueError: BEDROCK_KNOWLEDGE_BASE_ID é obrigatório...` |
| `BEDROCK_MODEL_ID` | `KNOWLEDGE_MODE=BEDROCK_RAG` | `ValueError: BEDROCK_MODEL_ID é obrigatório...` |

Mensagens de erro **não expõem** o valor real das variáveis.

---

## 7. Ausência de fallback silencioso

```
KNOWLEDGE_MODE=BEDROCK_RAG + BEDROCK_KNOWLEDGE_BASE_ID vazio
→ ValueError explícito
→ NÃO retorna MockKnowledgeClient
→ NÃO retorna resposta sintética
→ NÃO ignora a configuração inválida
```

---

## 8. Independência entre os dois eixos

| DATA_SOURCE_MODE | KNOWLEDGE_MODE | MaHrOrchClient | KnowledgeClient |
|---|---|---|---|
| MOCK | MOCK | MockMaHrOrchClient | MockKnowledgeClient |
| MOCK | BEDROCK_RAG | MockMaHrOrchClient | BedrockRagKnowledgeClient |
| INTEGRATED | MOCK | HttpMaHrOrchClient (Fase 2) | MockKnowledgeClient |
| INTEGRATED | BEDROCK_RAG | HttpMaHrOrchClient (Fase 2) | BedrockRagKnowledgeClient |

Alterar `DATA_SOURCE_MODE` não afeta `KnowledgeClient`.
Alterar `KNOWLEDGE_MODE` não afeta `MaHrOrchClient`.

**Combinação da Fase 3 isolada:** `DATA_SOURCE_MODE=MOCK + KNOWLEDGE_MODE=BEDROCK_RAG`

---

## 9. Construção sem chamada de rede

- Os construtores de `BedrockKnowledgeBaseRetriever` e `BedrockLanguageModelClient` criam clientes boto3 mas não fazem chamadas de rede.
- Nenhum import do módulo faz chamada AWS.
- O Orchestrator global é construído no cold start (módulo-nível) — comportamento preservado.

---

## 10. Observação sobre o Router (pendência futura)

O Router hardcoda `"flow_detail": "MOCK_KNOWLEDGE"` para qualquer `found=True` retornado pelo `KnowledgeClient`. Quando `KNOWLEDGE_MODE=BEDROCK_RAG`, o campo correto seria `"BEDROCK_RAG"`. Esta correção no Router é melhoria futura — não foi feita neste passo para manter o contrato: "não alterar o Router".

O campo `knowledge_source` é propagado corretamente (`source_section` do resultado).

---

## 11. Testes adicionados (28)

| Grupo | Quantidade |
|---|---|
| Modo MOCK — comportamento | 6 |
| Modo BEDROCK_RAG — instanciação | 7 |
| Configuração inválida — sem fallback | 7 |
| Independência dos eixos | 3 |
| Integração local com fakes | 5 |
| **Total** | **28** |

### Testes de integração local (sem AWS)

| Teste | Verificação |
|---|---|
| `test_pipeline_rag_with_fakes_int019` | INT-019 usa RAG, retorna mensagem do LLM fake, knowledge_source correto |
| `test_pipeline_rag_source_section_in_response` | source_section propagado no metadata |
| `test_pipeline_int001_does_not_use_rag` | INT-001 (colaborador) não chama Retriever |
| `test_pipeline_transactional_does_not_use_rag` | INT-022 (transacional) não chama Retriever |
| `test_pipeline_rag_below_threshold_returns_fallback` | Score baixo → fallback estático do Router |

---

## 12. Variáveis de ambiente (.env.example atualizado)

```bash
DATA_SOURCE_MODE=MOCK
KNOWLEDGE_MODE=MOCK
AGENT_MODE=MOCK_LOCAL         # legado — fallback de DATA_SOURCE_MODE
BEDROCK_REGION=sa-east-1      # corrigido de us-east-1
BEDROCK_EMBED_MODEL_ID=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_ID=             # obrigatório em BEDROCK_RAG — sem valor padrão
BEDROCK_KNOWLEDGE_BASE_ID=    # obrigatório em BEDROCK_RAG — sem valor padrão
RETRIEVAL_SCORE_THRESHOLD=0.70
```

---

## 13. Próximo passo

**Passo 8 — Gate end-to-end (antes do Terraform)**

Conforme ADR-001 e plano da Fase 3:
1. Criar KB temporária com S3 Vectors em sa-east-1
2. Fazer upload do corpus `marh_feature_knowledge.md`
3. Executar `StartIngestionJob`
4. Executar `Retrieve` real com queries do `topic_to_query`
5. Validar chunks e scores (calibrar threshold)
6. Destruir todos os recursos do probe
7. Emitir `GO_PHASE_3_INFRA` ou revisar ADR-001
