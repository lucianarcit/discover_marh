"""Modelos de dados para resultados de execução de API.

Status de execução possíveis:
- SUCCESS: chamada real executada e resposta válida recebida
- AUTH_TOKEN_EXPIRED: resposta explícita de token expirado
- AUTH_TOKEN_INVALID: resposta explícita de token/credencial inválida
- AUTH_REFRESH_TOKEN_INVALID: refresh token rejeitado
- AUTH_CONFIGURATION_ERROR: variáveis ausentes ou malformadas
- AUTH_GATEWAY_TIMEOUT: HTTP 504 do gateway de auth
- AUTH_SERVICE_UNAVAILABLE: HTTP 502/503 do gateway de auth
- AUTH_ERROR: outro erro de auth não classificável
- BLOCKED_BY_AUTH: a API não foi chamada porque a auth falhou
- HTTP_ERROR: erro HTTP da API (4xx exceto 401, ou outro)
- TIMEOUT: timeout de conexão ou leitura
- CONNECTION_ERROR: falha de rede / DNS / TCP
- INVALID_DOCUMENTATION: URL inválida ou fora de homologação
- SKIPPED_SAFETY: operação mutável não executada por segurança
- SKIPPED_NO_SAMPLE: sem exemplo para executar
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ApiResult:
    """Resultado da execução de uma chamada de API."""

    operation_name: str = ""
    method: str = ""
    url: str = ""
    started_at: str = ""
    duration_ms: int = 0
    status_code: int = 0
    success: bool = False
    execution_status: str = ""
    request_summary: dict[str, Any] = field(default_factory=dict)
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: Any = None
    error_type: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            "operation_name": self.operation_name,
            "method": self.method,
            "url": self.url,
            "started_at": self.started_at,
            "duration_ms": self.duration_ms,
            "status_code": self.status_code,
            "success": self.success,
            "execution_status": self.execution_status,
            "request_summary": self.request_summary,
            "response_headers": self.response_headers,
            "response_body": self.response_body,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }


@dataclass
class ApiOperation:
    """Definição de uma operação de API extraída da documentação."""

    operation_name: str = ""
    description: str = ""
    method: str = ""
    path: str = ""
    full_url: str = ""
    path_parameters: list[str] = field(default_factory=list)
    query_parameters: list[dict[str, str]] = field(default_factory=list)
    required_headers: list[str] = field(default_factory=list)
    optional_headers: list[str] = field(default_factory=list)
    request_body_example: Any = None
    documented_status_codes: list[dict[str, str]] = field(default_factory=list)
    documented_response_example: Any = None
    source_section: str = ""
    safe_to_execute: bool = True
    safety_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            "operation_name": self.operation_name,
            "description": self.description,
            "method": self.method,
            "path": self.path,
            "full_url": self.full_url,
            "path_parameters": self.path_parameters,
            "query_parameters": self.query_parameters,
            "required_headers": self.required_headers,
            "optional_headers": self.optional_headers,
            "request_body_example": self.request_body_example,
            "documented_status_codes": self.documented_status_codes,
            "documented_response_example": self.documented_response_example,
            "source_section": self.source_section,
            "safe_to_execute": self.safe_to_execute,
            "safety_reason": self.safety_reason,
        }


@dataclass
class ExecutionSummary:
    """Resumo de uma execução completa de testes."""

    timestamp: str = ""
    environment: str = ""
    total_operations: int = 0
    successes: int = 0
    failures: int = 0
    blocked_by_auth: int = 0
    skipped_safety: int = 0
    skipped_no_sample: int = 0
    status_codes_found: list[int] = field(default_factory=list)
    total_duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "environment": self.environment,
            "total_operations": self.total_operations,
            "successes": self.successes,
            "failures": self.failures,
            "blocked_by_auth": self.blocked_by_auth,
            "skipped_safety": self.skipped_safety,
            "skipped_no_sample": self.skipped_no_sample,
            "status_codes_found": sorted(set(self.status_codes_found)),
            "total_duration_ms": self.total_duration_ms,
        }
