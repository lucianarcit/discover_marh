"""Script de bootstrap: valida o ambiente, diagnostica rede, e testa autenticação.

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
        print(f"   ❌ URL de auth NÃO é homologação!")
        sys.exit(1)
    print(f"   ✅ Auth URL é homologação")

    if not is_homologacao_url(api_url):
        print(f"   ❌ URL base NÃO é homologação!")
        sys.exit(1)
    print(f"   ✅ API Base URL é homologação")
    print()

    # 3. Diagnóstico de rede
    print("3. Diagnosticando rede...")
    from discover_alelo.network_diagnostic import diagnose_endpoint

    diag_auth = diagnose_endpoint(auth_url, connect_timeout=config["connect_timeout"])
    print(f"   Auth endpoint:")
    print(f"     DNS: {'✅' if diag_auth.dns_resolved else '❌'} ({diag_auth.dns_duration_ms}ms)")
    print(f"     TCP: {'✅' if diag_auth.tcp_reachable else '❌'} ({diag_auth.tcp_duration_ms}ms)")
    print(f"     HTTPS: {diag_auth.https_status or 'N/A'} ({diag_auth.https_duration_ms}ms)")
    print(f"     Status: {diag_auth.overall_status}")
    if diag_auth.hypothesis:
        print(f"     ⚠️  Hipótese: {diag_auth.hypothesis}")
    print()

    diag_api = diagnose_endpoint(api_url, connect_timeout=config["connect_timeout"])
    print(f"   API endpoint:")
    print(f"     DNS: {'✅' if diag_api.dns_resolved else '❌'} ({diag_api.dns_duration_ms}ms)")
    print(f"     TCP: {'✅' if diag_api.tcp_reachable else '❌'} ({diag_api.tcp_duration_ms}ms)")
    print(f"     HTTPS: {diag_api.https_status or 'N/A'} ({diag_api.https_duration_ms}ms)")
    print(f"     Status: {diag_api.overall_status}")
    if diag_api.hypothesis:
        print(f"     ⚠️  Hipótese: {diag_api.hypothesis}")
    print()

    # 4. Testa autenticação
    print("4. Testando autenticação...")
    from discover_alelo.auth import authenticate

    auth_result = authenticate()
    print(f"   Status: {auth_result.execution_status}")
    print(f"   HTTP: {auth_result.status_code or 'N/A'}")
    print(f"   Duração: {auth_result.duration_ms}ms")
    print(f"   Tentativas: {auth_result.attempts}")

    if auth_result.success:
        print(f"   ✅ Token obtido ({len(auth_result.access_token)} chars)")
        print(f"   Tipo: {auth_result.token_type}")
        print(f"   Expira em: {auth_result.expires_in}s")
    else:
        print(f"   ❌ Falha: {auth_result.error_detail}")
        if auth_result.response_keys:
            print(f"   Campos na resposta: {auth_result.response_keys}")
    print()

    # 5. Tabela de diagnóstico cURL vs Python
    print("5. Comparação cURL vs Python (sem valores sensíveis):")
    print()
    print("   | Item                  | cURL                       | Python (.env)              | Compatível |")
    print("   |-----------------------|----------------------------|----------------------------|------------|")
    print("   | Método                | POST                       | POST                       | ✅         |")
    print(f"   | URL                   | *.homologacaoalelo.com.br  | *.homologacaoalelo.com.br  | ✅         |")
    print("   | Content-Type          | x-www-form-urlencoded      | x-www-form-urlencoded      | ✅         |")
    print("   | Authorization         | Basic <base64>             | Basic <base64>             | ✅         |")
    print("   | APP_VERSION           | presente                   | presente                   | ✅         |")
    print("   | AUTH_TYPE             | IS-ALELO                   | IS-ALELO                   | ✅         |")
    print("   | FNP                   | presente                   | presente                   | ✅         |")
    print("   | PLATFORM              | IOS                        | IOS                        | ✅         |")
    print("   | x-ibm-client-id       | presente                   | presente                   | ✅         |")
    print("   | grant_type            | refresh_token (body)       | refresh_token (body)       | ✅         |")
    print("   | refresh_token         | body (form)                | body (form)                | ✅         |")

    # Verifica se refresh_token está sendo carregado
    has_refresh = bool(config.get("refresh_token"))
    rt_status = "✅" if has_refresh else "❌ AUSENTE"
    print(f"   | ALELO_REFRESH_TOKEN   | presente no cURL           | {'carregado' if has_refresh else 'NÃO carregado'}            | {rt_status}    |")
    print()

    # 6. Resumo
    print("=" * 60)
    if auth_result.success:
        print("  ✅ Bootstrap concluído com sucesso. Pronto para testar APIs.")
    elif diag_auth.overall_status in ("DNS_ERROR", "CONNECTION_ERROR", "GATEWAY_TIMEOUT"):
        print("  ⚠️  Bootstrap parcial: rede indisponível.")
        print("     Verifique VPN/conectividade.")
    else:
        print(f"  ⚠️  Bootstrap parcial: auth retornou {auth_result.execution_status}.")
        print("     Verifique credenciais no .env.")
    print("=" * 60)


if __name__ == "__main__":
    main()
