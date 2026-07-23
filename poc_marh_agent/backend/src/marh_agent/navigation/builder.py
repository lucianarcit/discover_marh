"""Navigation Builder — monta deeplinks seguros.

Regras:
- Catálogo fechado de rotas.
- Base por ambiente (HML/PRD).
- URL encoding correto.
- Nunca aceita rota/URL do usuário.
- Nunca inclui CPF, CNPJ, token, beneficiaryId.
- Valida orderNumber.
- Não aceita idOrder.
- Não aceita path traversal.
- Preserva casing dos parâmetros do deeplink.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from marh_agent.config import WEBVIEW_BASE_URLS, Environment
from marh_agent.domain.responses import NavigationResponse


# Catálogo fechado de rotas permitidas
ALLOWED_ROUTES: dict[str, str] = {
    "ROUTE-003": "#/employees",
    "ROUTE-012": "#/orders",
    "ROUTE-014": "#/order-detail/{orderNumber}",
    "ROUTE-015": "#/order-detail/{orderNumber}/beneficiaries",
    "ROUTE-017": "#/new-order/products",
    "ROUTE-024": "#/card-tracking",
    "ROUTE-025": "#/card-tracking/{orderNumber}",
}

# Regex para validar orderNumber — apenas dígitos, sem path traversal
_ORDER_NUMBER_VALID = re.compile(r"^\d{1,10}$")
_PATH_TRAVERSAL = re.compile(r"\.\.|%2[eEfF]|/|\\")


def _validate_order_number(order_number: str | None) -> bool:
    """Valida que orderNumber é seguro para uso em rotas."""
    if not order_number:
        return False
    if _PATH_TRAVERSAL.search(order_number):
        return False
    if not _ORDER_NUMBER_VALID.match(order_number):
        return False
    return True


def build_navigation(
    route_id: str,
    environment: str,
    label: str,
    order_number: str | None = None,
) -> NavigationResponse | None:
    """Monta uma NavigationResponse segura.

    Retorna None se a rota não é permitida ou parâmetros são inválidos.
    """
    if route_id not in ALLOWED_ROUTES:
        return None

    route_template = ALLOWED_ROUTES[route_id]

    # Se a rota requer orderNumber, valida
    if "{orderNumber}" in route_template:
        if not _validate_order_number(order_number):
            return None
        route = route_template.replace("{orderNumber}", order_number)
    else:
        route = route_template

    # Monta URL da webview
    env = Environment(environment) if environment in ("HML", "PRD") else Environment.HML
    base_url = WEBVIEW_BASE_URLS[env.value]
    webview_url = f"{base_url}{route}"

    # URL encode para o deeplink
    encoded_url = quote(webview_url, safe="")

    # Monta deeplink com casing correto
    deeplink = (
        f"meualelo://app/webview?url={encoded_url}"
        f"&isModal=false&showNavbar=false&authRequired=true"
    )

    return NavigationResponse(
        type="list_navigation",
        route_id=route_id,
        label=label,
        deeplink=deeplink,
        webview_url=webview_url,
    )
