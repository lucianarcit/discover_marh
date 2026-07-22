"""Cliente HTTP reutilizável para as APIs Alelo.

Gerencia autenticação, headers comuns, retry em 401, e captura
métricas de cada chamada.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from .auth import AuthenticationError, get_access_token
from .config import get_all_config, is_homologacao_url
from .models import ApiResult
from .sanitization import sanitize_url


class AleloApiClient:
    """Cliente HTTP para APIs Alelo com gerenciamento de token."""

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
        """Executa uma chamada de API e retorna o resultado estruturado.

        Args:
            operation_name: Nome da operação para registro.
            method: Método HTTP (GET, POST, PUT, PATCH, DELETE).
            url: URL completa do endpoint.
            params: Query parameters.
            json_body: Body JSON (para POST/PUT/PATCH).
            data: Body form-data.
            extra_headers: Headers adicionais específicos desta operação.

        Returns:
            ApiResult com todos os detalhes da execução.
        """
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

        # Monta headers
        try:
            headers = self._build_common_headers()
        except AuthenticationError as e:
            result.execution_status = "AUTH_ERROR"
            result.error_type = "AuthenticationError"
            result.error_message = str(e)
            return result

        if extra_headers:
            headers.update(extra_headers)

        # Prepara request kwargs
        request_kwargs: dict[str, Any] = {
            "method": method.upper(),
            "url": url,
            "headers": headers,
            "timeout": self._config["timeout"],
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

        # Executa a chamada
        start = time.time()
        try:
            response = self._session.request(**request_kwargs)
        except requests.exceptions.Timeout:
            result.duration_ms = int((time.time() - start) * 1000)
            result.execution_status = "TIMEOUT"
            result.error_type = "Timeout"
            result.error_message = (
                f"Timeout após {result.duration_ms}ms "
                f"(limite: {self._config['timeout']}s)"
            )
            return result
        except requests.exceptions.ConnectionError as e:
            result.duration_ms = int((time.time() - start) * 1000)
            result.execution_status = "CONNECTION_ERROR"
            result.error_type = "ConnectionError"
            result.error_message = str(type(e).__name__)
            return result
        except requests.exceptions.RequestException as e:
            result.duration_ms = int((time.time() - start) * 1000)
            result.execution_status = "HTTP_ERROR"
            result.error_type = type(e).__name__
            result.error_message = str(e)[:200]
            return result

        result.duration_ms = int((time.time() - start) * 1000)
        result.status_code = response.status_code
        result.response_headers = dict(response.headers)

        # Trata 401 com retry de token (uma vez)
        if response.status_code == 401 and not self._token_refreshed:
            self._token = None
            self._token_refreshed = True
            try:
                self._token = get_access_token()
                # Repete a chamada com token novo
                headers["Authorization"] = f"Bearer {self._token}"
                request_kwargs["headers"] = headers

                start2 = time.time()
                response = self._session.request(**request_kwargs)
                result.duration_ms += int((time.time() - start2) * 1000)
                result.status_code = response.status_code
                result.response_headers = dict(response.headers)
            except AuthenticationError as e:
                result.execution_status = "AUTH_ERROR"
                result.error_type = "AuthenticationError"
                result.error_message = f"Retry de token falhou: {e}"
                return result

        # Processa resposta
        if 200 <= response.status_code < 300:
            result.success = True
            result.execution_status = "SUCCESS"
        else:
            result.success = False
            result.execution_status = "HTTP_ERROR"
            result.error_type = f"HTTP_{response.status_code}"
            result.error_message = response.text[:500] if response.text else ""

        # Body da resposta
        try:
            result.response_body = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            result.response_body = response.text[:2000] if response.text else None

        return result

    def close(self) -> None:
        """Fecha a sessão HTTP."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
