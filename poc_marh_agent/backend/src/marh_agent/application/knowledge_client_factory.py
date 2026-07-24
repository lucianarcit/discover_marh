"""Factory de KnowledgeClient — seleciona implementação por KNOWLEDGE_MODE.

KNOWLEDGE_MODE=MOCK      → MockKnowledgeClient (comportamento atual)
KNOWLEDGE_MODE=BEDROCK_RAG → BedrockRagKnowledgeClient + Retriever + LLM

Esta função é o único ponto de composição do pipeline RAG.
Usada por lambda_handler e local_api (cold start).

Regras:
- Não fazer fallback silencioso para MOCK quando BEDROCK_RAG falhar.
- Não criar cliente boto3 quando KNOWLEDGE_MODE=MOCK.
- Não exigir BEDROCK_KNOWLEDGE_BASE_ID quando KNOWLEDGE_MODE=MOCK.
- Não exigir BEDROCK_MODEL_ID quando KNOWLEDGE_MODE=MOCK.
- Não realizar chamada de rede no construtor.
- Não expor valores sensíveis em mensagens de erro.

STEP_7_COMPONENT=COMPOSITION_ROOT
DEFAULT_KNOWLEDGE_MODE=MOCK
RAG_PIPELINE_WIRED=true
AWS_CALLS_DURING_TESTS=ZERO
MOCK_BEHAVIOR_PRESERVED=true
KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED
"""

from __future__ import annotations

import logging

from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.config import (
    BEDROCK_KNOWLEDGE_BASE_ID,
    BEDROCK_MODEL_ID,
    BEDROCK_REGION,
    KNOWLEDGE_MODE,
    RETRIEVAL_SCORE_THRESHOLD,
    KnowledgeMode,
)

logger = logging.getLogger(__name__)

# top_k padrão para recuperação — calibrar com o dataset no Passo 10
_DEFAULT_TOP_K: int = 5


def build_knowledge_client() -> KnowledgeClient:
    """Constrói e retorna a implementação de KnowledgeClient para o modo atual.

    Lê KNOWLEDGE_MODE do config e instancia a implementação correta.
    Falha de forma explícita e controlada quando a configuração do modo
    BEDROCK_RAG estiver incompleta.

    Returns:
        KnowledgeClient pronto para uso pelo Orchestrator.

    Raises:
        ValueError: configuração inválida ou incompleta para o modo escolhido.
        ValueError: KNOWLEDGE_MODE desconhecido.
    """
    if KNOWLEDGE_MODE == KnowledgeMode.MOCK:
        return _build_mock()

    if KNOWLEDGE_MODE == KnowledgeMode.BEDROCK_RAG:
        return _build_bedrock_rag()

    raise ValueError(
        f"KNOWLEDGE_MODE desconhecido: '{KNOWLEDGE_MODE}'. "
        "Valores válidos: MOCK, BEDROCK_RAG."
    )


def _build_mock() -> KnowledgeClient:
    """Instancia MockKnowledgeClient sem nenhuma dependência AWS."""
    from marh_agent.clients.mock_knowledge_client import MockKnowledgeClient

    logger.info(
        "knowledge_client_initialized",
        extra={"knowledge_mode": "MOCK", "rag_enabled": False},
    )
    return MockKnowledgeClient()


def _build_bedrock_rag() -> KnowledgeClient:
    """Constrói o pipeline BedrockRagKnowledgeClient.

    Valida configurações obrigatórias antes de instanciar qualquer cliente.
    Não faz fallback silencioso para MOCK em caso de configuração inválida.
    """
    _require_config("BEDROCK_KNOWLEDGE_BASE_ID", BEDROCK_KNOWLEDGE_BASE_ID)
    _require_config("BEDROCK_MODEL_ID", BEDROCK_MODEL_ID)

    from marh_agent.clients.bedrock_knowledge_base_retriever import (
        BedrockKnowledgeBaseRetriever,
    )
    from marh_agent.clients.bedrock_language_model_client import (
        BedrockLanguageModelClient,
    )
    from marh_agent.clients.bedrock_rag_knowledge_client import (
        BedrockRagKnowledgeClient,
    )

    retriever = BedrockKnowledgeBaseRetriever(
        knowledge_base_id=BEDROCK_KNOWLEDGE_BASE_ID,
        region_name=BEDROCK_REGION,
    )

    llm = BedrockLanguageModelClient(
        model_id=BEDROCK_MODEL_ID,
        region_name=BEDROCK_REGION,
    )

    knowledge_client = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=RETRIEVAL_SCORE_THRESHOLD,
        top_k=_DEFAULT_TOP_K,
    )

    logger.info(
        "knowledge_client_initialized",
        extra={
            "knowledge_mode": "BEDROCK_RAG",
            "rag_enabled": True,
            "bedrock_region": BEDROCK_REGION,
            "score_threshold": RETRIEVAL_SCORE_THRESHOLD,
        },
    )

    return knowledge_client


def _require_config(name: str, value: str) -> None:
    """Valida que uma variável de configuração obrigatória está definida.

    Raises:
        ValueError: quando o valor está ausente ou vazio.
                    A mensagem não expõe o valor real.
    """
    if not value or not value.strip():
        raise ValueError(
            f"{name} é obrigatório quando KNOWLEDGE_MODE=BEDROCK_RAG. "
            "Defina a variável de ambiente correspondente."
        )
