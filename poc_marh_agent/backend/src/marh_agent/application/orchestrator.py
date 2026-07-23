"""Orquestrador principal do agente MARH.

Fluxo:
  Request -> validação -> contexto confiável -> classificador
  -> router -> (allowlist | knowledge_client) -> template -> NavigationBuilder -> Response

Independente de FastAPI — pode ser reutilizado no Lambda.
"""

from __future__ import annotations

import logging
import time

from marh_agent.classification.intent_classifier import classify
from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.clients.ma_hr_orch import MaHrOrchClient
from marh_agent.config import MODE
from marh_agent.domain.errors import ERROR_CATALOG
from marh_agent.domain.requests import ChatRequest
from marh_agent.domain.responses import ChatResponse
from marh_agent.security.trusted_context import validate_trusted_context
from marh_agent.application.router import route

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orquestrador do agente — núcleo independente de HTTP."""

    def __init__(
        self,
        client: MaHrOrchClient,
        knowledge_client: KnowledgeClient | None = None,
    ) -> None:
        self._client = client
        self._knowledge_client = knowledge_client

    def handle(self, request: ChatRequest) -> ChatResponse:
        """Processa uma requisição de chat e retorna a resposta."""
        start = time.perf_counter()
        correlation_id = request.ensure_correlation_id()

        metadata_base = {
            "mode": MODE.value,
            "data_classification": "SYNTHETIC_TEST_DATA" if MODE == "MOCK_LOCAL" else "LIVE_DATA",
        }

        # 1. Validação de contexto confiável
        error_code = validate_trusted_context(request)
        if error_code:
            self._log(correlation_id, None, "ERROR", error_code, start)
            return ChatResponse(
                correlation_id=correlation_id,
                intent_id=None,
                flow="ERROR",
                message=ERROR_CATALOG[error_code],
                error_code=error_code,
                metadata=metadata_base,
            )

        # 2. Classificação determinística
        classification = classify(request.message)

        # 3. Roteamento
        response = route(
            classification=classification,
            company_id=request.company_id,
            environment=request.environment,
            correlation_id=correlation_id,
            client=self._client,
            knowledge_client=self._knowledge_client,
        )

        # 4. Log estruturado (sem dados sensíveis)
        self._log(
            correlation_id,
            classification.intent_id,
            response.flow,
            response.error_code,
            start,
        )

        return response

    def _log(
        self,
        correlation_id: str,
        intent_id: str | None,
        flow: str,
        error_code: str | None,
        start: float,
    ) -> None:
        """Log estruturado — nunca loga message, CPF, nome ou dados."""
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_processed",
            extra={
                "correlation_id": correlation_id,
                "intent_id": intent_id,
                "flow": flow,
                "error_code": error_code,
                "duration_ms": duration_ms,
                "mode": MODE.value,
            },
        )
