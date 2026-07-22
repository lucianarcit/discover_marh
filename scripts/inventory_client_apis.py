"""Script para inventariar APIs documentadas no HTML do cliente.

Uso:
    python scripts/inventory_client_apis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.config import get_project_root
from discover_alelo.html_api_parser import parse_html_file, operations_to_json


def main() -> None:
    root = get_project_root()

    # Localiza o HTML do cliente
    html_path = root / "docs" / "client" / "Gestao_de_Colaboradores.html"
    if not html_path.exists():
        # Fallback para localização original
        html_path = root / "docs" / "cliente" / "Gestao_de_Colaboradores.html"

    if not html_path.exists():
        print(f"❌ HTML não encontrado: {html_path}")
        sys.exit(1)

    print(f"📄 Analisando: {html_path.name}")
    print()

    # Parse do HTML
    operations = parse_html_file(html_path)
    print(f"   Operações encontradas: {len(operations)}")
    print()

    for i, op in enumerate(operations, 1):
        safety_icon = "✅" if op.safe_to_execute else "⚠️"
        print(f"   {i}. [{op.method}] {op.path}")
        print(f"      Nome: {op.operation_name}")
        print(f"      Segura: {safety_icon} {op.safety_reason}")
        if op.path_parameters:
            print(f"      Path params: {op.path_parameters}")
        if op.query_parameters:
            params = [p["name"] for p in op.query_parameters]
            print(f"      Query params: {params}")
        print()

    # Salva inventário JSON
    output_dir = root / "artifacts" / "api_inventory"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "gestao_colaboradores_apis.json"

    api_data = operations_to_json(operations)
    output_path.write_text(
        json.dumps(api_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"💾 Inventário salvo em: {output_path.relative_to(root)}")

    # Gera relatório markdown
    _generate_report(operations, root)


def _generate_report(operations, root: Path) -> None:
    """Gera docs/reports/api_inventory.md"""
    report_dir = root / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "api_inventory.md"

    lines = [
        "# Inventário de APIs - Gestão de Colaboradores",
        "",
        f"**Gerado em:** {_now()}",
        f"**Fonte:** `docs/cliente/Gestao_de_Colaboradores.html`",
        f"**Total de operações:** {len(operations)}",
        "",
        "---",
        "",
        "## Operações Identificadas",
        "",
        "| # | Operação | Método | Endpoint | Tipo | Parâmetros | Token | Risco Alteração | Exemplo no HTML | Situação |",
        "|---|----------|--------|----------|------|-----------|-------|-----------------|----------------|----------|",
    ]

    for i, op in enumerate(operations, 1):
        params = ", ".join(
            [p["name"] for p in op.query_parameters] + op.path_parameters
        )
        has_example = "✅" if op.request_body_example or op.documented_response_example else "❌"
        risk = "🔴 Alto" if not op.safe_to_execute else "🟢 Baixo"
        situation = "Apta" if op.safe_to_execute else "SKIPPED_SAFETY"
        op_type = "Consulta" if op.method == "GET" else "Mutação"

        lines.append(
            f"| {i} | {op.operation_name} | `{op.method}` | `{op.path}` | "
            f"{op_type} | {params or 'N/A'} | Sim | {risk} | {has_example} | {situation} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Detalhes por Operação",
        "",
    ])

    for op in operations:
        lines.extend([
            f"### {op.operation_name}",
            "",
            f"- **Método:** `{op.method}`",
            f"- **Path:** `{op.path}`",
            f"- **Segura para execução:** {'Sim' if op.safe_to_execute else 'Não'}",
            f"- **Motivo:** {op.safety_reason}",
            f"- **Headers obrigatórios:** {', '.join(op.required_headers) if op.required_headers else 'Ver documentação'}",
            f"- **Status codes:** {', '.join(s['code'] + ' ' + s['description'] for s in op.documented_status_codes)}",
            "",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📋 Relatório salvo em: {report_path.relative_to(root)}")


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
