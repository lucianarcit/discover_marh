"""Interface abstrata para geração de texto fundamentada em chunks recuperados.

Responsabilidade exclusiva: dado um prompt de sistema, a query do usuário e
os chunks aprovados pelo Retriever, produzir uma resposta textual fundamentada.

O que esta interface NÃO faz:
- não realiza recuperação vetorial
- não conhece Knowledge Base nem vector store
- não conhece o Router, o Orchestrator ou o KnowledgeClient
- não interpreta intenção
- não recebe dados corporativos (colaboradores, pedidos, CPF)
- não executa actions nem escrita
- não retorna HTML
- não importa boto3 nem SDK AWS
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from marh_agent.domain.rag_exceptions import InvalidRagRequestError
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk


class LanguageModelClient(ABC):
    """Interface para geração de texto a partir de chunks aprovados."""

    def generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult:
        """Gera uma resposta textual fundamentada nos chunks fornecidos.

        Valida os parâmetros antes de delegar à implementação concreta.
        O texto produzido é texto plano — nunca tratado como HTML.

        Args:
            system_prompt: Instrução de sistema com restrições de groundedness.
                           Não pode ser vazio.
            user_query: Pergunta original do usuário no contexto da intenção.
                        Não pode ser vazia. Não deve conter CPF, dados corporativos
                        nem informações sensíveis.
            context_chunks: Trechos do corpus aprovado já filtrados pelo threshold.
                            Não pode ser vazio — se não há evidência, o pipeline
                            deve retornar found=False sem chamar esta interface.

        Returns:
            GenerationResult com o texto gerado e metadados de uso.

        Raises:
            InvalidRagRequestError: system_prompt, user_query ou context_chunks vazio.
            LanguageModelError: falha na geração (lançada pelas implementações).
        """
        if not system_prompt or not system_prompt.strip():
            raise InvalidRagRequestError("system_prompt não pode ser vazio")
        if not user_query or not user_query.strip():
            raise InvalidRagRequestError("user_query não pode ser vazia")
        if not context_chunks:
            raise InvalidRagRequestError(
                "context_chunks não pode ser vazio — "
                "se não há evidência, retornar found=False sem invocar geração"
            )
        return self._generate(
            system_prompt=system_prompt.strip(),
            user_query=user_query.strip(),
            context_chunks=context_chunks,
        )

    @abstractmethod
    def _generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult:
        """Implementação concreta da geração.

        Recebe parâmetros já validados.
        Nunca lança exceções específicas de boto3 — deve mapeá-las
        para LanguageModelError antes de propagar.
        O texto retornado é texto plano — não deve ser interpretado como HTML.
        """
