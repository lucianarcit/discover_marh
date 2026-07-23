"""Mock do cliente ma-hr-orch para POC local."""

from __future__ import annotations

import json
from pathlib import Path

from marh_agent.clients.ma_hr_orch import MaHrOrchClient


_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class MockMaHrOrchClient(MaHrOrchClient):
    """Implementação mock que lê de fixtures JSON."""

    def __init__(self) -> None:
        self._orders = self._load_fixture("orders.json")
        self._collaborators = self._load_fixture("collaborators.json")
        # Flags para simular erros (usadas em testes)
        self.simulate_error: int | None = None
        self.simulate_timeout: bool = False

    def _load_fixture(self, filename: str) -> list[dict]:
        filepath = _FIXTURES_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _check_simulated_errors(self) -> None:
        if self.simulate_timeout:
            raise TimeoutError("Simulated timeout")
        if self.simulate_error == 403:
            raise PermissionError("403")
        if self.simulate_error == 404:
            raise LookupError("404")
        if self.simulate_error == 429:
            raise ConnectionError("429")
        if self.simulate_error == 500:
            raise RuntimeError("500")

    def search_collaborator_by_name(
        self, company_id: str, name: str
    ) -> dict:
        self._check_simulated_errors()
        results = [
            c for c in self._collaborators
            if name.lower() in c.get("name", "").lower()
        ]
        return {"total": len(results), "content": results}

    def search_collaborator_by_document(
        self, company_id: str, cpf: str
    ) -> dict:
        self._check_simulated_errors()
        # Normalize CPF for comparison
        cpf_digits = "".join(c for c in cpf if c.isdigit())
        results = [
            c for c in self._collaborators
            if "".join(
                ch for ch in c.get("documentNumber", "") if ch.isdigit()
            ) == cpf_digits
        ]
        return {"total": len(results), "content": results}

    def get_order(self, company_id: str, order_number: str) -> dict:
        self._check_simulated_errors()
        for order in self._orders:
            if order.get("orderNumber") == order_number:
                return {"found": True, "order": order}
        return {"found": False, "order": None}

    def list_orders(self, company_id: str) -> dict:
        self._check_simulated_errors()
        return {"total": len(self._orders), "content": self._orders}

    def list_orders_by_status(
        self, company_id: str, status: str
    ) -> dict:
        self._check_simulated_errors()
        results = [
            o for o in self._orders
            if o.get("status") == status
        ]
        return {"total": len(results), "content": results}
