"""Validação de contexto confiável.

company_id nunca é extraído do texto do usuário.
Empresa digitada no chat nunca altera o contexto.
"""

from __future__ import annotations

from marh_agent.domain.requests import ChatRequest


def validate_trusted_context(request: ChatRequest) -> str | None:
    """Valida contexto obrigatório.

    Retorna error_code se inválido, None se OK.
    """
    if not request.company_id or not request.company_id.strip():
        return "ERR-001"
    if not request.user_id or not request.user_id.strip():
        return "ERR-001"
    if not request.session_id or not request.session_id.strip():
        return "ERR-001"
    return None
