"""Cliente HTTP para APIs Alelo — somente operações GET.

Gerencia autenticação, headers comuns, retry para erros transitórios,
e captura métricas de cada chamada.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from .auth import AuthenticationError, authenticate, get_access_token
from .config import get_all_config, get_timeout_tuple, is_homologacao_url
from .models import ApiResult
from .sanitization import sanitize_url

# Status HTTP transitórios que permitem retry
_TRANSIENT_STATUS_CODES = {502, 503, 504}
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 2


class AleloApiClient:
    """Cliente HTTP somente-leitura para APIs Alelo."""

    def __init__(self) -> None:
        self._config = get_all_config()
        self._session = requests.Session()
        self._token: str | None = None
        self._token_refreshed: bool = False

    def _ensure_token(self) -> str:
        """Garante que há um token válido disponível."""
        if not self._token:
            self._token = get_access_token()
            self._token_refreshed = False
        return self._token

    def _build_headers(self) -> dict[str, str]:
        """Monta headers para requisição GET — credenciais app portador."""
        config = self._config
        token = self._ensure_token()

        return {
            "APP_VERSION": config["app_version"],
            "AUTH_TYPE": config["auth_type"],
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "CLIENT_ID": config["ibm_client_id"],
            "CLIENT_SECRET": config["client_secret"],
            "Content-Type": "application/json",
            "FNP": config["fnp"],
            "PLATFORM": config["platform"],
            "X-BASIC-AUTHORIZATION": config["basic_auth"],
            "user_id": config["user_id"],
            "x-ibm-client-id": config["ibm_client_id"],
        }

    def get(
        self,
        operation_name: str,
        url: str,
        params: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> ApiResult:
        """Executa uma chamada GET e retorna o resultado estruturado.

        Args:
            operation_name: Nome da operação para registro.
            url: URL completa do endpoint.
            params: Query parameters.
            extra_headers: Headers adicionais.

        Returns:
            ApiResult com todos os detalhes da execução.
        """
        result = ApiResult(
            operation_name=operation_name,
            method="GET",
            url=sanitize_url(url),
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        # Validação de segurança: URL deve ser homologação
        if not is_homologacao_url(url):
            result.execution_status = "INVALID_DOCUMENTATION"
            result.error_type = "SECURITY"
            result.error_message = "URL não pertence ao ambiente de homologação."
            return result

        # Monta headers
        try:
            headers = self._build_headers()
        except AuthenticationError as e:
            result.execution_status = "BLOCKED_BY_AUTH"
            result.error_type = e.status
            result.error_message = str(e)
            return result

        if extra_headers:
            headers.update(extra_headers)

        # Prepara request
        timeout = get_timeout_tuple(self._config)
        request_kwargs: dict[str, Any] = {
            "url": url,
            "headers": headers,
            "timeout": timeout,
            "verify": self._config["verify_ssl"],
        }
        if params:
            request_kwargs["params"] = params

        result.request_summary = {
            "method": "GET",
            "url": sanitize_url(url),
            "has_params": bool(params),
            "param_keys": list(params.keys()) if params else [],
        }

        # Executa com retry para erros transitórios
        total_start = time.time()
        response = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self._session.get(**request_kwargs)
            except requests.exceptions.ConnectTimeout:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "TIMEOUT"
                result.error_type = "ConnectTimeout"
                result.error_message = f"Connect timeout ({attempt} tentativas)"
                return result

            except requests.exceptions.ReadTimeout:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_BACKOFF_SECONDS)
                    continue
                result.execution_status = "TIMEOUT"
                result.error_type = "ReadTimeout"
                result.error_message = f"Read timeout ({attempt} tentativas)"
                return result

            except requests.exceptions.ConnectionError as e:
                result.duration_ms = int((time.time() - total_start) * 1000)
                if attempt < _MAX_RETRIES:
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

            # Retry para gateway errors
            if response.status_code in _TRANSIENT_STATUS_CODES and attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS)
                continue

            break

        result.duration_ms = int((time.time() - total_start) * 1000)
        result.status_code = response.status_code
        result.response_headers = dict(response.headers)

        # Retry de token se 401
        if response.status_code == 401 and not self._token_refreshed:
            self._token = None
            self._token_refreshed = True
            try:
                self._token = get_access_token()
                headers["Authorization"] = f"Bearer {self._token}"
                request_kwargs["headers"] = headers
                response = self._session.get(**request_kwargs)
                result.duration_ms = int((time.time() - total_start) * 1000)
                result.status_code = response.status_code
                result.response_headers = dict(response.headers)
            except AuthenticationError as e:
                result.execution_status = "BLOCKED_BY_AUTH"
                result.error_type = e.status
                result.error_message = f"Retry de token falhou: {e}"
                return result

        # Classifica resposta
        _classify_response(result, response)
        return result

    # Alias para manter compatibilidade
    def execute(self, operation_name: str, method: str, url: str, **kwargs) -> ApiResult:
        """Executa chamada — aceita somente GET."""
        if method.upper() != "GET":
            r = ApiResult(operation_name=operation_name, method=method)
            r.execution_status = "SKIPPED_SAFETY"
            r.error_message = f"Método {method} não suportado. Somente GET."
            return r
        return self.get(operation_name=operation_name, url=url, **kwargs)

    def close(self) -> None:
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _classify_response(result: ApiResult, response: requests.Response) -> None:
    """Classifica a resposta HTTP."""
    status = response.status_code

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
    elif status == 504:
        result.success = False
        result.execution_status = "AUTH_GATEWAY_TIMEOUT"
        result.error_type = "HTTP_504"
        result.error_message = "Gateway Timeout"
    else:
        result.success = False
        result.execution_status = "HTTP_ERROR"
        result.error_type = f"HTTP_{status}"
        result.error_message = response.text[:300] if response.text else ""
