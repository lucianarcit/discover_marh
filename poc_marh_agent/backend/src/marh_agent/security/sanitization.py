"""Sanitização de dados sensíveis antes da resposta."""

from __future__ import annotations

import re

_CPF_PATTERN = re.compile(r"\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[\-\s]?\d{2}")
_CNPJ_PATTERN = re.compile(
    r"\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[/\\]?\d{4}[\-\s]?\d{2}"
)


def sanitize_response_text(text: str) -> str:
    """Remove CPF e CNPJ de texto de resposta."""
    text = _CPF_PATTERN.sub("[DADO PROTEGIDO]", text)
    text = _CNPJ_PATTERN.sub("[DADO PROTEGIDO]", text)
    return text


def contains_sensitive_data(text: str) -> bool:
    """Verifica se o texto contém dados sensíveis."""
    return bool(_CPF_PATTERN.search(text) or _CNPJ_PATTERN.search(text))
