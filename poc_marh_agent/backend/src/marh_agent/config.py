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
    """Modo de operação legado — mantido para retrocompatibilidade."""

    MOCK_LOCAL = "MOCK_LOCAL"          # Mock clients, dev local ou testes
    INTEGRATED = "INTEGRATED"          # Clientes reais (ma-hr-orch + Bedrock)


class DataSourceMode(StrEnum):
    """Controla qual implementação de MaHrOrchClient é usada."""

    MOCK = "MOCK"
    INTEGRATED = "INTEGRATED"


class KnowledgeMode(StrEnum):
    """Controla qual implementação de KnowledgeClient é usada."""

    MOCK = "MOCK"
    BEDROCK_RAG = "BEDROCK_RAG"


def _resolve_data_source_mode() -> DataSourceMode:
    """Resolve DATA_SOURCE_MODE com fallback para AGENT_MODE legado."""
    explicit = os.getenv("DATA_SOURCE_MODE")
    if explicit:
        return DataSourceMode(explicit)
    legacy = os.getenv("AGENT_MODE", "MOCK_LOCAL")
    if legacy == "INTEGRATED":
        return DataSourceMode.INTEGRATED
    return DataSourceMode.MOCK


# --- Variáveis de ambiente ---


ENVIRONMENT: Environment = Environment(
    os.getenv("ENVIRONMENT", "HML")
)

MODE: Mode = Mode(
    os.getenv("AGENT_MODE", "MOCK_LOCAL")
)

DATA_SOURCE_MODE: DataSourceMode = _resolve_data_source_mode()

KNOWLEDGE_MODE: KnowledgeMode = KnowledgeMode(
    os.getenv("KNOWLEDGE_MODE", "MOCK")
)

RETRIEVAL_SCORE_THRESHOLD: float = float(
    os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.70")
)

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

# --- ma-hr-orch ---

MA_HR_ORCH_BASE_URL: str = os.getenv("MA_HR_ORCH_BASE_URL", "")
MA_HR_ORCH_TIMEOUT_SECONDS: int = int(os.getenv("MA_HR_ORCH_TIMEOUT_SECONDS", "10"))

# --- Amazon Bedrock ---

BEDROCK_REGION: str = os.getenv("BEDROCK_REGION", "sa-east-1")
BEDROCK_EMBED_MODEL_ID: str = os.getenv(
    "BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"
)
BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "")  # sem padrão — definir após Passo 10
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
