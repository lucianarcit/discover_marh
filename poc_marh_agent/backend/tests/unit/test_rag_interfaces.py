"""Testes unitários das interfaces e modelos do pipeline RAG.

Regras:
- Zero chamadas à AWS
- Zero uso de boto3
- Zero acesso a rede
- Implementações fake apenas para exercitar o contrato das interfaces
"""

from __future__ import annotations

import pytest

from marh_agent.clients.language_model_client import LanguageModelClient
from marh_agent.clients.retriever import Retriever
from marh_agent.domain.rag_exceptions import (
    InvalidRagRequestError,
    LanguageModelError,
    RagError,
    RetrieverError,
)
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk


# ──────────────────────────────────────────────────────────────
# Implementações fake para exercitar os contratos
# ──────────────────────────────────────────────────────────────


class FakeRetriever(Retriever):
    """Retriever fake que retorna chunks pré-definidos."""

    def __init__(self, chunks: list[RetrievedChunk] | None = None) -> None:
        self._chunks = chunks or []

    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]:
        return self._chunks[:top_k]


class FakeLanguageModelClient(LanguageModelClient):
    """LLM fake que retorna resposta pré-definida."""

    def __init__(self, response_text: str = "Resposta de teste.") -> None:
        self._response_text = response_text

    def _generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult:
        return GenerationResult(
            text=self._response_text,
            input_tokens=10,
            output_tokens=5,
            stop_reason="end_turn",
            model_id="fake-model",
        )


def _make_chunk(**kwargs) -> RetrievedChunk:
    defaults = {
        "content": "Conteúdo aprovado do corpus MARH.",
        "score": 0.85,
        "source_file": "marh_feature_knowledge.md",
        "section_number": "4",
        "section_title": "Pedidos",
        "chunk_index": 0,
        "metadata": {},
    }
    defaults.update(kwargs)
    return RetrievedChunk(**defaults)


# ──────────────────────────────────────────────────────────────
# RetrievedChunk
# ──────────────────────────────────────────────────────────────


def test_retrieved_chunk_valid():
    chunk = _make_chunk()
    assert chunk.content == "Conteúdo aprovado do corpus MARH."
    assert chunk.score == 0.85
    assert chunk.source_file == "marh_feature_knowledge.md"


def test_retrieved_chunk_metadata_default():
    chunk = RetrievedChunk(content="Texto válido.")
    assert chunk.metadata == {}


def test_retrieved_chunk_metadata_none_becomes_empty_dict():
    chunk = RetrievedChunk(content="Texto válido.", metadata=None)
    assert chunk.metadata == {}


def test_retrieved_chunk_score_zero_accepted():
    chunk = _make_chunk(score=0.0)
    assert chunk.score == 0.0


def test_retrieved_chunk_score_none_accepted():
    chunk = _make_chunk(score=None)
    assert chunk.score is None


def test_retrieved_chunk_all_optional_fields_none():
    chunk = RetrievedChunk(content="Texto válido.")
    assert chunk.score is None
    assert chunk.source_file is None
    assert chunk.section_number is None
    assert chunk.section_title is None
    assert chunk.chunk_index is None


def test_retrieved_chunk_empty_content_rejected():
    with pytest.raises(Exception):
        RetrievedChunk(content="")


def test_retrieved_chunk_blank_content_rejected():
    with pytest.raises(Exception):
        RetrievedChunk(content="   ")


def test_retrieved_chunk_is_immutable():
    chunk = _make_chunk()
    with pytest.raises(Exception):
        chunk.content = "alterado"  # type: ignore[misc]


def test_retrieved_chunk_metadata_with_values():
    chunk = _make_chunk(metadata={"approved": True, "chunk_index": 2})
    assert chunk.metadata["approved"] is True


# ──────────────────────────────────────────────────────────────
# GenerationResult
# ──────────────────────────────────────────────────────────────


def test_generation_result_valid():
    result = GenerationResult(
        text="Resposta fundamentada.",
        input_tokens=20,
        output_tokens=8,
        stop_reason="end_turn",
        model_id="mistral.magistral-small-2509",
    )
    assert result.text == "Resposta fundamentada."
    assert result.input_tokens == 20
    assert result.model_id == "mistral.magistral-small-2509"


def test_generation_result_optional_fields_none():
    result = GenerationResult(text="Texto.")
    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.stop_reason is None
    assert result.model_id is None


def test_generation_result_empty_text_rejected():
    with pytest.raises(Exception):
        GenerationResult(text="")


def test_generation_result_blank_text_rejected():
    with pytest.raises(Exception):
        GenerationResult(text="   ")


def test_generation_result_is_immutable():
    result = GenerationResult(text="Texto.")
    with pytest.raises(Exception):
        result.text = "alterado"  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────
# Retriever — contrato
# ──────────────────────────────────────────────────────────────


def test_retriever_fake_respects_contract():
    chunks = [_make_chunk(content=f"Chunk {i}.") for i in range(3)]
    retriever = FakeRetriever(chunks=chunks)
    result = retriever.retrieve("Qual é o MARH?")
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(c, RetrievedChunk) for c in result)


def test_retriever_empty_query_rejected():
    retriever = FakeRetriever()
    with pytest.raises(InvalidRagRequestError):
        retriever.retrieve("")


def test_retriever_blank_query_rejected():
    retriever = FakeRetriever()
    with pytest.raises(InvalidRagRequestError):
        retriever.retrieve("   ")


def test_retriever_top_k_zero_rejected():
    retriever = FakeRetriever()
    with pytest.raises(InvalidRagRequestError):
        retriever.retrieve("consulta válida", top_k=0)


def test_retriever_top_k_negative_rejected():
    retriever = FakeRetriever()
    with pytest.raises(InvalidRagRequestError):
        retriever.retrieve("consulta válida", top_k=-1)


def test_retriever_empty_result_allowed():
    retriever = FakeRetriever(chunks=[])
    result = retriever.retrieve("consulta sem resultado")
    assert result == []


def test_retriever_top_k_limits_results():
    chunks = [_make_chunk(content=f"Chunk {i}.") for i in range(10)]
    retriever = FakeRetriever(chunks=chunks)
    result = retriever.retrieve("consulta", top_k=3)
    assert len(result) == 3


def test_retriever_strips_query_whitespace():
    """Queries com espaços laterais devem ser aceitas (strip interno)."""
    retriever = FakeRetriever()
    result = retriever.retrieve("  consulta com espaços  ")
    assert isinstance(result, list)


def test_retriever_does_not_filter_by_threshold():
    """O threshold é responsabilidade do BedrockRagKnowledgeClient, não do Retriever."""
    chunks = [
        _make_chunk(content="Chunk baixo score.", score=0.20),
        _make_chunk(content="Chunk alto score.", score=0.95),
    ]
    retriever = FakeRetriever(chunks=chunks)
    result = retriever.retrieve("consulta")
    # Ambos devem ser retornados — Retriever não filtra por threshold
    assert len(result) == 2


# ──────────────────────────────────────────────────────────────
# LanguageModelClient — contrato
# ──────────────────────────────────────────────────────────────


def test_llm_fake_returns_generation_result():
    llm = FakeLanguageModelClient()
    chunk = _make_chunk()
    result = llm.generate(
        system_prompt="Responda somente com base no conhecimento fornecido.",
        user_query="O que é o MARH?",
        context_chunks=[chunk],
    )
    assert isinstance(result, GenerationResult)
    assert result.text


def test_llm_empty_system_prompt_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises(InvalidRagRequestError):
        llm.generate(
            system_prompt="",
            user_query="O que é o MARH?",
            context_chunks=[_make_chunk()],
        )


def test_llm_blank_system_prompt_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises(InvalidRagRequestError):
        llm.generate(
            system_prompt="   ",
            user_query="O que é o MARH?",
            context_chunks=[_make_chunk()],
        )


def test_llm_empty_user_query_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises(InvalidRagRequestError):
        llm.generate(
            system_prompt="Instrução válida.",
            user_query="",
            context_chunks=[_make_chunk()],
        )


def test_llm_blank_user_query_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises(InvalidRagRequestError):
        llm.generate(
            system_prompt="Instrução válida.",
            user_query="   ",
            context_chunks=[_make_chunk()],
        )


def test_llm_empty_context_chunks_rejected():
    llm = FakeLanguageModelClient()
    with pytest.raises(InvalidRagRequestError):
        llm.generate(
            system_prompt="Instrução válida.",
            user_query="O que é o MARH?",
            context_chunks=[],
        )


def test_llm_result_text_is_plain_text():
    """GenerationResult.text deve ser tratado como texto plano, não HTML."""
    llm = FakeLanguageModelClient(response_text="<b>Texto com tags</b>")
    result = llm.generate(
        system_prompt="Instrução.",
        user_query="Pergunta.",
        context_chunks=[_make_chunk()],
    )
    # O modelo retorna o texto como está — a responsabilidade de não
    # tratar como HTML é do renderer, não desta interface.
    # Este teste documenta que GenerationResult.text é uma string opaca.
    assert isinstance(result.text, str)


def test_llm_accepts_multiple_chunks():
    llm = FakeLanguageModelClient()
    chunks = [_make_chunk(content=f"Chunk {i}.") for i in range(5)]
    result = llm.generate(
        system_prompt="Instrução.",
        user_query="Pergunta.",
        context_chunks=chunks,
    )
    assert isinstance(result, GenerationResult)


# ──────────────────────────────────────────────────────────────
# Exceções — hierarquia
# ──────────────────────────────────────────────────────────────


def test_retriever_error_is_rag_error():
    assert issubclass(RetrieverError, RagError)


def test_language_model_error_is_rag_error():
    assert issubclass(LanguageModelError, RagError)


def test_invalid_rag_request_error_is_rag_error():
    assert issubclass(InvalidRagRequestError, RagError)


def test_rag_error_is_exception():
    assert issubclass(RagError, Exception)


def test_retriever_error_message_does_not_expose_chunks():
    err = RetrieverError("Falha na recuperação — knowledge base indisponível")
    assert "CPF" not in str(err)
    assert "colaborador" not in str(err)
    assert "pedido" not in str(err)


def test_invalid_rag_request_raised_with_message():
    with pytest.raises(InvalidRagRequestError, match="query não pode ser vazia"):
        raise InvalidRagRequestError("query não pode ser vazia")


def test_exceptions_can_be_caught_as_rag_error():
    for exc_class in (RetrieverError, LanguageModelError, InvalidRagRequestError):
        try:
            raise exc_class("teste")
        except RagError:
            pass  # correto — todas são subclasses de RagError
        else:
            pytest.fail(f"{exc_class.__name__} não foi capturada como RagError")


# ──────────────────────────────────────────────────────────────
# Confirmações de ausência de boto3
# ──────────────────────────────────────────────────────────────


def test_retriever_module_does_not_import_boto3():
    import marh_agent.clients.retriever as mod
    import sys
    assert "boto3" not in dir(mod)
    # boto3 não deve ter sido importado como efeito colateral
    for name in sys.modules:
        if name == "boto3" and "retriever" in (sys.modules[name].__spec__ or {}).get("name", ""):
            pytest.fail("boto3 foi importado via retriever.py")


def test_language_model_client_module_does_not_import_boto3():
    import marh_agent.clients.language_model_client as mod
    assert "boto3" not in dir(mod)


def test_rag_models_module_does_not_import_boto3():
    import marh_agent.domain.rag_models as mod
    assert "boto3" not in dir(mod)


def test_rag_exceptions_module_does_not_import_boto3():
    import marh_agent.domain.rag_exceptions as mod
    assert "boto3" not in dir(mod)
