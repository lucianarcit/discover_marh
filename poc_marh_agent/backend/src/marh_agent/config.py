"""Configuração centralizada do backend MARH Agent.

Todas as configurações são lidas de variáveis de ambiente.
Valores padrão seguros para desenvolvimento local (mock).
"""

from __future__ import annotations

import os
from enum import StrEnum


# --- Enums ---


class Environment(StrEnum):
    HML = "HML"
    PRD = "PRD"


class Mode(StrEnum):
    """Modo de operação do agente."""

    MOCK_LOCAL = "MOCK_LOCAL"          # Mock clients, dev local ou testes
    INTEGRATED = "INTEGRATED"          # Clientes reais (ma-hr-orch + Bedrock)


# --- Variáveis de ambiente ---


ENVIRONMENT: Environment = Environment(
    os.getenv("ENVIRONMENT", "HML")
)

MODE: Mode = Mode(
    os.getenv("AGENT_MODE", "MOCK_LOCAL")
)

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

# --- ma-hr-orch ---

MA_HR_ORCH_BASE_URL: str = os.getenv("MA_HR_ORCH_BASE_URL", "")
MA_HR_ORCH_TIMEOUT_SECONDS: int = int(os.getenv("MA_HR_ORCH_TIMEOUT_SECONDS", "10"))

# --- Amazon Bedrock ---

BEDROCK_REGION: str = os.getenv("BEDROCK_REGION", "us-east-1")
BEDROCK_MODEL_ID: str = os.getenv(
    "BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"
)
BEDROCK_KNOWLEDGE_BASE_ID: str = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")

# --- CORS ---

CORS_ALLOWED_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080",
    ).split(",")
    if origin.strip()
]

# --- Webview URLs (deeplinks) ---

WEBVIEW_BASE_URLS: dict[str, str] = {
    "HML": "https://meualelo-webviews-hml.siteteste.inf.br/",
    "PRD": "https://meualelo-webviews.alelo.com.br/",
}
