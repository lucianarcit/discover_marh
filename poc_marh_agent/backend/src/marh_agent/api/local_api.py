"""FastAPI — adaptador HTTP local para o agente MARH.

FastAPI permanece isolado neste arquivo.
A lógica de negócio não depende de FastAPI.

Usa a mesma lógica de seleção de clientes que o lambda_handler.
"""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.config import (
    CORS_ALLOWED_ORIGINS,
    ENVIRONMENT,
    LOG_LEVEL,
    MODE,
    Mode,
)
from marh_agent.domain.requests import ChatRequest

# --- Logging ---

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# --- Seleção de clientes (mesma lógica do Lambda) ---


def _build_orchestrator() -> Orchestrator:
    """Constrói o Orchestrator com os clientes apropriados ao modo."""
    if MODE == Mode.INTEGRATED:
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


_orchestrator = _build_orchestrator()


# --- FastAPI App ---

app = FastAPI(
    title="MARH Agent Backend",
    version="0.2.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-Id"],
    allow_credentials=False,
)


# --- Endpoints ---


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "mode": MODE.value,
        "environment": ENVIRONMENT.value,
        "dependencies": {
            "ma_hr_orch": "MOCK" if MODE == Mode.MOCK_LOCAL else "INTEGRATED",
            "bedrock_classifier": "DISABLED" if MODE == Mode.MOCK_LOCAL else "ENABLED",
            "bedrock_rag": "DISABLED" if MODE == Mode.MOCK_LOCAL else "ENABLED",
        },
    }


@app.post("/chat")
async def chat(request: Request):
    """Endpoint principal de chat."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": "Requisição inválida.",
                "presentation": None,
                "navigation": None,
                "error_code": "ERR-PARSE",
                "metadata": {"mode": MODE.value},
            },
        )

    try:
        chat_request = ChatRequest(**body)
    except ValidationError:
        return JSONResponse(
            status_code=422,
            content={
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": "Dados obrigatórios ausentes ou inválidos.",
                "presentation": None,
                "navigation": None,
                "error_code": "ERR-VALIDATION",
                "metadata": {"mode": MODE.value},
            },
        )

    response = _orchestrator.handle(chat_request)
    return JSONResponse(
        status_code=200,
        content=response.model_dump(),
    )
