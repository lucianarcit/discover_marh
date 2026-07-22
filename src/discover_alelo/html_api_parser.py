"""Parser de documentação HTML de APIs do cliente.

Analisa arquivos HTML gerados pela documentação Alelo e extrai
operações de API com todos os seus componentes.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from .models import ApiOperation


def parse_html_file(filepath: str | Path) -> list[ApiOperation]:
    """Lê um arquivo HTML de documentação e extrai todas as operações de API.

    Args:
        filepath: Caminho para o arquivo HTML.

    Returns:
        Lista de operações de API encontradas.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo HTML não encontrado: {path.resolve()}")

    content = path.read_text(encoding="utf-8")
    return parse_html_string(content)


def parse_html_string(html_content: str) -> list[ApiOperation]:
    """Analisa uma string HTML e extrai operações de API."""
    soup = BeautifulSoup(html_content, "html.parser")
    operations: list[ApiOperation] = []

    # Busca seções de documentação
    sections = soup.find_all("article", class_="doc-section")

    for section in sections:
        op = _parse_section(section)
        if op and op.method:
            operations.append(op)

    return operations


def _parse_section(section) -> ApiOperation | None:
    """Extrai uma operação de API de uma seção HTML."""
    op = ApiOperation()

    # Nome da operação (do heading)
    heading = section.find("h2")
    if heading:
        op.operation_name = heading.get_text(strip=True)

    # Fonte da seção
    section_ref = section.find("p", class_=None)
    heading_div = section.find("div", class_="section-heading")
    if heading_div:
        p_tag = heading_div.find("p")
        if p_tag:
            op.source_section = p_tag.get_text(strip=True)

    # Data-search contém metadados úteis
    data_search = section.get("data-search", "")

    # Conteúdo markdown
    markdown_div = section.find("div", class_="markdown")
    if not markdown_div:
        return None

    # Extrai blocos de código
    code_blocks = markdown_div.find_all("pre")
    code_texts = [_decode_html_entities(cb.get_text()) for cb in code_blocks]

    # Processa request (primeiro bloco de código tipicamente)
    _extract_request_info(op, code_texts, data_search)

    # Extrai headers da documentação
    _extract_headers(op, code_texts)

    # Extrai query parameters de tabelas
    _extract_query_params(op, markdown_div)

    # Extrai response examples
    _extract_response(op, code_texts, markdown_div)

    # Extrai status codes
    _extract_status_codes(op, markdown_div)

    # Determina segurança de execução
    _assess_safety(op)

    return op


def _extract_request_info(
    op: ApiOperation, code_texts: list[str], data_search: str
) -> None:
    """Extrai método, path e body do request."""
    for text in code_texts:
        lines = text.strip().split("\n")
        first_line = lines[0].strip()

        # Detecta padrão "METHOD /path" ou "METHOD path"
        method_match = re.match(
            r"^(GET|POST|PUT|PATCH|DELETE)\s+(.+?)$",
            first_line,
            re.IGNORECASE,
        )
        if method_match and not op.method:
            op.method = method_match.group(1).upper()
            path = method_match.group(2).strip()
            op.path = path

            # Extrai path parameters
            path_params = re.findall(r"\{(\w+)\}", path)
            op.path_parameters = path_params

            # Tenta extrair body JSON do mesmo bloco
            remaining = "\n".join(lines[1:]).strip()
            if remaining and _looks_like_json(remaining):
                try:
                    # Remove comentários do JSON (// ...)
                    clean_json = re.sub(r"//[^\n]*", "", remaining)
                    # Remove trailing commas
                    clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)
                    op.request_body_example = json.loads(clean_json)
                except json.JSONDecodeError:
                    op.request_body_example = remaining
            break

    # Se não encontrou no código, tenta no data-search
    if not op.method:
        method_match = re.search(
            r"\b(GET|POST|PUT|PATCH|DELETE)\b",
            data_search,
            re.IGNORECASE,
        )
        if method_match:
            op.method = method_match.group(1).upper()


def _extract_headers(op: ApiOperation, code_texts: list[str]) -> None:
    """Extrai headers obrigatórios da documentação."""
    for text in code_texts:
        lines = text.strip().split("\n")
        # Detecta bloco de headers (linhas com "=" ou ":")
        header_lines = [
            line
            for line in lines
            if re.match(r"^[\w\-_]+\s*[=:]\s*.+", line.strip())
            and not line.strip().startswith("{")
            and not line.strip().startswith('"')
        ]

        if len(header_lines) >= 3:  # Provavelmente é um bloco de headers
            for line in header_lines:
                match = re.match(r"^([\w\-_]+)\s*[=:]\s*(.+)", line.strip())
                if match:
                    header_name = match.group(1).strip()
                    op.required_headers.append(header_name)


def _extract_query_params(op: ApiOperation, markdown_div) -> None:
    """Extrai query parameters de tabelas HTML."""
    tables = markdown_div.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:  # Pula header
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                param_name = cells[0].get_text(strip=True)
                param_desc = cells[1].get_text(strip=True)
                if param_name and not param_name.startswith("---"):
                    op.query_parameters.append(
                        {"name": param_name, "description": param_desc}
                    )


def _extract_response(
    op: ApiOperation, code_texts: list[str], markdown_div
) -> None:
    """Extrai exemplos de resposta da documentação."""
    # Procura o bloco JSON que aparece depois de "Response" ou "response"
    found_response_section = False

    for text in code_texts:
        stripped = text.strip()
        # Pula blocos que são requests ou headers
        if re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+", stripped, re.IGNORECASE):
            continue
        if re.match(r"^(Authorization|APP_VERSION|client_id)", stripped):
            continue

        # Verifica se parece um JSON de resposta
        if _looks_like_json(stripped):
            try:
                clean = re.sub(r"//[^\n]*", "", stripped)
                clean = re.sub(r",\s*([}\]])", r"\1", clean)
                parsed = json.loads(clean)
                # Se já temos body de request, este provavelmente é response
                if op.request_body_example or not op.documented_response_example:
                    # Se o JSON tem "total" e "content", é provavelmente um response
                    if isinstance(parsed, dict) and (
                        "total" in parsed
                        or "content" in parsed
                        or "id" in parsed
                    ):
                        op.documented_response_example = parsed
                    elif op.request_body_example and parsed != op.request_body_example:
                        # Se é diferente do body de request, pode ser response
                        if not op.documented_response_example:
                            op.documented_response_example = parsed
            except json.JSONDecodeError:
                pass


def _extract_status_codes(op: ApiOperation, markdown_div) -> None:
    """Extrai status codes documentados."""
    text = markdown_div.get_text()

    # Busca padrões como "✅ 200 - Sucesso" ou "❌ 403 - Sem permissão"
    status_patterns = re.findall(
        r"[✅❌]\s*(\d{3})\s*[-–]\s*(.+?)(?:\n|$)", text
    )
    for code, description in status_patterns:
        op.documented_status_codes.append(
            {"code": code, "description": description.strip()}
        )


def _assess_safety(op: ApiOperation) -> None:
    """Determina se é seguro executar a operação automaticamente."""
    if op.method != "GET":
        op.safe_to_execute = False
        op.safety_reason = (
            f"Método {op.method} removido do escopo. Somente GET é executado."
        )
    else:
        op.safe_to_execute = True
        op.safety_reason = "Operação de consulta (GET) segura para execução."


def _decode_html_entities(text: str) -> str:
    """Decodifica entidades HTML como &quot; para aspas."""
    return html.unescape(text)


def _looks_like_json(text: str) -> bool:
    """Verifica se um texto parece ser JSON."""
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


def operations_to_json(operations: list[ApiOperation]) -> list[dict[str, Any]]:
    """Converte lista de operações para formato JSON serializável."""
    return [op.to_dict() for op in operations]
