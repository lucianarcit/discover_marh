"""Interface abstrata do cliente ma-hr-orch."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MaHrOrchClient(ABC):
    """Interface para o orquestrador ma-hr-orch."""

    @abstractmethod
    def search_collaborator_by_name(
        self, company_id: str, name: str
    ) -> dict:
        ...

    @abstractmethod
    def search_collaborator_by_document(
        self, company_id: str, cpf: str
    ) -> dict:
        ...

    @abstractmethod
    def get_order(
        self, company_id: str, order_number: str
    ) -> dict:
        ...

    @abstractmethod
    def list_orders(
        self, company_id: str
    ) -> dict:
        ...

    @abstractmethod
    def list_orders_by_status(
        self, company_id: str, status: str
    ) -> dict:
        ...
