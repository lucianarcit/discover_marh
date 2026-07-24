"""Testes da análise de threshold query-level.

Verifica que a lógica de análise usa top_score por consulta,
não contagem de chunks, e produz os resultados corretos.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gate_runner import analyze_threshold


def _make_retrieve_scores(pos_max_scores: list[float], neg_max_scores: list[float]) -> dict:
    """Monta retrieve_scores mínimo para testar analyze_threshold."""
    pos_cases = [
        {
            "case_id": f"POS-TOPIC_{i}",
            "topic": f"TOPIC_{i}",
            "max_score": s,
            "scores": [s],
            "results_returned": 1,
        }
        for i, s in enumerate(pos_max_scores)
    ]
    neg_cases = [
        {
            "case_id": f"NEG-{i+1:03d}",
            "max_score": s,
            "scores": [s],
            "results_returned": 1,
        }
        for i, s in enumerate(neg_max_scores)
    ]
    return {
        "positive_cases": pos_cases,
        "negative_cases": neg_cases,
        "all_positive_scores": pos_max_scores,
    }


# ──────────────────────────────────────────────────────────────
# Métricas com dados reais do gate (14 pos, 3 neg)
# ──────────────────────────────────────────────────────────────

REAL_POS = [
    0.6515, 0.6617, 0.6714, 0.6728, 0.6759,
    0.6836, 0.6855, 0.6915, 0.7057, 0.7164,
    0.7169, 0.7380, 0.7541, 0.7727,
]
REAL_NEG = [0.5754, 0.6213, 0.7238]


def _get_row(analysis: dict, threshold: float) -> dict:
    for row in analysis["threshold_comparison"]:
        if row["threshold"] == threshold:
            return row
    raise KeyError(f"threshold {threshold} nao encontrado")


def test_threshold_050_tp14_fp3(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.50)
    assert row["TP"] == 14
    assert row["FN"] == 0
    assert row["TN"] == 0
    assert row["FP"] == 3


def test_threshold_060_tp14_fp2(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.60)
    assert row["TP"] == 14
    assert row["FN"] == 0
    assert row["TN"] == 1
    assert row["FP"] == 2


def test_threshold_065_tp14_fp1(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.65)
    assert row["TP"] == 14
    assert row["FN"] == 0
    assert row["TN"] == 2
    assert row["FP"] == 1


def test_threshold_070_tp6_fn8(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.70)
    assert row["TP"] == 6
    assert row["FN"] == 8
    assert row["TN"] == 2
    assert row["FP"] == 1


def test_threshold_075_tp2_fn12(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.75)
    assert row["TP"] == 2
    assert row["FN"] == 12
    assert row["TN"] == 3
    assert row["FP"] == 0


def test_threshold_080_tp0_fn14(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.80)
    assert row["TP"] == 0
    assert row["FN"] == 14
    assert row["TN"] == 3
    assert row["FP"] == 0


def test_recommendation_is_065(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    assert analysis["recommendation"] == 0.65


def test_status_use_065_provisionally(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    assert analysis["status"] == "USE_0_65_PROVISIONALLY"


def test_methodology_is_query_level(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    assert analysis["methodology"] == "query_level"


# ──────────────────────────────────────────────────────────────
# Métricas calculadas corretamente
# ──────────────────────────────────────────────────────────────

def test_recall_at_065_is_1(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    row = _get_row(analysis, 0.65)
    assert row["recall"] == 1.0


def test_f1_at_065_greater_than_at_070(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    f1_065 = _get_row(analysis, 0.65)["F1"]
    f1_070 = _get_row(analysis, 0.70)["F1"]
    assert f1_065 > f1_070


def test_balanced_accuracy_at_065_greater_than_at_070(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    bal_065 = _get_row(analysis, 0.65)["balanced_accuracy"]
    bal_070 = _get_row(analysis, 0.70)["balanced_accuracy"]
    assert bal_065 > bal_070


# ──────────────────────────────────────────────────────────────
# Artefatos
# ──────────────────────────────────────────────────────────────

def test_query_level_artifact_saved(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analyze_threshold(scores)
    assert (tmp_path / "threshold_analysis_query_level.json").exists()


def test_threshold_comparison_artifact_saved(tmp_path, monkeypatch):
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analyze_threshold(scores)
    assert (tmp_path / "threshold_comparison.json").exists()


def test_unit_is_query_not_chunk(tmp_path, monkeypatch):
    """Verifica que TP+FN = número de consultas positivas, não de chunks."""
    monkeypatch.setattr("gate_runner.ARTIFACTS_DIR", tmp_path)
    scores = _make_retrieve_scores(REAL_POS, REAL_NEG)
    analysis = analyze_threshold(scores)
    for row in analysis["threshold_comparison"]:
        assert row["TP"] + row["FN"] == len(REAL_POS), \
            f"TP+FN deveria ser {len(REAL_POS)} (consultas), nao numero de chunks"
        assert row["TN"] + row["FP"] == len(REAL_NEG)
