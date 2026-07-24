"""Exceções de domínio do pipeline RAG — independentes de fornecedor.

Hierarquia:
    RagError
      ├── RetrieverError
      ├── LanguageModelError
      └── InvalidRagRequestError

As implementações concretas (Bedrock, OpenSearch, etc.) devem capturar
exceções específicas do SDK e re-lançar como subclasses destas,
nunca expondo tipos do boto3 ou botocore às camadas superiores.
"""

from __future__ import annotations


class RagError(Exception):
    """Erro base do pipeline RAG."""


class RetrieverError(RagError):
    """Falha durante a recuperação de chunks do corpus.

    Exemplos de causas mapeadas pelas implementações:
    - Knowledge Base inacessível
    - Timeout de recuperação
    - Resposta malformada do vector store
    """


class LanguageModelError(RagError):
    """Falha durante a geração de texto pelo modelo de linguagem.

    Exemplos de causas mapeadas pelas implementações:
    - Modelo indisponível
    - Throttling
    - Resposta malformada
    """


class InvalidRagRequestError(RagError):
    """Requisição inválida para o pipeline RAG.

    Lançada quando query vazia, top_k inválido, prompts vazios
    ou context_chunks vazio são fornecidos.
    Não expõe conteúdo dos chunks na mensagem.
    """
