"""Runner de testes de integração — SOMENTE operações GET.

Executa chamadas reais contra o ambiente de homologação.
Apenas APIs de consulta (GET) são testadas.

Uso:
    python scripts/run_api_tests.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.api_client import AleloApiClient
from discover_alelo.config import get_all_config, get_project_root, validate_env
from discover_alelo.models import ApiResult
from discover_alelo.response_recorder import ResponseRecorder


def main() -> None:
    root = get_project_root()

    print("=" * 60)
    print("  TESTES DE INTEGRAÇÃO - APIs GET (Consulta)")
    print("=" * 60)
    print()

    # 1. Valida ambiente
    print("1. Validando ambiente...")
    config = validate_env()
    print("   ✅ Ambiente validado.")
    print()

    # 2. Carrega inventário e filtra apenas GETs
    print("2. Carregando inventário de APIs...")
    inventory_path = root / "artifacts" / "api_inventory" / "gestao_colaboradores_apis.json"
    if not inventory_path.exists():
        print(f"   ❌ Inventário não encontrado: {inventory_path}")
        print("   Execute primeiro: python scripts/inventory_client_apis.py")
        sys.exit(1)

    all_operations = json.loads(inventory_path.read_text(encoding="utf-8"))
    operations = [op for op in all_operations if op.get("method", "").upper() == "GET"]
    skipped = [op for op in all_operations if op.get("method", "").upper() != "GET"]

    print(f"   📋 {len(all_operations)} operações no inventário.")
    print(f"   ✅ {len(operations)} GET (serão executadas).")
    print(f"   ⏭️  {len(skipped)} mutáveis (ignoradas).")
    print()

    # 3. Executa testes GET
    print("3. Executando testes GET...")
    print("-" * 60)

    recorder = ResponseRecorder()

    with AleloApiClient() as client:
        for i, op in enumerate(operations, 1):
            print(f"\n   [{i}/{len(operations)}] {op['method']} {op['path']}")
            print(f"   Nome: {op['operation_name']}")

            result = _execute_get(client, op, config)
            recorder.record(result)

            # Status visual
            status_icons = {
                "SUCCESS": "✅",
                "HTTP_ERROR": "❌",
                "AUTH_TOKEN_INVALID": "🔐",
                "AUTH_GATEWAY_TIMEOUT": "⏱️",
                "BLOCKED_BY_AUTH": "🚫",
                "TIMEOUT": "⏱️",
                "CONNECTION_ERROR": "🔌",
            }
            icon = status_icons.get(result.execution_status, "❓")
            print(f"   {icon} Status: {result.execution_status}", end="")
            if result.status_code:
                print(f" (HTTP {result.status_code})", end="")
            if result.duration_ms:
                print(f" [{result.duration_ms}ms]", end="")
            print()

            # Info adicional para sucesso
            if result.success and result.response_body:
                body = result.response_body
                if isinstance(body, dict):
                    total = body.get("total", "?")
                    content = body.get("content", [])
                    print(f"      📊 Total: {total} | Registros: {len(content)} | Campos: {list(body.keys())}")
            elif result.error_message:
                print(f"      Detalhe: {result.error_message[:80]}")

    print()
    print("-" * 60)

    # 4. Salva resultados
    print("\n4. Salvando resultados...")
    summary_path = recorder.save_summary(environment="homologacao")
    print(f"   💾 Resumo: {summary_path.relative_to(root)}")
    print(f"   📁 Pasta: {recorder.run_dir.relative_to(root)}")
    print()

    # 5. Resumo final
    results = recorder.get_results()
    successes = sum(1 for r in results if r.success)
    blocked = sum(1 for r in results if r.execution_status == "BLOCKED_BY_AUTH")
    failures = sum(1 for r in results if not r.success and r.execution_status != "BLOCKED_BY_AUTH")

    print("=" * 60)
    print(f"  RESUMO GET: {successes} sucesso | {failures} falha | {blocked} bloqueadas (auth)")
    print(f"  Mutáveis ignoradas: {len(skipped)} (POST/PUT/DELETE)")
    if blocked > 0:
        print(f"\n  ⚠️  APIs bloqueadas por auth NÃO contam como aprovadas.")
    print("=" * 60)


def _execute_get(client: AleloApiClient, op: dict, config: dict) -> ApiResult:
    """Executa uma operação GET."""
    path = op.get("path", "")
    operation_name = op.get("operation_name", "")

    # Monta URL completa
    base_url = config["api_base_url"].rstrip("/")

    if "/v1/" in path:
        path_suffix = path.split("/v1/", 1)[1]
        full_url = f"{base_url}/cardholders-hr-management/v1/{path_suffix}"
    elif path.startswith("cardholders-"):
        full_url = f"{base_url}/{path}"
    else:
        full_url = f"{base_url}/cardholders-hr-management{path}"

    # Query parameters
    params = {}
    if op.get("query_parameters"):
        for qp in op["query_parameters"]:
            name = qp.get("name", "")
            if name.lower() == "page":
                params[name] = "0"

    return client.execute(
        operation_name=operation_name,
        method="GET",
        url=full_url,
        params=params if params else None,
    )


if __name__ == "__main__":
    main()
