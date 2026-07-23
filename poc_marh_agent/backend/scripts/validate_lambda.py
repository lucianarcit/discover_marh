"""Validação local do Lambda handler — 11 mensagens do HANDOFF (seção 7).

Simula eventos do API Gateway e valida que as respostas estão corretas.
Roda sem AWS, sem rede, só com mocks.

Uso:
    cd poc_marh_agent/backend
    python scripts/validate_lambda.py
"""

from __future__ import annotations

import json
import sys

# Garante que o src está no path
sys.path.insert(0, "src")

from marh_agent.api.lambda_handler import lambda_handler  # noqa: E402


def _make_event(message: str) -> dict:
    """Cria evento no formato API Gateway proxy integration."""
    return {
        "httpMethod": "POST",
        "body": json.dumps({
            "company_id": "empresa-sintetica-001",
            "user_id": "usuario-sintetico-001",
            "session_id": "sessao-sintetica-001",
            "message": message,
            "environment": "HML",
        }),
    }


# 11 mensagens de validação do HANDOFF
VALIDATION_CASES = [
    {
        "message": "O que posso fazer?",
        "expected_intent": "INT-008",
        "expected_variant": "capabilities_list",
    },
    {
        "message": "Consultar colaborador Pessoa Colaboradora A",
        "expected_intent": "INT-001",
        "expected_variant": "collaborator_summary",
    },
    {
        "message": "Consultar CPF 000.000.000-00",
        "expected_intent": "INT-002",
        "expected_variant": "collaborator_summary",
    },
    {
        "message": "Consultar pedido 342671",
        "expected_intent": "INT-003",
        "expected_variant": "order_summary",
    },
    {
        "message": "Qual foi o último pedido?",
        "expected_intent": "INT-004",
        "expected_variant": "order_summary",
    },
    {
        "message": "Pedidos com status pago",
        "expected_intent": "INT-005",
        "expected_variant": "order_list",
    },
    {
        "message": "Rastrear cartões pelo CPF",
        "expected_intent": "INT-006",
        "expected_variant": "clarification",
    },
    {
        "message": "Rastrear pedido 342671",
        "expected_intent": "INT-007",
        "expected_variant": "warning_notice",
    },
    {
        "message": "Cancele o pedido 342671",
        "expected_intent": "INT-022",
        "expected_variant": "transactional_redirect",
    },
    {
        "message": "Troque para outra empresa",
        "expected_intent": None,  # Router retorna intent_id=None para COMPANY_SWITCH
        "expected_variant": "informational_notice",
    },
    {
        "message": "O que é o MARH?",
        "expected_intent": "INT-019",
        "expected_variant": "knowledge_answer",
    },
]


def main():
    print("=" * 60)
    print("VALIDAÇÃO LOCAL — Lambda Handler (11 mensagens)")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for i, case in enumerate(VALIDATION_CASES, 1):
        event = _make_event(case["message"])
        response = lambda_handler(event, None)

        status_code = response["statusCode"]
        body = json.loads(response["body"])

        intent_ok = body.get("intent_id") == case["expected_intent"]
        variant_ok = (
            body.get("presentation", {}) or {}
        ).get("variant") == case["expected_variant"]
        message_present = bool(body.get("message"))
        status_ok = status_code == 200

        all_ok = intent_ok and variant_ok and message_present and status_ok

        icon = "✅" if all_ok else "❌"
        print(f"  {icon} [{i:02d}] \"{case['message']}\"")

        if not all_ok:
            failed += 1
            if not status_ok:
                print(f"       Status: {status_code} (esperado 200)")
            if not intent_ok:
                print(f"       Intent: {body.get('intent_id')} (esperado {case['expected_intent']})")
            if not variant_ok:
                actual_variant = (body.get("presentation", {}) or {}).get("variant")
                print(f"       Variant: {actual_variant} (esperado {case['expected_variant']})")
            if not message_present:
                print(f"       Message: AUSENTE")
        else:
            passed += 1

    print()
    print("-" * 60)
    print(f"  Resultado: {passed}/{len(VALIDATION_CASES)} passaram")
    if failed:
        print(f"  ⚠️  {failed} falharam")
        sys.exit(1)
    else:
        print("  🎉 Todas as validações passaram!")
        sys.exit(0)


if __name__ == "__main__":
    main()
