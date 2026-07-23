"""FastAPI — adaptador HTTP local para o agente MARH.

FastAPI permanece isolado neste arquivo.
A lógica de negócio não depende de FastAPI.
"""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest

# Logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout,
)

# Dependência: mock client
_client = MockMaHrOrchClient()
_orchestrator = Orchestrator(client=_client)

app = FastAPI(
    title="MARH Agent Backend — POC Mock Local",
    version="0.1.0",
    docs_url="/docs",
)

# CORS — somente origens locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "mode": "MOCK_LOCAL",
        "dependencies": {
            "ma_hr_orch": "MOCK",
            "bedrock": "DISABLED",
            "rag": "DISABLED",
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
                "navigation": None,
                "error_code": "ERR-PARSE",
                "metadata": {"mode": "MOCK_LOCAL"},
            },
        )

    try:
        chat_request = ChatRequest(**body)
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content={
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": "Dados obrigatórios ausentes ou inválidos.",
                "navigation": None,
                "error_code": "ERR-VALIDATION",
                "metadata": {"mode": "MOCK_LOCAL"},
            },
        )

    response = _orchestrator.handle(chat_request)
    return JSONResponse(
        status_code=200,
        content=response.model_dump(),
    )
