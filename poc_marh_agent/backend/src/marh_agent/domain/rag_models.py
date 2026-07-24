"""Modelos internos do pipeline RAG — independentes de boto3 e AWS SDK."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator


class RetrievedChunk(BaseModel):
    """Representa um trecho recuperado do corpus aprovado.

    Não armazena objetos do SDK AWS. Não armazena o response completo.
    Todos os campos derivam de dados já extraídos pela implementação
    do Retriever antes de construir este modelo.
    """

    content: str
    score: Optional[float] = None
    source_file: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    chunk_index: Optional[int] = None
    metadata: dict = {}

    model_config = {"frozen": True}

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content não pode ser vazio ou somente espaços")
        return v

    @field_validator("metadata", mode="before")
    @classmethod
    def metadata_default(cls, v: object) -> dict:
        if v is None:
            return {}
        return v


class GenerationResult(BaseModel):
    """Resultado de uma chamada ao modelo de linguagem.

    O campo `text` é texto plano — nunca tratado como HTML
    pelo pipeline RAG.
    """

    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    stop_reason: Optional[str] = None
    model_id: Optional[str] = None

    model_config = {"frozen": True}

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text não pode ser vazio ou somente espaços")
        return v
