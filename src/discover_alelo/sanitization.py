"""Módulo de sanitização de dados sensíveis.

Mascara valores de campos que contenham informações pessoais,
tokens, credenciais e outros dados que não devem aparecer em relatórios.
"""

from __future__ import annotations

import re
from typing import Any

# Campos que devem ter seus valores mascarados
SENSITIVE_FIELDS = {
    # Autenticação e tokens
    "authorization",
    "access_token",
    "accesstoken",
    "refresh_token",
    "refreshtoken",
    "id_token",
    "idtoken",
    "token",
    "client_secret",
    "clientsecret",
    "client_id",
    "clientid",
    "x-ibm-client-id",
    "x-basic-authorization",
    "basic_auth",
    "basic authorization",
    "api_key",
    "apikey",
    "secret",
    "password",
    "senha",
    # Identificadores pessoais
    "user_id",
    "userid",
    "fnp",
    "fingerprint",
    "cpf",
    "documentnumber",
    "document_number",
    "document",
    "cardid",
    "card_id",
    "contractnumber",
    "contract_number",
    "card number",
    "serialnumber",
    "serial_number",
    # Dados pessoais
    "email",
    "e-mail",
    "phonenumber",
    "phone_number",
    "telefone",
    "phone",
    "mothername",
    "mother_name",
    # Endereço (parcial)
    "postalcode",
    "postal_code",
    "cep",
    # IDs internos encriptados
    "beneficiaryidencrypted",
    "beneficiaryid",
    "beneficiary_id",
    "beneficiary_id_encrypted",
    # Sessão
    "cookie",
    "set-cookie",
    "session_id",
    "sessionid",
    "jsessionid",
    # Documentos empresariais
    "shippingaddressdocumentnumber",
    "contracteedocumentnumber",
    "spokesmandocumentnumber",
    "placedocumentnumber",
}

# Padrões regex para detecção adicional
SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),  # CPF formatado
    re.compile(r"\b\d{11}\b"),  # CPF sem formatação
    re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),  # CNPJ formatado
    re.compile(r"Bearer\s+[\w\-\.]+"),  # Bearer token
    re.compile(r"Basic\s+[\w\+/=]+"),  # Basic auth
]

REDACTED = "<REDACTED>"


def sanitize(data: Any) -> Any:
    """Sanitiza dados recursivamente, mascarando valores sensíveis.

    Args:
        data: Qualquer estrutura (dict, list, str, etc.)

    Returns:
        Estrutura com valores sensíveis substituídos por '<REDACTED>'.
    """
    if isinstance(data, dict):
        return _sanitize_dict(data)
    elif isinstance(data, list):
        return [sanitize(item) for item in data]
    elif isinstance(data, str):
        return _sanitize_string_value(data)
    return data


def _sanitize_dict(data: dict) -> dict:
    """Sanitiza um dicionário, verificando chaves sensíveis."""
    result = {}
    for key, value in data.items():
        key_lower = key.lower().replace("-", "").replace("_", "")
        normalized_key = key.lower().strip()

        if _is_sensitive_key(normalized_key):
            if isinstance(value, str) and value:
                result[key] = REDACTED
            elif isinstance(value, (dict, list)):
                result[key] = REDACTED
            else:
                result[key] = REDACTED
        else:
            result[key] = sanitize(value)

    return result


def _is_sensitive_key(key: str) -> bool:
    """Verifica se uma chave é considerada sensível."""
    # Remove caracteres de normalização
    key_clean = key.replace("-", "").replace("_", "").replace(" ", "").lower()

    for sensitive in SENSITIVE_FIELDS:
        sensitive_clean = sensitive.replace("-", "").replace("_", "").replace(" ", "")
        # Exige match exato ou que o campo sensível seja significativo (>3 chars)
        if sensitive_clean == key_clean:
            return True
        # Para substring match, exige que o campo sensível tenha pelo menos 4 chars
        # e que o key_clean não seja um campo comum (accept, content-type, etc.)
        if len(sensitive_clean) >= 4 and sensitive_clean in key_clean:
            # Exclusões para campos comuns que podem conter substrings sensíveis
            common_safe = {"accept", "contenttype", "content"}
            if key_clean not in common_safe:
                return True

    return False


def _sanitize_string_value(value: str) -> str:
    """Sanitiza valores string que contenham padrões sensíveis inline."""
    result = value
    for pattern in SENSITIVE_PATTERNS:
        result = pattern.sub(REDACTED, result)
    return result


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Sanitiza headers de uma requisição/resposta HTTP."""
    return _sanitize_dict(headers)


def sanitize_url(url: str) -> str:
    """Remove query parameters sensíveis de uma URL."""
    from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    sanitized_params = {}
    for key, values in params.items():
        if _is_sensitive_key(key.lower()):
            sanitized_params[key] = [REDACTED]
        else:
            sanitized_params[key] = values

    new_query = urlencode(sanitized_params, doseq=True)
    sanitized = urlunparse(parsed._replace(query=new_query))
    return sanitized
