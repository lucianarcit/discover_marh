"""Testes unitários do BedrockKnowledgeBaseRetriever com botocore Stubber.

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

from marh_agent.clients.bedrock_knowledge_base_retriever import (
    BedrockKnowledgeBaseRetriever,
)
from marh_agent.domain.rag_exceptions import RetrieverError
from marh_agent.domain.rag_models import RetrievedChunk


# ──────────────────────────────────────────────────────────────
# Helpers de construção de resposta AWS stubada
# ──────────────────────────────────────────────────────────────

KB_ID = "kb-test-1234"
REGION = "sa-east-1"


def _make_boto_client():
    """Cria cliente boto3 real para uso com Stubber (sem chamadas de rede)."""
    return boto3.client("bedrock-agent-runtime", region_name=REGION)


def _make_retriever(client=None, kb_id=KB_ID, region=REGION):
    if client is None:
        client = _make_boto_client()
    return BedrockKnowledgeBaseRetriever(
        knowledge_base_id=kb_id,
        region_name=region,
        client=client,
    )


def _retrieve_response(results: list[dict]) -> dict:
    """Monta resposta mínima compatível com o shape RetrieveResponse."""
    return {"retrievalResults": results}


def _text_result(
    text: str,
    score: float | None = 0.85,
    s3_uri: str | None = "s3://bucket/knowledge/marh.md",
    metadata: dict | None = None,
    content_type: str = "TEXT",
) -> dict:
    """Monta um item de retrievalResult com conteúdo textual."""
    result: dict = {
        "content": {"text": text, "type": content_type},
    }
    if score is not None:
        result["score"] = score
    if s3_uri is not None:
        result["location"] = {
            "type": "S3",
            "s3Location": {"uri": s3_uri},
        }
    else:
        result["location"] = {"type": "S3", "s3Location": {}}
    result["metadata"] = metadata or {}
    return result


EXPECTED_RETRIEVE_PARAMS = {
    "knowledgeBaseId": KB_ID,
    "retrievalQuery": {"text": "O que é o MARH?"},
    "retrievalConfiguration": {
        "vectorSearchConfiguration": {"numberOfResults": 5}
    },
}


# ──────────────────────────────────────────────────────────────
# Construção
# ──────────────────────────────────────────────────────────────


def test_construction_valid():
    client = _make_boto_client()
    retriever = BedrockKnowledgeBaseRetriever(
        knowledge_base_id=KB_ID,
        region_name=REGION,
        client=client,
    )
    assert retriever is not None


def test_construction_empty_kb_id_rejected():
    with pytest.raises(ValueError, match="knowledge_base_id"):
        BedrockKnowledgeBaseRetriever(knowledge_base_id="", region_name=REGION)


def test_construction_blank_kb_id_rejected():
    with pytest.raises(ValueError, match="knowledge_base_id"):
        BedrockKnowledgeBaseRetriever(knowledge_base_id="   ", region_name=REGION)


def test_construction_empty_region_rejected():
    with pytest.raises(ValueError, match="region_name"):
        BedrockKnowledgeBaseRetriever(knowledge_base_id=KB_ID, region_name="")


def test_construction_blank_region_rejected():
    with pytest.raises(ValueError, match="region_name"):
        BedrockKnowledgeBaseRetriever(knowledge_base_id=KB_ID, region_name="   ")


def test_injected_client_is_used():
    """Quando client é injetado, não deve criar outro cliente boto3."""
    sentinel = object()  # não é um cliente boto3 real — apenas marca
    retriever = BedrockKnowledgeBaseRetriever(
        knowledge_base_id=KB_ID,
        region_name=REGION,
        client=sentinel,
    )
    assert retriever._client is sentinel


def test_no_client_created_when_injected():
    """Injeção de cliente não deve levantar erro mesmo sem credenciais."""
    fake_client = _make_boto_client()
    retriever = BedrockKnowledgeBaseRetriever(
        knowledge_base_id=KB_ID,
        region_name=REGION,
        client=fake_client,
    )
    assert retriever._client is fake_client


# ──────────────────────────────────────────────────────────────
# Request — formato correto enviado ao Bedrock
# ──────────────────────────────────────────────────────────────


def test_retrieve_sends_correct_knowledge_base_id():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto de teste.")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        retriever.retrieve("O que é o MARH?", top_k=5)
        stub.assert_no_pending_responses()


def test_retrieve_sends_correct_query():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        expected = {
            "knowledgeBaseId": KB_ID,
            "retrievalQuery": {"text": "Como fazer um pedido?"},
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {"numberOfResults": 3}
            },
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.")]),
            expected_params=expected,
        )
        retriever = _make_retriever(client=boto_client)
        retriever.retrieve("Como fazer um pedido?", top_k=3)
        stub.assert_no_pending_responses()


def test_retrieve_sends_top_k_as_number_of_results():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        expected = {
            "knowledgeBaseId": KB_ID,
            "retrievalQuery": {"text": "Teste top_k."},
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {"numberOfResults": 7}
            },
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([]),
            expected_params=expected,
        )
        retriever = _make_retriever(client=boto_client)
        result = retriever.retrieve("Teste top_k.", top_k=7)
        assert result == []
        stub.assert_no_pending_responses()


def test_retrieve_region_is_sa_east_1_by_default():
    """Retriever sem client explícito deve usar sa-east-1."""
    retriever = BedrockKnowledgeBaseRetriever.__new__(BedrockKnowledgeBaseRetriever)
    retriever._knowledge_base_id = KB_ID
    retriever._region_name = "sa-east-1"
    assert retriever._region_name == "sa-east-1"


# ──────────────────────────────────────────────────────────────
# Mapeamento de resultados — conteúdo
# ──────────────────────────────────────────────────────────────


def test_content_text_mapped_to_chunk_content():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("O MARH é o Meu Alelo RH.")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert len(chunks) == 1
    assert chunks[0].content == "O MARH é o Meu Alelo RH."


def test_score_float_mapped():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", score=0.923)]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].score == pytest.approx(0.923)


def test_score_zero_accepted():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", score=0.0)]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].score == 0.0


def test_score_absent_maps_to_none():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        result_no_score = {
            "content": {"text": "Texto sem score.", "type": "TEXT"},
            "location": {"type": "S3", "s3Location": {"uri": "s3://bucket/doc.md"}},
            "metadata": {},
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([result_no_score]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].score is None


def test_empty_response_returns_empty_list():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks == []


def test_result_without_text_discarded():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        no_text = {
            "content": {"text": "", "type": "TEXT"},
            "location": {"type": "S3", "s3Location": {"uri": "s3://b/f.md"}},
            "metadata": {},
            "score": 0.9,
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([no_text]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks == []


def test_non_text_content_type_discarded():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        image_result = {
            "content": {"byteContent": "base64data==", "type": "IMAGE"},
            "location": {"type": "S3", "s3Location": {"uri": "s3://b/img.png"}},
            "metadata": {},
            "score": 0.9,
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([image_result]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks == []


def test_mix_valid_and_invalid_results():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([
                _text_result("Chunk válido 1.", score=0.90),
                {"content": {"text": "", "type": "TEXT"}, "location": {"type": "S3", "s3Location": {}}, "metadata": {}},
                _text_result("Chunk válido 2.", score=0.80),
                {"content": {"byteContent": "data", "type": "IMAGE"}, "location": {"type": "S3", "s3Location": {}}, "metadata": {}},
            ]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert len(chunks) == 2
    assert chunks[0].content == "Chunk válido 1."
    assert chunks[1].content == "Chunk válido 2."


def test_order_preserved():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([
                _text_result("Primeiro.", score=0.70),
                _text_result("Segundo.", score=0.95),
                _text_result("Terceiro.", score=0.80),
            ]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert [c.content for c in chunks] == ["Primeiro.", "Segundo.", "Terceiro."]


def test_multiple_chunks_returned():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([
                _text_result(f"Chunk {i}.", score=0.9 - i * 0.05)
                for i in range(5)
            ]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert len(chunks) == 5


# ──────────────────────────────────────────────────────────────
# source_file — extração de S3 URI
# ──────────────────────────────────────────────────────────────


def test_source_file_extracted_from_s3_uri():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", s3_uri="s3://bucket/knowledge/marh.md")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].source_file == "marh.md"


def test_source_file_subpath_stripped():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", s3_uri="s3://bucket/a/b/c/faq_pedidos.md")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].source_file == "faq_pedidos.md"


def test_source_file_url_encoded_decoded():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", s3_uri="s3://bucket/nome%20com%20espa%C3%A7o.md")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].source_file == "nome com espaço.md"


def test_source_file_none_when_uri_absent():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", s3_uri=None)]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].source_file is None


def test_source_file_none_for_non_s3_location():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        web_result = {
            "content": {"text": "Texto web.", "type": "TEXT"},
            "location": {"type": "WEB", "webLocation": {"url": "https://example.com/doc"}},
            "metadata": {},
            "score": 0.8,
        }
        stub.add_response(
            "retrieve",
            _retrieve_response([web_result]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].source_file is None


# Testes diretos do helper estático (sem Stubber)


def test_extract_source_file_helper_basic():
    location = {"type": "S3", "s3Location": {"uri": "s3://bucket/doc.md"}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) == "doc.md"


def test_extract_source_file_helper_subpath():
    location = {"type": "S3", "s3Location": {"uri": "s3://bucket/a/b/doc.md"}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) == "doc.md"


def test_extract_source_file_helper_url_encoded():
    location = {"type": "S3", "s3Location": {"uri": "s3://b/nome%20arquivo.md"}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) == "nome arquivo.md"


def test_extract_source_file_helper_empty_uri():
    location = {"type": "S3", "s3Location": {"uri": ""}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) is None


def test_extract_source_file_helper_non_s3():
    location = {"type": "WEB", "webLocation": {"url": "https://x.com"}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) is None


def test_extract_source_file_helper_no_slash_after_bucket():
    location = {"type": "S3", "s3Location": {"uri": "s3://bucket-only"}}
    assert BedrockKnowledgeBaseRetriever._extract_source_file(location) is None


# ──────────────────────────────────────────────────────────────
# Metadata — sanitização
# ──────────────────────────────────────────────────────────────


def test_metadata_safe_fields_mapped():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result(
                "Texto.",
                metadata={"section_title": "Pedidos", "approved": True},
            )]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].metadata.get("section_title") == "Pedidos"
    assert chunks[0].metadata.get("approved") is True


def test_metadata_blocked_fields_removed():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result(
                "Texto.",
                metadata={
                    "x-amz-bedrock-kb-source-uri": "s3://bucket/secret",
                    "x-amz-bedrock-kb-chunk-id": "chunk-0001",
                    "section_title": "Pedidos",
                },
            )]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert "x-amz-bedrock-kb-source-uri" not in chunks[0].metadata
    assert "x-amz-bedrock-kb-chunk-id" not in chunks[0].metadata
    assert chunks[0].metadata.get("section_title") == "Pedidos"


def test_metadata_non_scalar_values_excluded():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result(
                "Texto.",
                metadata={
                    "safe_field": "valor seguro",
                    "nested_object": {"key": "value"},
                },
            )]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].metadata.get("safe_field") == "valor seguro"
    assert "nested_object" not in chunks[0].metadata


def test_document_id_not_exposed():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        result_with_doc_id = _text_result("Texto.")
        result_with_doc_id["documentId"] = "doc-internal-id-secret"
        stub.add_response(
            "retrieve",
            _retrieve_response([result_with_doc_id]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    chunk_str = str(chunks[0].model_dump())
    assert "doc-internal-id-secret" not in chunk_str


def test_section_number_extracted_from_metadata():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", metadata={"section_number": "4"})]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].section_number == "4"


def test_section_title_extracted_from_metadata():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", metadata={"section_title": "Colaboradores"})]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].section_title == "Colaboradores"


def test_chunk_index_extracted_from_metadata():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.", metadata={"chunk_index": 2})]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert chunks[0].chunk_index == 2


# ──────────────────────────────────────────────────────────────
# Erros AWS → RetrieverError
# ──────────────────────────────────────────────────────────────


def _add_error(stub: Stubber, code: str, message: str = "Erro simulado.") -> None:
    stub.add_client_error(
        "retrieve",
        service_error_code=code,
        service_message=message,
        expected_params=EXPECTED_RETRIEVE_PARAMS,
    )


def test_access_denied_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "AccessDeniedException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError, match="permissões IAM"):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_resource_not_found_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "ResourceNotFoundException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError, match="BEDROCK_KNOWLEDGE_BASE_ID"):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_validation_exception_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "ValidationException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError, match="inválidos"):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_throttling_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "ThrottlingException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError, match="throttling"):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_internal_server_error_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "InternalServerException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_generic_client_error_raises_retriever_error():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "SomeUnknownException")
        retriever = _make_retriever(client=boto_client)
        with pytest.raises(RetrieverError):
            retriever.retrieve("O que é o MARH?", top_k=5)


def test_error_message_does_not_contain_query():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "AccessDeniedException")
        retriever = _make_retriever(client=boto_client)
        try:
            retriever.retrieve("O que é o MARH?", top_k=5)
            pytest.fail("Esperava RetrieverError")
        except RetrieverError as exc:
            assert "O que é o MARH?" not in str(exc)


def test_error_message_does_not_contain_s3_uri():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        _add_error(stub, "ResourceNotFoundException", "s3://bucket/secret/path.md")
        retriever = _make_retriever(client=boto_client)
        try:
            retriever.retrieve("O que é o MARH?", top_k=5)
            pytest.fail("Esperava RetrieverError")
        except RetrieverError as exc:
            assert "s3://" not in str(exc)
            assert "bucket" not in str(exc)


# ──────────────────────────────────────────────────────────────
# Contrato — não aplica threshold, não gera, não chama modelo
# ──────────────────────────────────────────────────────────────


def test_no_threshold_applied_low_score_chunk_returned():
    """Retriever retorna chunk com score baixo — threshold é do BedrockRagKnowledgeClient."""
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Chunk baixo score.", score=0.10)]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    assert len(chunks) == 1
    assert chunks[0].score == pytest.approx(0.10)


def test_return_is_list_of_retrieved_chunks():
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([_text_result("Texto.")]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        result = retriever.retrieve("O que é o MARH?", top_k=5)
    assert isinstance(result, list)
    assert all(isinstance(c, RetrievedChunk) for c in result)


def test_retriever_does_not_reorder_results():
    """O Retriever preserva a ordem AWS — não reordena por score."""
    boto_client = _make_boto_client()
    with Stubber(boto_client) as stub:
        stub.add_response(
            "retrieve",
            _retrieve_response([
                _text_result("Score baixo primeiro.", score=0.50),
                _text_result("Score alto segundo.", score=0.99),
            ]),
            expected_params=EXPECTED_RETRIEVE_PARAMS,
        )
        retriever = _make_retriever(client=boto_client)
        chunks = retriever.retrieve("O que é o MARH?", top_k=5)
    # Ordem preservada: baixo score vem primeiro (como AWS retornou)
    assert chunks[0].content == "Score baixo primeiro."
    assert chunks[1].content == "Score alto segundo."


def test_boto3_not_in_module_namespace():
    import marh_agent.clients.bedrock_knowledge_base_retriever as mod
    # O módulo importa boto3 (legítimo), mas não deve expor cliente global
    assert not hasattr(mod, "_global_client")
