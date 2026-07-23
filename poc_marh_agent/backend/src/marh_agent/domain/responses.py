"""Modelos de response do agente MARH."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class NavigationResponse(BaseModel):
    type: str = "list_navigation"
    route_id: str
    label: str
    deeplink: str
    webview_url: str


class PresentationTone(str, Enum):
    neutral = "neutral"
    positive = "positive"
    warning = "warning"
    negative = "negative"
    informative = "informative"


class PresentationVariant(str, Enum):
    capabilities_list = "capabilities_list"
    collaborator_summary = "collaborator_summary"
    order_summary = "order_summary"
    order_list = "order_list"
    knowledge_answer = "knowledge_answer"
    informational_notice = "informational_notice"
    warning_notice = "warning_notice"
    transactional_redirect = "transactional_redirect"
    clarification = "clarification"
    error_notice = "error_notice"


class PresentationField(BaseModel):
    label: str
    value: str
    emphasis: bool = False


class PresentationItem(BaseModel):
    title: str
    subtitle: Optional[str] = None
    value: Optional[str] = None
    badge: Optional[str] = None
    tone: Optional[PresentationTone] = None


class Presentation(BaseModel):
    variant: PresentationVariant
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    tone: PresentationTone = PresentationTone.neutral
    status_label: Optional[str] = None
    fields: list[PresentationField] = []
    items: list[PresentationItem] = []


class ChatResponse(BaseModel):
    correlation_id: str
    intent_id: str | None = None
    flow: str
    message: str
    presentation: Optional[Presentation] = None
    navigation: NavigationResponse | None = None
    error_code: str | None = None
    metadata: dict = {}
