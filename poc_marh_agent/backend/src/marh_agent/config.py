"""Configuração centralizada do backend MARH Agent."""

from __future__ import annotations

import os
from enum import StrEnum


class Environment(StrEnum):
    HML = "HML"
    PRD = "PRD"


class Mode(StrEnum):
    MOCK_LOCAL = "MOCK_LOCAL"


ENVIRONMENT: Environment = Environment(
    os.getenv("ENVIRONMENT", "HML")
)
MODE: Mode = Mode.MOCK_LOCAL
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

WEBVIEW_BASE_URLS: dict[str, str] = {
    "HML": "https://meualelo-webviews-hml.siteteste.inf.br/",
    "PRD": "https://meualelo-webviews.alelo.com.br/",
}
