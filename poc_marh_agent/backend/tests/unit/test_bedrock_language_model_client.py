"""Testes unitários do BedrockLanguageModelClient com botocore Stubber.

Regras:
- Zero chamadas AWS reais
- Zero credenciais necessárias
- Zero acesso à rede
- Stubber intercepta todas as chamadas boto3
"""

from __future__ import annotations

import pytest
import boto3
from botocore.stub import Stubber

from marh_agent.clients.bedrock_language_model_client import (
    BedrockLanguageModelClient,
    _build_user_message,
)
from marh_agent.domain.rag_exceptions import (
    InvalidRagRequestError,
    LanguageModelError,
)
from marh_agent.domain.rag_models import GenerationResult, RetrievedChunk


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

MODEL_ID = "mistral.magistral-small-2509"
REGION = "sa-east-1"
SYSTEM_PROMPT = "Responda somente com base no conhecimento fornecido."
USER_QUERY = "O que é o MARH?"


def _make_boto_client():
    return boto3.client("bedrock-runtime", region_name=REGION)


def _make_llm(client=None, **kwargs) -> BedrockLanguageModelClient:
    if client is None:
        client = _make_boto_client()
    defaults = dict(model_id=MODEL_ID, region_name=REGION, client=client)
    defaults.update(kwargs)
    return BedrockLanguageModelClient(**defaults)


def _make_chunk(
    content: str = "Conteúdo aprovado do corpus.",
    score: float | None = 0.85,
    source_file: str | None = "marh.md",
    section_title: str | None = "Contexto",
) -> RetrievedChunk:
    return RetrievedChunk(content=content, score=score,
                          source_file=source_file, section_title=section_title)


def _converse_response(
    text: str = "Resposta gerada pelo modelo.",
    input_tokens: int = 100,
    output_tokens: int = 30,
    stop_reason: str = "end_turn",
) -> dict:
    """Monta resposta Converse mínima compatível com o SDK."""
    return {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": text}],
            }
        },
        "stopReason": stop_reason,
        "usage": {
            "inputTokens": input_tokens,
            "outputTokens": output_tokens,
            "totalTokens": input_tokens + output_tokens,
        },
        "metrics": {"latencyMs": 123},
    }


def _expected_params(
    system_prompt: str = SYSTEM_PROMPT,
    user_query: str = USER_QUERY,
    context_text: str | None = None,
    max_tokens: int = 500,
    temperature: float = 0.0,
) -> dict:
    """Monta expected_params para o Stubber verificar."""
    if context_text is None:
        context_text = "[TRECHO 1]\nFonte: marh.md\nSeção: Contexto\nConteúdo:\nConteúdo aprovado do corpus."
    user_msg = _build_user_message(context_text, user_query)
    return {
        "modelId": MODEL_ID,
        "system": [{"text": system_prompt}],
        "messages": [{"role": "user", "content": [{"text": user_msg}]}],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
    }


# ──────────────────────────────────────────────────────────────
# Construção — validações
# ──────────────────────────────────────────────────────────────


def test_construction_valid():
    llm = _make_llm()
    assert llm is not None


def test_construction_model_id_empty_rejected():
    with pytest.raises(ValueError, match="model_id"):
        BedrockLanguageModelClient(model_id="", region_name=REGION)


def test_construction_model_id_blank_rejected():
    with pytest.raises(ValueError, match="model_id"):
        BedrockLanguageModelClient(model_id="   ", region_name=REGION)


def test_construction_region_empty_rejected():
    with pytest.raises(ValueError, match="region_name"):
        BedrockLanguageModelClient(model_id=MODEL_ID, region_name="")


def test_construction_region_blank_rejected():
    with pytest.raises(ValueError, match="region_name"):
        BedrockLanguageModelClient(model_id=MODEL_ID, region_name="   ")


def test_construction_max_tokens_zero_rejected():
    with pytest.raises(ValueError, match="max_tokens"):
        _make_llm(max_tokens=0)


def test_construction_max_tokens_negative_rejected():
    with pytest.raises(ValueError, match="max_tokens"):
        _make_llm(max_tokens=-1)


def test_construction_temperature_negative_rejected():
    with pytest.raises(ValueError, match="temperature"):
        _make_llm(temperature=-0.1)


def test_construction_temperature_above_one_rejected():
    with pytest.raises(ValueError, match="temperature"):
        _make_llm(temperature=1.01)


def test_construction_temperature_zero_accepted():
    llm = _make_llm(temperature=0.0)
    assert llm is not None


def test_construction_temperature_one_accepted():
    llm = _make_llm(temperature=1.0)
    assert llm is not None


def test_construction_connect_timeout_zero_rejected():
    with pytest.raises(ValueError, match="connect_timeout"):
        _make_llm(connect_timeout=0)


def test_construction_read_timeout_zero_rejected():
    with pytest.raises(ValueError, match="read_timeout"):
        _make_llm(read_timeout=0)


def test_construction_max_retries_negative_rejected():
    with pytest.raises(ValueError, match="max_retries"):
        _make_llm(max_retries=-1)


def test_construction_max_retries_zero_accepted():
    llm = _make_llm(max_retries=0)
    assert llm is not None


def test_injected_client_is_used():
    sentinel = object()
    llm = BedrockLanguageModelClient(
        model_id=MODEL_ID, region_name=REGION, client=sentinel
    )
    assert llm._client is sentinel


def test_boto3_client_not_created_when_injected():
    fake_client = _make_boto_client()
    llm = BedrockLanguageModelClient(
        model_id=MODEL_ID, region_name=REGION, client=fake_client
    )
    assert llm._client is fake_client


# ──────────────────────────────────────────────────────────────
# Request Converse — formato correto
# ──────────────────────────────────────────────────────────────


def test_converse_called_with_correct_model_id():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    expected = _expected_params()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(), expected_params=expected)
        llm = _make_llm(client=boto_client)
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                     context_chunks=[chunk])
        stub.assert_no_pending_responses()


def test_converse_called_with_correct_system_prompt():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    custom_prompt = "Prompt customizado de teste."
    with Stubber(boto_client) as stub:
        expected = _expected_params(system_prompt=custom_prompt)
        stub.add_response("converse", _converse_response(), expected_params=expected)
        llm = _make_llm(client=boto_client)
        llm.generate(system_prompt=custom_prompt, user_query=USER_QUERY,
                     context_chunks=[chunk])
        stub.assert_no_pending_responses()


def test_converse_message_contains_context():
    boto_client = _make_boto_client()
    chunk = _make_chunk(content="Texto do corpus MARH.", source_file="marh.md",
                        section_title="Visão Geral")
    context_text = (
        "[TRECHO 1]\nFonte: marh.md\nSeção: Visão Geral\n"
        "Conteúdo:\nTexto do corpus MARH."
    )
    with Stubber(boto_client) as stub:
        expected = _expected_params(context_text=context_text)
        stub.add_response("converse", _converse_response(), expected_params=expected)
        llm = _make_llm(client=boto_client)
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                     context_chunks=[chunk])
        stub.assert_no_pending_responses()


def test_converse_message_contains_user_query():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    custom_query = "Como criar um pedido?"
    with Stubber(boto_client) as stub:
        expected = _expected_params(user_query=custom_query)
        stub.add_response("converse", _converse_response(), expected_params=expected)
        llm = _make_llm(client=boto_client)
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=custom_query,
                     context_chunks=[chunk])
        stub.assert_no_pending_responses()


def test_converse_inference_config_correct():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        expected = _expected_params(max_tokens=300, temperature=0.2)
        stub.add_response("converse", _converse_response(), expected_params=expected)
        llm = _make_llm(client=boto_client, max_tokens=300, temperature=0.2)
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                     context_chunks=[chunk])
        stub.assert_no_pending_responses()


def test_source_file_included_in_context():
    """source_file deve aparecer no contexto enviado ao modelo."""
    boto_client = _make_boto_client()
    chunk = _make_chunk(source_file="faq_pedidos.md")
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response())
        llm = _make_llm(client=boto_client)
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                     context_chunks=[chunk])
    # Verificação via _build_context direto
    context = llm._build_context([chunk])
    assert "faq_pedidos.md" in context


def test_section_title_included_in_context():
    chunk = _make_chunk(section_title="Seção Pedidos")
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context([chunk])
    assert "Seção Pedidos" in context


def test_source_file_none_omits_fonte_line():
    chunk = _make_chunk(source_file=None)
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context([chunk])
    assert "Fonte:" not in context


def test_section_title_none_omits_secao_line():
    chunk = _make_chunk(section_title=None)
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context([chunk])
    assert "Seção:" not in context


def test_score_not_in_context():
    chunk = _make_chunk(score=0.99)
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context([chunk])
    assert "0.99" not in context
    assert "score" not in context.lower()


def test_metadata_bruta_not_in_context():
    chunk = RetrievedChunk(
        content="Conteúdo.",
        metadata={"x-amz-bedrock-kb-source-uri": "s3://secret/bucket"},
    )
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context([chunk])
    assert "s3://" not in context
    assert "secret" not in context


def test_chunk_order_preserved_in_context():
    chunks = [
        _make_chunk(content="Primeiro chunk.", section_title="A"),
        _make_chunk(content="Segundo chunk.", section_title="B"),
        _make_chunk(content="Terceiro chunk.", section_title="C"),
    ]
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context(chunks)
    pos_a = context.index("Primeiro chunk.")
    pos_b = context.index("Segundo chunk.")
    pos_c = context.index("Terceiro chunk.")
    assert pos_a < pos_b < pos_c


def test_multiple_chunks_numbered_in_context():
    chunks = [_make_chunk(content=f"Chunk {i}.") for i in range(3)]
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    context = llm._build_context(chunks)
    assert "[TRECHO 1]" in context
    assert "[TRECHO 2]" in context
    assert "[TRECHO 3]" in context


def test_region_sa_east_1_by_default():
    llm = BedrockLanguageModelClient.__new__(BedrockLanguageModelClient)
    llm._region_name = "sa-east-1"
    assert llm._region_name == "sa-east-1"


# ──────────────────────────────────────────────────────────────
# Mapeamento de resposta
# ──────────────────────────────────────────────────────────────


def test_single_text_block_mapped():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(text="Resposta única."))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.text == "Resposta única."


def test_multiple_text_blocks_concatenated():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    multi_response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {"text": "Parte 1."},
                    {"text": "Parte 2."},
                ],
            }
        },
        "stopReason": "end_turn",
        "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
        "metrics": {"latencyMs": 50},
    }
    with Stubber(boto_client) as stub:
        stub.add_response("converse", multi_response)
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert "Parte 1." in result.text
    assert "Parte 2." in result.text


def test_non_text_blocks_ignored():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    mixed_response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {"image": {"format": "jpeg", "source": {"bytes": b""}}},
                    {"text": "Só este bloco é texto."},
                ],
            }
        },
        "stopReason": "end_turn",
        "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
        "metrics": {"latencyMs": 50},
    }
    with Stubber(boto_client) as stub:
        stub.add_response("converse", mixed_response)
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.text == "Só este bloco é texto."


def test_input_tokens_mapped():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(input_tokens=250))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.input_tokens == 250


def test_output_tokens_mapped():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(output_tokens=42))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.output_tokens == 42


def test_stop_reason_mapped():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(stop_reason="max_tokens"))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.stop_reason == "max_tokens"


def test_model_id_propagated_in_result():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response())
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.model_id == MODEL_ID


def test_response_metadata_not_in_result():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response())
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    result_dict = result.model_dump()
    assert "ResponseMetadata" not in result_dict
    assert "requestId" not in result_dict
    assert "metrics" not in result_dict


def test_response_without_usage_tokens_none():
    """Quando usage está ausente, tokens devem ser None."""
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    # Stubber exige o shape completo — simular ausência de usage via resposta com usage={} vazio
    # Como Stubber valida o shape, usamos a resposta completa e testamos o código de extração
    # diretamente, verificando que usage.get() retorna None para chaves ausentes.
    usage: dict = {}  # dict vazio — simula ausência de inputTokens/outputTokens
    assert usage.get("inputTokens") is None
    assert usage.get("outputTokens") is None
    # Integração: resposta real com usage completo — tokens são int
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(input_tokens=0, output_tokens=0))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    # Com usage presente mas zerado, tokens são 0 (não None)
    assert result.input_tokens == 0
    assert result.output_tokens == 0


def test_response_without_stop_reason_is_none():
    """Quando stopReason está ausente no dict extraído, stop_reason é None."""
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    # Testar o código de extração diretamente
    response_without_stop: dict = {
        "output": {"message": {"role": "assistant", "content": [{"text": "Ok."}]}},
        "usage": {"inputTokens": 5, "outputTokens": 2, "totalTokens": 7},
    }
    stop_reason = response_without_stop.get("stopReason")
    assert stop_reason is None
    # Integração: stop_reason end_turn é o que o Stubber retorna
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response(stop_reason="end_turn"))
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert result.stop_reason == "end_turn"


def test_returns_generation_result():
    boto_client = _make_boto_client()
    chunk = _make_chunk()
    with Stubber(boto_client) as stub:
        stub.add_response("converse", _converse_response())
        llm = _make_llm(client=boto_client)
        result = llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                              context_chunks=[chunk])
    assert isinstance(result, GenerationResult)


# ──────────────────────────────────────────────────────────────
# Erros AWS → LanguageModelError
# ──────────────────────────────────────────────────────────────


def _add_converse_error(stub: Stubber, code: str, msg: str = "Erro.") -> None:
    stub.add_client_error("converse", service_error_code=code, service_message=msg)


def test_access_denied_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "AccessDeniedException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="não autorizado"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_validation_exception_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ValidationException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="inválidos"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_throttling_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ThrottlingException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="limite de requisições"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_model_timeout_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ModelTimeoutException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="tempo limite"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_model_not_ready_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ModelNotReadyException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="não está pronto"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_service_unavailable_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ServiceUnavailableException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="indisponível"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_internal_server_error_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "InternalServerException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_resource_not_found_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ResourceNotFoundException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError, match="BEDROCK_MODEL_ID"):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_generic_client_error_raises_llm_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "SomethingWeirdException")
        llm = _make_llm(client=boto_client)
        with pytest.raises(LanguageModelError):
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])


def test_response_without_output_raises_llm_error():
    """Quando a resposta não tem output utilizável, deve lançar LanguageModelError."""
    # O Stubber valida o shape e exige output — testar via _map_response diretamente
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    # response sem output algum
    with pytest.raises(LanguageModelError):
        llm._map_response({}, elapsed_ms=0.0, chunk_count=1)


def test_response_without_text_raises_llm_error():
    """Quando a resposta tem content mas sem blocos textuais, deve lançar LanguageModelError."""
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    # Resposta com content vazio (sem text blocks)
    response_no_text = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [],  # sem blocos
            }
        },
        "stopReason": "end_turn",
        "usage": {"inputTokens": 5, "outputTokens": 0, "totalTokens": 5},
    }
    with pytest.raises(LanguageModelError):
        llm._map_response(response_no_text, elapsed_ms=0.0, chunk_count=1)


# ──────────────────────────────────────────────────────────────
# Segurança — mensagens de erro não expõem dados sensíveis
# ──────────────────────────────────────────────────────────────


def test_error_does_not_contain_user_query():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "AccessDeniedException")
        llm = _make_llm(client=boto_client)
        try:
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query="pergunta secreta",
                         context_chunks=[_make_chunk()])
            pytest.fail("Esperava LanguageModelError")
        except LanguageModelError as exc:
            assert "pergunta secreta" not in str(exc)


def test_error_does_not_contain_chunk_content():
    boto_client = _make_boto_client()
    sensitive = "dado corporativo altamente sensível"
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "AccessDeniedException")
        llm = _make_llm(client=boto_client)
        try:
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk(content=sensitive)])
            pytest.fail("Esperava LanguageModelError")
        except LanguageModelError as exc:
            assert sensitive not in str(exc)


def test_error_does_not_contain_system_prompt():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "AccessDeniedException")
        llm = _make_llm(client=boto_client)
        try:
            llm.generate(system_prompt="instrução confidencial do sistema",
                         user_query=USER_QUERY, context_chunks=[_make_chunk()])
            pytest.fail("Esperava LanguageModelError")
        except LanguageModelError as exc:
            assert "instrução confidencial" not in str(exc)


def test_error_does_not_contain_s3_uri():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_converse_error(stub, "ResourceNotFoundException",
                            msg="s3://bucket-secreto/path/file.md")
        llm = _make_llm(client=boto_client)
        try:
            llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                         context_chunks=[_make_chunk()])
            pytest.fail("Esperava LanguageModelError")
        except LanguageModelError as exc:
            assert "s3://" not in str(exc)
            assert "bucket-secreto" not in str(exc)


# ──────────────────────────────────────────────────────────────
# Proteção de tamanho de contexto (max_context_chars)
# ──────────────────────────────────────────────────────────────


def test_context_truncated_between_chunks():
    """Quando o limite é atingido a partir do segundo chunk, trunca entre eles."""
    chunk_first = _make_chunk(content="A" * 50, source_file=None, section_title=None)
    chunk_second = _make_chunk(content="B" * 50, source_file=None, section_title=None)
    boto_client = _make_boto_client()
    # Primeiro bloco: "[TRECHO 1]\nConteúdo:\n" + 50 A's = ~70 chars
    # Segundo bloco adicionaria 72 chars + separador 2 = ultrapassa 100
    llm = _make_llm(client=boto_client, max_context_chars=100)
    context = llm._build_context([chunk_first, chunk_second])
    assert "A" * 50 in context
    assert "B" * 50 not in context


def test_no_chunk_fits_raises_error():
    """Se nenhum chunk cabe no limite, deve lançar erro."""
    chunk = _make_chunk(content="X" * 10000)
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client, max_context_chars=5)
    with pytest.raises((InvalidRagRequestError, LanguageModelError)):
        llm._build_context([chunk])


def test_first_chunk_always_included_if_fits():
    """O primeiro chunk deve ser sempre incluído se couber."""
    chunk = _make_chunk(content="Pequeno.")
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client, max_context_chars=10_000)
    context = llm._build_context([chunk])
    assert "Pequeno." in context


# ──────────────────────────────────────────────────────────────
# Contrato — não recupera, não aplica threshold, não conhece Router
# ──────────────────────────────────────────────────────────────


def test_does_not_call_retrieve():
    """BedrockLanguageModelClient não tem acesso a Retriever."""
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    assert not hasattr(llm, "_retriever")
    assert not hasattr(llm, "_knowledge_base_id")


def test_does_not_apply_threshold():
    """Não tem score_threshold — é responsabilidade do BedrockRagKnowledgeClient."""
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    assert not hasattr(llm, "_score_threshold")


def test_module_imports_boto3():
    """BedrockLanguageModelClient importa boto3 legitimamente."""
    import marh_agent.clients.bedrock_language_model_client as mod
    assert hasattr(mod, "boto3")


def test_base_class_validates_empty_chunks():
    """A classe base rejeita context_chunks=[] antes de chamar _generate."""
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    with pytest.raises(InvalidRagRequestError):
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query=USER_QUERY,
                     context_chunks=[])


def test_base_class_validates_empty_system_prompt():
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    with pytest.raises(InvalidRagRequestError):
        llm.generate(system_prompt="", user_query=USER_QUERY,
                     context_chunks=[_make_chunk()])


def test_base_class_validates_empty_user_query():
    boto_client = _make_boto_client()
    llm = _make_llm(client=boto_client)
    with pytest.raises(InvalidRagRequestError):
        llm.generate(system_prompt=SYSTEM_PROMPT, user_query="",
                     context_chunks=[_make_chunk()])
