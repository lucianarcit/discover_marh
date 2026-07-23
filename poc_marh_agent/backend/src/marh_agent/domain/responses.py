"""Modelos de response do agente MARH."""

from __future__ import annotations

from pydantic import BaseModel


class NavigationResponse(BaseModel):
    type: str = "list_navigation"
    route_id: str
    label: str
    deeplink: str
    webview_url: str


class ChatResponse(BaseModel):
    correlation_id: str
    intent_id: str | None = None
    flow: str
    message: str
    navigation: NavigationResponse | None = None
    error_code: str | None = None
    metadata: dict = {}
