"""Testes das funções auxiliares do notebook RAG — Fase 3.

Zero chamadas AWS. Zero acesso a artefatos reais (usa tmp_path).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers import (
    check_field_value,
    compute_threshold_metrics,
    extract_top_scores,
    format_metrics_table,
    load_artifact,
    mask_sensitive,
    pass_fail_badge,
    smoke_case_html,
    validate_artifact,
)


# ──────────────────────────────────────────────────────────────
# load_artifact
# ──────────────────────────────────────────────────────────────


def test_load_artifact_returns_dict(tmp_path):
    data = {"status": "COMPLETE", "value": 42}
    (tmp_path / "test.json").write_text(json.dumps(data))
    result = load_artifact("test.json", artifacts_dir=tmp_path)
    assert result == data


def test_load_artifact_returns_none_when_missing(tmp_path):
    result = load_artifact("nao_existe.json", artifacts_dir=tmp_path)
    assert result is None


def test_load_artifact_returns_none_on_invalid_json(tmp_path):
    (tmp_path / "bad.json").write_text("{not valid json")
    result = load_artifact("bad.json", artifacts_dir=tmp_path)
    assert result is None


def test_load_artifact_returns_list(tmp_path):
    data = [1, 2, 3]
    (tmp_path / "list.json").write_text(json.dumps(data))
    result = load_artifact("list.json", artifacts_dir=tmp_path)
    assert result == [1, 2, 3]


# ──────────────────────────────────────────────────────────────
# mask_sensitive
# ──────────────────────────────────────────────────────────────


def test_mask_removes_account_id():
    result = mask_sensitive("Account 445358171379 denied")
    assert "445358171379" not in result
    assert "<ACCOUNT_ID>" in result


def test_mask_removes_arn():
    result = mask_sensitive("arn:aws:bedrock:sa-east-1::foundation-model/titan")
    assert "arn:aws" not in result
    assert "<ARN>" in result


def test_mask_removes_s3_uri():
    result = mask_sensitive("s3://my-bucket/path/file.md")
    assert "s3://" not in result
    assert "<S3_URI>" in result


def test_mask_removes_uuid():
    result = mask_sensitive("job-id: 3a6f9b12-4e72-4b0e-9f3c-abc123456789")
    assert "3a6f9b12-4e72-4b0e-9f3c-abc123456789" not in result


def test_mask_preserves_safe_text():
    text = "Corpus indexado com sucesso."
    assert mask_sensitive(text) == text


def test_mask_empty_string():
    assert mask_sensitive("") == ""


# ──────────────────────────────────────────────────────────────
# validate_artifact
# ──────────────────────────────────────────────────────────────


def test_validate_passes_when_all_fields_present():
    data = {"status": "OK", "region": "sa-east-1"}
    errors = validate_artifact(data, ["status", "region"], "test")
    assert errors == []


def test_validate_reports_missing_field():
    data = {"status": "OK"}
    errors = validate_artifact(data, ["status", "region"], "test")
    assert any("region" in e for e in errors)


def test_validate_returns_error_when_none():
    errors = validate_artifact(None, ["status"], "test")
    assert len(errors) == 1
    assert "não encontrado" in errors[0]


def test_validate_multiple_missing_fields():
    errors = validate_artifact({}, ["a", "b", "c"], "test")
    assert len(errors) == 3


# ──────────────────────────────────────────────────────────────
# check_field_value
# ──────────────────────────────────────────────────────────────


def test_check_field_value_passes():
    result = check_field_value({"status": "VALIDATED"}, "status", "VALIDATED", "idx")
    assert result is None


def test_check_field_value_fails():
    result = check_field_value({"status": "FAILED"}, "status", "VALIDATED", "idx")
    assert result is not None
    assert "VALIDATED" in result
    assert "FAILED" in result


def test_check_field_value_missing_key():
    result = check_field_value({}, "status", "VALIDATED", "idx")
    assert result is not None


# ──────────────────────────────────────────────────────────────
# compute_threshold_metrics
# ──────────────────────────────────────────────────────────────

REAL_POS = [0.6515, 0.6617, 0.6714, 0.6728, 0.6759, 0.6836,
            0.6855, 0.6915, 0.7057, 0.7164, 0.7169, 0.7380, 0.7541, 0.7727]
REAL_NEG = [0.5754, 0.6213, 0.7238]


def test_metrics_at_065(tmp_path=None):
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.65])
    row = rows[0]
    assert row["TP"] == 14
    assert row["FN"] == 0
    assert row["TN"] == 2
    assert row["FP"] == 1
    assert row["recall"] == 1.0


def test_metrics_at_070():
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.70])
    row = rows[0]
    assert row["TP"] == 6
    assert row["FN"] == 8
    assert row["TN"] == 2
    assert row["FP"] == 1


def test_metrics_at_075():
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.75])
    row = rows[0]
    assert row["TP"] == 2
    assert row["FN"] == 12
    assert row["TN"] == 3
    assert row["FP"] == 0


def test_metrics_tp_plus_fn_equals_pos_count():
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.50, 0.65, 0.80])
    for row in rows:
        assert row["TP"] + row["FN"] == len(REAL_POS)
        assert row["TN"] + row["FP"] == len(REAL_NEG)


def test_metrics_recall_is_1_at_low_threshold():
    rows = compute_threshold_metrics([0.7, 0.8], [0.5], [0.50])
    assert rows[0]["recall"] == 1.0


def test_metrics_empty_inputs():
    rows = compute_threshold_metrics([], [], [0.70])
    row = rows[0]
    assert row["TP"] == 0 and row["FP"] == 0
    assert row["recall"] == 0.0
    assert row["F1"] == 0.0


def test_f1_higher_at_065_than_070():
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.65, 0.70])
    assert rows[0]["F1"] > rows[1]["F1"]


# ──────────────────────────────────────────────────────────────
# extract_top_scores
# ──────────────────────────────────────────────────────────────


def test_extract_top_scores_basic():
    data = {
        "positive_cases": [{"max_score": 0.8}, {"max_score": 0.7}],
        "negative_cases": [{"max_score": 0.5}],
    }
    pos, neg = extract_top_scores(data)
    assert pos == [0.8, 0.7]
    assert neg == [0.5]


def test_extract_top_scores_ignores_none():
    data = {
        "positive_cases": [{"max_score": 0.8}, {"max_score": None}],
        "negative_cases": [],
    }
    pos, neg = extract_top_scores(data)
    assert pos == [0.8]
    assert neg == []


def test_extract_top_scores_empty():
    pos, neg = extract_top_scores({})
    assert pos == []
    assert neg == []


# ──────────────────────────────────────────────────────────────
# pass_fail_badge
# ──────────────────────────────────────────────────────────────


def test_pass_badge_contains_pass():
    html = pass_fail_badge(True)
    assert "PASS" in html


def test_fail_badge_contains_fail():
    html = pass_fail_badge(False)
    assert "FAIL" in html


def test_pass_badge_color_green():
    html = pass_fail_badge(True)
    assert "#27ae60" in html


def test_fail_badge_color_red():
    html = pass_fail_badge(False)
    assert "#e74c3c" in html


def test_pass_fail_badge_with_label():
    html = pass_fail_badge(True, "Ingestão OK")
    assert "Ingestão OK" in html


# ──────────────────────────────────────────────────────────────
# format_metrics_table
# ──────────────────────────────────────────────────────────────


def test_format_metrics_table_contains_threshold():
    rows = compute_threshold_metrics([0.7], [0.5], [0.65])
    html = format_metrics_table(rows)
    assert "0.65" in html


def test_format_metrics_table_highlights_recommended(tmp_path=None):
    rows = compute_threshold_metrics(REAL_POS, REAL_NEG, [0.65, 0.70])
    html = format_metrics_table(rows, highlight_threshold=0.65)
    assert "#eafaf1" in html


def test_format_metrics_table_is_html():
    rows = compute_threshold_metrics([0.7], [0.5], [0.65])
    html = format_metrics_table(rows)
    assert "<table" in html and "</table>" in html


# ──────────────────────────────────────────────────────────────
# smoke_case_html
# ──────────────────────────────────────────────────────────────


def test_smoke_case_html_found_true():
    case = {"topic": "MARH_OVERVIEW", "found": True, "flow_detail": "BEDROCK_RAG"}
    html = smoke_case_html(case)
    assert "MARH_OVERVIEW" in html
    assert "PASS" in html


def test_smoke_case_html_found_false():
    case = {"topic": "TOPICO_DESCONHECIDO", "found": False, "reason": "topic_unknown"}
    html = smoke_case_html(case)
    assert "FAIL" in html
    assert "topic_unknown" in html


def test_smoke_case_html_is_html():
    html = smoke_case_html({"topic": "X", "found": True})
    assert "<div" in html
