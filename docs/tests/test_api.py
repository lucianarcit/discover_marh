"""
Script de teste da API Alelo HML — cardholders-hr-management v1
Credenciais e headers extraídos de docs/sample/sample_curl.txt e user_hml.txt

Uso:
    pip install requests
    python test_api.py --token <accessToken>

Como obter o token:
    O accessToken é gerado pelo app nativo Meu Alelo (TTL ~300s).
    Para testes em HML, use o Meu Alelo apontado para HML, faça login com:
        CPF:   750.636.377-10
        Senha: Alelo123
    Intercepte o token via proxy (Charles/Proxyman) ou extraia dos cookies
    da webview e passe via --token.

    Alternativa rápida: use o curl do arquivo docs/sample/sample_curl.txt
    (token pode estar expirado — se receber 401, obtenha um novo).
"""

import argparse
import base64
import json
import sys

import requests

# ─── Configuração ────────────────────────────────────────────────────────────

BASE_URL = "https://api-ma.homologacaoalelo.com.br/alelo/uat/cardholders-hr-management/v1"

# Credenciais fixas de HML (CLIENT_ID e CLIENT_SECRET não expiram)
CLIENT_ID     = "7b09e189-2d00-4c6d-a2ef-88d2805e61d0"
CLIENT_SECRET = "dc2cccc1-5886-4caf-b7e3-60a85113f550"
USER_ID       = "30a38791de9a33e115a29c241e9063c0"
FNP           = "8CCE640B-56E8-479B-8B18-57E55739AF6B"
APP_VERSION   = "8.55.0 (2026071702)"
PLATFORM      = "IOS"

X_BASIC_AUTH = "Basic " + base64.b64encode(
    f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
).decode()


def build_headers(access_token: str) -> dict:
    return {
        "Authorization":         f"Bearer {access_token}",
        "CLIENT_ID":             CLIENT_ID,
        "CLIENT_SECRET":         CLIENT_SECRET,
        "X-BASIC-AUTHORIZATION": X_BASIC_AUTH,
        "x-ibm-client-id":       CLIENT_ID,
        "APP_VERSION":           APP_VERSION,
        "PLATFORM":              PLATFORM,
        "FNP":                   FNP,
        "user_id":               USER_ID,
        "AUTH_TYPE":             "IS-ALELO",
        "Accept":                "application/json",
        "Content-Type":          "application/json",
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def print_separator():
    print(f"\n{'─'*60}")


def print_result(label: str, response: requests.Response) -> dict | None:
    status = response.status_code
    ok     = status in (200, 201, 204)
    color  = "\033[92m" if ok else "\033[91m"
    reset  = "\033[0m"
    print_separator()
    print(f"{color}[{status}]{reset} {label}")
    print(f"  URL: {response.url}")
    try:
        body = response.json()
        preview = json.dumps(body, ensure_ascii=False, indent=2)
        print(preview[:2000] + (" ..." if len(preview) > 2000 else ""))
        return body
    except Exception:
        if response.text:
            print(response.text[:500])
        return None


def get(path: str, headers: dict, params: dict = None) -> requests.Response:
    return requests.get(
        f"{BASE_URL}{path}",
        headers=headers,
        params=params,
        timeout=15,
    )


# ─── Casos de Teste ──────────────────────────────────────────────────────────

def test_profile(headers: dict) -> tuple[bool, dict | None]:
    """GET /profile — identifica perfil e empresa (base dos guardrails)"""
    resp = get("/profile", headers)
    body = print_result("GET /profile", resp)
    if body and "functions" in body:
        perfis = [f["functionType"] for f in body["functions"]]
        print(f"\n  → Perfil(s) do usuário: {perfis}")
        print(f"  → Nome: {body.get('name')} | CPF: {body.get('documentNumber')}")
    return resp.status_code == 200, body


def test_companies(headers: dict) -> tuple[bool, list]:
    """GET /companies — lista empresas do interlocutor"""
    resp = get("/companies", headers)
    body = print_result("GET /companies", resp)
    companies = []
    if body and "contractees" in body:
        companies = body["contractees"]
        print(f"\n  → {len(companies)} empresa(s) encontrada(s)")
    return resp.status_code in (200, 204), companies


def test_benefits(headers: dict) -> bool:
    """GET /benefits — benefícios das empresas"""
    resp = get("/benefits", headers)
    body = print_result("GET /benefits", resp)
    if isinstance(body, list):
        ativos = [b["benefitName"] for b in body if b.get("enabled")]
        print(f"\n  → Benefícios ativos: {ativos}")
    return resp.status_code in (200, 204)


def test_products(headers: dict) -> bool:
    """GET /products — produtos dos contratos"""
    resp = get("/products", headers)
    body = print_result("GET /products", resp)
    if body and "content" in body:
        print(f"\n  → {body.get('total', 0)} produto(s)")
    return resp.status_code in (200, 204)


def test_places(headers: dict) -> bool:
    """GET /places — locais de entrega"""
    resp = get("/places", headers, params={"page": 0, "size": 5})
    body = print_result("GET /places", resp)
    if body and "total" in body:
        print(f"\n  → {body['total']} local(is) de entrega")
    return resp.status_code in (200, 204)


def test_beneficiaries(headers: dict) -> bool:
    """GET /beneficiaries — colaboradores (p.0, s.5)"""
    resp = get("/beneficiaries", headers, params={"page": 0, "size": 5, "lang": "pt"})
    body = print_result("GET /beneficiaries", resp)
    if body and "total" in body:
        print(f"\n  → {body['total']} colaborador(es) no total")
    return resp.status_code in (200, 204)


def test_orders(headers: dict) -> tuple[bool, int | None]:
    """GET /orders — lista pedidos (p.0, s.5)"""
    resp = get("/orders", headers, params={"page": 0, "size": 5, "lang": "pt"})
    body = print_result("GET /orders", resp)
    order_number = None
    if body and "content" in body and body["content"]:
        orders = body["content"][0].get("orders", [])
        if orders:
            order_number = orders[0].get("orderNumber")
            status = orders[0].get("status", "?")
            print(f"\n  → Pedido mais recente: #{order_number} | status: {status}")
    return resp.status_code in (200, 204), order_number


def test_order_detail(headers: dict, order_number: int) -> bool:
    """GET /orders/{orderNumber} — detalhe de um pedido"""
    resp = get(f"/orders/{order_number}", headers)
    body = print_result(f"GET /orders/{order_number}", resp)
    if body:
        print(f"\n  → Status: {body.get('status')} | Total: R${body.get('totalOrder', 0):.2f}")
    return resp.status_code in (200, 204)


def test_availability_dates(headers: dict) -> bool:
    """GET /availability-dates-for-credit — datas disponíveis para crédito"""
    resp = get("/availability-dates-for-credit", headers)
    body = print_result("GET /availability-dates-for-credit", resp)
    if body:
        print(f"\n  → De {body.get('minDate')} até {body.get('maxDate')}")
        print(f"  → {len(body.get('holidaysList', []))} feriado(s) no período")
    return resp.status_code in (200, 204)


def test_tracking(headers: dict) -> bool:
    """GET /tracking — rastreio geral de cartões"""
    resp = get("/tracking", headers, params={"page": 0, "size": 5})
    body = print_result("GET /tracking", resp)
    if body and "total" in body:
        print(f"\n  → {body['total']} pedido(s) em rastreio")
    return resp.status_code in (200, 204)


# ─── Runner ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Teste da API Alelo HML")
    parser.add_argument(
        "--token", "-t",
        required=True,
        help="accessToken JWT obtido do app Meu Alelo (expira em ~300s)",
    )
    args = parser.parse_args()

    headers = build_headers(args.token)

    print("=" * 60)
    print("  Teste de API — Alelo HML")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Token:    {args.token[:20]}...")
    print("=" * 60)

    results: dict[str, bool] = {}

    results["profile"],      _ = test_profile(headers)
    results["companies"],    _            = test_companies(headers)
    results["benefits"]                  = test_benefits(headers)
    results["products"]                  = test_products(headers)
    results["places"]                    = test_places(headers)
    results["beneficiaries"]             = test_beneficiaries(headers)
    results["availability_dates"]        = test_availability_dates(headers)
    results["tracking"]                  = test_tracking(headers)
    results["orders"],       order_number = test_orders(headers)

    if order_number:
        results["order_detail"] = test_order_detail(headers, order_number)

    # ─── Resumo ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  RESUMO")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    total  = len(results)
    for name, ok in results.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {name}")

    print(f"\n  {passed}/{total} endpoints responderam com sucesso")

    if passed < total:
        falhou = [n for n, v in results.items() if not v]
        print(f"\n  Falharam: {falhou}")
        if not results.get("profile"):
            print("\n  ⚠️  Se todos retornaram 401, o token expirou.")
            print("     Obtenha um novo token e re-execute:")
            print("     python test_api.py --token <novo_token>")

    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
