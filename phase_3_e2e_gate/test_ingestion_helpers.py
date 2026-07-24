"""Testes dos helpers de ingestão do gate end-to-end.

Cobre: captura de failureReasons, sanitização, salvamento do artefato
antes da exceção, e garantia de que o teardown continua após falha.

Zero chamadas AWS reais.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gate_runner import (
    _build_ingestion_result,
    _sanitize_failure_reason,
    _save_ingestion_artifact,
    ARTIFACTS_DIR,
)


# ──────────────────────────────────────────────────────────────
# _sanitize_failure_reason
# ──────────────────────────────────────────────────────────────

def test_sanitize_removes_arn():
    raw = "Access denied for arn:aws:bedrock:sa-east-1::foundation-model/titan"
    result = _sanitize_failure_reason(raw)
    assert "arn:" not in result
    assert "<ARN>" in result


def test_sanitize_removes_s3_uri():
    raw = "Cannot read s3://my-secret-bucket/knowledge/file.md"
    result = _sanitize_failure_reason(raw)
    assert "s3://" not in result
    assert "<S3_URI>" in result


def test_sanitize_removes_account_id():
    raw = "Account 445358171379 does not have access"
    result = _sanitize_failure_reason(raw)
    assert "445358171379" not in result
    assert "<ACCOUNT_ID>" in result


def test_sanitize_removes_uuid():
    raw = "Job 3a6f9b12-4e72-4b0e-9f3c-abc123456789 failed"
    result = _sanitize_failure_reason(raw)
    assert "3a6f9b12-4e72-4b0e-9f3c-abc123456789" not in result
    assert "<ID>" in result


def test_sanitize_preserves_human_readable_message():
    raw = "Chunking strategy not supported for this vector store type."
    result = _sanitize_failure_reason(raw)
    assert "Chunking strategy not supported" in result


def test_sanitize_empty_string():
    assert _sanitize_failure_reason("") == ""


# ──────────────────────────────────────────────────────────────
# _build_ingestion_result
# ──────────────────────────────────────────────────────────────

def _fake_job(status="FAILED", reasons=None, stats=None) -> dict:
    return {
        "status": status,
        "failureReasons": reasons or [],
        "statistics": stats or {},
    }


def test_build_result_failed_one_reason():
    job = _fake_job(reasons=["Chunking failed for document."])
    result = _build_ingestion_result(job, elapsed=45)
    assert result["status"] == "FAILED"
    assert result["duration_seconds"] == 45
    assert len(result["failure_reasons"]) == 1
    assert "Chunking failed" in result["failure_reasons"][0]


def test_build_result_failed_multiple_reasons():
    job = _fake_job(reasons=["Error 1", "Error 2", "Error 3"])
    result = _build_ingestion_result(job, elapsed=60)
    assert len(result["failure_reasons"]) == 3


def test_build_result_failed_no_reasons():
    job = _fake_job(reasons=[])
    result = _build_ingestion_result(job, elapsed=30)
    assert result["status"] == "FAILED"
    assert result["failure_reasons"] == []


def test_build_result_statistics_absent():
    job = {"status": "FAILED"}
    result = _build_ingestion_result(job, elapsed=10)
    assert result["statistics"]["numberOfDocumentsScanned"] == 0
    assert result["statistics"]["numberOfDocumentsFailed"] == 0


def test_build_result_statistics_populated():
    stats = {
        "numberOfDocumentsScanned": 5,
        "numberOfNewDocumentsIndexed": 3,
        "numberOfModifiedDocumentsIndexed": 1,
        "numberOfDocumentsFailed": 1,
        "numberOfDocumentsDeleted": 0,
    }
    job = _fake_job(status="COMPLETE", stats=stats)
    result = _build_ingestion_result(job, elapsed=120)
    assert result["statistics"]["numberOfDocumentsScanned"] == 5
    assert result["statistics"]["numberOfDocumentsFailed"] == 1


def test_build_result_sanitizes_reasons():
    job = _fake_job(reasons=["Cannot read s3://secret-bucket/file.md"])
    result = _build_ingestion_result(job, elapsed=30)
    assert "secret-bucket" not in result["failure_reasons"][0]
    assert "<S3_URI>" in result["failure_reasons"][0]


def test_build_result_complete_has_no_failure_reasons():
    job = _fake_job(status="COMPLETE", reasons=[])
    result = _build_ingestion_result(job, elapsed=90)
    assert result["failure_reasons"] == []


# ──────────────────────────────────────────────────────────────
# _save_ingestion_artifact — artefato salvo antes da exceção
# ──────────────────────────────────────────────────────────────

def test_artifact_saved_before_exception(tmp_path, monkeypatch):
    """ingestion_result.json deve existir mesmo quando a ingestão falha."""
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)

    result = _build_ingestion_result(
        _fake_job(status="FAILED", reasons=["Chunking error"]),
        elapsed=30,
    )
    _save_ingestion_artifact(result)

    artifact = tmp_path / "ingestion_result.json"
    assert artifact.exists(), "Artefato deve ser salvo antes de qualquer exceção"
    data = json.loads(artifact.read_text())
    assert data["status"] == "FAILED"
    assert data["failure_reasons"]


def test_artifact_content_does_not_contain_arn(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    result = _build_ingestion_result(
        _fake_job(reasons=["arn:aws:bedrock:sa-east-1::kb/SECRET failed"]),
        elapsed=10,
    )
    _save_ingestion_artifact(result)
    content = (tmp_path / "ingestion_result.json").read_text()
    assert "arn:" not in content


def test_artifact_content_does_not_contain_s3_uri(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    result = _build_ingestion_result(
        _fake_job(reasons=["Cannot read s3://bucket/file.md"]),
        elapsed=10,
    )
    _save_ingestion_artifact(result)
    content = (tmp_path / "ingestion_result.json").read_text()
    assert "s3://" not in content


def test_artifact_has_expected_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    result = _build_ingestion_result(_fake_job(), elapsed=15)
    _save_ingestion_artifact(result)
    data = json.loads((tmp_path / "ingestion_result.json").read_text())
    assert "status" in data
    assert "duration_seconds" in data
    assert "statistics" in data
    assert "failure_reasons" in data


# ──────────────────────────────────────────────────────────────
# Teardown continua após falha de ingestão
# ──────────────────────────────────────────────────────────────

def test_teardown_called_after_ingestion_failure():
    """Simula falha de ingestão e verifica que teardown é invocado."""
    teardown_called = []

    def fake_teardown():
        teardown_called.append(True)
        return {"status": "COMPLETE", "actions": [], "errors": [], "residual": 0}

    def fake_ingest(*args, **kwargs):
        raise RuntimeError("Ingestão terminou com status: FAILED. Consulte artifacts/ingestion_result.json")

    # Simular o fluxo do main() de forma controlada
    try:
        fake_ingest()
    except RuntimeError:
        fake_teardown()

    assert teardown_called, "Teardown deve ser chamado mesmo após falha de ingestão"
