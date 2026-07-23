"""Mapeamento determinístico de status de pedido.

Carrega o catálogo de status do Discovery e provê:
- api_status canônico
- aliases de entrada do usuário
- display labels (completed / not_completed)

Regras:
- INVOICE e CANCEL_PROCESSING não possuem aliases (pendentes).
- Palavras ambíguas isoladas não classificam status.
- Lookup determinístico — sem LLM.
"""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class StatusEntry:
    api_status: str
    label_completed: str | None
    label_not_completed: str | None
    input_aliases: list[str]


_CATALOG_PATH = (
    Path(__file__).resolve().parents[4]
    / "fixtures"
    / "order_status_catalog.json"
)

_STATUS_ENTRIES: list[StatusEntry] = []
_ALIAS_MAP: dict[str, str] = {}


def _load_catalog() -> None:
    global _STATUS_ENTRIES, _ALIAS_MAP

    if _STATUS_ENTRIES:
        return

    # Catálogo inline para não depender de arquivo externo na POC
    raw_statuses = [
        {
            "api_status": "IN_PROCESSING",
            "completed": {"label": "Em Processamento"},
            "not_completed": {"label": "Aguardando Processamento"},
            "input_aliases": ["em processamento", "processando", "em andamento"],
        },
        {
            "api_status": "PENDING",
            "completed": {"label": "Pedido criado"},
            "not_completed": {"label": "Em processamento"},
            "input_aliases": ["pendente", "aguardando", "na fila"],
        },
        {
            "api_status": "PAID",
            "completed": {"label": "Pagamento confirmado"},
            "not_completed": {"label": "Aguardando pagamento"},
            "input_aliases": ["pago", "foi pago", "pagamento realizado"],
        },
        {
            "api_status": "CREDITED",
            "completed": {"label": "Pedido creditado"},
            "not_completed": {"label": "Aguardando disponibilização"},
            "input_aliases": ["creditado", "crédito realizado", "saldo creditado"],
        },
        {
            "api_status": "CANCELLED",
            "completed": {"label": "Pedido cancelado"},
            "not_completed": {"label": None},
            "input_aliases": ["cancelado", "cancelamento", "anulado"],
        },
        {
            "api_status": "REJECTED",
            "completed": {"label": "Pedido rejeitado"},
            "not_completed": {"label": None},
            "input_aliases": ["rejeitado", "rejeição", "recusado"],
        },
        {
            "api_status": "INVOICE",
            "completed": {"label": "Nota fiscal emitida"},
            "not_completed": {"label": "Aguardando emissão de nota fiscal"},
            "input_aliases": [],
        },
        {
            "api_status": "RELEASED",
            "completed": {"label": "Pedido liberado"},
            "not_completed": {"label": "Aguardando data de liberação"},
            "input_aliases": ["liberado", "desbloqueado", "disponível"],
        },
        {
            "api_status": "IN_BILLING_PROCESSING",
            "completed": {"label": "Cobrança gerada"},
            "not_completed": {"label": "Aguardando geração de cobrança"},
            "input_aliases": ["em faturamento", "processando fatura"],
        },
        {
            "api_status": "CANCEL_PROCESSING",
            "completed": {"label": "Cancelamento em proc."},
            "not_completed": {"label": "Aguardando cancelamento"},
            "input_aliases": [],
        },
        {
            "api_status": "REFUNDED",
            "completed": {"label": "Processado"},
            "not_completed": {"label": "Aguardando estorno"},
            "input_aliases": ["reembolsado", "reembolso", "dinheiro devolvido"],
        },
        {
            "api_status": "PARTIAL_REFUNDED",
            "completed": {"label": None},
            "not_completed": {"label": "Processado parcialmente"},
            "input_aliases": ["reembolso parcial", "parcialmente reembolsado"],
        },
    ]

    for item in raw_statuses:
        entry = StatusEntry(
            api_status=item["api_status"],
            label_completed=item["completed"].get("label"),
            label_not_completed=item["not_completed"].get("label"),
            input_aliases=item["input_aliases"],
        )
        _STATUS_ENTRIES.append(entry)
        for alias in entry.input_aliases:
            _ALIAS_MAP[alias.lower()] = entry.api_status


_load_catalog()


def resolve_status_from_input(user_text: str) -> str | None:
    """Resolve um alias de status para o api_status canônico.

    Retorna None se não reconhecido — exige contexto de pedido/status
    no chamador antes de invocar esta função.
    """
    normalized = user_text.strip().lower()
    # Direct match
    if normalized in _ALIAS_MAP:
        return _ALIAS_MAP[normalized]
    # Try without trailing 's' (plural)
    if normalized.endswith("s") and normalized[:-1] in _ALIAS_MAP:
        return _ALIAS_MAP[normalized[:-1]]
    # Try without trailing 'os' (plural pt-BR)
    if normalized.endswith("os") and normalized[:-2] + "o" in _ALIAS_MAP:
        return _ALIAS_MAP[normalized[:-2] + "o"]
    return None


def get_display_label(api_status: str) -> str:
    """Retorna o label de exibição (completed) para um status."""
    for entry in _STATUS_ENTRIES:
        if entry.api_status == api_status:
            return entry.label_completed or entry.api_status
    return api_status


def get_all_entries() -> list[StatusEntry]:
    return list(_STATUS_ENTRIES)
