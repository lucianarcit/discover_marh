"""Modelos de request do agente MARH."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from marh_agent.config import MAX_MESSAGE_LENGTH


class ChatRequest(BaseModel):
    company_id: str = Field(default="")
    user_id: str = Field(default="")
    session_id: str = Field(default="")
    message: str = Field(..., min_length=1)
    environment: Literal["HML", "PRD"] = "HML"
    correlation_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        if len(v) > MAX_MESSAGE_LENGTH:
            return v[:MAX_MESSAGE_LENGTH]
        return v

    def ensure_correlation_id(self) -> str:
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        return self.correlation_id
