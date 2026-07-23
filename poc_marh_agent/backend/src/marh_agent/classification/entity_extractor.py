"""Extração determinística de entidades da mensagem do usuário."""

from __future__ import annotations

import re


_CPF_PATTERN = re.compile(r"\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[\-\s]?\d{2}")
_ORDER_NUMBER_PATTERN = re.compile(r"\b(\d{4,10})\b")


def extract_cpf(text: str) -> str | None:
    """Extrai CPF da mensagem. Uso transitório — descartar após uso."""
    match = _CPF_PATTERN.search(text)
    if match:
        return match.group(0)
    return None


def extract_order_number(text: str) -> str | None:
    """Extrai número de pedido da mensagem."""
    match = _ORDER_NUMBER_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def extract_name(text: str, intent_keywords: list[str]) -> str | None:
    """Extrai nome do colaborador removendo keywords de intenção.

    Only removes keywords at the beginning of the text or as standalone words
    before the actual name content.
    """
    cleaned = text.strip()
    # Remove keywords only from the beginning of the phrase
    changed = True
    while changed:
        changed = False
        for kw in intent_keywords:
            pattern = r"^\s*" + re.escape(kw) + r"\s*"
            new_cleaned = re.sub(pattern, "", cleaned, count=1, flags=re.IGNORECASE)
            if new_cleaned != cleaned:
                cleaned = new_cleaned
                changed = True
    cleaned = cleaned.strip(" .,;:!?")
    if cleaned and len(cleaned) >= 2:
        return cleaned
    return None
