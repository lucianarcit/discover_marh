"""Módulo de autenticação com a API Alelo.

Obtém access_token dinamicamente usando o endpoint OAuth2.
O token permanece somente em memória — nunca é salvo em disco.
"""

from __future__ import annotations

import time

import requests

from .config import get_all_config, is_homologacao_url


class AuthenticationError(Exception):
    """Erro ao obter ou renovar token de autenticação."""


def get_access_token() -> str:
    """Obtém um access_token válido chamando o endpoint OAuth2.

    Returns:
        O access_token como string.

    Raises:
        AuthenticationError: Se a URL não for homologação, a chamada falhar,
            ou a resposta não contiver um token válido.
    """
    config = get_all_config()
    auth_url = config["auth_url"]

    # Segurança: verifica se é ambiente de homologação
    if not is_homologacao_url(auth_url):
        raise AuthenticationError(
            f"URL de autenticação não é de homologação. "
            f"Execução interrompida por segurança. URL: {_mask_url(auth_url)}"
        )

    headers = {
        "APP_VERSION": config["app_version"],
        "AUTH_TYPE": config["auth_type"],
        "Authorization": config["basic_auth"],
        "Content-Type": "application/x-www-form-urlencoded",
        "FNP": config["fnp"],
        "PLATFORM": config["platform"],
        "x-ibm-client-id": config["ibm_client_id"],
    }

    # Body da requisição de token (grant_type=refresh_token)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": config.get("refresh_token", ""),
    }

    # Se não tiver refresh_token no config, usa client_credentials
    if not data["refresh_token"]:
        data = {
            "grant_type": "client_credentials",
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        }

    start = time.time()
    try:
        response = requests.post(
            auth_url,
            headers=headers,
            data=data,
            timeout=config["timeout"],
            verify=config["verify_ssl"],
        )
    except requests.exceptions.Timeout:
        duration = int((time.time() - start) * 1000)
        raise AuthenticationError(
            f"Timeout ao obter token ({duration}ms). "
            f"Verifique a conectividade com o servidor de autenticação."
        )
    except requests.exceptions.ConnectionError as e:
        raise AuthenticationError(
            f"Erro de conexão ao obter token: {type(e).__name__}"
        )

    duration_ms = int((time.time() - start) * 1000)

    # Valida status HTTP
    if response.status_code != 200:
        raise AuthenticationError(
            f"Autenticação falhou. Status: {response.status_code}. "
            f"Duração: {duration_ms}ms. "
            f"Verifique as credenciais no .env."
        )

    # Extrai o token da resposta
    try:
        body = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        raise AuthenticationError(
            "Resposta de autenticação não é JSON válido."
        )

    # Campos possíveis para o token
    token = (
        body.get("access_token")
        or body.get("accessToken")
        or body.get("token")
    )

    if not token:
        available_keys = list(body.keys())
        raise AuthenticationError(
            f"Token não encontrado na resposta. "
            f"Campos disponíveis: {available_keys}. "
            f"Duração: {duration_ms}ms."
        )

    # Log sanitizado (sem expor o token)
    _log_auth_success(duration_ms, body)

    return token


def _log_auth_success(duration_ms: int, body: dict) -> None:
    """Registra sucesso na autenticação sem expor dados sensíveis."""
    token_type = body.get("token_type", body.get("tokenType", "unknown"))
    expires_in = body.get("expires_in", body.get("expiresIn", "N/A"))
    scope = body.get("scope", "N/A")

    print(
        f"✅ Token obtido com sucesso. "
        f"Tipo: {token_type} | "
        f"Expira em: {expires_in}s | "
        f"Scope: {scope} | "
        f"Duração: {duration_ms}ms"
    )


def _mask_url(url: str) -> str:
    """Mascara partes sensíveis da URL para log."""
    if len(url) > 30:
        return url[:20] + "..." + url[-10:]
    return url
