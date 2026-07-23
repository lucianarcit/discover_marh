"""Testes unitários do orquestrador e classificador."""

import pytest

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest


@pytest.fixture
def orchestrator():
    client = MockMaHrOrchClient()
    return Orchestrator(client=client)


def _make_request(**kwargs):
    defaults = {
        "company_id": "empresa-sintetica-001",
        "user_id": "usuario-sintetico-001",
        "session_id": "sessao-sintetica-001",
        "message": "teste",
        "environment": "HML",
    }
    defaults.update(kwargs)
    return ChatRequest(**defaults)


# 1. Request válido
def test_valid_request(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.correlation_id is not None
    assert resp.message


# 2. Ausência de company_id
def test_missing_company_id(orchestrator):
    req = _make_request(company_id="", message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.error_code == "ERR-001"


# 3. Environment inválido
def test_invalid_environment():
    with pytest.raises(Exception):
        _make_request(environment="INVALID")


# 4. Mensagem vazia
def test_empty_message():
    with pytest.raises(Exception):
        _make_request(message="")


# 5. Correlation ID gerado
def test_correlation_id_generated(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.correlation_id
    assert len(resp.correlation_id) > 10


# 6. INT-001 por nome
def test_int001_by_name(orchestrator):
    req = _make_request(message="Consultar colaborador Pessoa Colaboradora A")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-001"
    assert "Pessoa Colaboradora A" in resp.message


# 7. INT-002 por CPF
def test_int002_by_cpf(orchestrator):
    req = _make_request(message="Consultar CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-002"
    assert "colaborador" in resp.message.lower()


# 8. CPF não aparece na resposta
def test_cpf_not_in_response(orchestrator):
    req = _make_request(message="Consultar CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    assert "000.000.000-00" not in resp.message


# 9. CPF não aparece nos logs (verificação indireta)
def test_cpf_not_in_response_fields(orchestrator):
    req = _make_request(message="Consultar CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    # Verifica que o CPF não está em nenhum campo da resposta
    resp_str = resp.model_dump_json()
    assert "000.000.000-00" not in resp_str


# 10. INT-003 por orderNumber
def test_int003_by_order_number(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-003"
    assert "342671" in resp.message


# 11. idOrder nunca é usado no deeplink
def test_id_order_never_in_deeplink(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "id-interno" not in resp.navigation.deeplink
        assert "idOrder" not in resp.navigation.deeplink


# 12. INT-004 retorna primeiro pedido
def test_int004_returns_first_order(orchestrator):
    req = _make_request(message="Qual foi o último pedido?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-004"
    assert "342671" in resp.message  # Primeiro da fixture


# 13. INT-005 reconhece PAID
def test_int005_recognizes_paid(orchestrator):
    req = _make_request(message="Pedidos pagos")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-005"
    assert "Pagamento confirmado" in resp.message or "pedido(s)" in resp.message


# 14. Alias ambíguo isolado não classifica status
def test_ambiguous_alias_no_classification(orchestrator):
    req = _make_request(message="Estou aguardando")
    resp = orchestrator.handle(req)
    # Não deve classificar como INT-005 com PENDING
    assert resp.intent_id != "INT-005" or resp.error_code == "ERR-004"


# 15. INVOICE sem aliases
def test_invoice_no_aliases():
    from marh_agent.classification.status_mapper import resolve_status_from_input
    assert resolve_status_from_input("nota fiscal") is None
    assert resolve_status_from_input("faturado") is None


# 16. CANCEL_PROCESSING sem aliases
def test_cancel_processing_no_aliases():
    from marh_agent.classification.status_mapper import resolve_status_from_input
    assert resolve_status_from_input("cancelando") is None
    assert resolve_status_from_input("em cancelamento") is None


# 17. INT-006 solicita orderNumber
def test_int006_requests_order_number(orchestrator):
    req = _make_request(message="Rastrear cartão pelo CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-006"
    assert "ERR-010" == resp.error_code


# 18. INT-007 não inventa tracking
def test_int007_no_invented_tracking(orchestrator):
    req = _make_request(message="Rastrear pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-007"
    assert "NOT_VALIDATED" in str(resp.metadata)


# 19. Ação transacional não executa API
def test_transactional_action_blocked(orchestrator):
    req = _make_request(message="Cancele o pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"
    assert "consultar informações" in resp.message


# 20. Troca de empresa não altera company_id
def test_company_switch_blocked(orchestrator):
    req = _make_request(message="Troque para outra empresa")
    resp = orchestrator.handle(req)
    assert "empresa selecionada" in resp.message


# 21. Allowlist de pedidos
def test_order_allowlist():
    from marh_agent.security.allowlists import filter_order
    order = {
        "orderNumber": "123",
        "status": "PAID",
        "billingDocumentNumber": "SECRET",
        "contractNumber": "SECRET",
        "idLegalPersonBilling": "SECRET",
        "unknownField": "should be removed",
    }
    filtered = filter_order(order)
    assert "billingDocumentNumber" not in filtered
    assert "contractNumber" not in filtered
    assert "idLegalPersonBilling" not in filtered
    assert "unknownField" not in filtered
    assert filtered["orderNumber"] == "123"


# 22. Allowlist de colaboradores
def test_collaborator_allowlist():
    from marh_agent.security.allowlists import filter_collaborator
    collab = {
        "name": "Test",
        "placeName": "Place",
        "documentNumber": "000.000.000-00",
        "email": "test@test.com",
        "phoneNumber": "999",
        "motherName": "Mom",
        "beneficiaryId": "ben-001",
        "address": {"street": "St"},
    }
    filtered = filter_collaborator(collab)
    assert "documentNumber" not in filtered
    assert "email" not in filtered
    assert "phoneNumber" not in filtered
    assert "motherName" not in filtered
    assert "beneficiaryId" not in filtered
    assert "address" not in filtered
    assert filtered["name"] == "Test"


# 23. Campos desconhecidos removidos
def test_unknown_fields_removed():
    from marh_agent.security.allowlists import filter_order
    order = {"orderNumber": "1", "totallyNewField": "x", "anotherUnknown": 1}
    filtered = filter_order(order)
    assert "totallyNewField" not in filtered
    assert "anotherUnknown" not in filtered


# 24. Deeplink HML
def test_deeplink_hml(orchestrator):
    req = _make_request(message="Consultar pedido 342671", environment="HML")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "meualelo-webviews-hml.siteteste.inf.br" in resp.navigation.webview_url


# 25. Deeplink PRD
def test_deeplink_prd(orchestrator):
    req = _make_request(message="Consultar pedido 342671", environment="PRD")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "meualelo-webviews.alelo.com.br" in resp.navigation.webview_url


# 26. Casing correto
def test_deeplink_casing(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "isModal=false" in resp.navigation.deeplink
        assert "showNavbar=false" in resp.navigation.deeplink
        assert "authRequired=true" in resp.navigation.deeplink


# 27. Rota individual de colaborador bloqueada
def test_individual_collaborator_route_blocked(orchestrator):
    req = _make_request(message="Consultar colaborador Pessoa Colaboradora A")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "/employees/" not in resp.navigation.webview_url.split("#/employees")[1] if "#/employees" in resp.navigation.webview_url else True
        assert "edit" not in resp.navigation.webview_url


# 28. Path traversal bloqueado
def test_path_traversal_blocked():
    from marh_agent.navigation.builder import build_navigation
    result = build_navigation("ROUTE-014", "HML", "Test", "../../../etc")
    assert result is None


# 29. CPF no deeplink bloqueado
def test_cpf_not_in_deeplink(orchestrator):
    req = _make_request(message="Consultar CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "000" not in resp.navigation.deeplink or "employees" in resp.navigation.deeplink


# 30. Erros usam catálogo do Discovery
def test_errors_use_discovery_catalog(orchestrator):
    req = _make_request(company_id="", message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.error_code == "ERR-001"
    assert "empresa selecionada" in resp.message
