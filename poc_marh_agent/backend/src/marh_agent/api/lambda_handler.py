"""Lambda handler — adaptador AWS Lambda para o agente MARH.

Não importa FastAPI.
Não realiza chamadas AWS.
Criado para comprovar que o núcleo pode ser reutilizado no futuro.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from marh_agent.application.orchestrator import Orchestrator
from marh_agent.clients.mock_ma_hr_orch import MockMaHrOrchClient
from marh_agent.domain.requests import ChatRequest


_client = MockMaHrOrchClient()
_orchestrator = Orchestrator(client=_client)


def lambda_handler(event: dict, context: object) -> dict:
    """Ponto de entrada Lambda.

    event: body JSON com o contrato de ChatRequest
    context: contexto Lambda (não utilizado na POC)
    """
    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event
    except (json.JSONDecodeError, TypeError):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": "Requisição inválida.",
                "navigation": None,
                "error_code": "ERR-PARSE",
                "metadata": {"mode": "MOCK_LOCAL"},
            }),
        }

    try:
        chat_request = ChatRequest(**body)
    except ValidationError:
        return {
            "statusCode": 422,
            "body": json.dumps({
                "correlation_id": None,
                "intent_id": None,
                "flow": "ERROR",
                "message": "Dados obrigatórios ausentes ou inválidos.",
                "navigation": None,
                "error_code": "ERR-VALIDATION",
                "metadata": {"mode": "MOCK_LOCAL"},
            }),
        }

    response = _orchestrator.handle(chat_request)
    return {
        "statusCode": 200,
        "body": json.dumps(response.model_dump()),
        "headers": {"Content-Type": "application/json"},
    }
