"""Calcula métricas query-level a partir do retrieve_scores.json real."""
import json
from pathlib import Path

ARTIFACTS = Path(__file__).parent / "artifacts"

with open(ARTIFACTS / "retrieve_scores.json") as f:
    data = json.load(f)

thresholds = [0.50, 0.60, 0.65, 0.70, 0.75, 0.80]

pos = [(c["case_id"], c["max_score"]) for c in data["positive_cases"]]
neg = [(c["case_id"], c["max_score"]) for c in data["negative_cases"]]

print("--- TOP SCORES POSITIVOS ---")
for cid, s in sorted(pos, key=lambda x: x[1]):
    print(f"  {cid}: {round(s, 4)}")

print("\n--- TOP SCORES NEGATIVOS ---")
for cid, s in neg:
    print(f"  {cid}: {round(s, 4)}")

print()
header = f"{'thresh':<7} {'TP':<4} {'FN':<4} {'TN':<4} {'FP':<4} {'precision':<11} {'recall':<9} {'specificity':<13} {'F1':<8} {'bal_acc'}"
print(header)
print("-" * len(header))

rows = []
for t in thresholds:
    tp = sum(1 for _, s in pos if s >= t)
    fn = sum(1 for _, s in pos if s < t)
    tn = sum(1 for _, s in neg if s < t)
    fp = sum(1 for _, s in neg if s >= t)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1  = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    bal = (recall + specificity) / 2
    rows.append({
        "threshold": t,
        "TP": tp, "FN": fn, "TN": tn, "FP": fp,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "F1": round(f1, 4),
        "balanced_accuracy": round(bal, 4),
    })
    print(f"{t:<7} {tp:<4} {fn:<4} {tn:<4} {fp:<4} {round(precision,3):<11} {round(recall,3):<9} {round(specificity,3):<13} {round(f1,3):<8} {round(bal,3)}")

print("\nRows JSON:")
print(json.dumps(rows, indent=2))
