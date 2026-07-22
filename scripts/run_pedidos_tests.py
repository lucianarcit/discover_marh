"""Runner de testes — APIs GET de Gestão de Pedidos.

Executa chamadas reais contra o ambiente de homologação.
Endpoints que dependem de orderNumber são encadeados: primeiro consulta /orders,
depois usa o orderNumber retornado nas chamadas dependentes.

Uso:
    python scripts/run_pedidos_tests.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.api_client import AleloApiClient
from discover_alelo.config import get_all_config, get_project_root, validate_env
from discover_alelo.models import ApiResult
from discover_alelo.response_recorder import ResponseRecorder


def main() -> None:
    root = get_project_root()

    print("=" * 60)
    print("  TESTES DE INTEGRAÇÃO - APIs GET Gestão de Pedidos")
    print("=" * 60)
    print()

    # 1. Valida ambiente
    print("1. Validando ambiente...")
    config = validate_env()
    print("   ✅ Ambiente validado.")
    print()

    # 2. Carrega inventário
    print("2. Carregando inventário de APIs...")
    inventory_path = root / "artifacts" / "api_inventory" / "gestao_pedidos_apis.json"
    if not inventory_path.exists():
        print(f"   ❌ Inventário não encontrado: {inventory_path}")
        sys.exit(1)

    operations = json.loads(inventory_path.read_text(encoding="utf-8"))
    print(f"   📋 {len(operations)} operações GET carregadas.")
    print()

    # 3. Executa testes
    print("3. Executando testes GET...")
    print("-" * 60)

    recorder = ResponseRecorder()
    base_url = config["api_base_url"].rstrip("/")
    order_number = None  # Será preenchido pelo primeiro /orders

    with AleloApiClient() as client:
        # Primeiro: /orders (para obter orderNumber para os encadeados)
        orders_ops = [op for op in operations if not op.get("needs_path_param")]
        dependent_ops = [op for op in operations if op.get("needs_path_param")]

        # Executa APIs sem dependência
        for i, op in enumerate(orders_ops, 1):
            print(f"\n   [{i}/{len(operations)}] GET {op['path']}")
            print(f"   Nome: {op['operation_name']}")

            full_url = f"{base_url}/{op['path']}"
            params = {}
            for qp in op.get("query_parameters", []):
                if qp["name"] == "page":
                    params["page"] = "0"
                elif qp["name"] == "size":
                    params["size"] = "10"

            result = client.get(
                operation_name=op["operation_name"],
                url=full_url,
                params=params if params else None,
            )
            recorder.record(result)
            _print_result(result)

            # Extrai orderNumber para os endpoints dependentes
            if (
                "orders" in op["path"]
                and not order_number
                and result.success
                and result.response_body
            ):
                order_number = _extract_order_number(result.response_body)
                if order_number:
                    print(f"      🔗 orderNumber extraído para encadeamento: {order_number}")

        # Executa APIs com dependência de orderNumber
        if order_number:
            for op in dependent_ops:
                path = op["path"].replace("{orderNumber}", str(order_number))
                print(f"\n   [{orders_ops.__len__() + dependent_ops.index(op) + 1}/{len(operations)}] GET {path}")
                print(f"   Nome: {op['operation_name']}")

                full_url = f"{base_url}/{path}"
                params = {}
                for qp in op.get("query_parameters", []):
                    if qp["name"] == "page":
                        params["page"] = "0"
                    elif qp["name"] == "size":
                        params["size"] = "10"

                result = client.get(
                    operation_name=op["operation_name"],
                    url=full_url,
                    params=params if params else None,
                )
                recorder.record(result)
                _print_result(result)
        else:
            print(f"\n   ⚠️  Nenhum orderNumber encontrado — {len(dependent_ops)} APIs dependentes não executadas.")
            for op in dependent_ops:
                result = ApiResult(
                    operation_name=op["operation_name"],
                    method="GET",
                    url=op["path"],
                    execution_status="SKIPPED_NO_SAMPLE",
                    error_message="Sem orderNumber disponível (nenhum pedido encontrado em /orders)",
                )
                recorder.record(result)

    print()
    print("-" * 60)

    # 4. Salva resultados
    print("\n4. Salvando resultados...")
    summary_path = recorder.save_summary(environment="homologacao")
    print(f"   💾 Resumo: {summary_path.relative_to(root)}")
    print(f"   📁 Pasta: {recorder.run_dir.relative_to(root)}")
    print()

    # 5. Resumo
    results = recorder.get_results()
    successes = sum(1 for r in results if r.success)
    failures = sum(1 for r in results if not r.success and r.execution_status not in ("BLOCKED_BY_AUTH", "SKIPPED_NO_SAMPLE"))
    blocked = sum(1 for r in results if r.execution_status == "BLOCKED_BY_AUTH")
    skipped = sum(1 for r in results if r.execution_status == "SKIPPED_NO_SAMPLE")

    print("=" * 60)
    print(f"  RESUMO: {successes} sucesso | {failures} falha | {blocked} auth | {skipped} sem dados")
    print("=" * 60)


def _extract_order_number(body) -> str | None:
    """Extrai o primeiro orderNumber da resposta de /orders."""
    if not isinstance(body, dict):
        return None
    content = body.get("content", [])
    if not content:
        return None
    # content[0] contém orderNumberGroup e orders[]
    first_group = content[0]
    orders = first_group.get("orders", [])
    if orders:
        return str(orders[0].get("orderNumber", ""))
    return None


def _print_result(result: ApiResult) -> None:
    """Imprime resultado formatado."""
    icons = {
        "SUCCESS": "✅",
        "HTTP_ERROR": "❌",
        "AUTH_TOKEN_INVALID": "🔐",
        "BLOCKED_BY_AUTH": "🚫",
        "TIMEOUT": "⏱️",
        "CONNECTION_ERROR": "🔌",
    }
    icon = icons.get(result.execution_status, "❓")
    print(f"   {icon} Status: {result.execution_status}", end="")
    if result.status_code:
        print(f" (HTTP {result.status_code})", end="")
    if result.duration_ms:
        print(f" [{result.duration_ms}ms]", end="")
    print()

    if result.success and result.response_body:
        body = result.response_body
        if isinstance(body, dict):
            total = body.get("total", "?")
            keys = list(body.keys())[:5]
            print(f"      📊 Campos: {keys} | Total: {total}")
        elif isinstance(body, list):
            print(f"      📊 Lista com {len(body)} itens")
    elif result.error_message:
        print(f"      Detalhe: {result.error_message[:80]}")


if __name__ == "__main__":
    main()
