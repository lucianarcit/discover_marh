"""Funções auxiliares para o notebook de validação RAG — Fase 3.

Todas as funções são puras e testáveis independentemente do notebook.
Nenhuma função acessa AWS, modifica arquivos de artefatos ou lê segredos.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# ──────────────────────────────────────────────────────────────
# Carregamento de artefatos
# ──────────────────────────────────────────────────────────────

ARTIFACTS_DIR = Path(__file__).parent.parent / "phase_3_e2e_gate" / "artifacts"

_SENSITIVE_PATTERNS = [
    (r"\b\d{12}\b", "<ACCOUNT_ID>"),
    (r"arn:[^\s\"',]+", "<ARN>"),
    (r"s3://[^\s\"',]+", "<S3_URI>"),
    (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<ID>"),
]


def load_artifact(filename: str, artifacts_dir: Path | None = None) -> dict | list | None:
    """Carrega um artefato JSON do diretório de artefatos do gate.

    Args:
        filename: Nome do arquivo JSON (ex: "gate_summary.json").
        artifacts_dir: Diretório alternativo (para testes).

    Returns:
        Conteúdo parseado ou None se o arquivo não existir.
    """
    base = artifacts_dir or ARTIFACTS_DIR
    path = base / filename
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def mask_sensitive(value: str) -> str:
    """Remove Account IDs, ARNs, URIs S3 e UUIDs de uma string.

    Args:
        value: String possivelmente contendo dados sensíveis.

    Returns:
        String com dados sensíveis substituídos por marcadores.
    """
    result = str(value)
    for pattern, replacement in _SENSITIVE_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


# ──────────────────────────────────────────────────────────────
# Validação de campos obrigatórios
# ──────────────────────────────────────────────────────────────


def validate_artifact(data: dict | None, required_fields: list[str], name: str) -> list[str]:
    """Valida que um artefato contém todos os campos obrigatórios.

    Args:
        data: Dicionário do artefato carregado.
        required_fields: Lista de chaves obrigatórias.
        name: Nome do artefato (para mensagens de erro).

    Returns:
        Lista de campos ausentes. Vazia se todos presentes.
    """
    if data is None:
        return [f"Artefato '{name}' não encontrado."]
    missing = [f for f in required_fields if f not in data]
    return [f"Campo ausente em '{name}': '{m}'" for m in missing]


def check_field_value(
    data: dict,
    field: str,
    expected: Any,
    name: str,
) -> str | None:
    """Verifica que um campo tem o valor esperado.

    Args:
        data: Dicionário do artefato.
        field: Chave a verificar.
        expected: Valor esperado.
        name: Nome do artefato (para mensagens).

    Returns:
        Mensagem de erro ou None se correto.
    """
    actual = data.get(field)
    if actual != expected:
        return f"'{name}.{field}': esperado={expected!r}, obtido={actual!r}"
    return None


# ──────────────────────────────────────────────────────────────
# Métricas de threshold
# ──────────────────────────────────────────────────────────────


def compute_threshold_metrics(
    pos_top_scores: list[float],
    neg_top_scores: list[float],
    thresholds: list[float],
) -> list[dict]:
    """Calcula TP, FN, TN, FP e métricas derivadas por threshold (query-level).

    Unidade: uma consulta é aprovada quando top_score >= threshold.

    Args:
        pos_top_scores: top_score de cada consulta positiva.
        neg_top_scores: top_score de cada consulta negativa.
        thresholds: Lista de thresholds a comparar.

    Returns:
        Lista de dicts com threshold e métricas calculadas.
    """
    rows = []
    for t in thresholds:
        tp = sum(1 for s in pos_top_scores if s >= t)
        fn = sum(1 for s in pos_top_scores if s < t)
        tn = sum(1 for s in neg_top_scores if s < t)
        fp = sum(1 for s in neg_top_scores if s >= t)
        precision   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall      = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1          = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        bal_acc     = (recall + specificity) / 2
        rows.append({
            "threshold": t,
            "TP": tp, "FN": fn, "TN": tn, "FP": fp,
            "precision":          round(precision, 4),
            "recall":             round(recall, 4),
            "specificity":        round(specificity, 4),
            "F1":                 round(f1, 4),
            "balanced_accuracy":  round(bal_acc, 4),
        })
    return rows


def extract_top_scores(retrieve_scores: dict) -> tuple[list[float], list[float]]:
    """Extrai top_score por consulta dos artefatos do Retrieve.

    Args:
        retrieve_scores: Conteúdo de retrieve_scores.json.

    Returns:
        (pos_top_scores, neg_top_scores)
    """
    pos = [
        c["max_score"]
        for c in retrieve_scores.get("positive_cases", [])
        if c.get("max_score") is not None
    ]
    neg = [
        c["max_score"]
        for c in retrieve_scores.get("negative_cases", [])
        if c.get("max_score") is not None
    ]
    return pos, neg


# ──────────────────────────────────────────────────────────────
# Formatação de tabelas e cartões
# ──────────────────────────────────────────────────────────────


def pass_fail_badge(passed: bool, label: str = "") -> str:
    """Gera HTML de badge PASS/FAIL para exibição no notebook.

    Args:
        passed: True para PASS, False para FAIL.
        label: Texto adicional ao lado do badge.

    Returns:
        String HTML do badge.
    """
    color  = "#27ae60" if passed else "#e74c3c"
    text   = "PASS" if passed else "FAIL"
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:4px;font-weight:bold;font-family:monospace">{text}</span>'
        + (f" <span>{label}</span>" if label else "")
    )


def format_metrics_table(rows: list[dict], highlight_threshold: float | None = None) -> str:
    """Formata a tabela de métricas como HTML.

    Args:
        rows: Lista de dicts de métricas (saída de compute_threshold_metrics).
        highlight_threshold: Threshold a destacar em negrito.

    Returns:
        String HTML da tabela.
    """
    headers = ["threshold", "TP", "FN", "TN", "FP", "recall", "F1", "balanced_accuracy"]
    th_row = "".join(
        f"<th style='padding:6px 12px;background:#2c3e50;color:white'>{h}</th>"
        for h in headers
    )
    body_rows = []
    for row in rows:
        is_highlight = row["threshold"] == highlight_threshold
        bg = "#eafaf1" if is_highlight else "white"
        weight = "bold" if is_highlight else "normal"
        cells = "".join(
            f"<td style='padding:6px 12px;font-weight:{weight}'>{row.get(h, '')}</td>"
            for h in headers
        )
        body_rows.append(
            f"<tr style='background:{bg}'>{cells}</tr>"
        )
    body = "".join(body_rows)
    return (
        f"<table style='border-collapse:collapse;width:100%'>"
        f"<thead><tr>{th_row}</tr></thead>"
        f"<tbody>{body}</tbody>"
        f"</table>"
    )


def smoke_case_html(case: dict) -> str:
    """Formata um caso do smoke como HTML para exibição no notebook.

    Args:
        case: Dict de um caso do smoke (pipeline_smoke.json).

    Returns:
        String HTML do card do caso.
    """
    found = case.get("found", False)
    topic = case.get("topic", "-")
    badge = pass_fail_badge(found, "")
    items = []
    for key in ("found", "flow_detail", "data_classification", "approved_chunks",
                "content_len", "reason", "duration_ms"):
        val = case.get(key)
        if val is not None:
            items.append(f"<li><b>{key}:</b> {val}</li>")
    list_html = "<ul>" + "".join(items) + "</ul>"
    return (
        f"<div style='border:1px solid #bdc3c7;border-radius:6px;padding:12px;"
        f"margin:8px 0;background:#fdfefe'>"
        f"<b>{topic}</b> {badge}"
        f"{list_html}</div>"
    )
