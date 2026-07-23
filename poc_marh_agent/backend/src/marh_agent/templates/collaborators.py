"""Templates determinísticos para respostas de colaboradores."""

from __future__ import annotations


def template_collaborator_found(collaborator: dict) -> str:
    """Template para colaborador encontrado (INT-001, INT-002).

    Nunca repete CPF na resposta.
    """
    name = collaborator.get("name", "")
    place = collaborator.get("placeName", "")
    subtype = collaborator.get("subtype", "")

    lines = ["Encontrei o colaborador solicitado."]
    if name:
        lines.append(f"Nome: {name}")
    if place:
        lines.append(f"Local: {place}")
    if subtype:
        subtype_label = _subtype_label(subtype)
        lines.append(f"Tipo: {subtype_label}")

    products = collaborator.get("products", [])
    if products:
        product_names = [p.get("productName", "") for p in products if p.get("productName")]
        if product_names:
            lines.append(f"Produtos: {', '.join(product_names)}")

    return "\n".join(lines)


def template_multiple_collaborators(collaborators: list[dict]) -> str:
    """Template para múltiplos colaboradores encontrados."""
    count = len(collaborators)
    lines = [
        f"Encontrei {count} colaboradores. "
        "Por favor, indique qual deseja consultar:"
    ]
    for i, c in enumerate(collaborators[:10], 1):
        name = c.get("name", "")
        place = c.get("placeName", "")
        entry = f"{i}. {name}"
        if place:
            entry += f" — {place}"
        lines.append(entry)

    return "\n".join(lines)


def _subtype_label(subtype: str) -> str:
    """Converte subtype para label amigável."""
    labels = {
        "WORKPLACE": "Posto de trabalho",
        "HOME_DELIVERY": "Residência",
        "BRANCH": "Filial",
    }
    return labels.get(subtype, subtype)
