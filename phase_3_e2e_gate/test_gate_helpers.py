"""Testes do gate end-to-end — helpers e payload de create_knowledge_base.

Regras:
- Zero chamadas AWS reais
- Stubber para validar o payload exato enviado ao Bedrock
"""

from __future__ import annotations

import pytest
import boto3
from botocore.stub import Stubber

from gate_runner import _build_s3_vectors_storage_configuration


FAKE_BUCKET_ARN = "arn:aws:s3vectors:sa-east-1:445300000079:bucket/marh-rag-e2e-test-vbucket"
FAKE_INDEX_ARN  = "arn:aws:s3vectors:sa-east-1:445300000079:bucket/marh-rag-e2e-test-vbucket/index/marh-rag-e2e-test-vindex"
FAKE_EMBED_ARN  = "arn:aws:bedrock:sa-east-1::foundation-model/amazon.titan-embed-text-v2:0"
FAKE_ROLE_ARN   = "arn:aws:iam::445300000079:role/marh-rag-e2e-test-kb-role"


# ──────────────────────────────────────────────────────────────
# _build_s3_vectors_storage_configuration
# ──────────────────────────────────────────────────────────────


def test_contains_vector_bucket_arn():
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert cfg["s3VectorsConfiguration"]["vectorBucketArn"] == FAKE_BUCKET_ARN


def test_contains_index_arn():
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert cfg["s3VectorsConfiguration"]["indexArn"] == FAKE_INDEX_ARN


def test_type_is_s3_vectors():
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert cfg["type"] == "S3_VECTORS"


def test_does_not_contain_vector_bucket_name():
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert "vectorBucketName" not in cfg["s3VectorsConfiguration"]


def test_does_not_contain_bucket_name_as_string():
    """Garante que o bucket name puro não aparece no payload."""
    bucket_name = "marh-rag-e2e-test-vbucket"
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    cfg_str = str(cfg)
    # O ARN pode conter o nome, mas o campo "vectorBucketName" não deve existir
    assert "vectorBucketName" not in cfg_str


def test_does_not_contain_index_name_when_index_arn_used():
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert "indexName" not in cfg["s3VectorsConfiguration"]


def test_empty_vector_bucket_arn_raises():
    with pytest.raises(ValueError, match="vector_bucket_arn"):
        _build_s3_vectors_storage_configuration("", FAKE_INDEX_ARN)


def test_blank_vector_bucket_arn_raises():
    with pytest.raises(ValueError, match="vector_bucket_arn"):
        _build_s3_vectors_storage_configuration("   ", FAKE_INDEX_ARN)


def test_empty_index_arn_raises():
    with pytest.raises(ValueError, match="index_arn"):
        _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, "")


def test_blank_index_arn_raises():
    with pytest.raises(ValueError, match="index_arn"):
        _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, "   ")


def test_s3_vectors_configuration_has_exactly_two_keys():
    """Garante que nenhum campo extra é incluído."""
    cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    assert set(cfg["s3VectorsConfiguration"].keys()) == {"vectorBucketArn", "indexArn"}


# ──────────────────────────────────────────────────────────────
# Stubber — payload completo de create_knowledge_base
# ──────────────────────────────────────────────────────────────


def test_create_knowledge_base_payload_with_stubber():
    """Verifica que create_knowledge_base recebe o payload correto via Stubber."""
    ba_client = boto3.client("bedrock-agent", region_name="sa-east-1")

    storage_cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)

    expected_params = {
        "name": "test-kb",
        "description": "MARH Agent Fase 3 - e2e gate",
        "roleArn": FAKE_ROLE_ARN,
        "knowledgeBaseConfiguration": {
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": FAKE_EMBED_ARN,
            },
        },
        "storageConfiguration": storage_cfg,
        "tags": {"Project": "marh-agent"},
    }

    fake_response = {
        "knowledgeBase": {
            "knowledgeBaseId": "KBTEST0001",
            "name": "test-kb",
            "knowledgeBaseArn": f"arn:aws:bedrock:sa-east-1::knowledge-base/KBTEST0001",
            "roleArn": FAKE_ROLE_ARN,
            "knowledgeBaseConfiguration": expected_params["knowledgeBaseConfiguration"],
            "storageConfiguration": storage_cfg,
            "status": "ACTIVE",
            "createdAt": "2026-07-24T00:00:00Z",
            "updatedAt": "2026-07-24T00:00:00Z",
        }
    }

    with Stubber(ba_client) as stub:
        stub.add_response(
            "create_knowledge_base",
            fake_response,
            expected_params=expected_params,
        )
        resp = ba_client.create_knowledge_base(**expected_params)
        assert resp["knowledgeBase"]["knowledgeBaseId"] == "KBTEST0001"
        stub.assert_no_pending_responses()


def test_create_knowledge_base_payload_excludes_vector_bucket_name():
    """Confirma que vectorBucketName nunca está no payload enviado ao Bedrock."""
    storage_cfg = _build_s3_vectors_storage_configuration(FAKE_BUCKET_ARN, FAKE_INDEX_ARN)
    import json
    payload_str = json.dumps(storage_cfg)
    assert "vectorBucketName" not in payload_str
    assert "indexName" not in payload_str
