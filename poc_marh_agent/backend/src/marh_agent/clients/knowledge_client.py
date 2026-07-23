"""Interface abstrata para o cliente de conhecimento (RAG futuro)."""

from __future__ import annotations

from abc import ABC, abstractmethod


class KnowledgeClient(ABC):
    """Interface para consulta ao base de conhecimento MARH.

    Produção futura: S3 Vectors + Bedrock embeddings.
    Mock atual: conteúdo pré-definido por tópico, derivado de marh_feature_knowledge.md.
    """

    @abstractmethod
    def query(self, topic: str) -> dict:
        """Consulta conhecimento por tópico.

        Args:
            topic: identificador do tópico (ex: "MARH_OVERVIEW", "ORDER_PROCESS")

        Returns:
            dict com keys:
              - content: str — resposta aprovada
              - source_section: str — seção do markdown de origem
              - data_classification: str — sempre "APPROVED_KNOWLEDGE_MOCK"
              - found: bool
        """
