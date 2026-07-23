"""Templates determinísticos para respostas de pedidos."""

from __future__ import annotations

from datetime import datetime

from marh_agent.classification.status_mapper import get_display_label


def format_date_ptbr(date_str: str | None) -> str:
    """Formata data ISO para pt-BR."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return date_str


def format_currency_brl(value: float | int | None) -> str:
    """Formata valor em BRL."""
    if value is None:
        return ""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def template_order_detail(order: dict) -> str:
    """Template para pedido específico (INT-003)."""
    order_number = order.get("orderNumber", "")
    status = order.get("status", "")
    label = get_display_label(status)
    date = format_date_ptbr(order.get("orderDate"))
    product = ""
    if order.get("productInfo"):
        product = order["productInfo"].get("productName", "")
    total = format_currency_brl(order.get("totalOrder"))

    lines = [f"Encontrei o pedido {order_number}."]
    if label:
        lines.append(f"Status: {label}")
    if date:
        lines.append(f"Data do pedido: {date}")
    if product:
        lines.append(f"Produto: {product}")
    if total:
        lines.append(f"Valor: {total}")

    return "\n".join(lines)


def template_last_order(order: dict) -> str:
    """Template para último pedido (INT-004)."""
    order_number = order.get("orderNumber", "")
    status = order.get("status", "")
    label = get_display_label(status)
    date = format_date_ptbr(order.get("orderDate"))
    product = ""
    if order.get("productInfo"):
        product = order["productInfo"].get("productName", "")
    total = format_currency_brl(order.get("totalOrder"))

    lines = [f"Seu pedido mais recente é o {order_number}."]
    if label:
        lines.append(f"Status: {label}")
    if date:
        lines.append(f"Data do pedido: {date}")
    if product:
        lines.append(f"Produto: {product}")
    if total:
        lines.append(f"Valor: {total}")

    return "\n".join(lines)


def template_orders_by_status(
    orders: list[dict], status_label: str
) -> str:
    """Template para pedidos por status (INT-005)."""
    count = len(orders)
    if count == 0:
        return (
            f"Não encontrei pedidos com o status {status_label} "
            f"para a empresa selecionada."
        )

    lines = [f"Encontrei {count} pedido(s) com o status {status_label}."]
    for order in orders[:5]:  # Limita exibição a 5
        on = order.get("orderNumber", "")
        date = format_date_ptbr(order.get("orderDate"))
        total = format_currency_brl(order.get("totalOrder"))
        parts = [f"• Pedido {on}"]
        if date:
            parts.append(f"— {date}")
        if total:
            parts.append(f"— {total}")
        lines.append(" ".join(parts))

    return "\n".join(lines)
