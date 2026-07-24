"""Interface abstrata para recuperação vetorial de chunks do corpus.

Responsabilidade exclusiva: dado uma query de texto, retornar os trechos
do corpus aprovado mais relevantes com seus scores de similaridade.

O que esta interface NÃO faz:
- não gera texto
- não interpreta intenção
- não monta resposta ao usuário
- não filtra por threshold (responsabilidade do BedrockRagKnowledgeClient)
- não conhece o Router, o Orchestrator ou o KnowledgeClient
- não importa boto3 nem SDK AWS
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from marh_agent.domain.rag_exceptions import InvalidRagRequestError
from marh_agent.domain.rag_models import RetrievedChunk


class Retriever(ABC):
    """Interface para recuperação vetorial de chunks do corpus aprovado."""

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Recupera os chunks mais relevantes para a query fornecida.

        Valida os parâmetros antes de delegar à implementação concreta.
        Retorno vazio significa ausência de evidência — não é erro.

        Args:
            query: Texto da consulta. Não pode ser vazio.
            top_k: Número máximo de chunks a retornar. Deve ser > 0.

        Returns:
            Lista de RetrievedChunk ordenada por relevância decrescente.
            Lista vazia quando nenhum chunk é encontrado.

        Raises:
            InvalidRagRequestError: query vazia ou top_k <= 0.
            RetrieverError: falha na recuperação (lançada pelas implementações).
        """
        if not query or not query.strip():
            raise InvalidRagRequestError("query não pode ser vazia ou somente espaços")
        if top_k <= 0:
            raise InvalidRagRequestError(f"top_k deve ser maior que zero, recebido: {top_k}")
        return self._retrieve(query=query.strip(), top_k=top_k)

    @abstractmethod
    def _retrieve(
        self,
        query: str,
        *,
        top_k: int,
    ) -> list[RetrievedChunk]:
        """Implementação concreta da recuperação.

        Recebe query já validada e sem espaços extras.
        Nunca lança exceções específicas de boto3 — deve mapeá-las
        para RetrieverError antes de propagar.
        """
