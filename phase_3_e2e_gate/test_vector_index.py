"""Testes da criação e validação do vector index com metadataConfiguration.

Cobre:
- create_index inclui metadataConfiguration obrigatória via Stubber
- _validate_vector_index_metadata valida corretamente as keys
- artefato salvo em sucesso e em falha
- RuntimeError quando keys estão divergentes
"""

from __future__ import annotations

import json
from pathlib import Path

import boto3
import pytest
from botocore.stub import Stubber

from gate_runner import (
    _REQUIRED_NON_FILTERABLE_KEYS,
    _save_index_validation,
    _validate_vector_index_metadata,
)


VBUCKET = "marh-rag-e2e-test-vbucket"
VINDEX  = "marh-rag-e2e-test-vindex"
FAKE_BUCKET_ARN = "arn:aws:s3vectors:sa-east-1:445300000079:bucket/" + VBUCKET
FAKE_INDEX_ARN  = FAKE_BUCKET_ARN + "/index/" + VINDEX


def _make_s3v_client():
    return boto3.client("s3vectors", region_name="sa-east-1")


def _fake_index_response(non_filterable_keys=None) -> dict:
    """Resposta de GetIndex com as keys configuradas."""
    return {
        "index": {
            "vectorBucketName": VBUCKET,
            "indexName": VINDEX,
            "indexArn": FAKE_INDEX_ARN,
            "creationTime": "2026-07-24T00:00:00Z",
            "dataType": "float32",
            "dimension": 1024,
            "distanceMetric": "cosine",
            "metadataConfiguration": {
                "nonFilterableMetadataKeys": non_filterable_keys
                if non_filterable_keys is not None
                else _REQUIRED_NON_FILTERABLE_KEYS,
            },
        }
    }


# ──────────────────────────────────────────────────────────────
# create_index — payload contém metadataConfiguration (via Stubber)
# ──────────────────────────────────────────────────────────────


def test_create_index_sends_metadata_configuration():
    """Verifica que create_index envia metadataConfiguration com as duas keys."""
    s3v = _make_s3v_client()

    expected_create_params = {
        "vectorBucketName": VBUCKET,
        "indexName": VINDEX,
        "dataType": "float32",
        "dimension": 1024,
        "distanceMetric": "cosine",
        "metadataConfiguration": {
            "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"],
        },
    }

    with Stubber(s3v) as stub:
        stub.add_response(
            "create_index",
            {"indexArn": FAKE_INDEX_ARN},
            expected_params=expected_create_params,
        )
        resp = s3v.create_index(**expected_create_params)
        assert resp["indexArn"] == FAKE_INDEX_ARN
        stub.assert_no_pending_responses()


def test_create_index_includes_amazon_bedrock_text():
    """AMAZON_BEDROCK_TEXT deve estar em nonFilterableMetadataKeys."""
    s3v = _make_s3v_client()
    params = {
        "vectorBucketName": VBUCKET,
        "indexName": VINDEX,
        "dataType": "float32",
        "dimension": 1024,
        "distanceMetric": "cosine",
        "metadataConfiguration": {
            "nonFilterableMetadataKeys": _REQUIRED_NON_FILTERABLE_KEYS,
        },
    }
    with Stubber(s3v) as stub:
        stub.add_response("create_index", {"indexArn": FAKE_INDEX_ARN}, expected_params=params)
        s3v.create_index(**params)
        stub.assert_no_pending_responses()
    assert "AMAZON_BEDROCK_TEXT" in params["metadataConfiguration"]["nonFilterableMetadataKeys"]


def test_create_index_includes_amazon_bedrock_metadata():
    """AMAZON_BEDROCK_METADATA deve estar em nonFilterableMetadataKeys."""
    assert "AMAZON_BEDROCK_METADATA" in _REQUIRED_NON_FILTERABLE_KEYS


def test_create_index_has_exactly_two_non_filterable_keys():
    assert len(_REQUIRED_NON_FILTERABLE_KEYS) == 2


# ──────────────────────────────────────────────────────────────
# _validate_vector_index_metadata — validação via GetIndex
# ──────────────────────────────────────────────────────────────


def test_validate_passes_with_correct_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response(
            "get_index",
            _fake_index_response(),
            expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX},
        )
        _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)
        stub.assert_no_pending_responses()

    data = json.loads((tmp_path / "vector_index_validation.json").read_text())
    assert data["status"] == "VALIDATED"
    assert set(data["non_filterable_metadata_keys"]) == set(_REQUIRED_NON_FILTERABLE_KEYS)


def test_validate_saves_artifact_on_success(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response("get_index", _fake_index_response(),
                          expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX})
        _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    assert (tmp_path / "vector_index_validation.json").exists()


def test_validate_artifact_contains_expected_fields(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response("get_index", _fake_index_response(),
                          expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX})
        _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    data = json.loads((tmp_path / "vector_index_validation.json").read_text())
    assert "dimension" in data
    assert "distance_metric" in data
    assert "data_type" in data
    assert "non_filterable_metadata_keys" in data
    assert "status" in data


def test_validate_fails_with_wrong_keys(tmp_path, monkeypatch):
    """Keys completamente diferentes das esperadas — deve falhar."""
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        # Lista com uma key errada (min_length=1 satisfeito)
        stub.add_response(
            "get_index",
            _fake_index_response(non_filterable_keys=["SOME_OTHER_KEY"]),
            expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX},
        )
        with pytest.raises(RuntimeError, match="GATE_EXECUTION_FAILED_VECTOR_INDEX_VALIDATION"):
            _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    data = json.loads((tmp_path / "vector_index_validation.json").read_text())
    assert data["status"] == "FAILED"
    assert "missing_keys" in data
    assert "AMAZON_BEDROCK_TEXT" in data["missing_keys"]
    assert "AMAZON_BEDROCK_METADATA" in data["missing_keys"]


def test_validate_fails_with_partial_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response(
            "get_index",
            _fake_index_response(non_filterable_keys=["AMAZON_BEDROCK_TEXT"]),
            expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX},
        )
        with pytest.raises(RuntimeError, match="GATE_EXECUTION_FAILED_VECTOR_INDEX_VALIDATION"):
            _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    data = json.loads((tmp_path / "vector_index_validation.json").read_text())
    assert data["status"] == "FAILED"
    assert "AMAZON_BEDROCK_METADATA" in data["missing_keys"]


def test_validate_fails_saves_artifact_before_raising(tmp_path, monkeypatch):
    """Artefato deve existir mesmo quando a validação falha."""
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response(
            "get_index",
            _fake_index_response(non_filterable_keys=["ONLY_ONE_KEY"]),
            expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX},
        )
        with pytest.raises(RuntimeError):
            _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    assert (tmp_path / "vector_index_validation.json").exists()


def test_validate_artifact_does_not_contain_arn(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response("get_index", _fake_index_response(),
                          expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX})
        _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    content = (tmp_path / "vector_index_validation.json").read_text()
    assert "arn:" not in content.lower()


def test_validate_artifact_does_not_contain_bucket_name(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    s3v = _make_s3v_client()

    with Stubber(s3v) as stub:
        stub.add_response("get_index", _fake_index_response(),
                          expected_params={"vectorBucketName": VBUCKET, "indexName": VINDEX})
        _validate_vector_index_metadata(s3v, VBUCKET, VINDEX)

    content = (tmp_path / "vector_index_validation.json").read_text()
    assert VBUCKET not in content


# ──────────────────────────────────────────────────────────────
# _save_index_validation — artefato
# ──────────────────────────────────────────────────────────────


def test_save_index_validation_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    result = {
        "dimension": 1024,
        "distance_metric": "cosine",
        "data_type": "float32",
        "non_filterable_metadata_keys": _REQUIRED_NON_FILTERABLE_KEYS,
        "status": "VALIDATED",
    }
    _save_index_validation(result)
    assert (tmp_path / "vector_index_validation.json").exists()
    data = json.loads((tmp_path / "vector_index_validation.json").read_text())
    assert data["status"] == "VALIDATED"
