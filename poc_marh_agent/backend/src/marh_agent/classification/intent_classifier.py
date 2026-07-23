"""Classificador determinístico de intenções — sem LLM.

Usa regex e keywords do catálogo real de intenções (27 intents).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from marh_agent.classification.entity_extractor import (
    extract_cpf,
    extract_order_number,
)
from marh_agent.classification.status_mapper import resolve_status_from_input


@dataclass
class ClassificationResult:
    intent_id: str
    flow: str
    entities: dict


# Padrões para intenções FORA DO ESCOPO (Grupo C)
_TRANSACTIONAL_PATTERNS = [
    (r"cancel[ae]", "INT-022"),
    (r"alter[ae]|muda|trocar?\s.*(endere[çc]o|dados)", "INT-023"),
    (r"cri[ae]r?\s.*pedido|novo\s+pedido|fazer\s.*pedido", "INT-024"),
    (r"remov|exclu|delet", "INT-025"),
    (r"pag[aue]r?\s.*pedido|realizar\s+pagamento", "INT-026"),
    (r"emitir?\s.*cart[aã]o|segunda\s+via|reemitir", "INT-027"),
]

# Padrões para troca de empresa
_COMPANY_SWITCH_PATTERNS = [
    r"troc|outra\s+empresa|use\s+.*empresa",
    r"cnpj\s*\d",
    r"consulte?\s+.*(cnpj|empresa)",
]

# Padrões para intenções INFORMATIVAS (Grupo B)
_INFORMATIVE_PATTERNS = [
    (r"o\s+que\s+(posso|consigo)\s+fazer", "INT-008"),
    (r"quais?\s+informa[çc][õo]es?\s+(posso|consigo)\s+consultar", "INT-009"),
    (r"como\s+(fa[çc]o|posso)\s+(para\s+)?(fazer|criar)\s+.*pedido", "INT-010"),
    (r"como\s+(fa[çc]o|posso)\s+(para\s+)?consultar\s+.*pedido", "INT-011"),
    (r"como\s+(fa[çc]o|posso)\s+(para\s+)?consultar\s+.*colaborador", "INT-012"),
    (r"consigo\s+rastrear", "INT-013"),
    (r"(voc[êe]|agente)\s+(consegue|pode)\s+cancelar", "INT-014"),
    (r"(voc[êe]|agente)\s+(consegue|pode)\s+alterar.*colaborador", "INT-015"),
    (r"(consulta|acessa)\s+(dados\s+de\s+)?qualquer\s+empresa", "INT-016"),
    (r"preciso\s+selecionar\s+.*empresa", "INT-017"),
    (r"(agente|voc[êe])\s+substitu[ie].*portal", "INT-018"),
    (r"o\s+que\s+[eé]\s+o?\s*marh", "INT-019"),
    (r"o\s+que\s+[eé]\s+o?\s*espa[çc]o\s+rh", "INT-020"),
    (r"quais?\s+(tipos?\s+de\s+)?perguntas?\s+(posso|consigo)", "INT-021"),
]

# Padrões para rastreamento
_TRACKING_BY_CPF_PATTERNS = [
    r"rastr(ear|eamento|eio).*cpf",
    r"rastr(ear|eamento|eio).*colaborador.*\d{3}",
    r"rastr(ear|eamento|eio).*(cart[aã]o|cartões).*cpf",
]

_TRACKING_BY_ORDER_PATTERNS = [
    r"rastr(ear|eamento|eio).*pedido",
    r"rastr(ear|eamento|eio).*cart[aã]o.*pedido",
]

# Padrões para pedidos por status
_ORDER_STATUS_PATTERNS = [
    r"pedidos?\s+(com\s+status\s+|)(\w+)",
    r"(mostrar?|quais?|listar?)\s+.*pedidos?\s+(\w+)",
]


def classify(message: str) -> ClassificationResult:
    """Classifica a mensagem do usuário em uma intenção."""
    text = message.strip().lower()

    # 1. Troca de empresa
    for pattern in _COMPANY_SWITCH_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return ClassificationResult(
                intent_id="COMPANY_SWITCH",
                flow="STATIC_RESPONSE",
                entities={},
            )

    # 2. Ações transacionais (Grupo C)
    for pattern, intent_id in _TRANSACTIONAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return ClassificationResult(
                intent_id=intent_id,
                flow="REDIRECT_TO_OFFICIAL_JOURNEY",
                entities={},
            )

    # 3. Informativas (Grupo B)
    for pattern, intent_id in _INFORMATIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return ClassificationResult(
                intent_id=intent_id,
                flow="RAG_ONLY",
                entities={},
            )

    # 4. Rastreamento por CPF (INT-006)
    for pattern in _TRACKING_BY_CPF_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return ClassificationResult(
                intent_id="INT-006",
                flow="REQUIRES_CLARIFICATION",
                entities={},
            )

    # 5. Rastreamento por pedido (INT-007)
    for pattern in _TRACKING_BY_ORDER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            order_number = extract_order_number(text)
            return ClassificationResult(
                intent_id="INT-007",
                flow="API_ONLY",
                entities={"order_number": order_number},
            )

    # 6. Último pedido (INT-004)
    if re.search(r"[uú]ltimo\s+pedido|pedido\s+mais\s+recente", text):
        return ClassificationResult(
            intent_id="INT-004",
            flow="API_ONLY",
            entities={},
        )

    # 7. Pedido por número (INT-003)
    order_number = extract_order_number(text)
    if order_number and re.search(r"pedido", text):
        return ClassificationResult(
            intent_id="INT-003",
            flow="API_ONLY",
            entities={"order_number": order_number},
        )

    # 8. Pedidos por status (INT-005)
    if re.search(r"pedidos?", text):
        # Tenta extrair status
        for alias_candidate in _extract_status_candidates(text):
            resolved = resolve_status_from_input(alias_candidate)
            if resolved:
                return ClassificationResult(
                    intent_id="INT-005",
                    flow="API_ONLY",
                    entities={"status": resolved, "status_alias": alias_candidate},
                )
        # Se menciona pedido mas sem status reconhecido e sem número
        if not order_number:
            # Pode ser pedidos por status com alias não reconhecido
            status_words = _extract_status_candidates(text)
            if status_words:
                return ClassificationResult(
                    intent_id="INT-005",
                    flow="API_ONLY",
                    entities={"status": None, "unrecognized_alias": status_words[0]},
                )

    # 9. Colaborador por CPF (INT-002)
    cpf = extract_cpf(text)
    if cpf:
        return ClassificationResult(
            intent_id="INT-002",
            flow="API_ONLY",
            entities={"cpf": cpf},
        )

    # 10. Colaborador por nome (INT-001)
    if re.search(r"colaborador|buscar|encontr|consultar", text):
        name_keywords = [
            "consultar", "buscar", "encontrar", "encontre",
            "colaborador", "colaboradora", "pelo nome", "por nome",
        ]
        from marh_agent.classification.entity_extractor import extract_name
        name = extract_name(message, name_keywords)
        if name:
            return ClassificationResult(
                intent_id="INT-001",
                flow="API_ONLY",
                entities={"name": name},
            )

    # 11. Fora do escopo — não entendido
    return ClassificationResult(
        intent_id="OUT_OF_SCOPE",
        flow="STATIC_RESPONSE",
        entities={},
    )


def _extract_status_candidates(text: str) -> list[str]:
    """Extrai candidatos a status da mensagem."""
    candidates = []
    # Remove palavras comuns
    cleaned = re.sub(
        r"\b(pedidos?|com|status|mostrar?|quais?|são|os|últimos|listar?|"
        r"meus|da|de|do|no|em|que|estão)\b",
        "",
        text,
    )
    words = cleaned.strip().split()
    # Multi-word aliases
    multi_word_candidates = [
        "em processamento", "em andamento", "na fila",
        "foi pago", "pagamento realizado",
        "crédito realizado", "saldo creditado",
        "reembolso parcial", "parcialmente reembolsado",
        "em faturamento", "processando fatura",
        "dinheiro devolvido",
    ]
    for mw in multi_word_candidates:
        if mw in text:
            candidates.append(mw)

    # Single-word candidates
    for w in words:
        w = w.strip(" .,;:!?")
        if len(w) >= 3:
            candidates.append(w)

    return candidates
