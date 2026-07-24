# Fase 3 — Passo 5: BedrockKnowledgeBaseRetriever

**Data:** 2026-07-23
**Status:** CONCLUÍDO
**Testes:** 286/286 aprovados (235 anteriores + 51 novos)
**STEP_5_COMPONENT=BEDROCK_KNOWLEDGE_BASE_RETRIEVER**
**RETRIEVE_AND_GENERATE=PROHIBITED**
**AWS_REGION=sa-east-1**
**UNIT_TEST_AWS_CALLS=ZERO**
**KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `clients/bedrock_knowledge_base_retriever.py` | Implementação real do Retriever via Bedrock Retrieve API |
| `tests/unit/test_bedrock_knowledge_base_retriever.py` | 51 testes com botocore Stubber |

## 2. Arquivos alterados

| Arquivo | Motivo |
|---|---|
| `tests/unit/test_rag_interfaces.py` | Corrigido `test_retriever_module_does_not_import_boto3` — verificação de `__spec__` como dict era incorreta; simplificado para `hasattr` |

Nenhum arquivo de produção existente foi alterado. Router, KnowledgeClient, MockKnowledgeClient, BedrockRagKnowledgeClient e infraestrutura permanecem intactos.

---

## 3. Responsabilidade

`BedrockKnowledgeBaseRetriever` implementa `Retriever` e realiza a chamada real à API `bedrock-agent-runtime:Retrieve` em sa-east-1.

**Não faz:**
- Não aplica threshold (responsabilidade do `BedrockRagKnowledgeClient`)
- Não reordena chunks por score
- Não gera texto
- Não chama `RetrieveAndGenerate`
- Não chama `Converse` ou `InvokeModel`
- Não usa cross-region
- Não expõe URIs S3, ARNs, Account IDs ou queries nas mensagens de erro

---

## 4. Assinatura final

```python
class BedrockKnowledgeBaseRetriever(Retriever):

    def __init__(
        self,
        *,
        knowledge_base_id: str,        # obrigatório, não vazio
        region_name: str = "sa-east-1",
        client: object | None = None,  # injetável para testes
        connect_timeout: int = 5,
        read_timeout: int = 30,
        max_retries: int = 2,
    ) -> None: ...

    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]: ...
```

A interface pública herdada da classe base é:

```python
retriever.retrieve(query, top_k=5) -> list[RetrievedChunk]
```

---

## 5. Formato da chamada Retrieve

```python
client.retrieve(
    knowledgeBaseId=knowledge_base_id,
    retrievalQuery={"text": query},
    retrievalConfiguration={
        "vectorSearchConfiguration": {
            "numberOfResults": top_k,
        }
    },
)
```

`numberOfResults = top_k` — a paginação via `nextToken` não é buscada. Uma única chamada é feita. Decisão documentada: corpus pequeno com top_k ≤ 10; buscar múltiplas páginas aumentaria latência sem benefício para a POC.

---

## 6. Campos AWS mapeados

| Campo AWS | Campo RetrievedChunk | Observação |
|---|---|---|
| `content.text` | `content` | Obrigatório. Resultado descartado se vazio. |
| `score` | `score` | Float ou None se ausente. |
| `location.s3Location.uri` | `source_file` | Apenas nome do arquivo (ver seção 7). |
| `metadata.section_number` | `section_number` | Também tenta `section`, `sectionNumber`. |
| `metadata.section_title` | `section_title` | Também tenta `title`, `sectionTitle`, `heading`. |
| `metadata.chunk_index` | `chunk_index` | Também tenta `chunkIndex`, `chunk_id`. |
| `metadata.*` (seguros) | `metadata` | Após sanitização (ver seção 8). |
| `documentId` | — | Nunca exposto. |
| `content.type` | — | Usado para filtro; somente `TEXT` aceito. |

---

## 7. Regras de source_file

Extraído da URI S3 via método estático `_extract_source_file(location)`:

| Entrada | Saída |
|---|---|
| `s3://bucket/knowledge/marh.md` | `"marh.md"` |
| `s3://bucket/a/b/c/faq.md` | `"faq.md"` |
| `s3://bucket/nome%20com%20espa%C3%A7o.md` | `"nome com espaço.md"` |
| URI vazia ou ausente | `None` |
| `location.type != "S3"` | `None` |
| URI sem `/` após bucket | `None` |

**Nunca exposto:** `s3://`, nome do bucket, prefixo completo, ARN, Account ID.

---

## 8. Regras de metadata

A metadata bruta AWS é sanitizada antes de popular `RetrievedChunk.metadata`:

**Campos sempre removidos (`_METADATA_BLOCKLIST`):**
- `x-amz-bedrock-kb-source-uri`
- `x-amz-bedrock-kb-chunk-id`
- `x-amz-bedrock-kb-data-source-id`
- `uri`, `s3_uri`, `s3Uri`, `bucket`, `arn`, `accountId`, `account_id`
- `embedding`, `vector`

**Tipos aceitos:**
- `str`, `int`, `float`, `bool` (escalares)
- `list` de escalares

**Tipos rejeitados:**
- `dict` aninhado
- Objetos Python
- Tipos binários
- Não serializáveis

---

## 9. Tratamento de conteúdo não textual

Nesta Fase 3 o corpus é textual. Resultados sem texto utilizável são ignorados silenciosamente:

| Situação | Comportamento |
|---|---|
| `content.text` vazio ou ausente | Item descartado |
| `content.type = "IMAGE"` | Item descartado |
| `content.type = "AUDIO"` | Item descartado |
| Todos os itens inválidos | Retorna `[]` |
| Um item inválido em lista mista | Item ignorado; demais processados |

**Não implementado nesta etapa:** imagem, áudio, vídeo, SQL, base64.

---

## 10. Erros mapeados

| Código AWS | Mensagem RetrieverError |
|---|---|
| `AccessDeniedException` | "Acesso negado ao Bedrock Knowledge Base. Verifique as permissões IAM." |
| `ResourceNotFoundException` | "Knowledge Base não encontrada. Verifique o BEDROCK_KNOWLEDGE_BASE_ID." |
| `ValidationException` | "Parâmetros inválidos na chamada Retrieve ao Bedrock." |
| `ThrottlingException` / `TooManyRequestsException` | "Limite de requisições atingido no Bedrock Knowledge Base (throttling)." |
| `InternalServerException` / `ServiceUnavailableException` | "Erro interno do Bedrock Knowledge Base (HTTP N)." |
| Outros `ClientError` | "Erro na chamada ao Bedrock Knowledge Base: {code}" |
| `BotoCoreError` (timeout, rede) | "Erro de comunicação com Bedrock Knowledge Base: {type}" |
| Exceções inesperadas | "Erro inesperado durante recuperação: {type}" |

Mensagens nunca contêm: query, conteúdo de chunks, URI S3, ARN, Account ID, resposta bruta AWS.

---

## 11. Configuração boto3

```python
Config(
    connect_timeout=5,
    read_timeout=30,       # configurável
    retries={"max_attempts": 2, "mode": "standard"},
)
```

Retry automático do botocore para erros transientes. Sem retry manual duplicado.

---

## 12. Injeção de cliente para testes

```python
retriever = BedrockKnowledgeBaseRetriever(
    knowledge_base_id="kb-id",
    region_name="sa-east-1",
    client=boto_client_com_stubber,  # cliente injetado
)
```

Quando `client` é fornecido: usado diretamente, sem criar novo cliente boto3.
Os 51 testes usam `botocore.stub.Stubber` — zero chamadas de rede, zero credenciais.

---

## 13. Testes adicionados (51)

| Grupo | Quantidade |
|---|---|
| Construção | 7 |
| Request — formato enviado ao Bedrock | 4 |
| Mapeamento — conteúdo e score | 11 |
| source_file — extração e helper | 11 |
| Metadata — sanitização e campos estruturados | 7 |
| Erros AWS → RetrieverError | 8 |
| Contrato — sem threshold, sem geração | 3 |
| **Total** | **51** |

---

## 14. Paginação

Decisão: **sem paginação nesta etapa**.

`numberOfResults = top_k` instrui o Bedrock a retornar até `top_k` resultados em uma única chamada. A API pode retornar `nextToken`, mas não é buscado. Justificativa:
- Corpus pequeno (`marh_feature_knowledge.md`)
- `top_k` padrão = 5
- Buscar páginas adicionais aumentaria latência e complexidade desnecessariamente para a POC

Implementar paginação somente se o corpus crescer e top_k precisar exceder o limite por página.

---

## 15. Próximo passo

**Passo 6 — Implementar `BedrockLanguageModelClient`**

- Implementa `LanguageModelClient`
- Usa `bedrock-runtime:Converse` em sa-east-1
- Recebe chunks aprovados e system_prompt
- Retorna `GenerationResult` com texto plano
- Mapeia exceções boto3 para `LanguageModelError`
- Testes com botocore Stubber (zero chamadas reais)
- Modelo definitivo: `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION`
