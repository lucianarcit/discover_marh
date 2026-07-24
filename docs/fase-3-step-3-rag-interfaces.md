# Fase 3 — Passo 3: Interfaces e Modelos do Pipeline RAG

**Data:** 2026-07-23
**Status:** CONCLUÍDO
**Testes:** 150/150 aprovados (107 anteriores + 43 novos)
**Dependência AWS:** nenhuma — zero chamadas externas

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `domain/rag_models.py` | Modelos internos `RetrievedChunk` e `GenerationResult` |
| `domain/rag_exceptions.py` | Hierarquia de exceções RAG independente de fornecedor |
| `clients/retriever.py` | Interface abstrata `Retriever` |
| `clients/language_model_client.py` | Interface abstrata `LanguageModelClient` |
| `tests/unit/test_rag_interfaces.py` | 43 testes unitários das interfaces e modelos |

## 2. Arquivos alterados

Nenhum arquivo existente foi alterado. `Router`, `MockKnowledgeClient`, `KnowledgeClient`, `Orchestrator` e todos os demais arquivos permanecem intactos.

---

## 3. Modelos internos

### `RetrievedChunk`

```python
class RetrievedChunk(BaseModel):
    content: str                          # obrigatório, não vazio
    score: float | None = None            # score 0.0 é válido; None = sem score
    source_file: str | None = None
    section_number: str | None = None
    section_title: str | None = None
    chunk_index: int | None = None
    metadata: dict = {}                   # default seguro — nunca None

    model_config = {"frozen": True}       # imutável
```

**Regras:**
- `content` vazio ou somente espaços é rejeitado na validação
- `metadata=None` é convertido para `{}` automaticamente
- Score `0.0` é aceito — score baixo não é erro de modelo
- Imutável: não armazena objetos do SDK AWS nem response completo

### `GenerationResult`

```python
class GenerationResult(BaseModel):
    text: str                             # obrigatório, não vazio, texto plano
    input_tokens: int | None = None
    output_tokens: int | None = None
    stop_reason: str | None = None
    model_id: str | None = None

    model_config = {"frozen": True}       # imutável
```

**Regras:**
- `text` é texto plano — nunca tratado como HTML pelo pipeline RAG
- `text` vazio ou somente espaços é rejeitado
- Imutável

---

## 4. Interfaces

### `Retriever`

```python
class Retriever(ABC):
    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]: ...
    @abstractmethod
    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]: ...
```

**O que faz:** dado texto de consulta, retorna chunks do corpus ordenados por relevância.

**O que NÃO faz:**

| Proibido | Motivo |
|---|---|
| Filtrar por threshold | Responsabilidade de `BedrockRagKnowledgeClient` |
| Gerar texto | Responsabilidade de `LanguageModelClient` |
| Conhecer Router, Orchestrator ou intents | Separação de responsabilidades |
| Importar boto3 | Interface de domínio — independente de fornecedor |
| Lançar exceções boto3/botocore | Implementações devem mapear para `RetrieverError` |

**Contrato de validação (template method em `retrieve`):**

| Condição | Comportamento |
|---|---|
| `query` vazia ou só espaços | `InvalidRagRequestError` |
| `top_k <= 0` | `InvalidRagRequestError` |
| Resultado vazio | `[]` — ausência de evidência, não é erro |
| `query` com espaços laterais | Strip aplicado antes de chamar `_retrieve` |

### `LanguageModelClient`

```python
class LanguageModelClient(ABC):
    def generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult: ...
    @abstractmethod
    def _generate(self, *, system_prompt, user_query, context_chunks) -> GenerationResult: ...
```

**O que faz:** dado um prompt de sistema, a query do usuário e os chunks aprovados, produz resposta textual fundamentada.

**O que NÃO faz:**

| Proibido | Motivo |
|---|---|
| Realizar recuperação vetorial | Responsabilidade de `Retriever` |
| Conhecer Knowledge Base | Separação de responsabilidades |
| Conhecer Router, Orchestrator ou intents | Separação de responsabilidades |
| Receber CPF, colaboradores ou pedidos reais | Corpus apenas — sem dados corporativos |
| Executar actions ou escrita | Agente exclusivamente consultivo |
| Retornar HTML | Texto plano — renderização no frontend |
| Importar boto3 | Interface de domínio — independente de fornecedor |

**Contrato de validação:**

| Condição | Comportamento |
|---|---|
| `system_prompt` vazio | `InvalidRagRequestError` |
| `user_query` vazia | `InvalidRagRequestError` |
| `context_chunks` vazio | `InvalidRagRequestError` — se não há evidência, retornar `found=False` sem invocar geração |

---

## 5. Hierarquia de exceções

```
Exception
  └── RagError
        ├── RetrieverError           — falhas na recuperação de chunks
        ├── LanguageModelError       — falhas na geração de texto
        └── InvalidRagRequestError   — parâmetros inválidos
```

**Regras:**
- Exceções específicas de SDK (boto3, botocore) **nunca** são expostas às camadas superiores
- Implementações concretas capturam exceções do SDK e relançam como `RetrieverError` ou `LanguageModelError`
- Mensagens de erro **não expõem** conteúdo dos chunks, CPF nem dados corporativos
- As seguintes exceções **não existem ainda** (serão criadas pelas implementações no Passo 5/6):
  - `BedrockAccessDeniedError`
  - `BedrockThrottlingError`
  - `KnowledgeBaseNotFoundError`

---

## 6. Fluxo futuro documentado

```
BedrockRagKnowledgeClient.query(topic)
  │
  ├─► topic_to_query(topic)              # mapeamento fixo — 14 tópicos oficiais
  │       ↓
  ├─► Retriever.retrieve(query, top_k=5) # recuperação vetorial
  │       ↓
  │   list[RetrievedChunk]               # chunks com score
  │       ↓
  ├─► filtrar por RETRIEVAL_SCORE_THRESHOLD (0.70 — PROPOSED_PENDING_EVALUATION)
  │       ↓
  │   [chunks aprovados vazio?] ─► found=False, content=None  ← sem invenção
  │       ↓ (chunks aprovados)
  ├─► LanguageModelClient.generate(
  │       system_prompt=SYSTEM_PROMPT,
  │       user_query=query,
  │       context_chunks=chunks_aprovados
  │   )
  │       ↓
  │   GenerationResult.text              # texto plano, nunca HTML
  │       ↓
  └─► dict(found=True, content=text, data_classification="BEDROCK_RAG_GROUNDED")
```

**Ponto de injeção:** `lambda_handler._build_orchestrator()` — nenhuma camada superior conhece a implementação concreta.

---

## 7. Ausência de dependência AWS

Confirmado por testes explícitos:

- `test_retriever_module_does_not_import_boto3` — PASSOU
- `test_language_model_client_module_does_not_import_boto3` — PASSOU
- `test_rag_models_module_does_not_import_boto3` — PASSOU
- `test_rag_exceptions_module_does_not_import_boto3` — PASSOU

Nenhum dos 4 módulos criados importa boto3, botocore, ou qualquer SDK AWS.

---

## 8. Testes adicionados (43)

### `RetrievedChunk` (10)

| Teste | Verificação |
|---|---|
| `test_retrieved_chunk_valid` | Criação com todos os campos |
| `test_retrieved_chunk_metadata_default` | `metadata={}` quando omitido |
| `test_retrieved_chunk_metadata_none_becomes_empty_dict` | `None` convertido para `{}` |
| `test_retrieved_chunk_score_zero_accepted` | Score 0.0 é válido |
| `test_retrieved_chunk_score_none_accepted` | Score None é válido |
| `test_retrieved_chunk_all_optional_fields_none` | Todos os opcionais como None |
| `test_retrieved_chunk_empty_content_rejected` | Content `""` rejeitado |
| `test_retrieved_chunk_blank_content_rejected` | Content `"   "` rejeitado |
| `test_retrieved_chunk_is_immutable` | Atribuição falha (`frozen=True`) |
| `test_retrieved_chunk_metadata_with_values` | Metadata com valores arbitrários |

### `GenerationResult` (5)

| Teste | Verificação |
|---|---|
| `test_generation_result_valid` | Criação com todos os campos |
| `test_generation_result_optional_fields_none` | Opcionais como None |
| `test_generation_result_empty_text_rejected` | Text `""` rejeitado |
| `test_generation_result_blank_text_rejected` | Text `"   "` rejeitado |
| `test_generation_result_is_immutable` | Atribuição falha (`frozen=True`) |

### `Retriever` (9)

| Teste | Verificação |
|---|---|
| `test_retriever_fake_respects_contract` | Fake retorna `list[RetrievedChunk]` |
| `test_retriever_empty_query_rejected` | `InvalidRagRequestError` |
| `test_retriever_blank_query_rejected` | `InvalidRagRequestError` |
| `test_retriever_top_k_zero_rejected` | `InvalidRagRequestError` |
| `test_retriever_top_k_negative_rejected` | `InvalidRagRequestError` |
| `test_retriever_empty_result_allowed` | `[]` não é erro |
| `test_retriever_top_k_limits_results` | top_k limita retorno |
| `test_retriever_strips_query_whitespace` | Espaços laterais aceitos |
| `test_retriever_does_not_filter_by_threshold` | Threshold não é responsabilidade do Retriever |

### `LanguageModelClient` (8)

| Teste | Verificação |
|---|---|
| `test_llm_fake_returns_generation_result` | Fake retorna `GenerationResult` |
| `test_llm_empty_system_prompt_rejected` | `InvalidRagRequestError` |
| `test_llm_blank_system_prompt_rejected` | `InvalidRagRequestError` |
| `test_llm_empty_user_query_rejected` | `InvalidRagRequestError` |
| `test_llm_blank_user_query_rejected` | `InvalidRagRequestError` |
| `test_llm_empty_context_chunks_rejected` | `InvalidRagRequestError` |
| `test_llm_result_text_is_plain_text` | `text` é string opaca |
| `test_llm_accepts_multiple_chunks` | Múltiplos chunks aceitos |

### Exceções (7)

| Teste | Verificação |
|---|---|
| `test_retriever_error_is_rag_error` | Hierarquia correta |
| `test_language_model_error_is_rag_error` | Hierarquia correta |
| `test_invalid_rag_request_error_is_rag_error` | Hierarquia correta |
| `test_rag_error_is_exception` | Raiz da hierarquia |
| `test_retriever_error_message_does_not_expose_chunks` | Sem dados sensíveis na mensagem |
| `test_invalid_rag_request_raised_with_message` | Mensagem legível |
| `test_exceptions_can_be_caught_as_rag_error` | Polimorfismo de exceções |

### Ausência de boto3 (4)

`test_retriever_module_does_not_import_boto3`, `test_language_model_client_module_does_not_import_boto3`, `test_rag_models_module_does_not_import_boto3`, `test_rag_exceptions_module_does_not_import_boto3`

---

## 9. Compatibilidade confirmada

| Item | Status |
|---|---|
| `KnowledgeClient` — contrato inalterado | CONFIRMADO |
| `MockKnowledgeClient` — comportamento inalterado | CONFIRMADO |
| `router.py` — não alterado | CONFIRMADO |
| `orchestrator.py` — não alterado | CONFIRMADO |
| `lambda_handler.py` — não alterado | CONFIRMADO |
| `DATA_SOURCE_MODE=MOCK` e `KNOWLEDGE_MODE=MOCK` como padrão | CONFIRMADO |
| 107 testes anteriores aprovados | CONFIRMADO |
| **Total: 150/150 testes aprovados** | CONFIRMADO |

---

## 10. Próximo passo

**Passo 4 — Implementar `BedrockRagKnowledgeClient`**

- Implementa `KnowledgeClient`
- Recebe `Retriever` e `LanguageModelClient` por injeção no construtor
- Mapeia `topic → query_string` (14 tópicos oficiais)
- Aplica `RETRIEVAL_SCORE_THRESHOLD`
- Retorna `found=False` quando nenhum chunk aprovado
- Popula `data_classification=BEDROCK_RAG_GROUNDED`
- Stub com testes unitários usando `FakeRetriever` e `FakeLanguageModelClient`
- Sem chamadas boto3 — implementações reais vêm nos Passos 5 e 6
