"""Lambda handler — adaptador AWS Lambda para o agente MARH.

Responsabilidades:
  - Parsear o evento do API Gateway (proxy integration)
  - Instanciar clientes (mock ou real) com cold-start cache
  - Delegar ao Orchestrator
  - Retornar resposta no formato API Gateway proxy

Seleção de modo:
  - AGENT_MODE=MOCK_LOCAL  → MockMaHrOrchClient + MockKnowledgeClient
  - AGENT_MODE=INTEGRATED  → HttpMaHrOrchClient + BedrockKnowledgeClient (futuro)
"""

from __future__ import annotations

import json
import logging
import sys

from pydantic import ValidationError

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.config import MODE, ENVIRONMENT, Mode, LOG_LEVEL
from marh_agent.domain.requests import ChatRequest

# --- Logging ---

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# --- Cold-start: instanciação de clientes (executada UMA vez) ---


def _build_orchestrator() -> Orchestrator:
    """Constrói o Orchestrator com os clientes apropriados ao modo."""
    if MODE == Mode.INTEGRATED:
        # Fase 2+: importar clientes reais
        # from marh_agent.clients.http_ma_hr_orch import HttpMaHrOrchClient
        # from marh_agent.clients.bedrock_knowledge_client import BedrockKnowledgeClient
        # from marh_agent.config import (
        #     MA_HR_ORCH_BASE_URL,
        #     BEDROCK_KNOWLEDGE_BASE_ID,
        #     BEDROCK_REGION,
        # )
        # client = HttpMaHrOrchClient(base_url=MA_HR_ORCH_BASE_URL)
        # knowledge_client = BedrockKnowledgeClient(
        #     knowledge_base_id=BEDROCK_KNOWLEDGE_BASE_ID,
        #     region=BEDROCK_REGION,
        # )
        raise NotImplementedError(
            "INTEGRATED mode not yet available. Set AGENT_MODE=MOCK_LOCAL."
        )
    else:
        from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
        from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient

        client = MockMaHrOrchClient()
        knowledge_client = MockKnowledgeClient()

    logger.info(
        "orchestrator_initialized",
        extra={"mode": MODE.value, "environment": ENVIRONMENT.value},
    )

    return Orchestrator(client=client, knowledge_client=knowledge_client)


# Instanciado no cold-start — reutilizado entre invocações
_orchestrator = _build_orchestrator()


# --- Headers padrão ---

_CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",  # Restrito pelo API Gateway em produção
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Correlation-Id",
}


# --- Handler ---


def lambda_handler(event: dict, context: object) -> dict:
    """Ponto de entrada AWS Lambda (API Gateway proxy integration).

    Args:
        event: Evento do API Gateway com body JSON (ChatRequest).
        context: Contexto Lambda (runtime info, request ID, etc.).

    Returns:
        dict no formato API Gateway proxy response.
    """
    # OPTIONS preflight
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get(
        "http", {}
    ).get("method", "")
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": _CORS_HEADERS,
            "body": "",
        }

    # Parse body
    try:
        raw_body = event.get("body", "")
        if isinstance(raw_body, str) and raw_body:
            body = json.loads(raw_body)
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            # Fallback: evento pode vir direto (invocação direta / test)
            body = event
    except (json.JSONDecodeError, TypeError):
        return _error_response(400, "ERR-PARSE", "Requisição inválida.")

    # Validação Pydantic
    try:
        chat_request = ChatRequest(**body)
    except ValidationError:
        return _error_response(
            422, "ERR-VALIDATION", "Dados obrigatórios ausentes ou inválidos."
        )

    # Processamento
    response = _orchestrator.handle(chat_request)

    return {
        "statusCode": 200,
        "headers": _CORS_HEADERS,
        "body": json.dumps(response.model_dump(), ensure_ascii=False),
    }


# --- Helpers ---


def _error_response(status_code: int, error_code: str, message: str) -> dict:
    """Gera resposta de erro padronizada."""
    return {
        "statusCode": status_code,
        "headers": _CORS_HEADERS,
        "body": json.dumps(
            {
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": message,
                "presentation": None,
                "navigation": None,
                "error_code": error_code,
                "metadata": {"mode": MODE.value},
            },
            ensure_ascii=False,
        ),
    }



