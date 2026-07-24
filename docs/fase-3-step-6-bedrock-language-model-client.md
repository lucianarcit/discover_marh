# Fase 3 — Passo 6: BedrockLanguageModelClient

**Data:** 2026-07-23
**Status:** CONCLUÍDO
**Testes:** 352/352 aprovados (286 anteriores + 66 novos)
**STEP_6_COMPONENT=BEDROCK_LANGUAGE_MODEL_CLIENT**
**BEDROCK_API=CONVERSE**
**IAM_ACTION=bedrock:InvokeModel**
**AWS_REGION=sa-east-1**
**UNIT_TEST_AWS_CALLS=ZERO**
**GENERATION_MODEL=PROPOSED_PENDING_DATASET_EVALUATION**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `clients/bedrock_language_model_client.py` | Implementação real do LanguageModelClient via Converse API |
| `tests/unit/test_bedrock_language_model_client.py` | 66 testes com botocore Stubber |

## 2. Arquivos alterados

Nenhum arquivo de produção existente foi alterado. Router, KnowledgeClient, MockKnowledgeClient, BedrockRagKnowledgeClient, BedrockKnowledgeBaseRetriever e infraestrutura permanecem intactos.

---

## 3. Responsabilidade

`BedrockLanguageModelClient` implementa `LanguageModelClient` e chama a API `bedrock-runtime:Converse` em sa-east-1.

**Não faz:**
- Não recupera documentos (sem acesso a Retriever ou Knowledge Base)
- Não aplica threshold de score
- Não conhece Router nem intents
- Não aceita dados corporativos (colaboradores, pedidos, CPF)
- Não usa `InvokeModel` diretamente
- Não usa `ConverseStream` (sem streaming)
- Não usa `RetrieveAndGenerate`
- Não usa tools/function calling
- Não usa guardrails nesta etapa
- Não usa cross-region inference

---

## 4. Assinatura final

```python
class BedrockLanguageModelClient(LanguageModelClient):

    def __init__(
        self,
        *,
        model_id: str,                       # obrigatório, sem padrão
        region_name: str = "sa-east-1",
        client: object | None = None,        # injetável para testes
        max_tokens: int = 500,               # > 0
        temperature: float = 0.0,            # [0.0, 1.0]
        connect_timeout: int = 5,            # > 0
        read_timeout: int = 60,              # > 0
        max_retries: int = 2,                # >= 0
        max_context_chars: int = 40_000,     # > 0
    ) -> None: ...
```

Interface pública herdada:

```python
llm.generate(*, system_prompt, user_query, context_chunks) -> GenerationResult
```

---

## 5. Modelo

`model_id` é obrigatório e sem valor padrão. Não usar:
- Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`)
- Claude 3.5 Haiku
- Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
- Inference profile cross-region
- ARN de inference profile

Seleção definitiva no Passo 10 com o dataset de avaliação.
Configuração futura: `BEDROCK_MODEL_ID=<modelo selecionado>`

---

## 6. Permissão IAM

A API Converse usa a permissão `bedrock:InvokeModel`.
`bedrock:Converse` **não é uma action IAM** — não documentar assim.

---

## 7. Formato da chamada Converse

```python
client.converse(
    modelId=model_id,
    system=[{"text": system_prompt}],
    messages=[
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ],
    inferenceConfig={
        "maxTokens": max_tokens,
        "temperature": temperature,
    },
)
```

---

## 8. Formato do contexto

Construído por `_build_context(chunks)`. Campos incluídos: `source_file` e `section_title` (quando presentes). Score, metadata bruta, URI S3, ARN e hash de embedding nunca incluídos.

```
[TRECHO 1]
Fonte: marh_feature_knowledge.md
Seção: Pedidos
Conteúdo:
Texto do chunk aprovado.

[TRECHO 2]
Fonte: marh_feature_knowledge.md
Seção: Colaboradores
Conteúdo:
Texto do segundo chunk.
```

Separador entre blocos: `\n\n`. Numeração sequencial. Ordem preservada.

---

## 9. Formato da mensagem do usuário

```
CONHECIMENTO APROVADO:

{contexto_formatado}

PERGUNTA:

{user_query}

Responda utilizando somente o conhecimento aprovado.
```

Não inclui: topic interno, intent ID, correlation ID, metadata, score threshold, configurações de infraestrutura.

---

## 10. Proteção de tamanho de contexto

`max_context_chars = 40_000` (padrão, configurável).

- Truncamento ocorre **entre chunks** — nunca no meio de um chunk.
- O primeiro chunk é sempre incluído se couber.
- Se o primeiro chunk não couber: lança `InvalidRagRequestError`.
- Chunks de maior score chegam primeiro (já ordenados pelo `BedrockRagKnowledgeClient`).
- Calibração com tokenizer real: **pendência do Passo 10**.

---

## 11. Campos mapeados para GenerationResult

| Campo Converse | Campo GenerationResult |
|---|---|
| `output.message.content[*].text` | `text` (concatenados, strip) |
| `usage.inputTokens` | `input_tokens` |
| `usage.outputTokens` | `output_tokens` |
| `stopReason` | `stop_reason` |
| `model_id` (parâmetro) | `model_id` |

**Não propagado:** `ResponseMetadata`, `requestId`, `metrics.latencyMs`, campos de trace.

Blocos não textuais (`image`, `toolUse`, etc.) são ignorados silenciosamente.

---

## 12. Erros mapeados para LanguageModelError

| Código AWS | Mensagem segura |
|---|---|
| `AccessDeniedException` | "Acesso ao modelo de geração não autorizado." |
| `ValidationException` | "Parâmetros inválidos na chamada ao modelo de geração." |
| `ThrottlingException` | "Modelo de geração temporariamente indisponível (limite de requisições)." |
| `ModelTimeoutException` | "A geração excedeu o tempo limite." |
| `ModelNotReadyException` | "Modelo de geração não está pronto. Tente novamente em instantes." |
| `ServiceUnavailableException` | "Serviço de geração temporariamente indisponível." |
| `InternalServerException` | "Erro interno do serviço de geração (HTTP N)." |
| `ResourceNotFoundException` | "Modelo de geração não encontrado. Verifique o BEDROCK_MODEL_ID." |
| Outros `ClientError` | "Erro na chamada ao serviço de geração: {code}" |
| `BotoCoreError` | "Erro de comunicação com o serviço de geração: {type}" |
| Exceções inesperadas | "Erro inesperado durante geração: {type}" |
| Resposta sem texto | "Serviço de geração retornou resposta sem conteúdo textual utilizável." |

Nunca incluído nas mensagens: system_prompt, user_query, chunks, ARN, Account ID, URI S3, resposta bruta.

---

## 13. Proteções de segurança

- Mensagens de erro não expõem query, chunks, system prompt, URIs nem credenciais.
- Logs registram somente: operation, status, duração, model_id, chunk_count, tokens, stop_reason.
- Logs não registram: system_prompt, user_query, texto gerado, metadata dos chunks.
- `responseMetadata` e `requestId` não são propagados ao Router.
- Score e metadata bruta dos chunks não aparecem no prompt enviado ao modelo.

---

## 14. Testes adicionados (66)

| Grupo | Quantidade |
|---|---|
| Construção — validações | 17 |
| Request Converse — formato | 14 |
| Mapeamento de resposta | 11 |
| Erros AWS → LanguageModelError | 14 |
| Segurança — mensagens seguras | 4 |
| Proteção max_context_chars | 3 |
| Contrato | 6 |
| **Total** | **66** |

---

## 15. Limitações desta etapa

- Modelo definitivo não selecionado (`GENERATION_MODEL=PROPOSED_PENDING_DATASET_EVALUATION`)
- `max_context_chars` baseado em caracteres — calibrar com tokenizer real no Passo 10
- Guardrails não implementados
- Streaming não implementado
- Factory/composition root não atualizada (Passo 7)
- Knowledge Base end-to-end não validada (`KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED`)

---

## 16. Próximo passo

**Passo 7 — Atualizar factory/composition root**

- Atualizar `lambda_handler._build_orchestrator()` para instanciar `BedrockRagKnowledgeClient` quando `KNOWLEDGE_MODE=BEDROCK_RAG`
- Injetar `BedrockKnowledgeBaseRetriever` e `BedrockLanguageModelClient`
- Ler `BEDROCK_KNOWLEDGE_BASE_ID`, `BEDROCK_MODEL_ID`, `BEDROCK_REGION`, `RETRIEVAL_SCORE_THRESHOLD`
- Garantir que `KNOWLEDGE_MODE=MOCK` continua usando `MockKnowledgeClient` (comportamento atual)
- Garantir retrocompatibilidade com `AGENT_MODE` legado
- Nenhuma chamada AWS no construtor
- Testes de construção da factory com variáveis de ambiente
