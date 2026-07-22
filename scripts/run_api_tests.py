"""Runner de testes de integração com as APIs Alelo.

Executa chamadas reais contra o ambiente de homologação.
Apenas APIs seguras (GET) são executadas automaticamente.
APIs mutáveis (POST/PUT/PATCH/DELETE) são marcadas como SKIPPED_SAFETY.

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
from discover_alelo.sanitization import sanitize


def main() -> None:
    root = get_project_root()

    print("=" * 60)
    print("  TESTES DE INTEGRAÇÃO - APIs Gestão de Colaboradores")
    print("=" * 60)
    print()

    # 1. Valida ambiente
    print("1. Validando ambiente...")
    config = validate_env()
    print("   ✅ Ambiente validado.")
    print()

    # 2. Carrega inventário de APIs
    print("2. Carregando inventário de APIs...")
    inventory_path = root / "artifacts" / "api_inventory" / "gestao_colaboradores_apis.json"
    if not inventory_path.exists():
        print(f"   ❌ Inventário não encontrado: {inventory_path}")
        print("   Execute primeiro: python scripts/inventory_client_apis.py")
        sys.exit(1)

    operations = json.loads(inventory_path.read_text(encoding="utf-8"))
    print(f"   📋 {len(operations)} operações carregadas.")
    print()

    # 3. Executa testes
    print("3. Executando testes...")
    print("-" * 60)

    recorder = ResponseRecorder()

    with AleloApiClient() as client:
        for i, op in enumerate(operations, 1):
            print(f"\n   [{i}/{len(operations)}] {op['method']} {op['path']}")
            print(f"   Nome: {op['operation_name']}")

            result = _execute_operation(client, op, config)
            recorder.record(result)

            # Status visual
            status_icons = {
                "SUCCESS": "✅",
                "HTTP_ERROR": "❌",
                "AUTH_ERROR": "🔐",
                "TIMEOUT": "⏱️",
                "CONNECTION_ERROR": "🔌",
                "SKIPPED_SAFETY": "⚠️",
                "SKIPPED_NO_SAMPLE": "📝",
                "INVALID_DOCUMENTATION": "📄",
            }
            icon = status_icons.get(result.execution_status, "❓")
            print(f"   {icon} Status: {result.execution_status}", end="")
            if result.status_code:
                print(f" (HTTP {result.status_code})", end="")
            if result.duration_ms:
                print(f" [{result.duration_ms}ms]", end="")
            print()

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
    failures = sum(
        1 for r in results
        if not r.success and r.execution_status not in ("SKIPPED_SAFETY", "SKIPPED_NO_SAMPLE")
    )
    skipped = sum(
        1 for r in results
        if r.execution_status in ("SKIPPED_SAFETY", "SKIPPED_NO_SAMPLE")
    )

    print("=" * 60)
    print(f"  RESUMO: {successes} sucesso | {failures} falha | {skipped} ignoradas")
    print("=" * 60)


def _execute_operation(
    client: AleloApiClient,
    op: dict,
    config: dict,
) -> ApiResult:
    """Executa uma operação de API ou a marca como skipped."""

    method = op.get("method", "").upper()
    path = op.get("path", "")
    operation_name = op.get("operation_name", "")

    # Verifica se é segura para execução
    if not op.get("safe_to_execute", False):
        result = ApiResult(
            operation_name=operation_name,
            method=method,
            url=path,
            execution_status="SKIPPED_SAFETY",
            error_message=op.get("safety_reason", "Operação mutável não executada automaticamente."),
        )
        return result

    # Monta URL completa
    base_url = config["api_base_url"].rstrip("/")
    api_path = f"cardholders-hr-management/v1/beneficiaries"

    # Usa o path da documentação para montar a URL
    if "/v1/" in path:
        # Extrai a parte após o versão
        path_suffix = path.split("/v1/", 1)[1] if "/v1/" in path else path
        full_url = f"{base_url}/cardholders-hr-management/v1/{path_suffix}"
    else:
        full_url = f"{base_url}/cardholders-hr-management{path}"

    # Query parameters padrão para GET
    params = None
    if method == "GET" and op.get("query_parameters"):
        # Usa valores de teste seguros
        params = {}
        for qp in op["query_parameters"]:
            name = qp.get("name", "")
            # Valores seguros para consulta
            if name.lower() == "page":
                params[name] = "0"
            # Não envia CPF real como query param - deixa vazio para listar todos

    # Executa
    result = client.execute(
        operation_name=operation_name,
        method=method,
        url=full_url,
        params=params,
    )

    return result


if __name__ == "__main__":
    main()
