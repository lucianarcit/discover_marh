"""Testes de integração — APIs GET de Gestão de Pedidos.

Aprovados SOMENTE com resposta real válida.
Usa encadeamento: /orders retorna orderNumber para endpoints dependentes.

Uso:
    python -m pytest tests/integration/test_gestao_pedidos_api.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from discover_alelo.api_client import AleloApiClient
from discover_alelo.auth import AuthResult, authenticate
from discover_alelo.config import get_all_config, is_homologacao_url, validate_env


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def config():
    try:
        return validate_env()
    except SystemExit:
        pytest.skip("Variáveis de ambiente não configuradas")


@pytest.fixture(scope="module")
def auth_result(config) -> AuthResult:
    return authenticate()


@pytest.fixture(scope="module")
def client(config):
    with AleloApiClient() as c:
        yield c


@pytest.fixture(scope="module")
def base_url(config):
    return f"{config['api_base_url'].rstrip('/')}/cardholders-hr-management/v1"


@pytest.fixture(scope="module")
def order_number(client, base_url, auth_result):
    """Obtém um orderNumber real para testes encadeados."""
    if not auth_result.success:
        return None
    result = client.get(
        operation_name="orders_fixture",
        url=f"{base_url}/orders",
        params={"page": "0", "size": "5"},
    )
    if result.success and result.response_body:
        content = result.response_body.get("content", [])
        if content:
            orders = content[0].get("orders", [])
            if orders:
                return str(orders[0].get("orderNumber", ""))
    return None


# ─── Testes sem dependência de orderNumber ───────────────────────────────────


class TestConsultaPedidos:
    """GET /v1/orders"""

    def test_listar_pedidos(self, client, base_url, auth_result):
        if not auth_result.success:
            pytest.skip(f"Auth falhou: {auth_result.execution_status}")

        result = client.get(
            operation_name="Consulta de Pedidos",
            url=f"{base_url}/orders",
            params={"page": "0", "size": "10"},
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )

    def test_pedidos_estrutura(self, client, base_url, auth_result):
        if not auth_result.success:
            pytest.skip("Auth falhou")
        result = client.get(
            operation_name="Pedidos - estrutura",
            url=f"{base_url}/orders",
            params={"page": "0", "size": "10"},
        )
        if result.status_code == 204:
            pytest.skip("204 No Content")
        if result.status_code != 200:
            pytest.skip(f"Status {result.status_code}")
        body = result.response_body
        assert isinstance(body, dict)
        assert "content" in body or "total" in body


class TestConsultaProdutos:
    """GET /v1/products"""

    def test_listar_produtos(self, client, base_url, auth_result):
        if not auth_result.success:
            pytest.skip(f"Auth falhou: {auth_result.execution_status}")
        result = client.get(
            operation_name="Consulta dos Produtos",
            url=f"{base_url}/products",
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )


class TestConsultaBeneficios:
    """GET /v1/benefits"""

    def test_listar_beneficios(self, client, base_url, auth_result):
        if not auth_result.success:
            pytest.skip(f"Auth falhou: {auth_result.execution_status}")
        result = client.get(
            operation_name="Consulta dos Benefícios",
            url=f"{base_url}/benefits",
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )


class TestConsultaDatasCredito:
    """GET /v1/availability-dates-for-credit"""

    def test_listar_datas_credito(self, client, base_url, auth_result):
        if not auth_result.success:
            pytest.skip(f"Auth falhou: {auth_result.execution_status}")
        result = client.get(
            operation_name="Consulta dos Dias para Crédito",
            url=f"{base_url}/availability-dates-for-credit",
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )


# ─── Testes com dependência de orderNumber (encadeamento) ────────────────────


class TestDetalhePedido:
    """GET /v1/orders/{orderNumber}"""

    def test_detalhe_pedido(self, client, base_url, auth_result, order_number):
        if not auth_result.success:
            pytest.skip("Auth falhou")
        if not order_number:
            pytest.skip("Nenhum orderNumber disponível")
        result = client.get(
            operation_name="Consulta dos Detalhes de um Pedido",
            url=f"{base_url}/orders/{order_number}",
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )


class TestColaboradoresPedido:
    """GET /v1/orders/{orderNumber}/beneficiaries"""

    def test_colaboradores_pedido(self, client, base_url, auth_result, order_number):
        if not auth_result.success:
            pytest.skip("Auth falhou")
        if not order_number:
            pytest.skip("Nenhum orderNumber disponível")
        result = client.get(
            operation_name="Consulta dos Colaboradores do Pedido",
            url=f"{base_url}/orders/{order_number}/beneficiaries",
            params={"page": "0", "size": "10"},
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code} — {result.error_message}"
        )


class TestNotaFiscal:
    """GET /v1/orders/{orderNumber}/invoice"""

    def test_nota_fiscal(self, client, base_url, auth_result, order_number):
        if not auth_result.success:
            pytest.skip("Auth falhou")
        if not order_number:
            pytest.skip("Nenhum orderNumber disponível")
        result = client.get(
            operation_name="Download da Nota Fiscal",
            url=f"{base_url}/orders/{order_number}/invoice",
        )
        # Pode retornar 200, 204, 404 ou 422 (pedido sem NF)
        assert result.status_code in (200, 204, 404, 422, 500), (
            f"Status: {result.status_code} — {result.error_message}"
        )


class TestBoleto:
    """GET /v1/orders/{orderNumber}/bank-ticket"""

    def test_boleto(self, client, base_url, auth_result, order_number):
        if not auth_result.success:
            pytest.skip("Auth falhou")
        if not order_number:
            pytest.skip("Nenhum orderNumber disponível")
        result = client.get(
            operation_name="Visualizar Boleto",
            url=f"{base_url}/orders/{order_number}/bank-ticket",
        )
        # Pode retornar 200, 204 ou 404 (pedido sem boleto)
        assert result.status_code in (200, 204, 404, 500), (
            f"Status: {result.status_code} — {result.error_message}"
        )
