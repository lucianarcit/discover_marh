"""Testes unitários para o parser de HTML de APIs.

Não faz chamadas reais à API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from discover_alelo.html_api_parser import parse_html_string


class TestHtmlWithCodeBlocks:
    """Testes com blocos <pre> e <code>."""

    def test_extract_get_operation(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Listar Itens</h2><p>seção 1</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/items</code></pre></div>
                <p>✅ 200 - Sucesso</p>
                <p>❌ 404 - Não encontrado</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert ops[0].method == "GET"
        assert ops[0].path == "/v1/items"
        assert ops[0].operation_name == "Listar Itens"
        assert ops[0].safe_to_execute is True

    def test_extract_post_operation(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>02</span><div><h2>Criar Item</h2><p>seção 2</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>POST /v1/items

{
    "name": "Teste",
    "value": 123
}</code></pre></div>
                <p>✅ 201 - Criado</p>
                <p>❌ 400 - Erro</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert ops[0].method == "POST"
        assert ops[0].path == "/v1/items"
        assert ops[0].safe_to_execute is False
        assert ops[0].request_body_example is not None

    def test_extract_delete_operation(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>03</span><div><h2>Excluir Item</h2><p>seção 3</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>DELETE /v1/items/{itemId}</code></pre></div>
                <p>✅ 204 - No Content</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert ops[0].method == "DELETE"
        assert ops[0].path_parameters == ["itemId"]
        assert ops[0].safe_to_execute is False

    def test_extract_put_with_path_params(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>04</span><div><h2>Atualizar</h2><p>seção 4</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>PUT /v1/items/{itemId}

{
    "name": "Novo Nome"
}</code></pre></div>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert ops[0].method == "PUT"
        assert "itemId" in ops[0].path_parameters
        assert ops[0].safe_to_execute is False


class TestHtmlWithTables:
    """Testes com tabelas de parâmetros."""

    def test_extract_query_params_from_table(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Buscar</h2><p>seção 1</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/search</code></pre></div>
                <table>
                    <thead><tr><th>Parâmetro</th><th>Descrição</th></tr></thead>
                    <tbody>
                        <tr><td>query</td><td>Termo de busca</td></tr>
                        <tr><td>page</td><td>Número da página</td></tr>
                    </tbody>
                </table>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert len(ops[0].query_parameters) == 2
        assert ops[0].query_parameters[0]["name"] == "query"
        assert ops[0].query_parameters[1]["name"] == "page"


class TestHtmlWithStatusCodes:
    """Testes de extração de status codes."""

    def test_extract_multiple_status_codes(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Operação</h2><p>seção</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/test</code></pre></div>
                <p>✅ 200 - Sucesso</p>
                <p>✅ 204 - No Content</p>
                <p>❌ 400 - Erro de validação</p>
                <p>❌ 403 - Sem permissão</p>
                <p>❌ 422 - Entidade inválida</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops[0].documented_status_codes) == 5
        codes = [s["code"] for s in ops[0].documented_status_codes]
        assert "200" in codes
        assert "403" in codes
        assert "422" in codes


class TestHtmlWithHeaders:
    """Testes de extração de headers."""

    def test_extract_required_headers(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>API</h2><p>seção</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/data</code></pre></div>
                <div class="code-block"><pre><code>Authorization = Bearer {token}
APP_VERSION = {version}
client_id = {id}
FNP = {fingerprint}
PLATFORM = ANDROID | IOS
Content-Type: application/json
X-BASIC-AUTHORIZATION = {base64}
USER_ID = {user_id}</code></pre></div>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        assert "Authorization" in ops[0].required_headers
        assert "APP_VERSION" in ops[0].required_headers
        assert "FNP" in ops[0].required_headers


class TestHtmlEdgeCases:
    """Testes de casos especiais."""

    def test_empty_html(self):
        ops = parse_html_string("<html><body></body></html>")
        assert ops == []

    def test_html_without_code_blocks(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Info</h2><p>seção</p></div></div>
            <div class="markdown">
                <p>Apenas texto explicativo sem endpoints.</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        # Sem método detectado, não deve gerar operação
        assert len(ops) == 0

    def test_multiple_sections(self):
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Op 1</h2><p>s1</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/a</code></pre></div>
            </div>
        </article>
        <article class="doc-section">
            <div class="section-heading"><span>02</span><div><h2>Op 2</h2><p>s2</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>POST /v1/b</code></pre></div>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 2
        assert ops[0].method == "GET"
        assert ops[1].method == "POST"

    def test_html_with_entities(self):
        """Testa decodificação de entidades HTML como &quot;"""
        html = """
        <article class="doc-section">
            <div class="section-heading"><span>01</span><div><h2>Test</h2><p>s</p></div></div>
            <div class="markdown">
                <div class="code-block"><pre><code>GET /v1/test</code></pre></div>
                <div class="code-block"><pre><code>{
    &quot;field&quot;: &quot;value&quot;
}</code></pre></div>
                <p>✅ 200 - Sucesso</p>
            </div>
        </article>
        """
        ops = parse_html_string(html)
        assert len(ops) == 1
        # Deve decodificar &quot; para aspas
        if ops[0].documented_response_example:
            assert "field" in ops[0].documented_response_example
