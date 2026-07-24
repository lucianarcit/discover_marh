# Fase 3 — Passo 4: BedrockRagKnowledgeClient

**Data:** 2026-07-23
**Status:** CONCLUÍDO
**Testes:** 235/235 aprovados (150 anteriores + 85 novos)
**AWS_CALLS=ZERO**
**STEP_4_IMPLEMENTATION_MODE=FAKES_ONLY**
**KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED**

---

## 1. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `clients/bedrock_rag_knowledge_client.py` | Implementação do pipeline RAG (sem boto3) |
| `tests/unit/test_bedrock_rag_knowledge_client.py` | 85 testes + fakes inspecionáveis |

## 2. Arquivos alterados

Nenhum. Router, MockKnowledgeClient, KnowledgeClient, Orchestrator e todos os arquivos existentes permanecem intactos.

---

## 3. Responsabilidade da classe

`BedrockRagKnowledgeClient` implementa `KnowledgeClient` e orquestra o pipeline RAG:

```
topic → normalização → topic_query_map → query_string
  → Retriever.retrieve(query_string, top_k)
  → filtragem por score_threshold
  → [sem evidência] → found=False (sem chamar LLM)
  → [com evidência] → LanguageModelClient.generate(system_prompt, query, chunks)
  → dict compatível com Router
```

Não importa boto3. Não faz chamadas AWS. Recebe todas as dependências por injeção de construtor.

---

## 4. Assinatura do construtor

```python
class BedrockRagKnowledgeClient(KnowledgeClient):

    def __init__(
        self,
        *,
        retriever: Retriever,
        language_model_client: LanguageModelClient,
        score_threshold: float,           # [0.0, 1.0] — obrigatório
        top_k: int = 5,                   # > 0
        topic_query_map: Mapping[str, str] | None = None,  # None → mapa padrão dos 14 tópicos
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None: ...
```

---

## 5. Mapa estático dos 14 tópicos oficiais

Exatamente os tópicos roteados pelo Router para o fluxo `RAG_ONLY` (INT-008 a INT-021).
`ORDER_STATUS_INFO` **não incluído** — status `ORPHAN_TOPIC_PENDING_OFFICIAL_INTENT_ASSIGNMENT`.

| Tópico | Query de recuperação |
|---|---|
| `AGENT_CAPABILITIES` | "O que o agente consultivo MARH consegue fazer?" |
| `CONSULTABLE_INFO` | "Quais informações posso consultar pelo agente MARH?" |
| `ORDER_PROCESS` | "Como criar um pedido no Espaço RH?" |
| `HOW_CONSULT_ORDER` | "Como consultar um pedido pelo agente MARH?" |
| `HOW_CONSULT_COLLABORATOR` | "Como consultar um colaborador pelo agente MARH?" |
| `CARD_TRACKING_INFO` | "Como funciona o rastreamento de cartões no Espaço RH?" |
| `CANNOT_CANCEL` | "É possível cancelar um pedido pelo agente MARH?" |
| `CANNOT_EDIT_COLLABORATOR` | "O agente MARH consegue editar dados de colaboradores?" |
| `COMPANY_SCOPE` | "O agente MARH consulta dados de qualquer empresa?" |
| `COMPANY_REQUIRED` | "É necessário selecionar uma empresa para usar o agente MARH?" |
| `AGENT_VS_PORTAL` | "O agente MARH substitui o portal web do Espaço RH?" |
| `MARH_OVERVIEW` | "O que é o MARH (Meu Alelo RH)?" |
| `ESPACO_RH_OVERVIEW` | "O que é o Espaço RH do aplicativo Meu Alelo?" |
| `QUESTION_TYPES` | "Que tipos de perguntas posso fazer ao agente MARH?" |

O mapa é exposto como `MappingProxyType` — imutável e auditável. Nenhuma query é gerada dinamicamente.

---

## 6. Regra do threshold

```python
approved = [c for c in chunks if c.score is not None and c.score >= score_threshold]
```

| Condição | Resultado |
|---|---|
| `score >= threshold` | Chunk aprovado |
| `score < threshold` | Chunk descartado |
| `score == threshold` | Chunk aprovado (limiar inclusivo) |
| `score is None` | Chunk **sempre descartado** — sem score não é evidência |

Chunks aprovados são ordenados por score decrescente antes de passar ao LLM.

---

## 7. Fallback sem evidência

O fallback ocorre **antes** da chamada ao LLM. O modelo nunca decide se há evidência suficiente.

```
[nenhum chunk aprovado]
  → LanguageModelClient NÃO é chamado
  → retorna found=False, content=None
  → data_classification=BEDROCK_RAG_NO_EVIDENCE
```

Situações que ativam o fallback:
- Tópico vazio
- Tópico não encontrado no mapa
- Retriever retorna lista vazia
- Todos os chunks com score abaixo do threshold
- Todos os chunks com score `None`

---

## 8. Contrato de retorno

Compatível com o formato consumido pelo Router (campos `found`, `content`, `source_section`):

**Encontrado:**
```python
{
    "found": True,
    "content": "<texto gerado pelo modelo>",
    "source_section": "marh_feature_knowledge.md",
    "data_classification": "BEDROCK_RAG_GROUNDED",
    "metadata": {
        "flow_detail": "BEDROCK_RAG",
        "data_classification": "BEDROCK_RAG_GROUNDED",
        "retrieved_chunks": <int>,
        "approved_chunks": <int>,
        "score_threshold": <float>,
        "model_id": "<id do modelo ou None>",
    },
}
```

**Não encontrado:**
```python
{
    "found": False,
    "content": None,
    "source_section": "marh_feature_knowledge.md",
    "data_classification": "BEDROCK_RAG_NO_EVIDENCE",
    "metadata": {
        "flow_detail": "BEDROCK_RAG",
        "data_classification": "BEDROCK_RAG_NO_EVIDENCE",
        "retrieved_chunks": <int>,
        "approved_chunks": 0,
        "score_threshold": <float>,
        "reason": "<topic_empty | topic_unknown | below_threshold>",
    },
}
```

**Não exposto no retorno:**
- Conteúdo bruto dos chunks
- Vetores
- Prompt de sistema
- Tokens de entrada/saída
- Stack traces
- Objetos AWS
- Dados corporativos

---

## 9. Metadata segura

| Campo | Presente em | Valor |
|---|---|---|
| `flow_detail` | Sempre | `"BEDROCK_RAG"` |
| `data_classification` | Sempre | `BEDROCK_RAG_GROUNDED` ou `BEDROCK_RAG_NO_EVIDENCE` |
| `retrieved_chunks` | Sempre | Quantidade total recuperada pelo Retriever |
| `approved_chunks` | Sempre | Quantidade após filtragem por threshold |
| `score_threshold` | Sempre | Valor configurado |
| `model_id` | Apenas found=True | ID do modelo de geração (ou None) |
| `reason` | Apenas found=False | Causa do fallback |

Campos ausentes intencionalmente: conteúdo de chunks, tokens, prompt, vetores.

---

## 10. Prompt de sistema padrão

```
Você é um assistente consultivo do Meu Alelo RH.

Responda somente com base nos trechos de conhecimento fornecidos.
Não invente informações.
Não use conhecimento externo.
Quando os trechos forem insuficientes, informe que não há informação
disponível e oriente o usuário a acessar o Espaço RH.
Responda em português brasileiro.
Seja direto, claro e objetivo.
Não mencione Bedrock, RAG, embeddings, chunks ou documentos internos.
```

Substituível por injeção — `system_prompt` no construtor. Não pode ser vazio.

---

## 11. Fakes criados (no arquivo de testes)

### `FakeRetriever`

Inspecionável: `call_count`, `last_query`, `last_top_k`.
Configurável: `chunks` retornados, `raise_error` para simular falhas.

### `FakeLanguageModelClient`

Inspecionável: `call_count`, `last_system_prompt`, `last_user_query`, `last_chunks`.
Configurável: `result` retornado, `raise_error` para simular falhas.

Nenhum fake depende de boto3 ou AWS.

---

## 12. Tratamento de erros

| Exceção recebida | Ação |
|---|---|
| `RetrieverError` | Propagada diretamente |
| `LanguageModelError` | Propagada diretamente |
| `InvalidRagRequestError` | Propagada diretamente |
| Qualquer outra do Retriever | Envolve em `RetrieverError` |
| Qualquer outra do LLM | Envolve em `LanguageModelError` |

Mensagens de erro **nunca** contêm conteúdo de chunks, CPF ou dados corporativos.

---

## 13. Testes adicionados (85)

| Grupo | Quantidade |
|---|---|
| Construção — validações | 11 |
| Mapa de tópicos | 6 + 14 parametrizados = 20 |
| Tópicos — comportamento de query | 7 + 14 parametrizados = 21 |
| Recuperação — filtragem por threshold | 9 |
| Geração — comportamento do LLM | 10 |
| Contrato de retorno | 10 |
| Erros | 6 |
| Compatibilidade MOCK + boto3 | 3 |
| Injeção customizada | 2 |
| **Total** | **85** (85 novos, 150 anteriores — 235 total) |

---

## 14. Ausência de boto3 confirmada

`test_bedrock_rag_client_does_not_import_boto3` — PASSOU.

---

## 15. Limitações desta etapa

- `BedrockKnowledgeBaseRetriever` não implementado (Passo 5)
- `BedrockLanguageModelClient` não implementado (Passo 6)
- Factory / composition root não atualizada para `KNOWLEDGE_MODE=BEDROCK_RAG` (Passo 7)
- Knowledge Base end-to-end não validada (`KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED`)
- Threshold 0.70 ainda `PROPOSED_PENDING_EVALUATION` — calibrar no Passo 10

---

## 16. Próximo passo

**Passo 5 — Implementar `BedrockKnowledgeBaseRetriever`**

- Implementa `Retriever`
- Usa `bedrock-agent-runtime:Retrieve` em sa-east-1
- Mapeia exceções boto3/botocore para `RetrieverError`
- Converte `RetrieveResponse` em `list[RetrievedChunk]`
- Não usa `RetrieveAndGenerate`
- Testes com mocks do SDK (sem chamadas reais)
