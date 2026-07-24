"""Probe focado: modelos de geração candidatos para PT-BR com timeout."""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

REGION = "sa-east-1"
BOTO_CONFIG = Config(
    connect_timeout=5,
    read_timeout=25,
    retries={"max_attempts": 1},
)
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Candidatos priorizados: multilingual documentado, excluindo Haiku, safeguard, voz, coder, thinking
# Filtro por modelLifecycle.status == ACTIVE (campo real da API), não por palavras no nome
# Claude 3 Sonnet excluído da shortlist por risco de ciclo de vida (modelo de 2024)
CANDIDATES = [
    # Mistral — multilingual documentado
    "mistral.mistral-large-2402-v1:0",
    "mistral.magistral-small-2509",
    "mistral.ministral-3-14b-instruct",
    "mistral.ministral-3-8b-instruct",
    "mistral.mistral-7b-instruct-v0:2",
    "mistral.mixtral-8x7b-instruct-v0:1",
    # Google Gemma — multilingual documentado pelo provedor; qualidade PT-BR a avaliar no Passo 10
    "google.gemma-3-27b-it",
    "google.gemma-3-12b-it",
    "google.gemma-3-4b-it",
    # Nvidia Nemotron — multilingual
    "nvidia.nemotron-nano-12b-v2",
    # Qwen — multilingual amplo; qualidade PT-BR a avaliar no Passo 10
    "qwen.qwen3-32b-v1:0",
]

SYNTHETIC_PROMPT = "Responda apenas: OK"
MAX_TOKENS = 10
TIMEOUT_SECS = 20

bedrock_rt = boto3.client("bedrock-runtime", region_name=REGION, config=BOTO_CONFIG)


def test_converse(model_id: str) -> dict:
    try:
        t0 = time.perf_counter()
        resp = bedrock_rt.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": SYNTHETIC_PROMPT}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        usage = resp.get("usage", {})
        return {
            "status": "CONVERSE_ACTIVE_IN_REGION",
            "duration_ms": elapsed,
            "input_tokens": usage.get("inputTokens"),
            "output_tokens": usage.get("outputTokens"),
        }
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        if "AccessDeniedException" in code:
            return {"status": "ACCESS_NOT_GRANTED", "error_code": code, "message": msg[:120]}
        if "ValidationException" in code and "cross" in msg.lower():
            return {"status": "CROSS_REGION_REQUIRED", "error_code": code, "message": msg[:120]}
        if "ValidationException" in code:
            return {"status": "NOT_SUPPORTED", "error_code": code, "message": msg[:120]}
        return {"status": f"ERROR_{code}", "message": msg[:120]}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)[:120]}


results = {}

print(f"Testando {len(CANDIDATES)} candidatos de geração em {REGION}\n")
print(f"{'Modelo':<55} {'Status':<35} {'ms':>6}")
print("-" * 100)

for model_id in CANDIDATES:
    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(test_converse, model_id)
        try:
            r = future.result(timeout=TIMEOUT_SECS)
        except FuturesTimeout:
            r = {"status": "TIMEOUT", "timeout_secs": TIMEOUT_SECS}
        except Exception as e:
            r = {"status": "ERROR", "message": str(e)[:120]}

    results[model_id] = r
    ms = r.get("duration_ms", "-")
    print(f"{model_id:<55} {r['status']:<35} {ms:>6}")

# Salvar
with open(os.path.join(ARTIFACTS_DIR, "06_generation_converse_results.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n--- RESUMO ---")
active = [m for m, r in results.items() if r["status"] == "CONVERSE_ACTIVE_IN_REGION"]
pending = [m for m, r in results.items() if r["status"] == "ACCESS_NOT_GRANTED"]
no_cross = [m for m, r in results.items() if r["status"] == "CROSS_REGION_REQUIRED"]
timeout_list = [m for m, r in results.items() if r["status"] == "TIMEOUT"]

print(f"CONVERSE_ACTIVE_IN_REGION : {len(active)}")
for m in active:
    print(f"  {m}  ({results[m].get('duration_ms')}ms)")

print(f"ACCESS_NOT_GRANTED        : {len(pending)}")
for m in pending:
    print(f"  {m}")

print(f"CROSS_REGION_REQUIRED     : {len(no_cross)}")
for m in no_cross:
    print(f"  {m}")

print(f"TIMEOUT                   : {len(timeout_list)}")
for m in timeout_list:
    print(f"  {m}")

print(f"\nArtifact: {ARTIFACTS_DIR}/06_generation_converse_results.json")
