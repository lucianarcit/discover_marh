"""Testes de integração — SOMENTE operações GET.

Testes reais passam SOMENTE com resposta válida da API.
Quando a autenticação falha, são SKIPPED.

Uso:
    python -m pytest tests/integration/test_gestao_colaboradores_api.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from discover_alelo.api_client import AleloApiClient
from discover_alelo.auth import AuthResult, authenticate
from discover_alelo.config import get_all_config, is_homologacao_url, validate_env
from discover_alelo.network_diagnostic import diagnose_endpoint


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def config():
    """Carrega e valida configuração."""
    try:
        return validate_env()
    except SystemExit:
        pytest.skip("Variáveis de ambiente não configuradas")


@pytest.fixture(scope="module")
def auth_result(config) -> AuthResult:
    """Executa autenticação e retorna resultado detalhado."""
    return authenticate()


@pytest.fixture(scope="module")
def client(config):
    """Cria cliente HTTP."""
    with AleloApiClient() as c:
        yield c


@pytest.fixture(scope="module")
def base_url(config):
    """URL base da API de gestão de colaboradores."""
    api_base = config["api_base_url"].rstrip("/")
    return f"{api_base}/cardholders-hr-management/v1"


# ─── Testes de Diagnóstico ───────────────────────────────────────────────────


class TestNetworkDiagnostic:
    """Diagnóstico de rede — verifica alcançabilidade."""

    def test_auth_endpoint_reachable(self, config):
        diag = diagnose_endpoint(config["auth_url"], connect_timeout=10)
        if not diag.dns_resolved:
            pytest.skip(f"DNS não resolvido: {diag.hypothesis}")
        assert diag.tcp_reachable, f"TCP falhou: {diag.error_detail}"

    def test_api_endpoint_reachable(self, config):
        diag = diagnose_endpoint(config["api_base_url"], connect_timeout=10)
        if not diag.dns_resolved:
            pytest.skip(f"DNS não resolvido: {diag.hypothesis}")
        assert diag.tcp_reachable, f"TCP falhou: {diag.error_detail}"


# ─── Testes Reais GET (requerem token válido) ────────────────────────────────


class TestGetBeneficiaries:
    """GET /v1/beneficiaries — consulta de colaboradores."""

    def test_listar_colaboradores(self, client, base_url, auth_result):
        """Aprovado SOMENTE com resposta real 200 ou 204."""
        if not auth_result.success:
            pytest.skip(
                f"Auth falhou: {auth_result.execution_status} — {auth_result.error_detail}"
            )

        url = f"{base_url}/beneficiaries"
        assert is_homologacao_url(url)

        result = client.execute(
            operation_name="Consulta dos colaboradores",
            method="GET",
            url=url,
            params={"page": "0"},
        )

        assert result.execution_status != "BLOCKED_BY_AUTH", (
            f"Bloqueado: {result.error_message}"
        )
        assert result.status_code in (200, 204), (
            f"Status: {result.status_code}. "
            f"Erro: {result.execution_status} — {result.error_message}"
        )

    def test_resposta_tem_estrutura_esperada(self, client, base_url, auth_result):
        """Valida contrato mínimo da resposta GET."""
        if not auth_result.success:
            pytest.skip("Auth falhou")

        url = f"{base_url}/beneficiaries"
        result = client.execute(
            operation_name="Consulta colaboradores - estrutura",
            method="GET",
            url=url,
            params={"page": "0"},
        )

        if result.status_code == 204:
            pytest.skip("204 No Content — sem dados para validar estrutura")

        if result.status_code != 200:
            pytest.skip(f"Não obteve 200. Status: {result.status_code}")

        body = result.response_body
        assert isinstance(body, dict), "Resposta não é JSON object"

        # Campos documentados
        assert "content" in body or "total" in body, (
            f"Campos esperados ausentes. Recebidos: {list(body.keys())}"
        )

        if "content" in body and body["content"]:
            item = body["content"][0]
            assert "name" in item, f"Campo 'name' ausente. Campos: {list(item.keys())}"

    def test_paginacao(self, client, base_url, auth_result):
        """Verifica se a resposta contém informação de paginação."""
        if not auth_result.success:
            pytest.skip("Auth falhou")

        url = f"{base_url}/beneficiaries"
        result = client.execute(
            operation_name="Consulta colaboradores - paginação",
            method="GET",
            url=url,
            params={"page": "0"},
        )

        if result.status_code != 200:
            pytest.skip(f"Status {result.status_code}")

        body = result.response_body
        if isinstance(body, dict) and "pageable" in body:
            assert "page" in body["pageable"]
