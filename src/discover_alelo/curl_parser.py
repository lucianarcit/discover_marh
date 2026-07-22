"""Parser reutilizável de comandos cURL.

Lê um arquivo TXT contendo um cURL e extrai:
- Método HTTP
- URL
- Query parameters
- Headers
- Body (JSON, form-urlencoded, --data, --data-raw, --data-urlencode)
- Autenticação Basic
- Content-Type
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


def parse_curl_file(filepath: str | Path) -> dict[str, Any]:
    """Lê um arquivo com um comando cURL e retorna os componentes extraídos."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo cURL não encontrado: {path.resolve()}")

    content = path.read_text(encoding="utf-8")
    return parse_curl_string(content)


def parse_curl_string(curl_string: str) -> dict[str, Any]:
    """Analisa uma string cURL e extrai todos os componentes."""
    # Normaliza continuações de linha (backslash + newline)
    normalized = curl_string.replace("\\\n", " ").replace("\\\r\n", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Remove prefixo 'curl' se presente
    if normalized.lower().startswith("curl"):
        normalized = normalized[4:].strip()

    # Tokeniza respeitando aspas
    try:
        tokens = shlex.split(normalized)
    except ValueError:
        # Fallback para aspas malformadas
        tokens = _fallback_tokenize(normalized)

    result: dict[str, Any] = {
        "method": "GET",
        "url": "",
        "query_parameters": {},
        "headers": {},
        "body": None,
        "body_type": None,
        "basic_auth": None,
        "content_type": None,
    }

    data_parts: list[str] = []
    data_urlencode_parts: list[str] = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token in ("-X", "--request"):
            i += 1
            if i < len(tokens):
                result["method"] = tokens[i].upper()

        elif token in ("-H", "--header"):
            i += 1
            if i < len(tokens):
                header_str = tokens[i]
                key, value = _parse_header(header_str)
                if key:
                    result["headers"][key] = value

        elif token in ("-d", "--data", "--data-raw", "--data-binary"):
            i += 1
            if i < len(tokens):
                data_parts.append(tokens[i])
                if result["method"] == "GET":
                    result["method"] = "POST"

        elif token == "--data-urlencode":
            i += 1
            if i < len(tokens):
                data_urlencode_parts.append(tokens[i])
                if result["method"] == "GET":
                    result["method"] = "POST"

        elif token in ("-u", "--user"):
            i += 1
            if i < len(tokens):
                result["basic_auth"] = tokens[i]

        elif token.startswith("http://") or token.startswith("https://"):
            result["url"] = token

        elif not token.startswith("-") and not result["url"] and _is_url(token):
            result["url"] = token

        i += 1

    # Processa URL e query parameters
    if result["url"]:
        parsed_url = urlparse(result["url"])
        result["query_parameters"] = {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(parsed_url.query).items()
        }
        # URL sem query string
        result["url_base"] = (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        )
    else:
        result["url_base"] = ""

    # Processa body
    if data_urlencode_parts:
        decoded_parts = []
        for part in data_urlencode_parts:
            decoded = unquote(part)
            decoded_parts.append(decoded)
        body_str = "&".join(decoded_parts)
        result["body"] = dict(
            item.split("=", 1) for item in body_str.split("&") if "=" in item
        )
        result["body_type"] = "form-urlencoded"

    elif data_parts:
        raw_body = "&".join(data_parts) if len(data_parts) > 1 else data_parts[0]
        # Tenta interpretar como JSON
        if _looks_like_json(raw_body):
            import json

            try:
                result["body"] = json.loads(raw_body)
                result["body_type"] = "json"
            except json.JSONDecodeError:
                result["body"] = raw_body
                result["body_type"] = "raw"
        # Tenta interpretar como form-urlencoded
        elif "=" in raw_body and not raw_body.startswith("{"):
            result["body"] = dict(
                item.split("=", 1) for item in raw_body.split("&") if "=" in item
            )
            result["body_type"] = "form-urlencoded"
        else:
            result["body"] = raw_body
            result["body_type"] = "raw"

    # Extrai Content-Type dos headers
    for key, value in result["headers"].items():
        if key.lower() == "content-type":
            result["content_type"] = value
            break

    # Extrai Basic Auth do header Authorization se presente
    auth_header = result["headers"].get("Authorization", "")
    if auth_header.startswith("Basic "):
        result["basic_auth"] = auth_header

    return result


def _parse_header(header_str: str) -> tuple[str, str]:
    """Extrai nome e valor de um header no formato 'Name: Value' ou 'Name:Value'."""
    # Suporta separadores ': ' e ':'
    match = re.match(r"^([^:]+):\s*(.*)", header_str)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", ""


def _is_url(token: str) -> bool:
    """Verifica se um token parece uma URL."""
    return bool(re.match(r"https?://", token, re.IGNORECASE))


def _looks_like_json(text: str) -> bool:
    """Verifica se um texto parece ser JSON."""
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


def _fallback_tokenize(text: str) -> list[str]:
    """Tokenização de fallback para strings com aspas malformadas."""
    tokens = []
    current = ""
    in_quotes = False
    quote_char = ""

    for char in text:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = ""
        elif char == " " and not in_quotes:
            if current:
                tokens.append(current)
                current = ""
        else:
            current += char

    if current:
        tokens.append(current)

    return tokens
