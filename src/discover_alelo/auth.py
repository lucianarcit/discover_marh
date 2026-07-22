"""Módulo de autenticação com a API Alelo.

Fluxos suportados (em ordem de prioridade):
1. ALELO_ACCESS_TOKEN direto no .env → usa sem chamar OAuth2
2. client_credentials → POST com client_id e client_secret no body
3. refresh_token → POST com refresh_token no body (fallback)

O access_token permanece somente em memória.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from .config import get_all_config, get_timeout_tuple, is_homologacao_url


@dataclass
class AuthResult:
    """Resultado detalhado de uma tentativa de autenticação."""

    success: bool = False
    access_token: str = ""
    status_code: int = 0
    duration_ms: int = 0
    execution_status: str = ""
    error_detail: str = ""
    attempts: int = 0
    token_type: str = ""
    expires_in: str = ""
    response_keys: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "has_token": bool(self.access_token),
            "token_length": len(self.access_token) if self.access_token else 0,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "execution_status": self.execution_status,
            "error_detail": self.error_detail,
            "attempts": self.attempts,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "response_keys": self.response_keys,
        }


class AuthenticationError(Exception):
    """Erro ao obter ou renovar token de autenticação."""

    def __init__(self, message: str, status: str = "AUTH_ERROR", status_code: int = 0):
        super().__init__(message)
        self.status = status
        self.status_code = status_code


_TRANSIENT_STATUS_CODES = {502, 503, 504}
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 2


def get_access_token() -> str:
    """Obtém um access_token válido.

    Raises:
        AuthenticationError: Com status classificado conforme o erro.
    """
    result = authenticate()
    if not result.success:
        raise AuthenticationError(
            message=result.error_detail,
            status=result.execution_status,
            status_code=result.status_code,
        )
    return result.access_token


def authenticate() -> AuthResult:
    """Executa a autenticação e retorna resultado detalhado."""
    config = get_all_config()
    result = AuthResult()

    # ─── Fluxo 1: token direto do .env ────────────────────────────────────
    direct_token = config.get("access_token", "")
    if direct_token:
        result.success = True
        result.access_token = direct_token
        result.execution_status = "SUCCESS"
        result.token_type = "Bearer (direto do .env)"
        result.expires_in = "desconhecido"
        result.attempts = 0
        print(f"✅ Token direto do .env ({len(direct_token)} chars).")
        return result

    # ─── Fluxo 2: client_credentials ou refresh_token via OAuth2 ──────────
    auth_url = config["auth_url"]

    if not auth_url:
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "ALELO_AUTH_URL não definida no .env"
        return result

    if not is_homologacao_url(auth_url):
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "URL de auth não é homologação. Execução bloqueada."
        return result

    if not config.get("client_id") or not config.get("client_secret"):
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "ALELO_CLIENT_ID ou ALELO_CLIENT_SECRET ausente no .env"
        return result

    # Decide grant_type
    refresh_token = config.get("refresh_token", "")
    if refresh_token:
        # Refresh token disponível
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        }
        grant_desc = "refresh_token"
    else:
        # Sem refresh_token — não é possível autenticar sem token direto
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = (
            "ALELO_REFRESH_TOKEN vazio e ALELO_ACCESS_TOKEN vazio. "
            "Obtenha um token Bearer válido e cole em ALELO_ACCESS_TOKEN no .env, "
            "ou obtenha um refresh_token e cole em ALELO_REFRESH_TOKEN."
        )
        return result

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {config['basic_auth']}",
    }

    timeout = get_timeout_tuple(config)

    print(f"🔐 Autenticando via {grant_desc}...")

    # Executa com retry para erros transitórios
    total_start = time.time()
    response = None

    for attempt in range(1, _MAX_RETRIES + 1):
        result.attempts = attempt

        try:
            response = requests.post(
                auth_url,
                headers=headers,
                data=data,
                timeout=timeout,
                verify=config["verify_ssl"],
            )
        except requests.exceptions.ConnectTimeout:
            result.duration_ms = int((time.time() - total_start) * 1000)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            result.execution_status = "TIMEOUT"
            result.error_detail = f"Connect timeout ({result.duration_ms}ms, {attempt} tentativas)"
            return result

        except requests.exceptions.ReadTimeout:
            result.duration_ms = int((time.time() - total_start) * 1000)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            result.execution_status = "TIMEOUT"
            result.error_detail = f"Read timeout ({result.duration_ms}ms, {attempt} tentativas)"
            return result

        except requests.exceptions.ConnectionError as e:
            result.duration_ms = int((time.time() - total_start) * 1000)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            result.execution_status = "CONNECTION_ERROR"
            result.error_detail = f"Erro de conexão: {type(e).__name__}"
            return result

        # Retry para gateway errors
        if response.status_code in _TRANSIENT_STATUS_CODES and attempt < _MAX_RETRIES:
            time.sleep(_RETRY_BACKOFF_SECONDS)
            continue

        break

    result.duration_ms = int((time.time() - total_start) * 1000)
    result.status_code = response.status_code

    # Processa resposta
    if response.status_code == 200:
        return _process_success(result, response)
    else:
        return _process_error(result, response)


def _process_success(result: AuthResult, response: requests.Response) -> AuthResult:
    """Processa resposta 200 e extrai token."""
    try:
        body = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        result.execution_status = "AUTH_ERROR"
        result.error_detail = "Resposta 200 mas body não é JSON válido."
        return result

    result.response_keys = list(body.keys())

    token = (
        body.get("access_token")
        or body.get("accessToken")
        or body.get("token")
    )

    if not token:
        result.execution_status = "AUTH_ERROR"
        result.error_detail = f"HTTP 200 mas token ausente. Campos: {result.response_keys}"
        return result

    result.success = True
    result.access_token = token
    result.execution_status = "SUCCESS"
    result.token_type = body.get("token_type", "")
    result.expires_in = str(body.get("expires_in", ""))

    print(
        f"✅ Token obtido. Tipo: {result.token_type} | "
        f"Expira em: {result.expires_in}s | "
        f"Duração: {result.duration_ms}ms"
    )
    return result


def _process_error(result: AuthResult, response: requests.Response) -> AuthResult:
    """Classifica erro HTTP da autenticação."""
    status = response.status_code

    error_body = ""
    error_code = ""
    try:
        body = response.json()
        error_body = body.get("error_description", body.get("error", body.get("message", "")))
        error_code = str(body.get("error", body.get("code", "")))
        result.response_keys = list(body.keys())
    except (ValueError, requests.exceptions.JSONDecodeError):
        error_body = response.text[:200] if response.text else ""

    if status == 400:
        lower = (error_code + " " + error_body).lower()
        if "invalid_grant" in lower or "refresh" in lower:
            result.execution_status = "AUTH_REFRESH_TOKEN_INVALID"
        elif "invalid_client" in lower:
            result.execution_status = "AUTH_TOKEN_INVALID"
        else:
            result.execution_status = "AUTH_ERROR"
        result.error_detail = f"HTTP 400. Código: '{error_code}'. Detalhe: '{error_body[:100]}'"

    elif status == 401:
        result.execution_status = "AUTH_TOKEN_INVALID"
        result.error_detail = f"HTTP 401. Código: '{error_code}'. Detalhe: '{error_body[:100]}'"

    elif status == 504:
        result.execution_status = "AUTH_GATEWAY_TIMEOUT"
        result.error_detail = "HTTP 504 — Gateway Timeout."

    elif status in (502, 503):
        result.execution_status = "AUTH_SERVICE_UNAVAILABLE"
        result.error_detail = f"HTTP {status} — Serviço indisponível."

    else:
        result.execution_status = "AUTH_ERROR"
        result.error_detail = f"HTTP {status}. Resposta: '{error_body[:150]}'"

    return result
