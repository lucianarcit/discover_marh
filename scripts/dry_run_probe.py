"""Dry-run — mostra configuração e operações disponíveis sem executar chamadas HTTP."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.config import get_all_config, is_homologacao_url, get_project_root


def main():
    config = get_all_config()
    root = get_project_root()

    print("=" * 60)
    print("  DRY-RUN — Probe Configuration")
    print("=" * 60)
    print()

    # Auth mode
    has_direct_token = bool(config.get("access_token"))
    has_refresh = bool(config.get("refresh_token"))
    if has_direct_token:
        auth_mode = "STATIC_ACCESS_TOKEN (direto do .env)"
    elif has_refresh:
        auth_mode = "REFRESH_TOKEN (OAuth2 endpoint)"
    else:
        auth_mode = "NONE — nenhum token configurado"

    print(f"  Base URL:    {config['api_base_url']}")
    print(f"  Is HML:      {is_homologacao_url(config['api_base_url'])}")
    print(f"  Auth mode:   {auth_mode}")
    print(f"  Platform:    {config['platform']}")
    print(f"  App version: {config['app_version']}")
    print(f"  Output:      .local/api_runs/ (git ignored)")
    print()

    # Inventarios
    collab_path = root / "artifacts" / "api_inventory" / "gestao_colaboradores_apis.json"
    pedidos_path = root / "artifacts" / "api_inventory" / "gestao_pedidos_apis.json"

    print("  === OPERACOES DISPONIVEIS ===")
    print()

    if collab_path.exists():
        ops = json.loads(collab_path.read_text(encoding="utf-8"))
        gets = [o for o in ops if o.get("method") == "GET"]
        print(f"  Colaboradores: {len(gets)} GET (de {len(ops)} total)")
        for op in gets:
            print(f"    GET {op['path']} — {op['operation_name']}")
    else:
        print("  Colaboradores: inventario NAO ENCONTRADO")

    print()

    if pedidos_path.exists():
        ops = json.loads(pedidos_path.read_text(encoding="utf-8"))
        print(f"  Pedidos: {len(ops)} operacoes GET")
        for op in ops:
            dep = " [needs orderNumber]" if op.get("needs_path_param") else ""
            print(f"    GET {op['path']} — {op['operation_name']}{dep}")
    else:
        print("  Pedidos: inventario NAO ENCONTRADO")

    print()
    print("  Nenhuma chamada HTTP realizada (dry-run).")
    print("=" * 60)


if __name__ == "__main__":
    main()
