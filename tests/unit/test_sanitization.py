"""Testes unitários para o módulo de sanitização.

Não faz chamadas reais à API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from discover_alelo.sanitization import sanitize, sanitize_headers, sanitize_url, REDACTED


class TestSanitizeDict:
    """Testes de sanitização de dicionários."""

    def test_redacts_authorization(self):
        data = {"Authorization": "Bearer abc123xyz"}
        result = sanitize(data)
        assert result["Authorization"] == REDACTED

    def test_redacts_access_token(self):
        data = {"access_token": "secret-token-value"}
        result = sanitize(data)
        assert result["access_token"] == REDACTED

    def test_redacts_client_secret(self):
        data = {"client_secret": "my-secret"}
        result = sanitize(data)
        assert result["client_secret"] == REDACTED

    def test_redacts_document_number(self):
        data = {"documentNumber": "12345678901"}
        result = sanitize(data)
        assert result["documentNumber"] == REDACTED

    def test_redacts_email(self):
        data = {"email": "user@example.com"}
        result = sanitize(data)
        assert result["email"] == REDACTED

    def test_redacts_phone(self):
        data = {"phoneNumber": "11999887766"}
        result = sanitize(data)
        assert result["phoneNumber"] == REDACTED

    def test_redacts_user_id(self):
        data = {"user_id": "abc123"}
        result = sanitize(data)
        assert result["user_id"] == REDACTED

    def test_redacts_fnp(self):
        data = {"FNP": "D24E6833-4B70-495D-A50C-A4C47743CDCE"}
        result = sanitize(data)
        assert result["FNP"] == REDACTED

    def test_preserves_non_sensitive_fields(self):
        data = {
            "name": "João Silva",
            "total": 10,
            "page": 1,
            "isHomeDelivery": False,
            "subtype": "BRANCH",
        }
        result = sanitize(data)
        assert result["name"] == "João Silva"
        assert result["total"] == 10
        assert result["page"] == 1
        assert result["isHomeDelivery"] is False
        assert result["subtype"] == "BRANCH"

    def test_mixed_sensitive_and_safe(self):
        data = {
            "name": "Teste",
            "email": "test@example.com",
            "status": "active",
            "client_secret": "secret",
        }
        result = sanitize(data)
        assert result["name"] == "Teste"
        assert result["email"] == REDACTED
        assert result["status"] == "active"
        assert result["client_secret"] == REDACTED


class TestSanitizeList:
    """Testes de sanitização de listas."""

    def test_sanitize_list_of_dicts(self):
        data = [
            {"name": "A", "email": "a@test.com"},
            {"name": "B", "email": "b@test.com"},
        ]
        result = sanitize(data)
        assert result[0]["name"] == "A"
        assert result[0]["email"] == REDACTED
        assert result[1]["name"] == "B"
        assert result[1]["email"] == REDACTED

    def test_sanitize_empty_list(self):
        assert sanitize([]) == []

    def test_sanitize_list_of_strings(self):
        data = ["hello", "Bearer token123", "world"]
        result = sanitize(data)
        assert result[0] == "hello"
        assert REDACTED in result[1]
        assert result[2] == "world"


class TestSanitizeNested:
    """Testes de sanitização de objetos aninhados."""

    def test_nested_dict(self):
        data = {
            "user": {
                "name": "Test",
                "documentNumber": "12345678901",
                "address": {
                    "street": "Rua Test",
                    "postalCode": "01234567",
                },
            }
        }
        result = sanitize(data)
        assert result["user"]["name"] == "Test"
        assert result["user"]["documentNumber"] == REDACTED
        assert result["user"]["address"]["street"] == "Rua Test"
        assert result["user"]["address"]["postalCode"] == REDACTED

    def test_deeply_nested(self):
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "access_token": "should-be-redacted",
                        "safe_field": "visible",
                    }
                }
            }
        }
        result = sanitize(data)
        assert result["level1"]["level2"]["level3"]["access_token"] == REDACTED
        assert result["level1"]["level2"]["level3"]["safe_field"] == "visible"

    def test_list_inside_dict(self):
        data = {
            "content": [
                {"beneficiaryId": "secret", "name": "Test"},
            ]
        }
        result = sanitize(data)
        assert result["content"][0]["beneficiaryId"] == REDACTED
        assert result["content"][0]["name"] == "Test"


class TestSanitizeHeaders:
    """Testes de sanitização de headers HTTP."""

    def test_redacts_auth_header(self):
        headers = {
            "Authorization": "Bearer secret-token",
            "Content-Type": "application/json",
        }
        result = sanitize_headers(headers)
        assert result["Authorization"] == REDACTED
        assert result["Content-Type"] == "application/json"

    def test_redacts_x_basic_authorization(self):
        headers = {
            "X-BASIC-AUTHORIZATION": "Basic c2VjcmV0",
            "Accept": "application/json",
        }
        result = sanitize_headers(headers)
        assert result["X-BASIC-AUTHORIZATION"] == REDACTED
        assert result["Accept"] == "application/json"

    def test_redacts_ibm_client_id(self):
        headers = {"x-ibm-client-id": "some-id"}
        result = sanitize_headers(headers)
        assert result["x-ibm-client-id"] == REDACTED


class TestSanitizeUrl:
    """Testes de sanitização de URLs."""

    def test_removes_token_from_query(self):
        url = "https://api.example.com/v1/data?access_token=secret123&page=1"
        result = sanitize_url(url)
        assert "secret123" not in result
        assert "page=1" in result

    def test_preserves_safe_params(self):
        url = "https://api.example.com/v1/data?page=1&size=10"
        result = sanitize_url(url)
        assert "page=1" in result
        assert "size=10" in result

    def test_no_query_params(self):
        url = "https://api.example.com/v1/data"
        result = sanitize_url(url)
        assert result == url


class TestPreservation:
    """Testes que garantem que campos seguros são preservados."""

    def test_preserves_numeric_values(self):
        data = {"total": 100, "page": 0, "size": 10}
        result = sanitize(data)
        assert result == data

    def test_preserves_boolean_values(self):
        data = {"isActive": True, "isDeleted": False}
        result = sanitize(data)
        assert result == data

    def test_preserves_none_values(self):
        data = {"products": None, "notes": None}
        result = sanitize(data)
        assert result["products"] is None
        assert result["notes"] is None

    def test_preserves_operation_status_fields(self):
        data = {
            "execution_status": "SUCCESS",
            "method": "GET",
            "status_code": 200,
            "duration_ms": 450,
            "success": True,
        }
        result = sanitize(data)
        assert result == data
