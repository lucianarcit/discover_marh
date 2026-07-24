"""Testes da correção do Router — flow_detail lido do KnowledgeClient.

Cobre:
- MockKnowledgeClient continua retornando MOCK_KNOWLEDGE
- BedrockRagKnowledgeClient retorna BEDROCK_RAG
- source_files e campos seguros propagados
- metadata desconhecida não é propagada
- intenções fora do RAG não são afetadas
"""

from __future__ import annotations

import pytest

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest


def _req(msg: str) -> ChatRequest:
    return ChatRequest(
        company_id="emp-001",
        user_id="usr-001",
        session_id="ses-001",
        message=msg,
        environment="HML",
    )


def _make_orch(knowledge_client: KnowledgeClient) -> Orchestrator:
    return Orchestrator(client=MockMaHrOrchClient(), knowledge_client=knowledge_client)


# ──────────────────────────────────────────────────────────────
# Fake KnowledgeClients para testar o Router
# ──────────────────────────────────────────────────────────────


class FakeBedrockKnowledgeClient(KnowledgeClient):
    """Simula retorno do BedrockRagKnowledgeClient com metadata BEDROCK_RAG."""

    def query(self, topic: str) -> dict:
        return {
            "found": True,
            "content": f"Resposta RAG para {topic}.",
            "source_section": "marh_feature_knowledge.md",
            "data_classification": "BEDROCK_RAG_GROUNDED",
            "metadata": {
                "flow_detail": "BEDROCK_RAG",
                "data_classification": "BEDROCK_RAG_GROUNDED",
                "retrieved_chunks": 3,
                "approved_chunks": 2,
                "score_threshold": 0.70,
                "model_id": "fake-model",
            },
        }


class FakeKnowledgeClientNotFound(KnowledgeClient):
    """Simula retorno not_found."""

    def query(self, topic: str) -> dict:
        return {
            "found": False,
            "content": None,
            "source_section": "marh_feature_knowledge.md",
            "data_classification": "BEDROCK_RAG_NO_EVIDENCE",
            "metadata": {
                "flow_detail": "BEDROCK_RAG",
                "retrieved_chunks": 0,
                "approved_chunks": 0,
                "score_threshold": 0.70,
            },
        }


class FakeKnowledgeClientDangerousMeta(KnowledgeClient):
    """Tenta injetar campos não permitidos."""

    def query(self, topic: str) -> dict:
        return {
            "found": True,
            "content": "Conteúdo aprovado.",
            "source_section": "marh_feature_knowledge.md",
            "data_classification": "BEDROCK_RAG_GROUNDED",
            "metadata": {
                "flow_detail": "BEDROCK_RAG",
                "intent_id": "INT-INJECT",          # não deve ser propagado
                "authorization": "override",         # não deve ser propagado
                "navigation_override": "evil",       # não deve ser propagado
                "retrieved_chunks": 1,
                "approved_chunks": 1,
                "score_threshold": 0.70,
            },
        }


# ──────────────────────────────────────────────────────────────
# MockKnowledgeClient — deve manter MOCK_KNOWLEDGE
# ──────────────────────────────────────────────────────────────


def test_mock_knowledge_client_flow_detail_is_mock_knowledge():
    orch = _make_orch(MockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.intent_id == "INT-019"
    assert resp.flow == "RAG_ONLY"
    assert resp.metadata.get("flow_detail") == "MOCK_KNOWLEDGE"


def test_mock_knowledge_client_source_propagated():
    orch = _make_orch(MockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "knowledge_source" in resp.metadata


def test_mock_knowledge_client_int019_still_works():
    orch = _make_orch(MockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "marh" in resp.message.lower() or "meu alelo" in resp.message.lower()


# ──────────────────────────────────────────────────────────────
# BedrockRagKnowledgeClient fake — deve usar BEDROCK_RAG
# ──────────────────────────────────────────────────────────────


def test_bedrock_rag_client_flow_detail_is_bedrock_rag():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("flow_detail") == "BEDROCK_RAG"


def test_bedrock_rag_data_classification_propagated():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("data_classification") == "BEDROCK_RAG_GROUNDED"


def test_bedrock_rag_retrieved_chunks_propagated():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("retrieved_chunks") == 3


def test_bedrock_rag_approved_chunks_propagated():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("approved_chunks") == 2


def test_bedrock_rag_score_threshold_propagated():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("score_threshold") == 0.70


def test_bedrock_rag_source_section_propagated():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("knowledge_source") == "marh_feature_knowledge.md"


def test_bedrock_rag_content_used_as_message():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "Resposta RAG" in resp.message


# ──────────────────────────────────────────────────────────────
# Not-found — fallback estático
# ──────────────────────────────────────────────────────────────


def test_not_found_uses_static_fallback():
    orch = _make_orch(FakeKnowledgeClientNotFound())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("flow_detail") == "STATIC_POLICY_FALLBACK"


def test_not_found_message_is_not_empty():
    orch = _make_orch(FakeKnowledgeClientNotFound())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.message


# ──────────────────────────────────────────────────────────────
# Metadata desconhecida — não propagada
# ──────────────────────────────────────────────────────────────


def test_dangerous_metadata_intent_not_propagated():
    orch = _make_orch(FakeKnowledgeClientDangerousMeta())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "intent_id" not in resp.metadata
    # intent_id deve continuar sendo o da classificação, não o injetado
    assert resp.intent_id == "INT-019"


def test_dangerous_metadata_authorization_not_propagated():
    orch = _make_orch(FakeKnowledgeClientDangerousMeta())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "authorization" not in resp.metadata


def test_dangerous_metadata_navigation_not_propagated():
    orch = _make_orch(FakeKnowledgeClientDangerousMeta())
    resp = orch.handle(_req("O que é o MARH?"))
    assert "navigation_override" not in resp.metadata


def test_dangerous_metadata_safe_fields_still_propagated():
    """Campos seguros do mesmo resultado devem ser propagados normalmente."""
    orch = _make_orch(FakeKnowledgeClientDangerousMeta())
    resp = orch.handle(_req("O que é o MARH?"))
    assert resp.metadata.get("flow_detail") == "BEDROCK_RAG"
    assert resp.metadata.get("retrieved_chunks") == 1


# ──────────────────────────────────────────────────────────────
# Intenções fora do RAG — não afetadas
# ──────────────────────────────────────────────────────────────


def test_int001_not_affected_by_rag_client():
    """INT-001 não passa por KnowledgeClient — não deve ser afetada."""
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("Consultar colaborador Pessoa Colaboradora A"))
    assert resp.intent_id == "INT-001"
    assert resp.flow == "API_ONLY"
    assert resp.metadata.get("flow_detail") != "BEDROCK_RAG"


def test_transactional_not_affected_by_rag_client():
    """Ação transacional não passa por KnowledgeClient."""
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("Cancele o pedido 342671"))
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


def test_int003_not_affected_by_rag_client():
    orch = _make_orch(FakeBedrockKnowledgeClient())
    resp = orch.handle(_req("Consultar pedido 342671"))
    assert resp.intent_id == "INT-003"
    assert resp.flow == "API_ONLY"
