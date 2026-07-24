"""BedrockRagKnowledgeClient — implementação do KnowledgeClient via RAG.

Nesta etapa (Passo 4) a classe não importa boto3 nem faz chamadas AWS.
As dependências reais (BedrockKnowledgeBaseRetriever, BedrockLanguageModelClient)
serão injetadas nos Passos 5 e 6. Aqui apenas o orquestramento do pipeline.

STEP_4_IMPLEMENTATION_MODE=FAKES_ONLY
AWS_CALLS=ZERO
KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED
"""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import Mapping

from marh_agent.clients.knowledge_client import KnowledgeClient
from marh_agent.clients.language_model_client import LanguageModelClient
from marh_agent.clients.retriever import Retriever
from marh_agent.domain.rag_exceptions import (
    InvalidRagRequestError,
    LanguageModelError,
    RagError,
    RetrieverError,
)
from marh_agent.domain.rag_models import RetrievedChunk

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Prompt de sistema padrão
# ──────────────────────────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT: str = (
    "Você é um assistente consultivo do Meu Alelo RH.\n\n"
    "Responda somente com base nos trechos de conhecimento fornecidos.\n"
    "Não invente informações.\n"
    "Não use conhecimento externo.\n"
    "Quando os trechos forem insuficientes, informe que não há informação "
    "disponível e oriente o usuário a acessar o Espaço RH.\n"
    "Responda em português brasileiro.\n"
    "Seja direto, claro e objetivo.\n"
    "Não mencione Bedrock, RAG, embeddings, chunks ou documentos internos."
)

# ──────────────────────────────────────────────────────────────
# Mapeamento estático: tópico → query de recuperação
# Exatamente os 14 tópicos oficiais (INT-008 a INT-021).
# ORDER_STATUS_INFO excluído: ORPHAN_TOPIC_PENDING_OFFICIAL_INTENT_ASSIGNMENT.
# ──────────────────────────────────────────────────────────────

_DEFAULT_TOPIC_QUERY_MAP: Mapping[str, str] = MappingProxyType({
    "AGENT_CAPABILITIES":       "O que o agente consultivo MARH consegue fazer?",
    "CONSULTABLE_INFO":         "Quais informações posso consultar pelo agente MARH?",
    "ORDER_PROCESS":            "Como criar um pedido no Espaço RH?",
    "HOW_CONSULT_ORDER":        "Como consultar um pedido pelo agente MARH?",
    "HOW_CONSULT_COLLABORATOR": "Como consultar um colaborador pelo agente MARH?",
    "CARD_TRACKING_INFO":       "Como funciona o rastreamento de cartões no Espaço RH?",
    "CANNOT_CANCEL":            "É possível cancelar um pedido pelo agente MARH?",
    "CANNOT_EDIT_COLLABORATOR": "O agente MARH consegue editar dados de colaboradores?",
    "COMPANY_SCOPE":            "O agente MARH consulta dados de qualquer empresa?",
    "COMPANY_REQUIRED":         "É necessário selecionar uma empresa para usar o agente MARH?",
    "AGENT_VS_PORTAL":          "O agente MARH substitui o portal web do Espaço RH?",
    "MARH_OVERVIEW":            "O que é o MARH (Meu Alelo RH)?",
    "ESPACO_RH_OVERVIEW":       "O que é o Espaço RH do aplicativo Meu Alelo?",
    "QUESTION_TYPES":           "Que tipos de perguntas posso fazer ao agente MARH?",
})

# Nome do corpus aprovado — propagado em source_section para compatibilidade
# com o contrato existente do KnowledgeClient.
_CORPUS_SOURCE = "marh_feature_knowledge.md"


class BedrockRagKnowledgeClient(KnowledgeClient):
    """KnowledgeClient que usa RAG para responder intenções informativas.

    Orquestra o pipeline:
      topic → query_string → Retriever → filtragem → LanguageModelClient → dict

    Não importa boto3. Não faz chamadas AWS. As implementações concretas
    de Retriever e LanguageModelClient são injetadas pelo caller.
    """

    def __init__(
        self,
        *,
        retriever: Retriever,
        language_model_client: LanguageModelClient,
        score_threshold: float,
        top_k: int = 5,
        topic_query_map: Mapping[str, str] | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        """Inicializa e valida todas as dependências.

        Args:
            retriever: Implementação de Retriever. Não pode ser None.
            language_model_client: Implementação de LanguageModelClient. Não pode ser None.
            score_threshold: Limiar de score [0.0, 1.0]. Chunks abaixo são descartados.
            top_k: Número máximo de chunks a recuperar. Deve ser > 0.
            topic_query_map: Mapeamento tópico → query. None usa o mapa padrão dos 14 tópicos.
            system_prompt: Instrução de sistema para o modelo. Não pode ser vazia.

        Raises:
            ValueError: parâmetros inválidos.
        """
        if retriever is None:
            raise ValueError("retriever não pode ser None")
        if language_model_client is None:
            raise ValueError("language_model_client não pode ser None")
        if not (0.0 <= score_threshold <= 1.0):
            raise ValueError(
                f"score_threshold deve estar em [0.0, 1.0], recebido: {score_threshold}"
            )
        if top_k <= 0:
            raise ValueError(f"top_k deve ser maior que zero, recebido: {top_k}")
        if not system_prompt or not system_prompt.strip():
            raise ValueError("system_prompt não pode ser vazio")

        resolved_map = topic_query_map if topic_query_map is not None else _DEFAULT_TOPIC_QUERY_MAP
        if not resolved_map:
            raise ValueError("topic_query_map não pode ser vazio")

        self._retriever = retriever
        self._llm = language_model_client
        self._score_threshold = score_threshold
        self._top_k = top_k
        self._topic_query_map: Mapping[str, str] = MappingProxyType(dict(resolved_map))
        self._system_prompt = system_prompt.strip()

    def query(self, topic: str) -> dict:
        """Executa o pipeline RAG para o tópico solicitado.

        Implementa o contrato de KnowledgeClient.query().
        Nunca expõe conteúdo bruto dos chunks, vetores, prompts,
        dados corporativos ou stack traces no retorno.

        Args:
            topic: Identificador do tópico (ex: "MARH_OVERVIEW").
                   Tópico vazio ou desconhecido retorna found=False.

        Returns:
            dict com found, content, source_section, data_classification
            e metadata segura. Formato compatível com MockKnowledgeClient.
        """
        topic_normalized = (topic or "").strip().upper()

        # Tópico vazio
        if not topic_normalized:
            return self._not_found(
                topic=topic_normalized,
                retrieved=0,
                approved=0,
                reason="topic_empty",
            )

        # Tópico desconhecido — não chama Retriever
        query_string = self._topic_query_map.get(topic_normalized)
        if query_string is None:
            return self._not_found(
                topic=topic_normalized,
                retrieved=0,
                approved=0,
                reason="topic_unknown",
            )

        # Recuperação
        try:
            chunks: list[RetrievedChunk] = self._retriever.retrieve(
                query_string, top_k=self._top_k
            )
        except RetrieverError:
            raise
        except InvalidRagRequestError:
            raise
        except Exception as exc:
            raise RetrieverError(
                f"Falha inesperada na recuperação para tópico '{topic_normalized}'"
            ) from exc

        retrieved_count = len(chunks)

        # Filtragem por threshold (score None nunca aprovado)
        approved: list[RetrievedChunk] = [
            c for c in chunks
            if c.score is not None and c.score >= self._score_threshold
        ]

        # Ordenar por score decrescente (caso o Retriever não garanta ordem)
        approved.sort(key=lambda c: c.score, reverse=True)  # type: ignore[arg-type]

        approved_count = len(approved)

        # Sem evidência — não chama LLM
        if not approved:
            logger.info(
                "rag_no_evidence",
                extra={
                    "topic": topic_normalized,
                    "retrieved": retrieved_count,
                    "approved": approved_count,
                    "threshold": self._score_threshold,
                },
            )
            return self._not_found(
                topic=topic_normalized,
                retrieved=retrieved_count,
                approved=0,
                reason="below_threshold",
            )

        # Geração
        try:
            result = self._llm.generate(
                system_prompt=self._system_prompt,
                user_query=query_string,
                context_chunks=approved,
            )
        except LanguageModelError:
            raise
        except InvalidRagRequestError:
            raise
        except Exception as exc:
            raise LanguageModelError(
                f"Falha inesperada na geração para tópico '{topic_normalized}'"
            ) from exc

        # Texto gerado vazio (GenerationResult.text valida no construtor,
        # mas por defesa verificamos após possíveis transformações futuras)
        if not result.text or not result.text.strip():
            raise LanguageModelError(
                f"Modelo retornou texto vazio para tópico '{topic_normalized}'"
            )

        logger.info(
            "rag_generation_ok",
            extra={
                "topic": topic_normalized,
                "retrieved": retrieved_count,
                "approved": approved_count,
                "threshold": self._score_threshold,
                "model_id": result.model_id or "unknown",
            },
        )

        return {
            "found": True,
            "content": result.text,
            # source_section: campo exigido pelo Router (lê knowledge_result["source_section"])
            "source_section": _CORPUS_SOURCE,
            "data_classification": "BEDROCK_RAG_GROUNDED",
            "metadata": {
                "flow_detail": "BEDROCK_RAG",
                "data_classification": "BEDROCK_RAG_GROUNDED",
                "retrieved_chunks": retrieved_count,
                "approved_chunks": approved_count,
                "score_threshold": self._score_threshold,
                "model_id": result.model_id,
            },
        }

    # ──────────────────────────────────────────────────────────
    # Helpers privados
    # ──────────────────────────────────────────────────────────

    def _not_found(
        self,
        *,
        topic: str,
        retrieved: int,
        approved: int,
        reason: str,
    ) -> dict:
        """Retorna resposta negativa com metadata segura."""
        return {
            "found": False,
            "content": None,
            "source_section": _CORPUS_SOURCE,
            "data_classification": "BEDROCK_RAG_NO_EVIDENCE",
            "metadata": {
                "flow_detail": "BEDROCK_RAG",
                "data_classification": "BEDROCK_RAG_NO_EVIDENCE",
                "retrieved_chunks": retrieved,
                "approved_chunks": approved,
                "score_threshold": self._score_threshold,
                "reason": reason,
            },
        }
