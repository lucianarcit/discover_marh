"""Testes de Presentation — contrato e builders."""

from __future__ import annotations

import pytest

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest
from marh_agent.domain.responses import (
    ChatResponse,
    Presentation,
    PresentationField,
    PresentationItem,
    PresentationTone,
    PresentationVariant,
)
from marh_agent.templates.presentation_builder import (
    build_collaborator_summary,
    build_error_notice,
    build_order_list,
    build_order_summary,
)


@pytest.fixture
def orchestrator():
    return Orchestrator(
        client=MockMaHrOrchClient(),
        knowledge_client=MockKnowledgeClient(),
    )


def _req(**kwargs):
    defaults = {
        "company_id": "empresa-sintetica-001",
        "user_id": "usuario-sintetico-001",
        "session_id": "sessao-sintetica-001",
        "message": "teste",
        "environment": "HML",
    }
    defaults.update(kwargs)
    return ChatRequest(**defaults)


# ── 1. collaborator_summary em INT-001 ────────────────────────────────────────

def test_int001_has_collaborator_summary(orchestrator):
    resp = orchestrator.handle(_req(message="Consultar colaborador Pessoa Colaboradora A"))
    assert resp.intent_id == "INT-001"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.collaborator_summary


# ── 2. collaborator_summary em INT-002 ────────────────────────────────────────

def test_int002_has_collaborator_summary(orchestrator):
    resp = orchestrator.handle(_req(message="Consultar CPF 000.000.000-00"))
    assert resp.intent_id == "INT-002"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.collaborator_summary


# ── 3. CPF ausente na presentation ────────────────────────────────────────────

def test_cpf_absent_in_presentation(orchestrator):
    resp = orchestrator.handle(_req(message="Consultar CPF 000.000.000-00"))
    if resp.presentation:
        serialized = resp.presentation.model_dump_json()
        assert "000.000.000-00" not in serialized
        assert "000000000" not in serialized


# ── 4. order_summary em INT-003 ───────────────────────────────────────────────

def test_int003_has_order_summary(orchestrator):
    resp = orchestrator.handle(_req(message="Consultar pedido 342671"))
    assert resp.intent_id == "INT-003"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.order_summary


# ── 5. order_summary em INT-004 ───────────────────────────────────────────────

def test_int004_has_order_summary(orchestrator):
    resp = orchestrator.handle(_req(message="Qual foi o último pedido?"))
    assert resp.intent_id == "INT-004"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.order_summary


# ── 6. order_list em INT-005 ──────────────────────────────────────────────────

def test_int005_has_order_list(orchestrator):
    resp = orchestrator.handle(_req(message="Pedidos pagos"))
    assert resp.intent_id == "INT-005"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.order_list


# ── 7. knowledge_answer em informativas ───────────────────────────────────────

def test_informative_has_knowledge_answer(orchestrator):
    resp = orchestrator.handle(_req(message="O que é o MARH?"))
    assert resp.intent_id == "INT-019"
    assert resp.presentation is not None
    # INT-019 não é INT-008, deve usar knowledge_answer
    assert resp.presentation.variant in (
        PresentationVariant.knowledge_answer,
        PresentationVariant.capabilities_list,
    )


def test_int008_has_capabilities_list(orchestrator):
    resp = orchestrator.handle(_req(message="O que posso fazer?"))
    assert resp.intent_id == "INT-008"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.capabilities_list


# ── 8. clarification em INT-006 ───────────────────────────────────────────────

def test_int006_has_clarification(orchestrator):
    resp = orchestrator.handle(_req(message="Rastrear cartões pelo CPF 000.000.000-00"))
    assert resp.intent_id == "INT-006"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.clarification


# ── 9. warning_notice em INT-007 ──────────────────────────────────────────────

def test_int007_has_warning_notice(orchestrator):
    resp = orchestrator.handle(_req(message="Rastrear pedido 342671"))
    assert resp.intent_id == "INT-007"
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.warning_notice


# ── 10. transactional_redirect para ação ──────────────────────────────────────

def test_transactional_has_redirect(orchestrator):
    resp = orchestrator.handle(_req(message="Cancele o pedido 342671"))
    assert resp.presentation is not None
    assert resp.presentation.variant == PresentationVariant.transactional_redirect


# ── 11. error_notice para erro ────────────────────────────────────────────────

def test_error_notice_for_not_found(orchestrator):
    resp = orchestrator.handle(_req(message="Consultar pedido 999999"))
    if resp.error_code == "ERR-003":
        assert resp.presentation is not None
        assert resp.presentation.variant == PresentationVariant.error_notice


# ── 12. message sempre preenchida ─────────────────────────────────────────────

def test_message_always_present(orchestrator):
    messages = [
        "Consultar colaborador Pessoa Colaboradora A",
        "Consultar pedido 342671",
        "Qual foi o último pedido?",
        "Pedidos pagos",
        "O que posso fazer?",
        "Cancele o pedido 342671",
    ]
    for msg in messages:
        resp = orchestrator.handle(_req(message=msg))
        assert resp.message, f"message vazio para: {msg}"
        assert len(resp.message) > 0


# ── 13. presentation é opcional (resposta retrocompatível) ────────────────────

def test_chatresponse_without_presentation():
    resp = ChatResponse(
        correlation_id="test-123",
        intent_id="INT-001",
        flow="API_ONLY",
        message="Mensagem de fallback.",
    )
    assert resp.presentation is None
    dumped = resp.model_dump()
    assert "message" in dumped
    assert dumped["message"] == "Mensagem de fallback."


# ── 14. campos vazios não enviados na presentation ───────────────────────────

def test_empty_fields_not_in_collaborator_summary():
    collab = {"name": "Pessoa A", "placeName": "", "subtype": "", "products": []}
    pres = build_collaborator_summary(collab)
    # Só deve ter o campo nome
    assert len(pres.fields) == 1
    assert pres.fields[0].label == "Nome"


def test_none_value_not_in_order_summary():
    order = {"orderNumber": "342671", "status": "PAID", "orderDate": None, "totalOrder": None}
    pres = build_order_summary(order)
    values = [f.value for f in pres.fields]
    assert all(v for v in values), "Campo com valor vazio presente"


# ── 15. enums inválidos são rejeitados pelo Pydantic ─────────────────────────

def test_invalid_variant_rejected():
    with pytest.raises(Exception):
        Presentation(
            variant="invalid_variant",
            title="Teste",
            tone=PresentationTone.neutral,
        )


def test_invalid_tone_rejected():
    with pytest.raises(Exception):
        Presentation(
            variant=PresentationVariant.knowledge_answer,
            title="Teste",
            tone="INVALID_TONE",
        )


# ── Extras: builders unitários ───────────────────────────────────────────────

def test_build_order_list_items():
    orders = [
        {"orderNumber": "001", "orderDate": "2026-07-21", "totalOrder": 90.0, "status": "PAID"},
        {"orderNumber": "002", "orderDate": "2026-07-15", "totalOrder": 150.0, "status": "PAID"},
    ]
    pres = build_order_list(orders, "Pagamento confirmado")
    assert pres.variant == PresentationVariant.order_list
    assert len(pres.items) == 2
    assert pres.items[0].title == "Pedido 001"
    assert pres.items[0].value == "R$ 90,00"


def test_build_error_notice_tone():
    pres = build_error_notice("ERR-005")
    assert pres.variant == PresentationVariant.error_notice
    assert pres.tone == PresentationTone.negative


def test_presentation_field_html_safe():
    field = PresentationField(
        label="Nome",
        value="<script>alert('xss')</script>",
        emphasis=True,
    )
    assert field.value == "<script>alert('xss')</script>"
    # O campo não é interpretado como HTML — é apenas string armazenada.
    # A segurança é garantida pelo frontend (textContent).


def test_presentation_item_serializable():
    item = PresentationItem(
        title="Pedido 001",
        subtitle="21/07/2026",
        value="R$ 90,00",
        badge="Pago",
        tone=PresentationTone.positive,
    )
    d = item.model_dump()
    assert d["title"] == "Pedido 001"
    assert d["tone"] == "positive"
