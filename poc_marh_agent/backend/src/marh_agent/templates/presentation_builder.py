"""Construtores de Presentation para cada variant."""

from __future__ import annotations

from marh_agent.domain.responses import (
    Presentation,
    PresentationField,
    PresentationItem,
    PresentationTone,
    PresentationVariant,
)
from marh_agent.templates.orders import format_currency_brl, format_date_ptbr


def build_collaborator_summary(collaborator: dict) -> Presentation:
    """Monta Presentation para colaborador encontrado (INT-001, INT-002)."""
    fields: list[PresentationField] = []

    name = collaborator.get("name", "")
    if name:
        fields.append(PresentationField(label="Nome", value=name, emphasis=True))

    place = collaborator.get("placeName", "")
    if place:
        fields.append(PresentationField(label="Local", value=place))

    subtype = collaborator.get("subtype", "")
    if subtype:
        fields.append(PresentationField(label="Tipo", value=_subtype_label(subtype)))

    products = collaborator.get("products", [])
    product_names = [p.get("productName", "") for p in products if p.get("productName")]
    if product_names:
        fields.append(PresentationField(label="Produtos", value=", ".join(product_names)))

    return Presentation(
        variant=PresentationVariant.collaborator_summary,
        title="Colaborador encontrado",
        icon="person",
        tone=PresentationTone.neutral,
        fields=fields,
    )


def build_order_summary(order: dict, intro_title: str = "Pedido") -> Presentation:
    """Monta Presentation para pedido único (INT-003, INT-004)."""
    from marh_agent.classification.status_mapper import get_display_label

    order_number = order.get("orderNumber", "")
    status = order.get("status", "")
    status_label = get_display_label(status) if status else None
    tone = _tone_for_status(status)

    fields: list[PresentationField] = []

    product = ""
    if order.get("productInfo"):
        product = order["productInfo"].get("productName", "")
    if product:
        fields.append(PresentationField(label="Produto", value=product, emphasis=True))

    date = format_date_ptbr(order.get("orderDate"))
    if date:
        fields.append(PresentationField(label="Data", value=date))

    payment = order.get("paymentMethod", "")
    if payment:
        fields.append(PresentationField(label="Pagamento", value=payment))

    total = format_currency_brl(order.get("totalOrder"))
    if total:
        fields.append(PresentationField(label="Valor", value=total, emphasis=True))

    title = f"{intro_title} {order_number}" if order_number else intro_title

    return Presentation(
        variant=PresentationVariant.order_summary,
        title=title,
        icon="order",
        tone=tone,
        status_label=status_label,
        fields=fields,
    )


def build_order_list(orders: list[dict], status_label: str) -> Presentation:
    """Monta Presentation para lista de pedidos (INT-005)."""
    from marh_agent.classification.status_mapper import get_display_label

    items: list[PresentationItem] = []
    for order in orders[:5]:
        on = order.get("orderNumber", "")
        date = format_date_ptbr(order.get("orderDate"))
        total = format_currency_brl(order.get("totalOrder"))
        status = order.get("status", "")
        badge = get_display_label(status) if status else None
        tone = _tone_for_status(status)

        items.append(PresentationItem(
            title=f"Pedido {on}" if on else "Pedido",
            subtitle=date or None,
            value=total or None,
            badge=badge,
            tone=tone,
        ))

    count = len(orders)
    subtitle = f"{count} pedido{'s' if count != 1 else ''} encontrado{'s' if count != 1 else ''}"

    return Presentation(
        variant=PresentationVariant.order_list,
        title=f"Pedidos com status: {status_label}",
        subtitle=subtitle,
        icon="list",
        tone=PresentationTone.neutral,
        status_label=status_label,
        items=items,
    )


def build_capabilities_list() -> Presentation:
    """Monta Presentation para capacidades do agente (INT-008)."""
    items = [
        PresentationItem(title="Consultar colaboradores por nome ou CPF"),
        PresentationItem(title="Consultar pedidos pelo número"),
        PresentationItem(title="Verificar o último pedido"),
        PresentationItem(title="Listar pedidos por status"),
        PresentationItem(title="Informações sobre rastreamento de cartões"),
        PresentationItem(title="Dúvidas sobre o Espaço RH e o MARH"),
    ]
    return Presentation(
        variant=PresentationVariant.capabilities_list,
        title="Como posso ajudar?",
        subtitle="Sou um assistente consultivo — não realizo ações.",
        icon="sparkles",
        tone=PresentationTone.informative,
        items=items,
    )


def build_knowledge_answer(title: str) -> Presentation:
    """Monta Presentation para resposta informativa (INT-009 a INT-021)."""
    return Presentation(
        variant=PresentationVariant.knowledge_answer,
        title=title,
        icon="info",
        tone=PresentationTone.informative,
    )


def build_warning_notice(title: str) -> Presentation:
    """Monta Presentation para aviso (INT-007)."""
    return Presentation(
        variant=PresentationVariant.warning_notice,
        title=title,
        icon="warning",
        tone=PresentationTone.warning,
    )


def build_clarification(title: str) -> Presentation:
    """Monta Presentation para pedido de esclarecimento (INT-006)."""
    return Presentation(
        variant=PresentationVariant.clarification,
        title=title,
        icon="question",
        tone=PresentationTone.neutral,
    )


def build_transactional_redirect() -> Presentation:
    """Monta Presentation para redirecionamento transacional."""
    return Presentation(
        variant=PresentationVariant.transactional_redirect,
        title="Ação não disponível aqui",
        icon="redirect",
        tone=PresentationTone.informative,
    )


def build_error_notice(error_code: str) -> Presentation:
    """Monta Presentation para erros."""
    tone = _tone_for_error(error_code)
    titles = {
        "ERR-001": "Empresa não identificada",
        "ERR-002": "Colaborador não encontrado",
        "ERR-003": "Pedido não encontrado",
        "ERR-004": "Status não reconhecido",
        "ERR-005": "Sem permissão",
        "ERR-006": "Sessão inválida",
        "ERR-007": "Serviço indisponível",
        "ERR-008": "Informação não disponível",
        "ERR-009": "Navegação indisponível",
        "ERR-010": "Número do pedido necessário",
    }
    return Presentation(
        variant=PresentationVariant.error_notice,
        title=titles.get(error_code, "Não foi possível completar"),
        icon="error",
        tone=tone,
    )


def _tone_for_status(status: str) -> PresentationTone:
    positive = {"PAID", "CREDITED", "RELEASED", "REFUNDED"}
    warning = {"PENDING", "IN_PROCESSING", "INVOICE", "IN_BILLING_PROCESSING", "CANCEL_PROCESSING"}
    negative = {"CANCELLED", "REJECTED"}
    if status in positive:
        return PresentationTone.positive
    if status in warning:
        return PresentationTone.warning
    if status in negative:
        return PresentationTone.negative
    return PresentationTone.neutral


def _tone_for_error(error_code: str) -> PresentationTone:
    warning_codes = {"ERR-002", "ERR-003", "ERR-004", "ERR-008", "ERR-009", "ERR-010"}
    negative_codes = {"ERR-001", "ERR-005", "ERR-006", "ERR-007"}
    if error_code in warning_codes:
        return PresentationTone.warning
    if error_code in negative_codes:
        return PresentationTone.negative
    return PresentationTone.neutral


def _subtype_label(subtype: str) -> str:
    labels = {
        "WORKPLACE": "Posto de trabalho",
        "HOME_DELIVERY": "Residência",
        "BRANCH": "Filial",
    }
    return labels.get(subtype, subtype)


_KNOWLEDGE_TITLES: dict[str, str] = {
    "INT-008": "Como posso ajudar?",
    "INT-009": "Informações consultáveis",
    "INT-010": "Fazer um novo pedido",
    "INT-011": "Como consultar pedidos",
    "INT-012": "Como consultar colaboradores",
    "INT-013": "Rastreamento de cartões",
    "INT-014": "Cancelamento de pedidos",
    "INT-015": "Edição de colaboradores",
    "INT-016": "Escopo da empresa",
    "INT-017": "Empresa necessária",
    "INT-018": "Agente vs. portal web",
    "INT-019": "O que é o MARH",
    "INT-020": "O que é o Espaço RH",
    "INT-021": "Tipos de perguntas",
}


def knowledge_title_for_intent(intent_id: str) -> str:
    return _KNOWLEDGE_TITLES.get(intent_id, "Informação")
