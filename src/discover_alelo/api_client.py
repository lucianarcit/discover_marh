"""Cliente HTTP reutilizável para as APIs Alelo.

Gerencia autenticação, headers comuns, retry para erros transitórios,
e captura métricas de cada chamada.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from .auth import AuthResult, AuthenticationError, authenticate, get_access_token
from .config import get_all_config, get_timeout_tuple, is_homologacao_url
from .models import ApiResult
from .sanitization import sanitize_url

# Status HTTP transitórios que permitem retry (apenas para GET)
_TRANSIENT_STATUS_CODES = {502, 503, 504}
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 2


class AleloApiClient:
    """Cliente HTTP para APIs Alelo com gerenciamento de token."""

    def __init__(self) -> None:
        self._config = get_all_config()
        self._session = requests.Session()
        self._token: str | None = None
        self._token_refreshed: bool = False
        self._auth_result: AuthResult | None = None

    @property
    def auth_result(self) -> AuthResult | None:
        """Resultado da última tentativa de autenticação."""
        return self._auth_result

    def _ensure_token(self) -> str:
        """Garante que há um token válido disponível."""
        if not self._token:
            self._auth_result = authenticate()
            if not self._auth_result.success:
                raise AuthenticationError(
                    message=self._auth_result.error_detail,
                    status=self._auth_result.execution_status,
                    status_code=self._auth_result.status_code,
                )
            self._token = self._auth_result.access_token
            self._token_refreshed = False
        return self._token

    def _build_common_headers(self) -> dict[str, str]:
        """Monta headers comuns a todas as requisições."""
        config = self._config
        token = self._ensure_token()

        return {
            "Authorization": f"Bearer {token}",
            "APP_VERSION": config["app_version"],
            "AUTH_TYPE": config["auth_type"],
            "Content-Type": "application/json",
            "FNP": config["fnp"],
            "PLATFORM": config["platform"],
            "client_id": config["ibm_client_id"],
            "X-BASIC-AUTHORIZATION": config["basic_auth"],
            "USER_ID": config["user_id"],
        }

    def execute(
        self,
        operation_name: str,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: Any = None,
        extra_headers: dict[str, str] | None = None,
    ) -> ApiResult:
        """Executa uma chamada de API e retorna o resultado estruturado."""
        result = ApiResult(
            operation_name=operation_name,
            method=method.upper(),
            url=sanitize_url(url),
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        # Validação de segurança: URL deve ser homologação
        if not is_homologacao_url(url):
            result.execution_status = "INVALID_DOCUMENTATION"
            result.error_type = "SECURITY"
            result.error_message = (
                "URL não pertence ao ambiente de homologação. Execução bloqueada."
            )
            return result

        # Monta headers — pode falhar na autenticação
        try:
            headers = self._build_common_headers()
        except AuthenticationError as e:
            # Propaga o status detalhado do auth
            result.execution_status = f"BLOCKED_BY_AUTH"
            result.error_type = e.status
            result.error_message = str(e)
            return result

        if extra_headers:
            headers.update(extra_headers)

        # Prepara request kwargs
        timeout = get_timeout_tuple(self._config)
        request_kwargs: dict[str, Any] = {
            "method": method.upper(),
            "url": url,
            "headers": headers,
            "timeout": timeout,
            "verify": self._config["verify_ssl"],
        }

        if params:
            request_kwargs["params"] = params
        if json_body:
            request_kwargs["json"] = json_body
        if data:
            request_kwargs["data"] = data

        # Request summary (sanitizado)
        result.request_summary = {
            "method": method.upper(),
            "url": sanitize_url(url),
            "has_params": bool(params),
            "has_body": bool(json_body or data),
            "param_keys": list(params.keys()) if params else [],
            "body_keys": list(json_body.keys()) if json_body else [],
        }

        # Executa com retry para erros transitórios (apenas GET)
        is_safe_method = method.upper() in ("GET", "HEAD", "OPTIONS")
        max_attempts = _MAX_RETRIES if is_safe_method else 1

        total_start = time.time()
        response = None

        for attempt in range(1, max_attempts + 1):
            start = time.time()
            try:
                response = self._session.request(**request_kwargs)
            except requests.exceptions.ConnectTimeout:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < max_attempts:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "TIMEOUT"
                result.error_type = "ConnectTimeout"
                result.error_message = (
                    f"Connect timeout após {result.duration_ms}ms "
                    f"({attempt} tentativas)"
                )
                return result

            except requests.exceptions.ReadTimeout:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < max_attempts:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "TIMEOUT"
                result.error_type = "ReadTimeout"
                result.error_message = (
                    f"Read timeout após {result.duration_ms}ms "
                    f"({attempt} tentativas)"
                )
                return result

            except requests.exceptions.Timeout:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < max_attempts:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "TIMEOUT"
                result.error_type = "Timeout"
                result.error_message = f"Timeout ({attempt} tentativas)"
                return result

            except requests.exceptions.ConnectionError as e:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < max_attempts:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "CONNECTION_ERROR"
                result.error_type = "ConnectionError"
                result.error_message = f"{type(e).__name__} ({attempt} tentativas)"
                return result

            except requests.exceptions.RequestException as e:
                result.duration_ms = int((time.time() - total_start) * 1000)
                result.execution_status = "HTTP_ERROR"
                result.error_type = type(e).__name__
                result.error_message = str(e)[:200]
                return result

            # Retry para gateway errors transitórios
            if response.status_code in _TRANSIENT_STATUS_CODES and attempt < max_attempts:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue

            break

        result.duration_ms = int((time.time() - total_start) * 1000)
        result.status_code = response.status_code
        result.response_headers = dict(response.headers)

        # Trata 401 com retry de token (uma vez)
        if response.status_code == 401 and not self._token_refreshed:
            self._token = None
            self._token_refreshed = True
            try:
                self._token = get_access_token()
                headers["Authorization"] = f"Bearer {self._token}"
                request_kwargs["headers"] = headers

                start2 = time.time()
                response = self._session.request(**request_kwargs)
                result.duration_ms += int((time.time() - start2) * 1000)
                result.status_code = response.status_code
                result.response_headers = dict(response.headers)
            except AuthenticationError as e:
                result.execution_status = "BLOCKED_BY_AUTH"
                result.error_type = e.status
                result.error_message = f"Retry de token falhou: {e}"
                return result

        # Classifica resposta final
        result = _classify_response(result, response)

        return result

    def close(self) -> None:
        """Fecha a sessão HTTP."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _classify_response(result: ApiResult, response: requests.Response) -> ApiResult:
    """Classifica a resposta HTTP de forma granular."""
    status = response.status_code

    # Body da resposta
    try:
        result.response_body = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        result.response_body = response.text[:2000] if response.text else None

    if 200 <= status < 300:
        result.success = True
        result.execution_status = "SUCCESS"
    elif status == 401:
        result.success = False
        result.execution_status = "AUTH_TOKEN_INVALID"
        result.error_type = "HTTP_401"
        result.error_message = "Token rejeitado pelo endpoint"
    elif status == 403:
        result.success = False
        result.execution_status = "HTTP_ERROR"
        result.error_type = "HTTP_403"
        result.error_message = "Sem permissão (FNP, prova de vida ou interlocutor)"
    elif status == 502:
        result.success = False
        result.execution_status = "AUTH_SERVICE_UNAVAILABLE"
        result.error_type = "HTTP_502"
        result.error_message = "Bad Gateway"
    elif status == 503:
        result.success = False
        result.execution_status = "AUTH_SERVICE_UNAVAILABLE"
        result.error_type = "HTTP_503"
        result.error_message = "Serviço indisponível"
    elif status == 504:
        result.success = False
        result.execution_status = "AUTH_GATEWAY_TIMEOUT"
        result.error_type = "HTTP_504"
        result.error_message = "Gateway Timeout — backend não respondeu"
    else:
        result.success = False
        result.execution_status = "HTTP_ERROR"
        result.error_type = f"HTTP_{status}"
        result.error_message = response.text[:500] if response.text else ""

    return result
