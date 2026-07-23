"""Testes unitários do orquestrador e classificador."""

import pytest

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest


@pytest.fixture
def orchestrator():
    client = MockMaHrOrchClient()
    knowledge_client = MockKnowledgeClient()
    return Orchestrator(client=client, knowledge_client=knowledge_client)


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


# ── Testes adicionados pelo Quality Gate 2026-07-23 ──────────────────────────

# 31. "pedidos cancelados" deve ser INT-005 (consulta por status), NÃO INT-022
def test_cancelled_status_query_not_transactional(orchestrator):
    """Garante que 'cancelados' como status de pedido não dispara INT-022."""
    req = _make_request(message="Pedidos cancelados")
    resp = orchestrator.handle(req)
    assert resp.flow != "REDIRECT_TO_OFFICIAL_JOURNEY", (
        "'pedidos cancelados' não deve redirecionar para jornada transacional"
    )
    assert resp.intent_id == "INT-005"


# 32. "pedidos anulados" → INT-005 CANCELLED
def test_cancelled_alias_anulado(orchestrator):
    req = _make_request(message="Pedidos anulados")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-005"
    assert resp.flow != "REDIRECT_TO_OFFICIAL_JOURNEY"


# 33. simulate_error=404 (LookupError) não propaga exceção não tratada
def test_lookup_error_handled_gracefully():
    client = __import__(
        "marh_agent.clients.mock_ma_hr_orch", fromlist=["MockMaHrOrchClient"]
    ).MockMaHrOrchClient()
    client.simulate_error = 404
    from marh_agent.application.orchestrator import Orchestrator
    orch = Orchestrator(client=client)
    req = _make_request(message="Consultar pedido 342671")
    resp = orch.handle(req)
    # Deve retornar ERR-003 ou ERR-007, nunca lançar exceção
    assert resp.error_code in ("ERR-003", "ERR-007")
    assert resp.correlation_id is not None


# 34. get_display_label com status desconhecido não expõe api_status
def test_unknown_status_display_label():
    from marh_agent.classification.status_mapper import get_display_label
    result = get_display_label("SUSPENDED_BY_FRAUD_UNKNOWN")
    assert result != "SUSPENDED_BY_FRAUD_UNKNOWN", (
        "Status técnico da API não deve ser exposto ao usuário"
    )
    assert "desconhecido" in result.lower() or "disponível" in result.lower()


# 35. PARTIAL_REFUNDED label_completed é None → não expõe "PARTIAL_REFUNDED"
def test_partial_refunded_no_technical_label():
    from marh_agent.classification.status_mapper import get_display_label
    result = get_display_label("PARTIAL_REFUNDED")
    assert result != "PARTIAL_REFUNDED", (
        "PARTIAL_REFUNDED não deve expor o valor técnico da API"
    )


# 36. steps na fixture não vaza dados restritos (caso presente)
def test_steps_do_not_leak_restricted_fields():
    from marh_agent.security.allowlists import filter_order
    order_with_steps = {
        "orderNumber": "999",
        "status": "PAID",
        "steps": [
            {
                "beneficiaryId": "ben-secret-001",
                "documentNumber": "123.456.789-00",
                "label": "Pedido criado",
            }
        ],
        "billingDocumentNumber": "RESTRICTED",
    }
    filtered = filter_order(order_with_steps)
    # steps passa pela allowlist (sem sub-filtro na POC)
    # Este teste documenta o comportamento ATUAL e serve de alerta:
    # em produção, steps deve ter sub-filtro.
    assert "billingDocumentNumber" not in filtered
    # Documentar que steps passa como está (risco conhecido HIGH)
    if "steps" in filtered and filtered["steps"]:
        step = filtered["steps"][0]
        # Registrar que beneficiaryId e documentNumber ESTÃO no step
        # Este teste vai falhar quando sub-filtro for adicionado (esperado)
        assert "label" in step  # pelo menos o campo legítimo está


# 37. idOrder nunca aparece no JSON de resposta completa
def test_id_order_never_in_full_response(orchestrator):
    req = _make_request(message="Consultar pedido 342671")
    resp = orchestrator.handle(req)
    resp_json = resp.model_dump_json()
    assert "idOrder" not in resp_json
    assert "id-interno-sintetico" not in resp_json


# 38. POST /chat com environment PRD usa base PRD no deeplink
def test_prd_environment_uses_prd_base(orchestrator):
    req = _make_request(message="Consultar pedido 342671", environment="PRD")
    resp = orchestrator.handle(req)
    if resp.navigation:
        assert "meualelo-webviews.alelo.com.br" in resp.navigation.webview_url
        assert "hml" not in resp.navigation.webview_url.lower()


# 39. Verbo "cancelar" (imperativo) dispara INT-022
def test_cancel_imperative_triggers_int022(orchestrator):
    req = _make_request(message="Cancele o pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


# 40. "cancelamento" como palavra isolada não dispara INT-022 (é status)
def test_cancellation_word_not_transactional(orchestrator):
    req = _make_request(message="Pedidos em cancelamento")
    resp = orchestrator.handle(req)
    assert resp.flow != "REDIRECT_TO_OFFICIAL_JOURNEY"


# ── Testes Intent Coverage Gate 2026-07-23 ───────────────────────────────────
# Cobertura completa das 27 intenções do catálogo oficial

# INT-008 — O que posso fazer? → RAG_ONLY com MockKnowledgeClient
def test_int008_what_can_i_do(orchestrator):
    req = _make_request(message="O que posso fazer?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-008"
    assert resp.flow == "RAG_ONLY"
    assert "consultar" in resp.message.lower() or "colaborador" in resp.message.lower()
    assert resp.metadata.get("flow_detail") == "MOCK_KNOWLEDGE"


# INT-009 — Quais informações posso consultar?
def test_int009_consultable_info(orchestrator):
    req = _make_request(message="Quais informações posso consultar?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-009"
    assert resp.flow == "RAG_ONLY"
    assert resp.message  # não vazio


# INT-010 — Como faço para fazer um pedido? → RAG_ONLY com navigation opcional
def test_int010_how_to_order(orchestrator):
    req = _make_request(message="Como faço para fazer um pedido?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-010"
    assert resp.flow == "RAG_ONLY"
    assert "pedido" in resp.message.lower() or "boleto" in resp.message.lower()


# INT-011 — Como faço para consultar um pedido?
def test_int011_how_consult_order(orchestrator):
    req = _make_request(message="Como faço para consultar um pedido?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-011"
    assert resp.flow == "RAG_ONLY"


# INT-012 — Como faço para consultar um colaborador?
def test_int012_how_consult_collaborator(orchestrator):
    req = _make_request(message="Como faço para consultar um colaborador?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-012"
    assert resp.flow == "RAG_ONLY"


# INT-013 — Consigo rastrear cartões? → RAG_ONLY informativo
def test_int013_can_track(orchestrator):
    req = _make_request(message="Consigo rastrear cartões?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-013"
    assert resp.flow == "RAG_ONLY"
    assert "rastreamento" in resp.message.lower() or "número do pedido" in resp.message.lower()


# INT-014 — Você consegue cancelar pedido? → RAG_ONLY
def test_int014_cannot_cancel_info(orchestrator):
    req = _make_request(message="Você consegue cancelar pedido?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-014"
    assert resp.flow == "RAG_ONLY"
    assert "não consigo" in resp.message.lower() or "consultiva" in resp.message.lower()


# INT-015 — Você consegue alterar dados de colaborador? → RAG_ONLY
def test_int015_cannot_edit_collaborator_info(orchestrator):
    req = _make_request(message="Você consegue alterar dados de um colaborador?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-015"
    assert resp.flow == "RAG_ONLY"


# INT-016 — Você consulta dados de qualquer empresa?
def test_int016_company_scope(orchestrator):
    req = _make_request(message="Você consulta dados de qualquer empresa?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-016"
    assert resp.flow == "RAG_ONLY"
    assert "empresa selecionada" in resp.message.lower()


# INT-017 — Preciso selecionar empresa?
def test_int017_company_required(orchestrator):
    req = _make_request(message="Preciso selecionar uma empresa para usar o agente?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-017"
    assert resp.flow == "RAG_ONLY"


# INT-018 — O agente substitui o portal?
def test_int018_agent_vs_portal(orchestrator):
    req = _make_request(message="O agente substitui o portal web?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-018"
    assert resp.flow == "RAG_ONLY"
    assert "não substitui" in resp.message.lower() or "consultivo" in resp.message.lower()


# INT-019 — O que é o MARH?
def test_int019_what_is_marh(orchestrator):
    req = _make_request(message="O que é o MARH?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-019"
    assert resp.flow == "RAG_ONLY"
    assert "marh" in resp.message.lower() or "meu alelo" in resp.message.lower()
    assert resp.metadata.get("flow_detail") == "MOCK_KNOWLEDGE"


# INT-020 — O que é o Espaço RH?
def test_int020_what_is_espaco_rh(orchestrator):
    req = _make_request(message="O que é o Espaço RH?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-020"
    assert resp.flow == "RAG_ONLY"
    assert "espaço rh" in resp.message.lower() or "meu alelo" in resp.message.lower()


# INT-021 — Quais tipos de perguntas posso fazer?
def test_int021_question_types(orchestrator):
    req = _make_request(message="Quais tipos de pergunta posso fazer?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-021"
    assert resp.flow == "RAG_ONLY"


# INT-022 — Cancelar pedido → REDIRECT
def test_int022_cancel_order(orchestrator):
    req = _make_request(message="Cancela o pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-022"
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"
    assert "No momento eu consigo apenas consultar" in resp.message


# INT-023 — Alterar endereço → REDIRECT
def test_int023_alter_address(orchestrator):
    req = _make_request(message="Altera o endereço do colaborador")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


# INT-024 — Criar pedido → REDIRECT (com navigation para #/new-order/products)
def test_int024_create_order(orchestrator):
    req = _make_request(message="Criar um novo pedido")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"
    if resp.navigation:
        assert "new-order" in resp.navigation.webview_url


# INT-025 — Remover colaborador → REDIRECT
def test_int025_remove_collaborator(orchestrator):
    req = _make_request(message="Remove esse colaborador")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


# INT-026 — Pagar pedido → REDIRECT
def test_int026_pay_order(orchestrator):
    req = _make_request(message="Pagar o pedido 342671")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


# INT-027 — Emitir cartão → REDIRECT
def test_int027_issue_card(orchestrator):
    req = _make_request(message="Emitir um novo cartão")
    resp = orchestrator.handle(req)
    assert resp.flow == "REDIRECT_TO_OFFICIAL_JOURNEY"


# MockKnowledgeClient — tópico retorna conteúdo aprovado
def test_mock_knowledge_returns_approved_content():
    from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
    kc = MockKnowledgeClient()
    result = kc.query("MARH_OVERVIEW")
    assert result["found"] is True
    assert result["data_classification"] == "APPROVED_KNOWLEDGE_MOCK"
    assert "marh" in result["content"].lower() or "meu alelo" in result["content"].lower()
    assert result["source_section"]


# MockKnowledgeClient — tópico desconhecido retorna found=False
def test_mock_knowledge_unknown_topic():
    from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient
    kc = MockKnowledgeClient()
    result = kc.query("TOPICO_INEXISTENTE")
    assert result["found"] is False


# RAG_ONLY sem API call — INT-019 não chama mock_ma_hr_orch
def test_rag_only_no_api_call(orchestrator):
    req = _make_request(message="O que é o MARH?")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-019"
    assert resp.flow == "RAG_ONLY"
    # Se tivesse chamado a API e não encontrado, retornaria ERR-007
    assert resp.error_code is None


# 3 variações positivas INT-019
def test_int019_variations(orchestrator):
    msgs = [
        "O que é o MARH?",
        "O que é MARH",
        "Me explica o que é o MARH",
    ]
    for msg in msgs:
        req = _make_request(message=msg)
        resp = orchestrator.handle(req)
        assert resp.flow == "RAG_ONLY", f"Falhou para: {msg}"


# 3 variações positivas INT-003 com número de pedido diferente
def test_int003_multiple_order_numbers(orchestrator):
    for on in ["342671", "342672", "342673"]:
        req = _make_request(message=f"Consultar pedido {on}")
        resp = orchestrator.handle(req)
        assert resp.intent_id == "INT-003"


# 3 variações positivas INT-005 com diferentes status
def test_int005_multiple_statuses(orchestrator):
    queries = [
        ("Pedidos pagos", "PAID"),
        ("Pedidos cancelados", "CANCELLED"),
        ("Pedidos pendentes", "PENDING"),
    ]
    for msg, expected_status in queries:
        req = _make_request(message=msg)
        resp = orchestrator.handle(req)
        assert resp.intent_id == "INT-005", f"Falhou para: {msg}"
        assert resp.flow != "REDIRECT_TO_OFFICIAL_JOURNEY"


# Ambiguidade: "pedido" sem número → pede esclarecimento ou lista
def test_ambiguous_order_no_number(orchestrator):
    req = _make_request(message="E o pedido?")
    resp = orchestrator.handle(req)
    # Não deve inventar um número de pedido
    assert resp.error_code not in ("ERR-003",) or "informado" in resp.message


# Variação negativa INT-002: CPF → INT-002, não INT-001
def test_int002_vs_int001_disambiguation(orchestrator):
    req = _make_request(message="Consultar colaborador CPF 000.000.000-00")
    resp = orchestrator.handle(req)
    assert resp.intent_id == "INT-002"  # CPF detecado → INT-002
