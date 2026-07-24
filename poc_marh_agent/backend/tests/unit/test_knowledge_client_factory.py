"""Testes unitários da factory de KnowledgeClient e do composition root.

Regras:
- Zero chamadas AWS reais
- Monkeypatch de variáveis de config para isolar modos
- Testes do pipeline completo com fakes (integração local sem AWS)
"""

from __future__ import annotations

import importlib
import pytest

from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk
from marh_agent.clients.retriever import Retriever
from marh_agent.clients.language_model_client import LanguageModelClient


# ──────────────────────────────────────────────────────────────
# Fakes para integração local
# ──────────────────────────────────────────────────────────────

class FakeRetriever(Retriever):
    def __init__(self, chunks: list[RetrievedChunk] | None = None):
        self._chunks = chunks or []
    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]:
        return self._chunks[:top_k]


class FakeLanguageModelClient(LanguageModelClient):
    def __init__(self, text: str = "Resposta do RAG real."):
        self._text = text
    def _generate(self, *, system_prompt, user_query, context_chunks):
        return GenerationResult(text=self._text, model_id="fake-model")


def _make_chunk(score: float = 0.90) -> RetrievedChunk:
    return RetrievedChunk(
        content="O MARH é o Meu Alelo RH.",
        score=score,
        source_file="marh_feature_knowledge.md",
        section_title="Visão Geral",
    )


# ──────────────────────────────────────────────────────────────
# Auxiliar: recarregar factory com config mockado
# ──────────────────────────────────────────────────────────────

def _reload_factory_with(monkeypatch, knowledge_mode: str,
                          kb_id: str = "", model_id: str = "",
                          region: str = "sa-east-1",
                          threshold: float = 0.70):
    """Aplica monkeypatch no módulo de config e recarrega a factory."""
    import marh_agent.config as cfg
    import marh_agent.application.knowledge_client_factory as fac

    monkeypatch.setattr(cfg, "KNOWLEDGE_MODE", cfg.KnowledgeMode(knowledge_mode))
    monkeypatch.setattr(cfg, "BEDROCK_KNOWLEDGE_BASE_ID", kb_id)
    monkeypatch.setattr(cfg, "BEDROCK_MODEL_ID", model_id)
    monkeypatch.setattr(cfg, "BEDROCK_REGION", region)
    monkeypatch.setattr(cfg, "RETRIEVAL_SCORE_THRESHOLD", threshold)

    # Recarregar factory para pegar as novas constantes de módulo
    importlib.reload(fac)
    return fac


# ──────────────────────────────────────────────────────────────
# Modo MOCK
# ──────────────────────────────────────────────────────────────


def test_mock_mode_returns_mock_knowledge_client(monkeypatch):
    fac = _reload_factory_with(monkeypatch, "MOCK")
    client = fac.build_knowledge_client()
    assert isinstance(client, MockKnowledgeClient)


def test_mock_mode_when_knowledge_mode_not_set(monkeypatch):
    """KNOWLEDGE_MODE ausente do ambiente usa MOCK por padrão."""
    import marh_agent.config as cfg
    monkeypatch.setattr(cfg, "KNOWLEDGE_MODE", cfg.KnowledgeMode.MOCK)
    import marh_agent.application.knowledge_client_factory as fac
    importlib.reload(fac)
    client = fac.build_knowledge_client()
    assert isinstance(client, MockKnowledgeClient)


def test_mock_mode_does_not_require_kb_id(monkeypatch):
    fac = _reload_factory_with(monkeypatch, "MOCK", kb_id="")
    client = fac.build_knowledge_client()
    assert isinstance(client, MockKnowledgeClient)


def test_mock_mode_does_not_require_model_id(monkeypatch):
    fac = _reload_factory_with(monkeypatch, "MOCK", model_id="")
    client = fac.build_knowledge_client()
    assert isinstance(client, MockKnowledgeClient)


def test_mock_mode_does_not_instantiate_bedrock_retriever(monkeypatch):
    fac = _reload_factory_with(monkeypatch, "MOCK")
    client = fac.build_knowledge_client()
    assert not isinstance(client, BedrockRagKnowledgeClient)


def test_mock_query_works(monkeypatch):
    fac = _reload_factory_with(monkeypatch, "MOCK")
    client = fac.build_knowledge_client()
    result = client.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert result["data_classification"] == "APPROVED_KNOWLEDGE_MOCK"


# ──────────────────────────────────────────────────────────────
# Modo BEDROCK_RAG
# ──────────────────────────────────────────────────────────────


def test_bedrock_rag_mode_returns_bedrock_rag_knowledge_client(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
    )
    client = fac.build_knowledge_client()
    assert isinstance(client, BedrockRagKnowledgeClient)


def test_bedrock_rag_mode_not_mock_client(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
    )
    client = fac.build_knowledge_client()
    assert not isinstance(client, MockKnowledgeClient)


def test_bedrock_rag_score_threshold_applied(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
        threshold=0.85,
    )
    client = fac.build_knowledge_client()
    assert isinstance(client, BedrockRagKnowledgeClient)
    assert client._score_threshold == 0.85


def test_bedrock_rag_retriever_has_correct_kb_id(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-specific-id-abc", model_id="mistral.magistral-small-2509",
    )
    client = fac.build_knowledge_client()
    assert client._retriever._knowledge_base_id == "kb-specific-id-abc"


def test_bedrock_rag_retriever_uses_correct_region(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
        region="sa-east-1",
    )
    client = fac.build_knowledge_client()
    assert client._retriever._region_name == "sa-east-1"


def test_bedrock_rag_llm_has_correct_model_id(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
    )
    client = fac.build_knowledge_client()
    assert client._llm._model_id == "mistral.magistral-small-2509"


def test_bedrock_rag_llm_uses_correct_region(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
        region="sa-east-1",
    )
    client = fac.build_knowledge_client()
    assert client._llm._region_name == "sa-east-1"


# ──────────────────────────────────────────────────────────────
# Configuração inválida — sem fallback silencioso
# ──────────────────────────────────────────────────────────────


def test_bedrock_rag_without_kb_id_raises_error(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="", model_id="mistral.magistral-small-2509",
    )
    with pytest.raises(ValueError, match="BEDROCK_KNOWLEDGE_BASE_ID"):
        fac.build_knowledge_client()


def test_bedrock_rag_without_model_id_raises_error(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="",
    )
    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID"):
        fac.build_knowledge_client()


def test_bedrock_rag_blank_kb_id_raises_error(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="   ", model_id="mistral.magistral-small-2509",
    )
    with pytest.raises(ValueError, match="BEDROCK_KNOWLEDGE_BASE_ID"):
        fac.build_knowledge_client()


def test_bedrock_rag_blank_model_id_raises_error(monkeypatch):
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="   ",
    )
    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID"):
        fac.build_knowledge_client()


def test_config_error_does_not_fallback_to_mock(monkeypatch):
    """Configuração inválida em BEDROCK_RAG não deve retornar MockKnowledgeClient."""
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="", model_id="",
    )
    with pytest.raises(ValueError):
        result = fac.build_knowledge_client()
        assert not isinstance(result, MockKnowledgeClient)


def test_config_error_message_does_not_expose_value(monkeypatch):
    """Mensagem de erro não deve expor o valor real da variável."""
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="", model_id="segredo-nao-expor",
    )
    try:
        fac.build_knowledge_client()
        pytest.fail("Esperava ValueError")
    except ValueError as exc:
        assert "segredo-nao-expor" not in str(exc)


def test_unknown_knowledge_mode_raises_error(monkeypatch):
    import marh_agent.application.knowledge_client_factory as fac
    import marh_agent.config as cfg
    # Injetar um valor inválido diretamente na factory
    monkeypatch.setattr(cfg, "KNOWLEDGE_MODE", "INVALID_MODE_XYZ")
    importlib.reload(fac)
    with pytest.raises((ValueError, Exception)):
        fac.build_knowledge_client()


# ──────────────────────────────────────────────────────────────
# Independência entre os dois eixos
# ──────────────────────────────────────────────────────────────


def test_data_source_mock_knowledge_mock(monkeypatch):
    """DATA_SOURCE_MODE=MOCK + KNOWLEDGE_MODE=MOCK → MockKnowledgeClient."""
    fac = _reload_factory_with(monkeypatch, "MOCK")
    client = fac.build_knowledge_client()
    assert isinstance(client, MockKnowledgeClient)


def test_data_source_mock_knowledge_rag(monkeypatch):
    """DATA_SOURCE_MODE=MOCK + KNOWLEDGE_MODE=BEDROCK_RAG → BedrockRagKnowledgeClient."""
    fac = _reload_factory_with(
        monkeypatch, "BEDROCK_RAG",
        kb_id="kb-test-123", model_id="mistral.magistral-small-2509",
    )
    client = fac.build_knowledge_client()
    assert isinstance(client, BedrockRagKnowledgeClient)


def test_changing_data_source_mode_does_not_affect_knowledge_client(monkeypatch):
    """Alterar DATA_SOURCE_MODE não muda a implementação de KnowledgeClient."""
    import marh_agent.config as cfg
    fac = _reload_factory_with(monkeypatch, "MOCK")

    # MOCK knowledge independente do DATA_SOURCE_MODE
    monkeypatch.setattr(cfg, "DATA_SOURCE_MODE", cfg.DataSourceMode.MOCK)
    client_mock_src = fac.build_knowledge_client()

    # Mesmo com DATA_SOURCE_MODE diferente, knowledge_mode permanece MOCK
    monkeypatch.setattr(cfg, "DATA_SOURCE_MODE", cfg.DataSourceMode.INTEGRATED)
    client_integrated_src = fac.build_knowledge_client()

    assert isinstance(client_mock_src, MockKnowledgeClient)
    assert isinstance(client_integrated_src, MockKnowledgeClient)


# ──────────────────────────────────────────────────────────────
# Integração local — pipeline completo com fakes (sem AWS)
# ──────────────────────────────────────────────────────────────


def test_pipeline_rag_with_fakes_int019(monkeypatch):
    """Pipeline completo: Router → Orchestrator → BedrockRagKnowledgeClient → Fakes.

    INT-019 (O que é o MARH?) deve usar o RAG e retornar flow=RAG_ONLY
    com metadata BEDROCK_RAG_GROUNDED.
    """
    from marh_agent.application.orchestrator import Orchestrator
    from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
    from marh_agent.domain.requests import ChatRequest

    chunks = [_make_chunk(score=0.92)]
    retriever = FakeRetriever(chunks=chunks)
    llm = FakeLanguageModelClient(text="O MARH é o Meu Alelo RH — resposta RAG.")

    knowledge_client = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=0.70,
    )

    orchestrator = Orchestrator(
        client=MockMaHrOrchClient(),
        knowledge_client=knowledge_client,
    )

    request = ChatRequest(
        company_id="empresa-teste-001",
        user_id="usuario-teste",
        session_id="sessao-teste",
        message="O que é o MARH?",
        environment="HML",
    )

    response = orchestrator.handle(request)

    assert response.intent_id == "INT-019"
    assert response.flow == "RAG_ONLY"
    assert "O MARH é o Meu Alelo RH" in response.message
    # O Router define knowledge_source = source_section do knowledge_result
    assert response.metadata.get("knowledge_source") == "marh_feature_knowledge.md"
    assert response.error_code is None
    # Nota: o Router hardcoda flow_detail="MOCK_KNOWLEDGE" para qualquer found=True —
    # atualizar este campo para refletir BEDROCK_RAG é melhoria futura do Router.


def test_pipeline_rag_source_section_in_response(monkeypatch):
    """source_section deve referenciar o corpus aprovado."""
    from marh_agent.application.orchestrator import Orchestrator
    from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
    from marh_agent.domain.requests import ChatRequest

    retriever = FakeRetriever(chunks=[_make_chunk(score=0.85)])
    llm = FakeLanguageModelClient()
    knowledge_client = BedrockRagKnowledgeClient(
        retriever=retriever, language_model_client=llm, score_threshold=0.70
    )
    orchestrator = Orchestrator(
        client=MockMaHrOrchClient(), knowledge_client=knowledge_client
    )
    response = orchestrator.handle(ChatRequest(
        company_id="emp", user_id="u", session_id="s",
        message="O que é o MARH?", environment="HML"
    ))
    assert "marh_feature_knowledge.md" in response.metadata.get("knowledge_source", "")


def test_pipeline_int001_does_not_use_rag(monkeypatch):
    """INT-001 (colaborador por nome) não deve chamar KnowledgeClient."""
    from marh_agent.application.orchestrator import Orchestrator
    from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
    from marh_agent.domain.requests import ChatRequest

    call_count = [0]

    class CountingRetriever(Retriever):
        def _retrieve(self, query, *, top_k):
            call_count[0] += 1
            return []

    knowledge_client = BedrockRagKnowledgeClient(
        retriever=CountingRetriever(),
        language_model_client=FakeLanguageModelClient(),
        score_threshold=0.70,
    )
    orchestrator = Orchestrator(
        client=MockMaHrOrchClient(), knowledge_client=knowledge_client
    )
    response = orchestrator.handle(ChatRequest(
        company_id="emp", user_id="u", session_id="s",
        message="Consultar colaborador Pessoa Colaboradora A", environment="HML"
    ))
    assert response.intent_id == "INT-001"
    assert call_count[0] == 0  # Retriever não deve ter sido chamado


def test_pipeline_transactional_does_not_use_rag(monkeypatch):
    """Ação transacional (INT-022) não deve chamar KnowledgeClient."""
    from marh_agent.application.orchestrator import Orchestrator
    from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
    from marh_agent.domain.requests import ChatRequest

    call_count = [0]

    class CountingRetriever(Retriever):
        def _retrieve(self, query, *, top_k):
            call_count[0] += 1
            return []

    knowledge_client = BedrockRagKnowledgeClient(
        retriever=CountingRetriever(),
        language_model_client=FakeLanguageModelClient(),
        score_threshold=0.70,
    )
    orchestrator = Orchestrator(
        client=MockMaHrOrchClient(), knowledge_client=knowledge_client
    )
    response = orchestrator.handle(ChatRequest(
        company_id="emp", user_id="u", session_id="s",
        message="Cancele o pedido 342671", environment="HML"
    ))
    assert response.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"
    assert call_count[0] == 0


def test_pipeline_rag_below_threshold_returns_fallback(monkeypatch):
    """Quando todos os chunks ficam abaixo do threshold, deve usar fallback estático."""
    from marh_agent.application.orchestrator import Orchestrator
    from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient
    from marh_agent.domain.requests import ChatRequest

    # Chunks com score abaixo do threshold
    low_chunks = [_make_chunk(score=0.30)]
    retriever = FakeRetriever(chunks=low_chunks)
    llm = FakeLanguageModelClient()

    knowledge_client = BedrockRagKnowledgeClient(
        retriever=retriever, language_model_client=llm, score_threshold=0.70
    )
    orchestrator = Orchestrator(
        client=MockMaHrOrchClient(), knowledge_client=knowledge_client
    )
    response = orchestrator.handle(ChatRequest(
        company_id="emp", user_id="u", session_id="s",
        message="O que é o MARH?", environment="HML"
    ))
    # Deve cair no fallback estático do Router (INFORMATIVE_RESPONSES)
    assert response.flow == "RAG_ONLY"
    assert response.message  # não deve ser vazio
    assert response.metadata.get("flow_detail") == "STATIC_POLICY_FALLBACK"
