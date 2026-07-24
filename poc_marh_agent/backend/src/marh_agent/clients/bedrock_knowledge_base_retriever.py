"""BedrockKnowledgeBaseRetriever — implementação real do Retriever via Bedrock.

Chama bedrock-agent-runtime:Retrieve em sa-east-1.
NÃO usa RetrieveAndGenerate.
NÃO gera texto.
NÃO aplica threshold (responsabilidade do BedrockRagKnowledgeClient).

STEP_5_COMPONENT=BEDROCK_KNOWLEDGE_BASE_RETRIEVER
RETRIEVE_AND_GENERATE=PROHIBITED
AWS_REGION=sa-east-1
UNIT_TEST_AWS_CALLS=ZERO
KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED
"""

from __future__ import annotations

import logging
import time
from urllib.parse import unquote

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from marh_agent.clients.retriever import Retriever
from marh_agent.domain.rag_exceptions import RetrieverError
from marh_agent.domain.rag_models import RetrievedChunk

logger = logging.getLogger(__name__)

# Campos de metadata bruta que nunca devem aparecer em RetrievedChunk.metadata.
# Inclui campos sensíveis da AWS e duplicados do modelo.
_METADATA_BLOCKLIST: frozenset[str] = frozenset({
    "x-amz-bedrock-kb-source-uri",
    "x-amz-bedrock-kb-chunk-id",
    "x-amz-bedrock-kb-data-source-id",
    "uri",
    "s3_uri",
    "s3Uri",
    "bucket",
    "arn",
    "accountId",
    "account_id",
    "embedding",
    "vector",
})

# Chaves de metadata onde procurar os campos estruturados do chunk.
# Ordem de preferência: mais específico primeiro.
_SECTION_NUMBER_KEYS = ("section_number", "section", "sectionNumber")
_SECTION_TITLE_KEYS  = ("section_title", "title", "sectionTitle", "heading")
_CHUNK_INDEX_KEYS    = ("chunk_index", "chunkIndex", "chunk_id", "chunkId")
_SOURCE_FILE_KEYS    = ("source_file", "sourceFile", "filename", "file_name")

_DEFAULT_CONNECT_TIMEOUT = 5
_DEFAULT_READ_TIMEOUT    = 30
_DEFAULT_MAX_RETRIES     = 2


class BedrockKnowledgeBaseRetriever(Retriever):
    """Recupera chunks do corpus via Bedrock Knowledge Bases (Retrieve API).

    A operação Retrieve é chamada diretamente — sem RetrieveAndGenerate.
    O threshold e a filtragem são responsabilidade do BedrockRagKnowledgeClient.
    """

    def __init__(
        self,
        *,
        knowledge_base_id: str,
        region_name: str = "sa-east-1",
        client: object | None = None,
        connect_timeout: int = _DEFAULT_CONNECT_TIMEOUT,
        read_timeout: int = _DEFAULT_READ_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        """Inicializa o retriever.

        Args:
            knowledge_base_id: ID da Knowledge Base no Bedrock. Obrigatório.
            region_name: Região AWS. Padrão sa-east-1. Cross-region proibido.
            client: Cliente boto3 pré-construído (para testes). Quando fornecido,
                    não cria outro cliente — usa o recebido diretamente.
            connect_timeout: Timeout de conexão em segundos.
            read_timeout: Timeout de leitura em segundos.
            max_retries: Número máximo de tentativas do botocore.

        Raises:
            ValueError: knowledge_base_id ou region_name vazios.
        """
        if not knowledge_base_id or not knowledge_base_id.strip():
            raise ValueError("knowledge_base_id não pode ser vazio")
        if not region_name or not region_name.strip():
            raise ValueError("region_name não pode ser vazio")

        self._knowledge_base_id = knowledge_base_id.strip()
        self._region_name = region_name.strip()

        if client is not None:
            self._client = client
        else:
            boto_config = Config(
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                retries={"max_attempts": max_retries, "mode": "standard"},
            )
            self._client = boto3.client(
                "bedrock-agent-runtime",
                region_name=self._region_name,
                config=boto_config,
            )

    def _retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]:
        """Chama Retrieve e converte o resultado em lista de RetrievedChunk.

        Recebe query já validada e sem espaços extras (validação na classe base).
        Nunca aplica threshold — retorna todos os resultados em ordem AWS.
        Nunca chama RetrieveAndGenerate.

        Args:
            query: Texto da consulta (já validado).
            top_k: Número máximo de chunks a retornar.

        Returns:
            Lista de RetrievedChunk na ordem retornada pelo Bedrock.
            Lista vazia se nenhum resultado textual válido foi encontrado.

        Raises:
            RetrieverError: qualquer falha de comunicação, acesso ou validação.
        """
        t0 = time.perf_counter()
        try:
            response = self._client.retrieve(
                knowledgeBaseId=self._knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": top_k,
                    }
                },
            )
        except ClientError as exc:
            self._handle_client_error(exc)
        except BotoCoreError as exc:
            raise RetrieverError(
                f"Erro de comunicação com Bedrock Knowledge Base: {type(exc).__name__}"
            ) from exc
        except Exception as exc:
            raise RetrieverError(
                f"Erro inesperado durante recuperação: {type(exc).__name__}"
            ) from exc

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        raw_results = response.get("retrievalResults", [])

        chunks = self._map_results(raw_results)

        logger.info(
            "knowledge_base_retrieve",
            extra={
                "operation": "knowledge_base_retrieve",
                "status": "ok",
                "region": self._region_name,
                "results_returned": len(raw_results),
                "chunks_mapped": len(chunks),
                "duration_ms": elapsed_ms,
            },
        )

        return chunks

    # ──────────────────────────────────────────────────────────
    # Mapeamento de resultados AWS → RetrievedChunk
    # ──────────────────────────────────────────────────────────

    def _map_results(self, raw_results: list[dict]) -> list[RetrievedChunk]:
        """Converte lista bruta AWS em lista de RetrievedChunk.

        Ignora silenciosamente itens sem texto utilizável.
        Nunca levanta erro por um único item inválido.
        """
        chunks: list[RetrievedChunk] = []
        for item in raw_results:
            chunk = self._map_single(item)
            if chunk is not None:
                chunks.append(chunk)
        return chunks

    def _map_single(self, item: dict) -> RetrievedChunk | None:
        """Converte um único resultado AWS em RetrievedChunk.

        Retorna None quando o conteúdo não é textual ou está vazio.
        """
        content_block = item.get("content") or {}
        text = content_block.get("text") or ""
        content_type = content_block.get("type") or ""

        # Aceitar somente conteúdo TEXT (ou ausência de type com text presente)
        if not text or not text.strip():
            return None
        if content_type and content_type.upper() not in ("TEXT", ""):
            return None

        score: float | None = item.get("score")
        # score deve ser float ou None — descartar tipos inesperados
        if score is not None and not isinstance(score, (int, float)):
            score = None
        elif isinstance(score, int):
            score = float(score)

        location = item.get("location") or {}
        source_file = self._extract_source_file(location)

        raw_metadata: dict = item.get("metadata") or {}
        safe_metadata = self._sanitize_metadata(raw_metadata)

        section_number = _first_str(raw_metadata, _SECTION_NUMBER_KEYS)
        section_title  = _first_str(raw_metadata, _SECTION_TITLE_KEYS)
        chunk_index    = _first_int(raw_metadata, _CHUNK_INDEX_KEYS)

        # source_file da metadata tem prioridade sobre S3 URI apenas quando
        # explicitamente presente na metadata aprovada
        if source_file is None:
            source_file = _first_str(raw_metadata, _SOURCE_FILE_KEYS)

        return RetrievedChunk(
            content=text.strip(),
            score=score,
            source_file=source_file,
            section_number=section_number,
            section_title=section_title,
            chunk_index=chunk_index,
            metadata=safe_metadata,
        )

    # ──────────────────────────────────────────────────────────
    # source_file a partir da URI S3
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _extract_source_file(location: dict) -> str | None:
        """Extrai somente o nome do arquivo de uma localização S3.

        Nunca expõe: s3://, bucket, prefixo, URI completa, ARN.
        Trata URL encoding e caminhos com subpastas.

        Exemplos:
            s3://bucket/knowledge/marh.md  →  "marh.md"
            s3://bucket/a/b/c/faq.md       →  "faq.md"
            s3://bucket/nome%20com%20espaço.md → "nome com espaço.md"
            location ausente               →  None
            location não S3                →  None
            URI vazia ou sem /             →  None
        """
        loc_type = (location.get("type") or "").upper()
        if loc_type != "S3":
            return None

        s3_loc = location.get("s3Location") or {}
        uri = (s3_loc.get("uri") or "").strip()
        if not uri:
            return None

        # Remover prefixo s3:// e extrair somente o nome do arquivo
        path = uri
        if path.startswith("s3://"):
            path = path[5:]  # remove "s3://"
        # Remover bucket (primeira parte antes de /)
        slash = path.find("/")
        if slash == -1:
            return None
        path = path[slash + 1:]  # remove bucket/

        # Extrair nome do arquivo (última parte do caminho)
        last_slash = path.rfind("/")
        filename = path[last_slash + 1:] if last_slash >= 0 else path

        # Decodificar URL encoding
        filename = unquote(filename).strip()

        return filename if filename else None

    # ──────────────────────────────────────────────────────────
    # Sanitização de metadata
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _sanitize_metadata(raw: dict) -> dict:
        """Remove campos sensíveis e não serializáveis da metadata bruta.

        Nunca copia: URIs S3, bucket, ARN, Account ID, IDs internos,
        embeddings, vetores, campos binários, objetos não serializáveis.
        """
        safe: dict = {}
        for key, value in raw.items():
            if key in _METADATA_BLOCKLIST:
                continue
            # Aceitar apenas tipos serializáveis seguros
            if isinstance(value, (str, int, float, bool)) and not isinstance(value, type):
                safe[key] = value
            # Listas simples de escalares
            elif isinstance(value, list) and all(
                isinstance(v, (str, int, float, bool)) for v in value
            ):
                safe[key] = value
        return safe

    # ──────────────────────────────────────────────────────────
    # Tratamento de erros AWS
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _handle_client_error(exc: ClientError) -> None:
        """Converte ClientError em RetrieverError com mensagem segura.

        Nunca expõe: query, conteúdo, URI S3, ARN, Account ID, response bruta.
        """
        error_code = exc.response.get("Error", {}).get("Code", "Unknown")
        http_status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)

        if error_code == "AccessDeniedException":
            raise RetrieverError(
                "Acesso negado ao Bedrock Knowledge Base. Verifique as permissões IAM."
            ) from exc
        if error_code == "ResourceNotFoundException":
            raise RetrieverError(
                "Knowledge Base não encontrada. Verifique o BEDROCK_KNOWLEDGE_BASE_ID."
            ) from exc
        if error_code == "ValidationException":
            raise RetrieverError(
                "Parâmetros inválidos na chamada Retrieve ao Bedrock."
            ) from exc
        if error_code in ("ThrottlingException", "TooManyRequestsException"):
            raise RetrieverError(
                "Limite de requisições atingido no Bedrock Knowledge Base (throttling)."
            ) from exc
        if error_code in ("InternalServerException", "ServiceUnavailableException"):
            raise RetrieverError(
                f"Erro interno do Bedrock Knowledge Base (HTTP {http_status})."
            ) from exc

        raise RetrieverError(
            f"Erro na chamada ao Bedrock Knowledge Base: {error_code}"
        ) from exc


# ──────────────────────────────────────────────────────────────
# Helpers de extração de metadata
# ──────────────────────────────────────────────────────────────


def _first_str(metadata: dict, keys: tuple[str, ...]) -> str | None:
    """Retorna o primeiro valor str encontrado entre as chaves candidatas."""
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _first_int(metadata: dict, keys: tuple[str, ...]) -> int | None:
    """Retorna o primeiro valor int encontrado entre as chaves candidatas."""
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
    return None
