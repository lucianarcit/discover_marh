"""Testes unitários para o parser de cURL.

Não faz chamadas reais à API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from discover_alelo.curl_parser import parse_curl_string, parse_curl_file


class TestExtractUrl:
    """Testes de extração de URL."""

    def test_extract_simple_url(self):
        curl = 'curl "https://api.example.com/v1/users"'
        result = parse_curl_string(curl)
        assert result["url"] == "https://api.example.com/v1/users"

    def test_extract_url_with_query_params(self):
        curl = 'curl "https://api.example.com/v1/users?page=1&size=10"'
        result = parse_curl_string(curl)
        assert result["url_base"] == "https://api.example.com/v1/users"
        assert result["query_parameters"]["page"] == "1"
        assert result["query_parameters"]["size"] == "10"

    def test_extract_url_single_quotes(self):
        curl = "curl 'https://api.example.com/v1/data'"
        result = parse_curl_string(curl)
        assert result["url"] == "https://api.example.com/v1/data"

    def test_extract_url_double_quotes(self):
        curl = 'curl "https://api.example.com/v1/data"'
        result = parse_curl_string(curl)
        assert result["url"] == "https://api.example.com/v1/data"


class TestExtractMethod:
    """Testes de extração do método HTTP."""

    def test_explicit_get(self):
        curl = 'curl -X GET "https://api.example.com/v1/users"'
        result = parse_curl_string(curl)
        assert result["method"] == "GET"

    def test_explicit_post(self):
        curl = 'curl -X POST "https://api.example.com/v1/users"'
        result = parse_curl_string(curl)
        assert result["method"] == "POST"

    def test_explicit_put(self):
        curl = 'curl -X PUT "https://api.example.com/v1/users/1"'
        result = parse_curl_string(curl)
        assert result["method"] == "PUT"

    def test_explicit_delete(self):
        curl = 'curl -X DELETE "https://api.example.com/v1/users/1"'
        result = parse_curl_string(curl)
        assert result["method"] == "DELETE"

    def test_implicit_get_without_method(self):
        curl = 'curl "https://api.example.com/v1/users"'
        result = parse_curl_string(curl)
        assert result["method"] == "GET"

    def test_implicit_post_with_data(self):
        curl = 'curl "https://api.example.com/v1/users" -d \'{"name":"test"}\''
        result = parse_curl_string(curl)
        assert result["method"] == "POST"

    def test_long_request_flag(self):
        curl = 'curl --request PATCH "https://api.example.com/v1/users/1"'
        result = parse_curl_string(curl)
        assert result["method"] == "PATCH"


class TestExtractHeaders:
    """Testes de extração de headers."""

    def test_single_header(self):
        curl = 'curl -H "Content-Type: application/json" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["headers"]["Content-Type"] == "application/json"

    def test_multiple_headers(self):
        curl = (
            'curl -H "Content-Type: application/json" '
            '-H "Authorization: Bearer token123" '
            '-H "X-Custom: value" '
            '"https://api.example.com"'
        )
        result = parse_curl_string(curl)
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["headers"]["Authorization"] == "Bearer token123"
        assert result["headers"]["X-Custom"] == "value"

    def test_header_with_hyphen(self):
        curl = 'curl -H "X-IBM-Client-Id: abc123" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["headers"]["X-IBM-Client-Id"] == "abc123"

    def test_header_with_underscore(self):
        curl = 'curl -H "APP_VERSION: 8.55.0 (2026072003)" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["headers"]["APP_VERSION"] == "8.55.0 (2026072003)"

    def test_header_value_with_spaces(self):
        curl = 'curl -H "User-Agent: Mozilla/5.0 (Windows NT 10.0)" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["headers"]["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0)"

    def test_long_header_flag(self):
        curl = 'curl --header "Accept: text/html" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["headers"]["Accept"] == "text/html"


class TestExtractBody:
    """Testes de extração de body."""

    def test_json_body(self):
        curl = 'curl -X POST -d \'{"name":"test","age":30}\' "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["body"] == {"name": "test", "age": 30}
        assert result["body_type"] == "json"

    def test_form_urlencoded_body(self):
        curl = 'curl -X POST -d "grant_type=client_credentials&client_id=abc" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["body"]["grant_type"] == "client_credentials"
        assert result["body"]["client_id"] == "abc"
        assert result["body_type"] == "form-urlencoded"

    def test_data_urlencode(self):
        curl = (
            "curl -X POST "
            '"https://api.example.com/token" '
            "--data-urlencode 'grant_type=refresh_token' "
            "--data-urlencode 'refresh_token=abc123'"
        )
        result = parse_curl_string(curl)
        assert result["body"]["grant_type"] == "refresh_token"
        assert result["body"]["refresh_token"] == "abc123"
        assert result["body_type"] == "form-urlencoded"

    def test_data_urlencode_encoded_values(self):
        """Testa --data-urlencode com valores percent-encoded."""
        curl = (
            'curl -X POST "https://api.example.com/token" '
            "--data-urlencode 'grant%5Ftype=refresh%5Ftoken' "
            "--data-urlencode 'refresh%5Ftoken=abc%2D123'"
        )
        result = parse_curl_string(curl)
        assert result["body"]["grant_type"] == "refresh_token"
        assert result["body"]["refresh_token"] == "abc-123"

    def test_data_raw(self):
        curl = 'curl -X POST --data-raw \'{"key":"value"}\' "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["body"] == {"key": "value"}
        assert result["body_type"] == "json"


class TestEdgeCases:
    """Testes de casos especiais."""

    def test_multiline_curl(self):
        curl = """curl -X POST \\
    "https://api.example.com/token" \\
    -H "Content-Type: application/json" \\
    -d '{"test": true}'"""
        result = parse_curl_string(curl)
        assert result["method"] == "POST"
        assert result["url"] == "https://api.example.com/token"
        assert result["headers"]["Content-Type"] == "application/json"

    def test_basic_auth_in_header(self):
        curl = 'curl -H "Authorization: Basic dXNlcjpwYXNz" "https://api.example.com"'
        result = parse_curl_string(curl)
        assert result["basic_auth"] == "Basic dXNlcjpwYXNz"

    def test_real_get_token_format(self):
        """Testa o formato real do get_token.txt do projeto."""
        curl = """curl -X POST \\
    "https://api.homologacaoalelo.com.br/alelo/uat/identity-server-auth/v1/oauth2/token" \\
    -H "APP_VERSION: 8.55.0 (2026072003)" \\
    -H "AUTH_TYPE: IS-ALELO" \\
    -H "Authorization: Basic dGVzdDp0ZXN0" \\
    -H "Content-Type: application/x-www-form-urlencoded" \\
    -H "FNP: D24E6833-4B70-495D-A50C-A4C47743CDCE" \\
    -H "PLATFORM: IOS" \\
    -H "x-ibm-client-id: test-id-123" \\
    --data-urlencode 'grant%5Ftype=refresh%5Ftoken' \\
    --data-urlencode 'refresh%5Ftoken=test-refresh-token'"""

        result = parse_curl_string(curl)
        assert result["method"] == "POST"
        assert "homologacaoalelo" in result["url"]
        assert result["headers"]["APP_VERSION"] == "8.55.0 (2026072003)"
        assert result["headers"]["AUTH_TYPE"] == "IS-ALELO"
        assert result["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
        assert result["headers"]["FNP"] == "D24E6833-4B70-495D-A50C-A4C47743CDCE"
        assert result["headers"]["PLATFORM"] == "IOS"
        assert result["body"]["grant_type"] == "refresh_token"
        assert result["body"]["refresh_token"] == "test-refresh-token"
        assert result["body_type"] == "form-urlencoded"
        assert result["content_type"] == "application/x-www-form-urlencoded"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_curl_file("/nonexistent/path/curl.txt")

    def test_empty_curl(self):
        result = parse_curl_string("curl")
        assert result["method"] == "GET"
        assert result["url"] == ""
