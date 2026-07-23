"""Testes de integração da API HTTP."""

import pytest
from httpx import AsyncClient, ASGITransport

from marh_agent.api.local_api import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _payload(**kwargs):
    defaults = {
        "company_id": "empresa-sintetica-001",
        "user_id": "usuario-sintetico-001",
        "session_id": "sessao-sintetica-001",
        "message": "teste",
        "environment": "HML",
    }
    defaults.update(kwargs)
    return defaults


# 1. GET /health
@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mode"] == "MOCK_LOCAL"
    assert data["dependencies"]["ma_hr_orch"] == "MOCK"


# 2. POST /chat pedido específico
@pytest.mark.asyncio
async def test_chat_order_specific(client):
    resp = await client.post("/chat", json=_payload(message="Consultar pedido 342671"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-003"
    assert "342671" in data["message"]
    assert data["navigation"] is not None


# 3. POST /chat último pedido
@pytest.mark.asyncio
async def test_chat_last_order(client):
    resp = await client.post("/chat", json=_payload(message="Qual foi o último pedido?"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-004"
    assert "342671" in data["message"]


# 4. POST /chat pedidos pagos
@pytest.mark.asyncio
async def test_chat_orders_paid(client):
    resp = await client.post("/chat", json=_payload(message="Pedidos pagos"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-005"
    assert "pedido(s)" in data["message"]


# 5. POST /chat colaborador por nome
@pytest.mark.asyncio
async def test_chat_collaborator_by_name(client):
    resp = await client.post(
        "/chat", json=_payload(message="Consultar colaborador Pessoa Colaboradora A")
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-001"
    assert "Pessoa Colaboradora A" in data["message"]


# 6. POST /chat colaborador por CPF
@pytest.mark.asyncio
async def test_chat_collaborator_by_cpf(client):
    resp = await client.post(
        "/chat", json=_payload(message="Consultar CPF 000.000.000-00")
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-002"
    assert "000.000.000-00" not in data["message"]


# 7. POST /chat rastreamento por CPF
@pytest.mark.asyncio
async def test_chat_tracking_by_cpf(client):
    resp = await client.post(
        "/chat", json=_payload(message="Rastrear cartão pelo CPF 000.000.000-00")
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_id"] == "INT-006"
    assert data["error_code"] == "ERR-010"


# 8. POST /chat ação transacional
@pytest.mark.asyncio
async def test_chat_transactional_action(client):
    resp = await client.post(
        "/chat", json=_payload(message="Cancele o pedido 342671")
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["flow"] == "REDIRECT_TO_OFFICIAL_JOURNEY"


# 9. POST /chat troca de empresa
@pytest.mark.asyncio
async def test_chat_company_switch(client):
    resp = await client.post(
        "/chat", json=_payload(message="Troque para outra empresa")
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "empresa selecionada" in data["message"]


# 10. CORS localhost aceito
@pytest.mark.asyncio
async def test_cors_localhost_accepted(client):
    resp = await client.options(
        "/chat",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers


# 11. Origem não autorizada rejeitada
@pytest.mark.asyncio
async def test_cors_unauthorized_origin(client):
    resp = await client.options(
        "/chat",
        headers={
            "Origin": "http://evil-site.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    # FastAPI CORS middleware may return 400 or no allow-origin header
    allow_origin = resp.headers.get("access-control-allow-origin", "")
    assert "evil-site.com" not in allow_origin


# 12. Contrato de resposta compatível com frontend
@pytest.mark.asyncio
async def test_response_contract(client):
    resp = await client.post("/chat", json=_payload(message="Consultar pedido 342671"))
    assert resp.status_code == 200
    data = resp.json()
    # Campos obrigatórios do contrato
    assert "correlation_id" in data
    assert "intent_id" in data
    assert "flow" in data
    assert "message" in data
    assert "navigation" in data
    assert "error_code" in data
    assert "metadata" in data
    assert data["metadata"]["mode"] == "MOCK_LOCAL"
    assert data["metadata"]["data_classification"] == "SYNTHETIC_TEST_DATA"


# ── Testes adicionados pelo Quality Gate 2026-07-23 ──────────────────────────

# 13. idOrder nunca aparece no JSON de resposta
@pytest.mark.asyncio
async def test_id_order_never_in_response(client):
    resp = await client.post("/chat", json=_payload(message="Consultar pedido 342671"))
    assert resp.status_code == 200
    text = resp.text
    assert "idOrder" not in text
    assert "id-interno-sintetico" not in text


# 14. POST /chat body JSON inválido retorna 400
@pytest.mark.asyncio
async def test_invalid_json_body(client):
    resp = await client.post(
        "/chat",
        content=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error_code"] == "ERR-PARSE"


# 15. POST /chat sem campo message retorna 422
@pytest.mark.asyncio
async def test_missing_message_field(client):
    payload = {
        "company_id": "empresa-sintetica-001",
        "user_id": "usuario-sintetico-001",
        "session_id": "sessao-sintetica-001",
        "environment": "HML",
        # message ausente
    }
    resp = await client.post("/chat", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["error_code"] == "ERR-VALIDATION"


# 16. "pedidos cancelados" → INT-005, não redirect transacional
@pytest.mark.asyncio
async def test_cancelled_orders_query_not_transactional(client):
    resp = await client.post("/chat", json=_payload(message="Pedidos cancelados"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["flow"] != "REDIRECT_TO_OFFICIAL_JOURNEY"
    assert data["intent_id"] == "INT-005"


# 17. deeplink não contém beneficiaryId nem idOrder
@pytest.mark.asyncio
async def test_deeplink_no_sensitive_ids(client):
    resp = await client.post("/chat", json=_payload(message="Consultar pedido 342671"))
    assert resp.status_code == 200
    data = resp.json()
    if data.get("navigation") and data["navigation"].get("deeplink"):
        deeplink = data["navigation"]["deeplink"]
        assert "idOrder" not in deeplink
        assert "beneficiaryId" not in deeplink
        assert "ben-sintetico" not in deeplink
        assert "id-interno" not in deeplink
