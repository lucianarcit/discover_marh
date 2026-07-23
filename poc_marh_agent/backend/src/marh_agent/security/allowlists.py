"""Allowlists de campos por domínio.

Controle principal: somente campos na allowlist passam.
Campos desconhecidos são removidos.
"""

from __future__ import annotations

# Campos permitidos para colaboradores na resposta
COLLABORATOR_ALLOWED_FIELDS: set[str] = {
    "name",
    "placeName",
    "subtype",
    "isHomeDelivery",
    "products",
}

# Campos permitidos para pedidos na resposta
ORDER_ALLOWED_FIELDS: set[str] = {
    "orderNumber",
    "status",
    "orderDate",
    "totalOrder",
    "productInfo",
    "paymentMethod",
    "steps",
}

# Campos permitidos dentro de productInfo
ORDER_PRODUCT_INFO_FIELDS: set[str] = {
    "productName",
}


def filter_collaborator(data: dict) -> dict:
    """Remove campos não permitidos de um colaborador."""
    return {k: v for k, v in data.items() if k in COLLABORATOR_ALLOWED_FIELDS}


def filter_order(data: dict) -> dict:
    """Remove campos não permitidos de um pedido."""
    filtered = {}
    for k, v in data.items():
        if k not in ORDER_ALLOWED_FIELDS:
            continue
        if k == "productInfo" and isinstance(v, dict):
            filtered[k] = {
                pk: pv for pk, pv in v.items()
                if pk in ORDER_PRODUCT_INFO_FIELDS
            }
        else:
            filtered[k] = v
    return filtered


def filter_order_list(orders: list[dict]) -> list[dict]:
    """Filtra lista de pedidos."""
    return [filter_order(o) for o in orders]


def filter_collaborator_list(collaborators: list[dict]) -> list[dict]:
    """Filtra lista de colaboradores."""
    return [filter_collaborator(c) for c in collaborators]
