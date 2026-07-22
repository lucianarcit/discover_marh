"""Script de bootstrap: valida o ambiente e testa a autenticação.

Uso:
    python scripts/bootstrap_env.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.config import validate_env, is_homologacao_url


def main() -> None:
    print("=" * 60)
    print("  BOOTSTRAP - Discover Alelo")
    print("=" * 60)
    print()

    # 1. Valida variáveis de ambiente
    print("1. Validando variáveis de ambiente...")
    config = validate_env()
    print("   ✅ Todas as variáveis obrigatórias estão definidas.")
    print()

    # 2. Verifica URLs de homologação
    print("2. Verificando URLs de homologação...")
    auth_url = config["auth_url"]
    api_url = config["api_base_url"]

    if not is_homologacao_url(auth_url):
        print(f"   ❌ URL de auth NÃO é homologação: {auth_url[:40]}...")
        sys.exit(1)
    print(f"   ✅ Auth URL é homologação")

    if not is_homologacao_url(api_url):
        print(f"   ❌ URL base NÃO é homologação: {api_url[:40]}...")
        sys.exit(1)
    print(f"   ✅ API Base URL é homologação")
    print()

    # 3. Testa autenticação
    print("3. Testando autenticação...")
    try:
        from discover_alelo.auth import get_access_token

        token = get_access_token()
        # Mostra apenas tamanho (nunca o valor)
        print(f"   ✅ Token obtido ({len(token)} caracteres)")
    except Exception as e:
        print(f"   ❌ Falha na autenticação: {e}")
        print("   O ambiente está configurado, mas o token pode estar expirado.")
        print("   Verifique ALELO_REFRESH_TOKEN no .env")
        # Não é fatal — ambiente pode estar OK mas token expirou
    print()

    print("=" * 60)
    print("  Bootstrap concluído.")
    print("=" * 60)


if __name__ == "__main__":
    main()
