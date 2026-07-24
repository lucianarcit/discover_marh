"""Lambda handler — adaptador AWS Lambda para o agente MARH.

Responsabilidades:
  - Parsear o evento do API Gateway (proxy integration)
  - Instanciar clientes (mock ou real) com cold-start cache
  - Delegar ao Orchestrator
  - Retornar resposta no formato API Gateway proxy

Seleção de modo (eixos independentes):
  DATA_SOURCE_MODE=MOCK       → MockMaHrOrchClient
  DATA_SOURCE_MODE=INTEGRATED → HttpMaHrOrchClient (Fase 2)

  KNOWLEDGE_MODE=MOCK         → MockKnowledgeClient
  KNOWLEDGE_MODE=BEDROCK_RAG  → BedrockRagKnowledgeClient (Fase 3)

Combinação da Fase 3 isolada:
  DATA_SOURCE_MODE=MOCK + KNOWLEDGE_MODE=BEDROCK_RAG
"""

from __future__ import annotations

import json
import logging
import sys

from pydantic import ValidationError

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.application.knowledge_client_factory import build_knowledge_client
from marh_agent.config import MODE, ENVIRONMENT, Mode, LOG_LEVEL, DATA_SOURCE_MODE, DataSourceMode
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
    """Constrói o Orchestrator com os clientes apropriados aos modos ativos.

    DATA_SOURCE_MODE controla MaHrOrchClient (independente de KNOWLEDGE_MODE).
    KNOWLEDGE_MODE controla KnowledgeClient (independente de DATA_SOURCE_MODE).
    """
    # --- MaHrOrchClient (eixo DATA_SOURCE_MODE) ---
    if DATA_SOURCE_MODE == DataSourceMode.INTEGRATED:
        raise NotImplementedError(
            "DATA_SOURCE_MODE=INTEGRATED not yet available. "
            "Set DATA_SOURCE_MODE=MOCK or AGENT_MODE=MOCK_LOCAL."
        )
    else:
        from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
        ma_hr_client = MockMaHrOrchClient()

    # --- KnowledgeClient (eixo KNOWLEDGE_MODE) ---
    knowledge_client = build_knowledge_client()

    logger.info(
        "orchestrator_initialized",
        extra={
            "data_source_mode": DATA_SOURCE_MODE.value,
            "knowledge_mode": str(KNOWLEDGE_MODE),
            "environment": ENVIRONMENT.value,
        },
    )

    return Orchestrator(client=ma_hr_client, knowledge_client=knowledge_client)


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
    # Detectar método HTTP (API Gateway v1 e v2)
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get(
        "http", {}
    ).get("method", "")

    # Detectar path (API Gateway v1 e v2)
    raw_path = event.get("rawPath") or event.get("path") or ""

    # OPTIONS preflight
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": _CORS_HEADERS,
            "body": "",
        }

    # GET /health
    if http_method == "GET" and raw_path.rstrip("/").endswith("/health"):
        return {
            "statusCode": 200,
            "headers": _CORS_HEADERS,
            "body": json.dumps({
                "status": "ok",
                "mode": MODE.value,
                "environment": ENVIRONMENT.value,
                "dependencies": {
                    "ma_hr_orch": "MOCK" if MODE == Mode.MOCK_LOCAL else "INTEGRATED",
                    "bedrock_classifier": "DISABLED" if MODE == Mode.MOCK_LOCAL else "ENABLED",
                    "bedrock_rag": "DISABLED" if MODE == Mode.MOCK_LOCAL else "ENABLED",
                },
            }),
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



