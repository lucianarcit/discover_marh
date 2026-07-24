"""BedrockLanguageModelClient — implementação real do LanguageModelClient.

Chama bedrock-runtime:Converse em sa-east-1.
Permissão IAM necessária: bedrock:InvokeModel (não bedrock:Converse).

NÃO usa RetrieveAndGenerate.
NÃO usa InvokeModel diretamente.
NÃO usa streaming (ConverseStream).
NÃO recupera documentos.
NÃO aplica threshold.
NÃO conhece Router nem intents.
NÃO aceita dados corporativos.

STEP_6_COMPONENT=BEDROCK_LANGUAGE_MODEL_CLIENT
BEDROCK_API=CONVERSE
IAM_ACTION=bedrock:InvokeModel
AWS_REGION=sa-east-1
UNIT_TEST_AWS_CALLS=ZERO
GENERATION_MODEL=PROPOSED_PENDING_DATASET_EVALUATION
"""

from __future__ import annotations

import logging
import time

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from marh_agent.clients.language_model_client import LanguageModelClient
from marh_agent.domain.rag_exceptions import (
    InvalidRagRequestError,
    LanguageModelError,
)
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk

logger = logging.getLogger(__name__)

# Proteção de tamanho de contexto.
# Limita o total de caracteres enviados ao modelo para evitar ultrapassar
# a janela de contexto. Truncamento ocorre entre chunks (nunca no meio).
# O tokenizer real varia por modelo e será calibrado no Passo 10.
_DEFAULT_MAX_CONTEXT_CHARS: int = 40_000


class BedrockLanguageModelClient(LanguageModelClient):
    """Gera texto fundamentado em chunks aprovados via Bedrock Converse API.

    Recebe somente chunks já filtrados pelo BedrockRagKnowledgeClient.
    Não aplica threshold, não recupera documentos, não conhece intents.
    """

    def __init__(
        self,
        *,
        model_id: str,
        region_name: str = "sa-east-1",
        client: object | None = None,
        max_tokens: int = 500,
        temperature: float = 0.0,
        connect_timeout: int = 5,
        read_timeout: int = 60,
        max_retries: int = 2,
        max_context_chars: int = _DEFAULT_MAX_CONTEXT_CHARS,
    ) -> None:
        """Inicializa e valida todas as configurações.

        Args:
            model_id: ID do modelo Bedrock. Obrigatório. Sem valor padrão.
                      Não usar Claude 3 Haiku, 3.5 Haiku, 3 Sonnet.
                      Seleção definitiva no Passo 10.
            region_name: Região AWS. Padrão sa-east-1.
            client: Cliente boto3 pré-construído (para testes com Stubber).
            max_tokens: Máximo de tokens na resposta. Deve ser > 0.
            temperature: Temperatura da geração [0.0, 1.0]. 0.0 = determinístico.
            connect_timeout: Timeout de conexão em segundos. Deve ser > 0.
            read_timeout: Timeout de leitura em segundos. Deve ser > 0.
            max_retries: Tentativas botocore. Deve ser >= 0.
            max_context_chars: Limite de caracteres do contexto enviado.

        Raises:
            ValueError: parâmetros inválidos.
        """
        if not model_id or not model_id.strip():
            raise ValueError("model_id não pode ser vazio")
        if not region_name or not region_name.strip():
            raise ValueError("region_name não pode ser vazio")
        if max_tokens <= 0:
            raise ValueError(f"max_tokens deve ser maior que zero, recebido: {max_tokens}")
        if not (0.0 <= temperature <= 1.0):
            raise ValueError(
                f"temperature deve estar em [0.0, 1.0], recebido: {temperature}"
            )
        if connect_timeout <= 0:
            raise ValueError(f"connect_timeout deve ser maior que zero, recebido: {connect_timeout}")
        if read_timeout <= 0:
            raise ValueError(f"read_timeout deve ser maior que zero, recebido: {read_timeout}")
        if max_retries < 0:
            raise ValueError(f"max_retries deve ser >= 0, recebido: {max_retries}")
        if max_context_chars <= 0:
            raise ValueError(f"max_context_chars deve ser maior que zero, recebido: {max_context_chars}")

        self._model_id = model_id.strip()
        self._region_name = region_name.strip()
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._max_context_chars = max_context_chars

        if client is not None:
            self._client = client
        else:
            boto_config = Config(
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                retries={"max_attempts": max_retries, "mode": "standard"},
            )
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self._region_name,
                config=boto_config,
            )

    def _generate(
        self,
        *,
        system_prompt: str,
        user_query: str,
        context_chunks: list[RetrievedChunk],
    ) -> GenerationResult:
        """Chama Converse e converte a resposta em GenerationResult.

        Recebe parâmetros já validados pela classe base.
        Nunca aplica threshold, nunca recupera documentos, nunca usa streaming.
        A permissão IAM correspondente é bedrock:InvokeModel.

        Args:
            system_prompt: Instrução de sistema com restrições de groundedness.
            user_query: Query fixa do mapeamento topic → query_string.
            context_chunks: Chunks aprovados pelo BedrockRagKnowledgeClient.

        Returns:
            GenerationResult com texto plano, tokens e stop_reason.

        Raises:
            LanguageModelError: qualquer falha de comunicação ou resposta inválida.
            InvalidRagRequestError: contexto vazio após truncamento.
        """
        context_text = self._build_context(context_chunks)
        user_message = _build_user_message(context_text, user_query)

        t0 = time.perf_counter()
        try:
            response = self._client.converse(
                modelId=self._model_id,
                system=[{"text": system_prompt}],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_message}],
                    }
                ],
                inferenceConfig={
                    "maxTokens": self._max_tokens,
                    "temperature": self._temperature,
                },
            )
        except ClientError as exc:
            self._handle_client_error(exc)
        except BotoCoreError as exc:
            raise LanguageModelError(
                f"Erro de comunicação com o serviço de geração: {type(exc).__name__}"
            ) from exc
        except Exception as exc:
            raise LanguageModelError(
                f"Erro inesperado durante geração: {type(exc).__name__}"
            ) from exc

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return self._map_response(response, elapsed_ms, len(context_chunks))

    # ──────────────────────────────────────────────────────────
    # Montagem do contexto
    # ──────────────────────────────────────────────────────────

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Formata chunks aprovados em texto de contexto para o prompt.

        Regras:
        - Preserva ordem recebida (chunks já ordenados por BedrockRagKnowledgeClient)
        - Inclui somente source_file e section_title — nunca URI S3, ARN, score
        - Trunca entre chunks quando max_context_chars for atingido
        - Nunca corta um chunk no meio
        - Nunca resume ou modifica o conteúdo factual
        """
        parts: list[str] = []
        total_chars = 0

        for i, chunk in enumerate(chunks, start=1):
            lines: list[str] = [f"[TRECHO {i}]"]
            if chunk.source_file:
                lines.append(f"Fonte: {chunk.source_file}")
            if chunk.section_title:
                lines.append(f"Seção: {chunk.section_title}")
            lines.append("Conteúdo:")
            lines.append(chunk.content)
            block = "\n".join(lines)

            separator = 2 if parts else 0  # "\n\n" apenas entre blocos
            if total_chars + separator + len(block) > self._max_context_chars:
                if not parts:
                    # Nem o primeiro chunk cabe — levantar erro
                    raise InvalidRagRequestError(
                        "Nenhum chunk cabe no limite de contexto configurado."
                    )
                # Atingiu limite a partir do segundo — parar
                break

            parts.append(block)
            total_chars += separator + len(block)

        return "\n\n".join(parts)

    # ──────────────────────────────────────────────────────────
    # Mapeamento da resposta Converse
    # ──────────────────────────────────────────────────────────

    def _map_response(
        self, response: dict, elapsed_ms: float, chunk_count: int
    ) -> GenerationResult:
        """Converte resposta Converse em GenerationResult.

        Coleta somente blocos ContentBlock.text em ordem.
        Ignora blocos não textuais (imagem, toolUse, etc.).
        Nunca propaga responseMetadata, requestId nem métricas de latência.
        """
        output = response.get("output") or {}
        message = output.get("message") or {}
        content_blocks = message.get("content") or []

        text_parts: list[str] = []
        for block in content_blocks:
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            raise LanguageModelError(
                "Serviço de geração retornou resposta sem conteúdo textual utilizável."
            )

        usage = response.get("usage") or {}
        input_tokens: int | None = usage.get("inputTokens")
        output_tokens: int | None = usage.get("outputTokens")
        stop_reason: str | None = response.get("stopReason")

        logger.info(
            "bedrock_converse",
            extra={
                "operation": "bedrock_converse",
                "status": "ok",
                "region": self._region_name,
                "model_id": self._model_id,
                "chunk_count": chunk_count,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "stop_reason": stop_reason,
                "duration_ms": elapsed_ms,
            },
        )

        return GenerationResult(
            text=full_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            stop_reason=stop_reason,
            model_id=self._model_id,
        )

    # ──────────────────────────────────────────────────────────
    # Tratamento de erros AWS
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _handle_client_error(exc: ClientError) -> None:
        """Converte ClientError em LanguageModelError com mensagem segura.

        Nunca expõe: system_prompt, user_query, chunks, resposta bruta,
        ARN, Account ID, credenciais, stack trace, URI S3.
        """
        error_code = exc.response.get("Error", {}).get("Code", "Unknown")
        http_status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)

        if error_code == "AccessDeniedException":
            raise LanguageModelError(
                "Acesso ao modelo de geração não autorizado."
            ) from exc
        if error_code == "ValidationException":
            raise LanguageModelError(
                "Parâmetros inválidos na chamada ao modelo de geração."
            ) from exc
        if error_code in ("ThrottlingException", "TooManyRequestsException"):
            raise LanguageModelError(
                "Modelo de geração temporariamente indisponível (limite de requisições)."
            ) from exc
        if error_code == "ModelTimeoutException":
            raise LanguageModelError(
                "A geração excedeu o tempo limite."
            ) from exc
        if error_code == "ModelNotReadyException":
            raise LanguageModelError(
                "Modelo de geração não está pronto. Tente novamente em instantes."
            ) from exc
        if error_code in ("ServiceUnavailableException", "ServiceQuotaExceededException"):
            raise LanguageModelError(
                "Serviço de geração temporariamente indisponível."
            ) from exc
        if error_code == "InternalServerException":
            raise LanguageModelError(
                f"Erro interno do serviço de geração (HTTP {http_status})."
            ) from exc
        if error_code == "ResourceNotFoundException":
            raise LanguageModelError(
                "Modelo de geração não encontrado. Verifique o BEDROCK_MODEL_ID."
            ) from exc

        raise LanguageModelError(
            f"Erro na chamada ao serviço de geração: {error_code}"
        ) from exc


# ──────────────────────────────────────────────────────────────
# Helpers de montagem do prompt
# ──────────────────────────────────────────────────────────────


def _build_user_message(context_text: str, user_query: str) -> str:
    """Monta a mensagem do usuário com contexto e pergunta separados.

    Não inclui: topic interno, intent ID, correlation ID, metadata,
    score threshold, configurações de infraestrutura.
    """
    return (
        "CONHECIMENTO APROVADO:\n\n"
        f"{context_text}\n\n"
        "PERGUNTA:\n\n"
        f"{user_query}\n\n"
        "Responda utilizando somente o conhecimento aprovado."
    )
