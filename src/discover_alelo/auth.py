"""Módulo de autenticação com a API Alelo.

Obtém access_token dinamicamente usando o endpoint OAuth2.
O token permanece somente em memória — nunca é salvo em disco.

Classifica erros de autenticação de forma granular:
- AUTH_TOKEN_EXPIRED: resposta explícita de token expirado
- AUTH_TOKEN_INVALID: resposta explícita de token/credencial inválida
- AUTH_REFRESH_TOKEN_INVALID: refresh token rejeitado
- AUTH_CONFIGURATION_ERROR: variáveis ausentes ou malformadas
- AUTH_GATEWAY_TIMEOUT: HTTP 504 do gateway
- AUTH_SERVICE_UNAVAILABLE: HTTP 502/503
- AUTH_ERROR: outro erro de auth não classificável
- TIMEOUT: timeout da biblioteca requests
- CONNECTION_ERROR: falha de rede
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
        """Serializa sem expor o token."""
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


# Status HTTP transitórios que permitem retry
_TRANSIENT_STATUS_CODES = {502, 503, 504}
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 2


def get_access_token() -> str:
    """Obtém um access_token válido chamando o endpoint OAuth2.

    Returns:
        O access_token como string.

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
    """Executa a autenticação e retorna resultado detalhado.

    Não lança exceção — retorna AuthResult com sucesso ou erro classificado.
    """
    config = get_all_config()
    auth_url = config["auth_url"]
    result = AuthResult()

    # Validação de configuração
    if not auth_url:
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "ALELO_AUTH_URL não definida no .env"
        return result

    if not is_homologacao_url(auth_url):
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = (
            "URL de autenticação não contém indicador de homologação. "
            "Execução bloqueada por segurança."
        )
        return result

    if not config.get("refresh_token"):
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "ALELO_REFRESH_TOKEN não definido ou vazio no .env"
        return result

    if not config.get("basic_auth"):
        result.execution_status = "AUTH_CONFIGURATION_ERROR"
        result.error_detail = "ALELO_BASIC_AUTH não definido no .env"
        return result

    # Monta request idêntico ao cURL
    headers = {
        "APP_VERSION": config["app_version"],
        "AUTH_TYPE": config["auth_type"],
        "Authorization": config["basic_auth"],
        "Content-Type": "application/x-www-form-urlencoded",
        "FNP": config["fnp"],
        "PLATFORM": config["platform"],
        "x-ibm-client-id": config["ibm_client_id"],
    }

    # Body form-urlencoded — exatamente como no cURL
    data = {
        "grant_type": "refresh_token",
        "refresh_token": config["refresh_token"],
    }

    timeout = get_timeout_tuple(config)

    # Executa com retry para erros transitórios
    total_start = time.time()
    last_status_code = 0
    last_error = ""

    for attempt in range(1, _MAX_RETRIES + 1):
        result.attempts = attempt

        start = time.time()
        try:
            response = requests.post(
                auth_url,
                headers=headers,
                data=data,
                timeout=timeout,
                verify=config["verify_ssl"],
            )
        except requests.exceptions.ConnectTimeout:
            duration = int((time.time() - start) * 1000)
            result.duration_ms = int((time.time() - total_start) * 1000)
            result.execution_status = "TIMEOUT"
            result.error_detail = (
                f"Connect timeout após {duration}ms (tentativa {attempt}/{_MAX_RETRIES}). "
                f"O servidor não aceitou a conexão TCP no tempo limite."
            )
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            return result

        except requests.exceptions.ReadTimeout:
            duration = int((time.time() - start) * 1000)
            result.duration_ms = int((time.time() - total_start) * 1000)
            result.execution_status = "TIMEOUT"
            result.error_detail = (
                f"Read timeout após {duration}ms (tentativa {attempt}/{_MAX_RETRIES}). "
                f"A conexão foi estabelecida mas o servidor não respondeu."
            )
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            return result

        except requests.exceptions.Timeout:
            result.duration_ms = int((time.time() - total_start) * 1000)
            result.execution_status = "TIMEOUT"
            result.error_detail = f"Timeout genérico (tentativa {attempt}/{_MAX_RETRIES})."
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            return result

        except requests.exceptions.ConnectionError as e:
            result.duration_ms = int((time.time() - total_start) * 1000)
            result.execution_status = "CONNECTION_ERROR"
            result.error_detail = (
                f"Erro de conexão: {type(e).__name__}. "
                f"Verifique VPN, proxy ou conectividade de rede."
            )
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            return result

        # Resposta recebida
        last_status_code = response.status_code
        result.status_code = response.status_code
        result.duration_ms = int((time.time() - total_start) * 1000)

        # Retry para erros transitórios de gateway
        if response.status_code in _TRANSIENT_STATUS_CODES:
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue
            # Última tentativa — classifica conforme status
            result.execution_status = _classify_gateway_error(response.status_code)
            result.error_detail = (
                f"HTTP {response.status_code} após {attempt} tentativas. "
                f"Duração total: {result.duration_ms}ms. "
                f"O gateway não encaminhou a requisição ao backend."
            )
            return result

        # Resposta não-transitória: processar
        break

    # Classifica resposta HTTP
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

    # Extrai token — busca nos campos conhecidos
    token = (
        body.get("access_token")
        or body.get("accessToken")
        or body.get("token")
    )

    if not token:
        result.execution_status = "AUTH_ERROR"
        result.error_detail = (
            f"HTTP 200 mas token não encontrado. "
            f"Campos na resposta: {result.response_keys}"
        )
        return result

    result.success = True
    result.access_token = token
    result.execution_status = "SUCCESS"
    result.token_type = body.get("token_type", body.get("tokenType", ""))
    result.expires_in = str(body.get("expires_in", body.get("expiresIn", "")))

    # Log sanitizado
    print(
        f"✅ Token obtido. "
        f"Tipo: {result.token_type} | "
        f"Expira em: {result.expires_in}s | "
        f"Duração: {result.duration_ms}ms | "
        f"Tentativas: {result.attempts}"
    )

    return result


def _process_error(result: AuthResult, response: requests.Response) -> AuthResult:
    """Classifica erro HTTP da autenticação com base no status e corpo."""
    status = response.status_code

    # Tenta extrair mensagem de erro do body
    error_body = ""
    error_code = ""
    try:
        body = response.json()
        error_body = body.get("error_description", body.get("error", ""))
        error_code = body.get("error", body.get("errorCode", ""))
        result.response_keys = list(body.keys())
    except (ValueError, requests.exceptions.JSONDecodeError):
        error_body = response.text[:200] if response.text else ""

    # Classificação por status code
    if status == 400:
        result.execution_status = _classify_400(error_code, error_body)
        result.error_detail = (
            f"HTTP 400. Código: '{error_code}'. Detalhe: '{error_body[:100]}'"
        )

    elif status == 401:
        result.execution_status = _classify_401(error_code, error_body)
        result.error_detail = (
            f"HTTP 401. Código: '{error_code}'. Detalhe: '{error_body[:100]}'"
        )

    elif status == 403:
        result.execution_status = "AUTH_ERROR"
        result.error_detail = f"HTTP 403 — Acesso negado. Detalhe: '{error_body[:100]}'"

    elif status == 502:
        result.execution_status = "AUTH_SERVICE_UNAVAILABLE"
        result.error_detail = "HTTP 502 — Bad Gateway. Backend de autenticação pode estar fora."

    elif status == 503:
        result.execution_status = "AUTH_SERVICE_UNAVAILABLE"
        result.error_detail = "HTTP 503 — Serviço indisponível."

    elif status == 504:
        result.execution_status = "AUTH_GATEWAY_TIMEOUT"
        result.error_detail = (
            "HTTP 504 — Gateway Timeout. "
            "O gateway não obteve resposta do backend de autenticação no tempo limite."
        )

    else:
        result.execution_status = "AUTH_ERROR"
        result.error_detail = (
            f"HTTP {status}. Resposta: '{error_body[:150]}'"
        )

    return result


def _classify_400(error_code: str, error_body: str) -> str:
    """Classifica HTTP 400 baseado na mensagem."""
    lower = (error_code + " " + error_body).lower()
    if "invalid_grant" in lower or "refresh" in lower:
        return "AUTH_REFRESH_TOKEN_INVALID"
    if "invalid_client" in lower:
        return "AUTH_TOKEN_INVALID"
    if "expired" in lower:
        return "AUTH_TOKEN_EXPIRED"
    return "AUTH_ERROR"


def _classify_401(error_code: str, error_body: str) -> str:
    """Classifica HTTP 401 baseado na mensagem."""
    lower = (error_code + " " + error_body).lower()
    if "expired" in lower:
        return "AUTH_TOKEN_EXPIRED"
    if "invalid" in lower:
        return "AUTH_TOKEN_INVALID"
    return "AUTH_TOKEN_INVALID"


def _classify_gateway_error(status_code: int) -> str:
    """Classifica erros de gateway."""
    if status_code == 504:
        return "AUTH_GATEWAY_TIMEOUT"
    return "AUTH_SERVICE_UNAVAILABLE"
