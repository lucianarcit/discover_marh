"""Testes unitários do BedrockRagKnowledgeClient com fakes.

Regras:
- Zero chamadas AWS
- Zero uso de boto3
- Zero acesso à rede
- Implementações fake completas e inspecionáveis
"""

from __future__ import annotations

import pytest

from marh_agent.clients.bedrock_rag_knowledge_client import (
    DEFAULT_SYSTEM_PROMPT,
    BedrockRagKnowledgeClient,
    _DEFAULT_TOPIC_QUERY_MAP,
)
from marh_agent.clients.language_model_client import LanguageModelClient
from marh_agent.clients.retriever import Retriever
from marh_agent.domain.rag_exceptions import (
    InvalidRagRequestError,
    LanguageModelError,
    RetrieverError,
)
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk


# ──────────────────────────────────────────────────────────────
# Fakes inspecionáveis
# ──────────────────────────────────────────────────────────────


class FakeRetriever(Retriever):
    """Retriever fake totalmente controlável por teste."""

    def __init__(
        self,
        chunks: list[RetrievedChunk] | None = None,
        raise_error: Exception | None = None,
    ) -> None:
        self._chunks = chunks or []
        self._raise_error = raise_error
        # Inspeção
        self.call_count: int = 0
        self.last_query: str | None = None
        self.last_top_k: int | None = None

    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]:
        self.call_count += 1
        self.last_query = query
        self.last_top_k = top_k
        if self._raise_error is not None:
            raise self._raise_error
        return self._chunks[:top_k]


class FakeLanguageModelClient(LanguageModelClient):
    """LLM fake totalmente controlável por teste."""

    def __init__(
        self,
        result: GenerationResult | None = None,
        raise_error: Exception | None = None,
    ) -> None:
        self._result = result or GenerationResult(
            text="Resposta fundamentada no corpus aprovado.",
            input_tokens=10,
            output_tokens=5,
            stop_reason="end_turn",
            model_id="fake-model-v1",
        )
        self._raise_error = raise_error
        # Inspeção
        self.call_count: int = 0
        self.last_system_prompt: str | None = None
        self.last_user_query: str | None = None
        self.last_chunks: list[RetrievedChunk] | None = None

    def _generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult:
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_query = user_query
        self.last_chunks = list(context_chunks)
        if self._raise_error is not None:
            raise self._raise_error
        return self._result


def _make_chunk(score: float | None = 0.85, content: str = "Conteúdo aprovado.") -> RetrievedChunk:
    return RetrievedChunk(
        content=content,
        score=score,
        source_file="marh_feature_knowledge.md",
        section_number="1",
        section_title="Contexto",
    )


def _make_client(
    chunks: list[RetrievedChunk] | None = None,
    llm_result: GenerationResult | None = None,
    retriever_error: Exception | None = None,
    llm_error: Exception | None = None,
    score_threshold: float = 0.70,
    top_k: int = 5,
) -> tuple[BedrockRagKnowledgeClient, FakeRetriever, FakeLanguageModelClient]:
    retriever = FakeRetriever(chunks=chunks, raise_error=retriever_error)
    llm = FakeLanguageModelClient(result=llm_result, raise_error=llm_error)
    client = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=score_threshold,
        top_k=top_k,
    )
    return client, retriever, llm


# ──────────────────────────────────────────────────────────────
# Construção — validações de parâmetros
# ──────────────────────────────────────────────────────────────


def test_construction_valid():
    client, _, _ = _make_client(score_threshold=0.70)
    assert client is not None


def test_construction_threshold_zero_accepted():
    client, _, _ = _make_client(score_threshold=0.0)
    assert client is not None


def test_construction_threshold_one_accepted():
    client, _, _ = _make_client(score_threshold=1.0)
    assert client is not None


def test_construction_threshold_negative_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="score_threshold"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=-0.01,
        )


def test_construction_threshold_above_one_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="score_threshold"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=1.01,
        )


def test_construction_top_k_zero_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="top_k"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=0.70,
            top_k=0,
        )


def test_construction_retriever_none_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises((ValueError, TypeError)):
        BedrockRagKnowledgeClient(
            retriever=None,  # type: ignore[arg-type]
            language_model_client=llm,
            score_threshold=0.70,
        )


def test_construction_llm_none_rejected():
    retriever = FakeRetriever()
    with pytest.raises((ValueError, TypeError)):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=None,  # type: ignore[arg-type]
            score_threshold=0.70,
        )


def test_construction_system_prompt_empty_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="system_prompt"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=0.70,
            system_prompt="",
        )


def test_construction_system_prompt_blank_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="system_prompt"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=0.70,
            system_prompt="   ",
        )


def test_construction_empty_topic_map_rejected():
    retriever = FakeRetriever()
    llm = FakeLanguageModelClient()
    with pytest.raises(ValueError, match="topic_query_map"):
        BedrockRagKnowledgeClient(
            retriever=retriever,
            language_model_client=llm,
            score_threshold=0.70,
            topic_query_map={},
        )


# ──────────────────────────────────────────────────────────────
# Mapa de tópicos — 14 tópicos oficiais
# ──────────────────────────────────────────────────────────────

OFFICIAL_TOPICS = [
    "AGENT_CAPABILITIES",
    "CONSULTABLE_INFO",
    "ORDER_PROCESS",
    "HOW_CONSULT_ORDER",
    "HOW_CONSULT_COLLABORATOR",
    "CARD_TRACKING_INFO",
    "CANNOT_CANCEL",
    "CANNOT_EDIT_COLLABORATOR",
    "COMPANY_SCOPE",
    "COMPANY_REQUIRED",
    "AGENT_VS_PORTAL",
    "MARH_OVERVIEW",
    "ESPACO_RH_OVERVIEW",
    "QUESTION_TYPES",
]


@pytest.mark.parametrize("topic", OFFICIAL_TOPICS)
def test_all_14_official_topics_have_query(topic):
    assert topic in _DEFAULT_TOPIC_QUERY_MAP
    assert _DEFAULT_TOPIC_QUERY_MAP[topic]


def test_exactly_14_topics_in_default_map():
    assert len(_DEFAULT_TOPIC_QUERY_MAP) == 14


def test_order_status_info_not_in_default_map():
    """ORDER_STATUS_INFO é tópico órfão — não deve estar no mapa."""
    assert "ORDER_STATUS_INFO" not in _DEFAULT_TOPIC_QUERY_MAP


def test_all_queries_are_nonempty_strings():
    for topic, query in _DEFAULT_TOPIC_QUERY_MAP.items():
        assert isinstance(query, str) and query.strip(), (
            f"Query vazia para tópico: {topic}"
        )


def test_topic_map_is_immutable():
    """O mapa padrão deve ser imutável."""
    from types import MappingProxyType
    assert isinstance(_DEFAULT_TOPIC_QUERY_MAP, MappingProxyType)


# ──────────────────────────────────────────────────────────────
# Tópicos — comportamento do método query
# ──────────────────────────────────────────────────────────────


def test_unknown_topic_returns_not_found():
    client, retriever, llm = _make_client()
    result = client.query("TOPICO_INEXISTENTE")
    assert result["found"] is False
    assert result["content"] is None
    assert retriever.call_count == 0
    assert llm.call_count == 0


def test_empty_topic_returns_not_found():
    client, retriever, llm = _make_client()
    result = client.query("")
    assert result["found"] is False
    assert retriever.call_count == 0


def test_blank_topic_treated_as_empty():
    client, retriever, llm = _make_client()
    result = client.query("   ")
    assert result["found"] is False
    assert retriever.call_count == 0


def test_known_topic_calls_retriever_with_correct_query():
    chunk = _make_chunk(score=0.90)
    client, retriever, llm = _make_client(chunks=[chunk])
    client.query("MARH_OVERVIEW")
    assert retriever.call_count == 1
    assert "MARH" in retriever.last_query or "Meu Alelo" in retriever.last_query


@pytest.mark.parametrize("topic", OFFICIAL_TOPICS)
def test_each_official_topic_calls_retriever_with_expected_query(topic):
    chunk = _make_chunk(score=0.90)
    client, retriever, llm = _make_client(chunks=[chunk])
    client.query(topic)
    assert retriever.call_count == 1
    assert retriever.last_query == _DEFAULT_TOPIC_QUERY_MAP[topic]


def test_topic_normalization_uppercase():
    """Tópico em letras minúsculas deve ser normalizado e encontrado."""
    chunk = _make_chunk(score=0.90)
    client, retriever, llm = _make_client(chunks=[chunk])
    result = client.query("marh_overview")
    assert result["found"] is True


# ──────────────────────────────────────────────────────────────
# Recuperação — filtragem por threshold
# ──────────────────────────────────────────────────────────────


def test_no_chunks_returns_not_found():
    client, retriever, llm = _make_client(chunks=[])
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is False
    assert llm.call_count == 0


def test_chunk_below_threshold_discarded():
    chunk = _make_chunk(score=0.50)  # abaixo de 0.70
    client, retriever, llm = _make_client(chunks=[chunk], score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is False
    assert llm.call_count == 0


def test_chunk_at_threshold_accepted():
    chunk = _make_chunk(score=0.70)  # igual ao threshold
    client, retriever, llm = _make_client(chunks=[chunk], score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert llm.call_count == 1


def test_chunk_above_threshold_accepted():
    chunk = _make_chunk(score=0.95)
    client, retriever, llm = _make_client(chunks=[chunk], score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is True


def test_score_none_discarded():
    chunk = _make_chunk(score=None)
    client, retriever, llm = _make_client(chunks=[chunk], score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is False
    assert llm.call_count == 0


def test_mixed_chunks_only_approved_passed_to_llm():
    chunks = [
        _make_chunk(score=0.90, content="Chunk aprovado alto."),
        _make_chunk(score=0.50, content="Chunk rejeitado baixo."),
        _make_chunk(score=None, content="Chunk rejeitado sem score."),
        _make_chunk(score=0.75, content="Chunk aprovado medio."),
    ]
    client, retriever, llm = _make_client(chunks=chunks, score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert llm.call_count == 1
    assert len(llm.last_chunks) == 2
    # Nenhum chunk rejeitado passou para o LLM
    contents = {c.content for c in llm.last_chunks}
    assert "Chunk rejeitado baixo." not in contents
    assert "Chunk rejeitado sem score." not in contents


def test_approved_chunks_ordered_by_score_descending():
    chunks = [
        _make_chunk(score=0.75, content="Chunk medio."),
        _make_chunk(score=0.95, content="Chunk alto."),
        _make_chunk(score=0.80, content="Chunk bom."),
    ]
    client, retriever, llm = _make_client(chunks=chunks, score_threshold=0.70)
    client.query("MARH_OVERVIEW")
    scores = [c.score for c in llm.last_chunks]
    assert scores == sorted(scores, reverse=True)


def test_top_k_forwarded_to_retriever():
    client, retriever, llm = _make_client(top_k=3)
    client.query("MARH_OVERVIEW")
    assert retriever.last_top_k == 3


def test_metadata_reports_retrieved_and_approved_counts():
    chunks = [
        _make_chunk(score=0.90),
        _make_chunk(score=0.40),  # rejeitado
        _make_chunk(score=None),  # rejeitado
    ]
    client, _, _ = _make_client(chunks=chunks, score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["metadata"]["retrieved_chunks"] == 3
    assert result["metadata"]["approved_chunks"] == 1


# ──────────────────────────────────────────────────────────────
# Geração — comportamento do LLM
# ──────────────────────────────────────────────────────────────


def test_llm_not_called_without_evidence():
    client, _, llm = _make_client(chunks=[])
    client.query("MARH_OVERVIEW")
    assert llm.call_count == 0


def test_llm_called_once_with_evidence():
    chunk = _make_chunk(score=0.90)
    client, _, llm = _make_client(chunks=[chunk])
    client.query("MARH_OVERVIEW")
    assert llm.call_count == 1


def test_llm_receives_only_approved_chunks():
    chunks = [_make_chunk(score=0.90), _make_chunk(score=0.30)]
    client, _, llm = _make_client(chunks=chunks, score_threshold=0.70)
    client.query("MARH_OVERVIEW")
    assert all(c.score >= 0.70 for c in llm.last_chunks)


def test_llm_receives_system_prompt():
    chunk = _make_chunk(score=0.90)
    client, _, llm = _make_client(chunks=[chunk])
    client.query("MARH_OVERVIEW")
    assert llm.last_system_prompt == DEFAULT_SYSTEM_PROMPT.strip()


def test_llm_receives_fixed_query_not_intent():
    chunk = _make_chunk(score=0.90)
    client, _, llm = _make_client(chunks=[chunk])
    client.query("MARH_OVERVIEW")
    assert llm.last_user_query == _DEFAULT_TOPIC_QUERY_MAP["MARH_OVERVIEW"]


def test_valid_generation_result_produces_found_true():
    chunk = _make_chunk(score=0.90)
    custom_result = GenerationResult(
        text="MARH é o Meu Alelo RH.",
        model_id="mistral.magistral-small-2509",
    )
    client, _, _ = _make_client(chunks=[chunk], llm_result=custom_result)
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert result["content"] == "MARH é o Meu Alelo RH."


def test_model_id_propagated_in_metadata_only():
    chunk = _make_chunk(score=0.90)
    custom_result = GenerationResult(
        text="Resposta.",
        model_id="mistral.magistral-small-2509",
    )
    client, _, _ = _make_client(chunks=[chunk], llm_result=custom_result)
    result = client.query("MARH_OVERVIEW")
    # model_id na metadata segura
    assert result["metadata"]["model_id"] == "mistral.magistral-small-2509"
    # model_id não aparece no content
    assert "mistral" not in result["content"]


def test_tokens_not_exposed_in_return():
    chunk = _make_chunk(score=0.90)
    custom_result = GenerationResult(text="Resposta.", input_tokens=100, output_tokens=20)
    client, _, _ = _make_client(chunks=[chunk], llm_result=custom_result)
    result = client.query("MARH_OVERVIEW")
    # tokens não devem aparecer no retorno ao Router
    assert "input_tokens" not in result
    assert "output_tokens" not in result
    assert "input_tokens" not in result.get("metadata", {})


# ──────────────────────────────────────────────────────────────
# Contrato de retorno — compatibilidade com MockKnowledgeClient
# ──────────────────────────────────────────────────────────────


def test_found_true_has_all_required_fields():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk])
    result = client.query("MARH_OVERVIEW")
    # Campos exigidos pelo Router (lê found, content, source_section)
    assert "found" in result
    assert "content" in result
    assert "source_section" in result
    assert "data_classification" in result
    assert "metadata" in result


def test_found_false_has_all_required_fields():
    client, _, _ = _make_client(chunks=[])
    result = client.query("MARH_OVERVIEW")
    assert "found" in result
    assert "content" in result
    assert "source_section" in result
    assert "metadata" in result


def test_source_section_references_corpus():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk])
    result = client.query("MARH_OVERVIEW")
    assert "marh_feature_knowledge.md" in result["source_section"]


def test_not_found_content_is_none():
    client, _, _ = _make_client(chunks=[])
    result = client.query("MARH_OVERVIEW")
    assert result["content"] is None


def test_data_classification_grounded_when_found():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk])
    result = client.query("MARH_OVERVIEW")
    assert result["data_classification"] == "BEDROCK_RAG_GROUNDED"


def test_data_classification_no_evidence_when_not_found():
    client, _, _ = _make_client(chunks=[])
    result = client.query("MARH_OVERVIEW")
    assert result["data_classification"] == "BEDROCK_RAG_NO_EVIDENCE"


def test_metadata_score_threshold_present():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk], score_threshold=0.70)
    result = client.query("MARH_OVERVIEW")
    assert result["metadata"]["score_threshold"] == 0.70


def test_metadata_flow_detail_always_bedrock_rag():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk])
    result_found = client.query("MARH_OVERVIEW")
    result_not_found = client.query("TOPICO_INEXISTENTE")
    assert result_found["metadata"]["flow_detail"] == "BEDROCK_RAG"
    assert result_not_found["metadata"]["flow_detail"] == "BEDROCK_RAG"


def test_metadata_does_not_contain_chunk_content():
    chunks = [_make_chunk(score=0.90, content="Texto sensível do corpus.")]
    client, _, _ = _make_client(chunks=chunks)
    result = client.query("MARH_OVERVIEW")
    metadata_str = str(result["metadata"])
    assert "Texto sensível do corpus." not in metadata_str


# ──────────────────────────────────────────────────────────────
# Erros — mapeamento e propagação
# ──────────────────────────────────────────────────────────────


def test_retriever_error_propagates():
    client, _, _ = _make_client(retriever_error=RetrieverError("KB indisponível"))
    with pytest.raises(RetrieverError):
        client.query("MARH_OVERVIEW")


def test_retriever_unexpected_error_wrapped_as_retriever_error():
    client, _, _ = _make_client(retriever_error=RuntimeError("conexão recusada"))
    with pytest.raises(RetrieverError):
        client.query("MARH_OVERVIEW")


def test_llm_error_propagates():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk], llm_error=LanguageModelError("throttle"))
    with pytest.raises(LanguageModelError):
        client.query("MARH_OVERVIEW")


def test_llm_unexpected_error_wrapped_as_llm_error():
    chunk = _make_chunk(score=0.90)
    client, _, _ = _make_client(chunks=[chunk], llm_error=OSError("timeout"))
    with pytest.raises(LanguageModelError):
        client.query("MARH_OVERVIEW")


def test_error_message_does_not_contain_chunk_content():
    sensitive_content = "Dados sensíveis do colaborador CPF 123."
    chunk = _make_chunk(score=0.90, content=sensitive_content)
    client, _, _ = _make_client(chunks=[chunk], llm_error=LanguageModelError("falha"))
    with pytest.raises(LanguageModelError) as exc_info:
        client.query("MARH_OVERVIEW")
    assert sensitive_content not in str(exc_info.value)


def test_invalid_rag_request_from_retriever_propagates():
    client, _, _ = _make_client(retriever_error=InvalidRagRequestError("parâmetro inválido"))
    with pytest.raises(InvalidRagRequestError):
        client.query("MARH_OVERVIEW")


# ──────────────────────────────────────────────────────────────
# Compatibilidade com MOCK existente
# ──────────────────────────────────────────────────────────────


def test_mock_knowledge_client_unaffected():
    """Garantia de que MockKnowledgeClient não foi alterado."""
    from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
    kc = MockKnowledgeClient()
    result = kc.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert result["data_classification"] == "APPROVED_KNOWLEDGE_MOCK"


def test_mock_knowledge_client_unknown_topic_unaffected():
    from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
    kc = MockKnowledgeClient()
    result = kc.query("TOPICO_INEXISTENTE")
    assert result["found"] is False


def test_bedrock_rag_client_does_not_import_boto3():
    import marh_agent.clients.bedrock_rag_knowledge_client as mod
    assert "boto3" not in dir(mod)


# ──────────────────────────────────────────────────────────────
# Injeção de mapa customizado
# ──────────────────────────────────────────────────────────────


def test_custom_topic_map_used():
    retriever = FakeRetriever(chunks=[_make_chunk(score=0.90)])
    llm = FakeLanguageModelClient()
    custom_map = {"CUSTOM_TOPIC": "Query personalizada para tópico customizado."}
    client = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=0.70,
        topic_query_map=custom_map,
    )
    result = client.query("CUSTOM_TOPIC")
    assert result["found"] is True
    assert retriever.last_query == "Query personalizada para tópico customizado."


def test_custom_system_prompt_forwarded_to_llm():
    retriever = FakeRetriever(chunks=[_make_chunk(score=0.90)])
    llm = FakeLanguageModelClient()
    custom_prompt = "Prompt customizado para avaliação."
    client = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=0.70,
        system_prompt=custom_prompt,
    )
    client.query("MARH_OVERVIEW")
    assert llm.last_system_prompt == custom_prompt
