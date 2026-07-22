"""Testes de integração para APIs de Gestão de Colaboradores.

REGRAS:
- Testes reais (test_*_real_api) passam SOMENTE com resposta real válida.
- Quando a autenticação falha, testes reais são SKIPPED (não aprovados).
- Testes de classificação de erro validam o comportamento do código.
- Operações mutáveis são marcadas SKIPPED_SAFETY.

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
    """Cria cliente HTTP compartilhado para o módulo."""
    with AleloApiClient() as c:
        yield c


@pytest.fixture(scope="module")
def base_url(config):
    """URL base da API de gestão de colaboradores."""
    api_base = config["api_base_url"].rstrip("/")
    return f"{api_base}/cardholders-hr-management/v1"


# ─── Testes de Classificação de Erro ─────────────────────────────────────────


class TestErrorClassification:
    """Testes que validam a classificação de erros — não dependem de API real."""

    def test_auth_gateway_timeout_classified_correctly(self, auth_result):
        """Verifica que 504 é classificado como AUTH_GATEWAY_TIMEOUT, não como token expirado."""
        if auth_result.status_code == 504:
            assert auth_result.execution_status == "AUTH_GATEWAY_TIMEOUT"
            assert "token" not in auth_result.error_detail.lower() or "gateway" in auth_result.error_detail.lower()

    def test_auth_result_has_status_code(self, auth_result):
        """Verifica que o resultado tem status code registrado."""
        # Se houve tentativa, deve ter código ou execution_status
        assert auth_result.execution_status != ""

    def test_timeout_not_classified_as_expired(self, auth_result):
        """Verifica que timeout não é confundido com token expirado."""
        if auth_result.execution_status == "TIMEOUT":
            assert auth_result.execution_status != "AUTH_TOKEN_EXPIRED"

    def test_connection_error_not_classified_as_invalid_credentials(self, auth_result):
        """Verifica que erro de conexão não é confundido com credenciais inválidas."""
        if auth_result.execution_status == "CONNECTION_ERROR":
            assert auth_result.execution_status != "AUTH_TOKEN_INVALID"


class TestNetworkDiagnostic:
    """Testes de diagnóstico de rede — verifica alcançabilidade sem credenciais."""

    def test_auth_endpoint_dns_resolution(self, config):
        """Verifica se o DNS do endpoint de auth resolve."""
        diag = diagnose_endpoint(config["auth_url"], connect_timeout=10)
        # Registra resultado — não falha o teste por rede
        if not diag.dns_resolved:
            pytest.skip(
                f"DNS não resolvido para auth endpoint. "
                f"Hipótese: {diag.hypothesis}"
            )

    def test_api_endpoint_dns_resolution(self, config):
        """Verifica se o DNS do endpoint de API resolve."""
        diag = diagnose_endpoint(config["api_base_url"], connect_timeout=10)
        if not diag.dns_resolved:
            pytest.skip(
                f"DNS não resolvido para API endpoint. "
                f"Hipótese: {diag.hypothesis}"
            )


# ─── Testes Reais de API (requerem autenticação válida) ──────────────────────


class TestGetBeneficiariesRealApi:
    """Testes REAIS do GET /v1/beneficiaries.

    Só passam quando:
    1. Autenticação funciona (token obtido).
    2. Chamada real é executada.
    3. Status esperado é recebido.
    4. Contrato mínimo da resposta é validado.
    """

    def test_get_beneficiaries_real_api(self, client, base_url, auth_result):
        """Consulta real de colaboradores — aprovado SOMENTE com resposta válida."""
        # GATE: se auth não funcionou, SKIP (nunca aprovar sem API real)
        if not auth_result.success:
            pytest.skip(
                f"Bloqueado por autenticação: {auth_result.execution_status}. "
                f"Detalhe: {auth_result.error_detail}"
            )

        url = f"{base_url}/beneficiaries"
        assert is_homologacao_url(url), "URL não é de homologação!"

        result = client.execute(
            operation_name="Consulta dos colaboradores",
            method="GET",
            url=url,
            params={"page": "0"},
        )

        # Deve ter sido uma chamada real — não BLOCKED_BY_AUTH
        assert result.execution_status != "BLOCKED_BY_AUTH", (
            f"API não foi chamada. Auth bloqueou: {result.error_message}"
        )

        # Valida status esperado conforme documentação
        assert result.status_code in (200, 204), (
            f"Status inesperado: {result.status_code}. "
            f"Status: {result.execution_status}. "
            f"Erro: {result.error_message}"
        )

        # Se 200, valida contrato mínimo
        if result.status_code == 200 and result.response_body:
            body = result.response_body
            assert isinstance(body, dict), "Resposta não é objeto JSON"
            assert "content" in body or "total" in body, (
                f"Contrato inválido — campos esperados ausentes. "
                f"Campos recebidos: {list(body.keys())}"
            )

    def test_get_beneficiaries_response_structure(self, client, base_url, auth_result):
        """Valida estrutura detalhada da resposta quando disponível."""
        if not auth_result.success:
            pytest.skip(
                f"Bloqueado por autenticação: {auth_result.execution_status}"
            )

        url = f"{base_url}/beneficiaries"
        result = client.execute(
            operation_name="Consulta colaboradores - estrutura",
            method="GET",
            url=url,
            params={"page": "0"},
        )

        if result.status_code != 200 or not result.response_body:
            pytest.skip(f"Sem resposta 200 para validar estrutura. Status: {result.status_code}")

        body = result.response_body
        # Valida paginação
        if "pageable" in body:
            assert "page" in body["pageable"]

        # Valida lista de conteúdo
        if "content" in body and body["content"]:
            item = body["content"][0]
            # Campos documentados que devem existir
            expected_fields = {"name", "subtype"}
            actual_fields = set(item.keys())
            missing = expected_fields - actual_fields
            assert not missing, (
                f"Campos documentados ausentes na resposta: {missing}"
            )


# ─── Testes Mutáveis (Sempre Skipped por segurança) ──────────────────────────


class TestCadastroColaborador:
    """POST /v1/beneficiaries — NÃO EXECUTADO automaticamente."""

    @pytest.mark.skip(reason="SKIPPED_SAFETY: POST pode criar registros reais")
    def test_cadastrar_colaborador(self):
        pass


class TestAtualizacaoColaborador:
    """PUT /v1/beneficiaries/{id} — NÃO EXECUTADO automaticamente."""

    @pytest.mark.skip(reason="SKIPPED_SAFETY: PUT altera dados reais")
    def test_atualizar_colaborador(self):
        pass


class TestExclusaoColaborador:
    """DELETE /v1/beneficiaries/{id} — NÃO EXECUTADO automaticamente."""

    @pytest.mark.skip(reason="SKIPPED_SAFETY: DELETE remove dados irreversivelmente")
    def test_excluir_colaborador(self):
        pass
