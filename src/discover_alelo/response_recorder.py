"""Registrador de respostas de API.

Salva resultados sanitizados em artifacts/api_runs/<timestamp>/
e opcionalmente respostas brutas em .local/api_runs/ para debug.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import get_project_root
from .models import ApiResult, ExecutionSummary
from .sanitization import sanitize


def _get_run_dir() -> Path:
    """Cria e retorna o diretório da execução atual."""
    root = get_project_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = root / "artifacts" / "api_runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "individual").mkdir(exist_ok=True)
    return run_dir


def _get_local_run_dir() -> Path:
    """Cria diretório local para respostas brutas (não versionado)."""
    root = get_project_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_dir = root / ".local" / "api_runs" / timestamp
    local_dir.mkdir(parents=True, exist_ok=True)

    # Cria aviso de conteúdo sensível
    warning_file = local_dir / "WARNING_SENSITIVE_DATA.txt"
    if not warning_file.exists():
        warning_file.write_text(
            "⚠️  ATENÇÃO: Esta pasta contém respostas brutas de API com dados sensíveis.\n"
            "NÃO versione este conteúdo no Git.\n"
            "Esta pasta existe apenas para depuração local.\n",
            encoding="utf-8",
        )

    return local_dir


class ResponseRecorder:
    """Registra resultados de execução de APIs."""

    def __init__(self) -> None:
        self._run_dir = _get_run_dir()
        self._local_dir = _get_local_run_dir()
        self._results: list[ApiResult] = []

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def record(self, result: ApiResult) -> None:
        """Registra um resultado de API."""
        self._results.append(result)

        # Salva individual sanitizado
        slug = _slugify(result.operation_name or f"op_{len(self._results)}")
        individual_path = self._run_dir / "individual" / f"{slug}.json"
        sanitized = sanitize(result.to_dict())
        individual_path.write_text(
            json.dumps(sanitized, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Salva bruto localmente (para debug)
        local_path = self._local_dir / f"{slug}_raw.json"
        local_path.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save_summary(self, environment: str = "homologacao") -> Path:
        """Gera e salva o resumo da execução.

        Returns:
            Caminho do arquivo de resumo.
        """
        summary = ExecutionSummary(
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=environment,
            total_operations=len(self._results),
            successes=sum(1 for r in self._results if r.success),
            failures=sum(
                1
                for r in self._results
                if not r.success
                and r.execution_status not in ("SKIPPED_SAFETY", "SKIPPED_NO_SAMPLE")
            ),
            skipped_safety=sum(
                1 for r in self._results if r.execution_status == "SKIPPED_SAFETY"
            ),
            skipped_no_sample=sum(
                1 for r in self._results if r.execution_status == "SKIPPED_NO_SAMPLE"
            ),
            status_codes_found=[
                r.status_code for r in self._results if r.status_code > 0
            ],
            total_duration_ms=sum(r.duration_ms for r in self._results),
        )

        # Salva execution_summary.json
        summary_path = self._run_dir / "execution_summary.json"
        summary_path.write_text(
            json.dumps(summary.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Salva sanitized_responses.json
        all_sanitized = [sanitize(r.to_dict()) for r in self._results]
        responses_path = self._run_dir / "sanitized_responses.json"
        responses_path.write_text(
            json.dumps(all_sanitized, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Gera schemas.json
        schemas = _extract_schemas(self._results)
        schemas_path = self._run_dir / "schemas.json"
        schemas_path.write_text(
            json.dumps(schemas, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return summary_path

    def get_results(self) -> list[ApiResult]:
        """Retorna todos os resultados registrados."""
        return self._results.copy()


def _extract_schemas(results: list[ApiResult]) -> dict[str, Any]:
    """Extrai schemas observados das respostas."""
    schemas: dict[str, Any] = {}

    for result in results:
        if result.response_body and isinstance(result.response_body, dict):
            schema = _infer_schema(result.response_body)
            schemas[result.operation_name or "unknown"] = {
                "status_code": result.status_code,
                "fields": schema,
            }

    return schemas


def _infer_schema(data: Any, max_depth: int = 5) -> Any:
    """Infere o schema de um objeto JSON recursivamente."""
    if max_depth <= 0:
        return {"type": type(data).__name__}

    if isinstance(data, dict):
        return {
            key: _infer_schema(value, max_depth - 1) for key, value in data.items()
        }
    elif isinstance(data, list):
        if data:
            return {"type": "array", "item_schema": _infer_schema(data[0], max_depth - 1), "length": len(data)}
        return {"type": "array", "item_schema": None, "length": 0}
    elif data is None:
        return {"type": "null"}
    else:
        return {"type": type(data).__name__, "sample_length": len(str(data)) if isinstance(data, str) else None}


def _slugify(text: str) -> str:
    """Converte texto para slug seguro para nomes de arquivo."""
    import re

    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s]+", "_", slug)
    slug = slug.strip("_")
    return slug[:80] or "unnamed"
