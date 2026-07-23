"""Router — direciona a classificação para o handler correto."""

from __future__ import annotations

from marh_agent.classification.intent_classifier import ClassificationResult
from marh_agent.classification.status_mapper import get_display_label
from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.clients.ma_hr_orch import MaHrOrchClient
from marh_agent.domain.errors import ERROR_CATALOG
from marh_agent.domain.responses import ChatResponse, NavigationResponse
from marh_agent.navigation.builder import build_navigation
from marh_agent.security.allowlists import (
    filter_collaborator,
    filter_collaborator_list,
    filter_order,
    filter_order_list,
)
from marh_agent.templates.collaborators import (
    template_collaborator_found,
    template_multiple_collaborators,
)
from marh_agent.templates.orders import (
    template_last_order,
    template_order_detail,
    template_orders_by_status,
)
from marh_agent.templates.policies import (
    COMPANY_SWITCH_BLOCKED,
    INFORMATIVE_RESPONSES,
    REDIRECT_TO_OFFICIAL_JOURNEY,
    TRACKING_NOT_VALIDATED,
)

# Mapeamento de intent_id para tópico do KnowledgeClient
_INTENT_KNOWLEDGE_TOPIC: dict[str, str] = {
    "INT-008": "AGENT_CAPABILITIES",
    "INT-009": "CONSULTABLE_INFO",
    "INT-010": "ORDER_PROCESS",
    "INT-011": "HOW_CONSULT_ORDER",
    "INT-012": "HOW_CONSULT_COLLABORATOR",
    "INT-013": "CARD_TRACKING_INFO",
    "INT-014": "CANNOT_CANCEL",
    "INT-015": "CANNOT_EDIT_COLLABORATOR",
    "INT-016": "COMPANY_SCOPE",
    "INT-017": "COMPANY_REQUIRED",
    "INT-018": "AGENT_VS_PORTAL",
    "INT-019": "MARH_OVERVIEW",
    "INT-020": "ESPACO_RH_OVERVIEW",
    "INT-021": "QUESTION_TYPES",
}


def route(
    classification: ClassificationResult,
    company_id: str,
    environment: str,
    correlation_id: str,
    client: MaHrOrchClient,
    knowledge_client: KnowledgeClient | None = None,
) -> ChatResponse:
    """Roteia a classificação para o handler correto."""
    intent_id = classification.intent_id
    flow = classification.flow
    entities = classification.entities

    metadata = {
        "mode": "MOCK_LOCAL",
        "data_classification": "SYNTHETIC_TEST_DATA",
    }

    try:
        # Troca de empresa
        if intent_id == "COMPANY_SWITCH":
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id=None,
                flow="STATIC_RESPONSE",
                message=COMPANY_SWITCH_BLOCKED,
                error_code=None,
                metadata=metadata,
            )

        # Ações transacionais (Grupo C)
        if flow == "REDIRECT_TO_OFFICIAL_JOURNEY":
            nav = None
            if intent_id == "INT-024":
                nav = build_navigation(
                    "ROUTE-017", environment, "Criar novo pedido"
                )
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id=intent_id,
                flow=flow,
                message=REDIRECT_TO_OFFICIAL_JOURNEY,
                navigation=nav,
                error_code=None,
                metadata=metadata,
            )

        # Informativas (Grupo B) — MOCK_KNOWLEDGE quando disponível
        if flow == "RAG_ONLY":
            topic = _INTENT_KNOWLEDGE_TOPIC.get(intent_id)
            knowledge_result = None
            if topic and knowledge_client:
                knowledge_result = knowledge_client.query(topic)

            if knowledge_result and knowledge_result.get("found"):
                msg = knowledge_result["content"]
                metadata = {
                    **metadata,
                    "knowledge_source": knowledge_result["source_section"],
                    "knowledge_topic": topic,
                    "flow_detail": "MOCK_KNOWLEDGE",
                }
            else:
                # Fallback: resposta estática de policies.py
                msg = INFORMATIVE_RESPONSES.get(intent_id, ERROR_CATALOG["ERR-008"])
                metadata = {**metadata, "flow_detail": "STATIC_POLICY_FALLBACK"}

            return ChatResponse(
                correlation_id=correlation_id,
                intent_id=intent_id,
                flow=flow,
                message=msg,
                error_code=None,
                metadata=metadata,
            )

        # INT-006 — Rastreamento por CPF (solicita orderNumber)
        if intent_id == "INT-006":
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id="INT-006",
                flow="REQUIRES_CLARIFICATION",
                message=ERROR_CATALOG["ERR-010"],
                error_code="ERR-010",
                metadata=metadata,
            )

        # INT-007 — Rastreamento por pedido (não validado)
        if intent_id == "INT-007":
            order_number = entities.get("order_number")
            nav = None
            if order_number:
                nav = build_navigation(
                    "ROUTE-025", environment,
                    "Ver rastreamento", order_number
                )
            metadata["backend_tracking_api_status"] = "NOT_VALIDATED"
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id="INT-007",
                flow="API_ONLY",
                message=TRACKING_NOT_VALIDATED,
                navigation=nav,
                error_code=None,
                metadata=metadata,
            )

        # INT-001 — Colaborador por nome
        if intent_id == "INT-001":
            name = entities.get("name", "")
            result = client.search_collaborator_by_name(company_id, name)
            return _handle_collaborator_result(
                result, correlation_id, "INT-001", environment, metadata
            )

        # INT-002 — Colaborador por CPF
        if intent_id == "INT-002":
            cpf = entities.get("cpf", "")
            result = client.search_collaborator_by_document(company_id, cpf)
            return _handle_collaborator_result(
                result, correlation_id, "INT-002", environment, metadata
            )

        # INT-003 — Pedido por número
        if intent_id == "INT-003":
            order_number = entities.get("order_number", "")
            result = client.get_order(company_id, order_number)
            if not result.get("found"):
                return ChatResponse(
                    correlation_id=correlation_id,
                    intent_id="INT-003",
                    flow="API_ONLY",
                    message=ERROR_CATALOG["ERR-003"],
                    error_code="ERR-003",
                    metadata=metadata,
                )
            order = filter_order(result["order"])
            msg = template_order_detail(order)
            nav = build_navigation(
                "ROUTE-014", environment,
                "Ver detalhes do pedido", order_number
            )
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id="INT-003",
                flow="API_ONLY",
                message=msg,
                navigation=nav,
                error_code=None,
                metadata=metadata,
            )

        # INT-004 — Último pedido
        if intent_id == "INT-004":
            result = client.list_orders(company_id)
            content = result.get("content", [])
            if not content:
                return ChatResponse(
                    correlation_id=correlation_id,
                    intent_id="INT-004",
                    flow="API_ONLY",
                    message=ERROR_CATALOG["ERR-007"],
                    error_code="ERR-007",
                    metadata=metadata,
                )
            first_order = filter_order(content[0])
            msg = template_last_order(first_order)
            order_number = first_order.get("orderNumber")
            nav = None
            if order_number:
                nav = build_navigation(
                    "ROUTE-014", environment,
                    "Ver detalhes do pedido", order_number
                )
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id="INT-004",
                flow="API_ONLY",
                message=msg,
                navigation=nav,
                error_code=None,
                metadata=metadata,
            )

        # INT-005 — Pedidos por status
        if intent_id == "INT-005":
            status = entities.get("status")
            if not status:
                return ChatResponse(
                    correlation_id=correlation_id,
                    intent_id="INT-005",
                    flow="API_ONLY",
                    message=ERROR_CATALOG["ERR-004"],
                    error_code="ERR-004",
                    metadata=metadata,
                )
            result = client.list_orders_by_status(company_id, status)
            orders = filter_order_list(result.get("content", []))
            label = get_display_label(status)
            msg = template_orders_by_status(orders, label)
            nav = build_navigation(
                "ROUTE-012", environment, "Ver todos os pedidos"
            )
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id="INT-005",
                flow="API_ONLY",
                message=msg,
                navigation=nav,
                error_code=None,
                metadata=metadata,
            )

        # Fora do escopo
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=None,
            flow="STATIC_RESPONSE",
            message=ERROR_CATALOG["ERR-008"],
            error_code="ERR-008",
            metadata=metadata,
        )

    except PermissionError:
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=intent_id,
            flow="API_ONLY",
            message=ERROR_CATALOG["ERR-005"],
            error_code="ERR-005",
            metadata=metadata,
        )
    except LookupError:
        # 404 do backend — recurso não encontrado
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=intent_id,
            flow="API_ONLY",
            message=ERROR_CATALOG["ERR-003"],
            error_code="ERR-003",
            metadata=metadata,
        )
    except TimeoutError:
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=intent_id,
            flow="API_ONLY",
            message=ERROR_CATALOG["ERR-007"],
            error_code="ERR-007",
            metadata=metadata,
        )
    except (RuntimeError, ConnectionError):
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=intent_id,
            flow="API_ONLY",
            message=ERROR_CATALOG["ERR-007"],
            error_code="ERR-007",
            metadata=metadata,
        )


def _handle_collaborator_result(
    result: dict,
    correlation_id: str,
    intent_id: str,
    environment: str,
    metadata: dict,
) -> ChatResponse:
    """Processa resultado de busca de colaborador."""
    total = result.get("total", 0)
    content = result.get("content", [])

    if total == 0:
        return ChatResponse(
            correlation_id=correlation_id,
            intent_id=intent_id,
            flow="API_ONLY",
            message=ERROR_CATALOG["ERR-002"],
            error_code="ERR-002",
            metadata=metadata,
        )

    filtered = filter_collaborator_list(content)
    nav = build_navigation("ROUTE-003", environment, "Ver colaboradores")

    if total == 1:
        msg = template_collaborator_found(filtered[0])
    else:
        msg = template_multiple_collaborators(filtered)

    return ChatResponse(
        correlation_id=correlation_id,
        intent_id=intent_id,
        flow="API_ONLY",
        message=msg,
        navigation=nav,
        error_code=None,
        metadata=metadata,
    )
