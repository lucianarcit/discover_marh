"""Probe de serviços: Knowledge Bases, S3 Vectors, IAM."""
from __future__ import annotations

import json
import os
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

BOTO_CONFIG = Config(
    connect_timeout=5,
    read_timeout=15,
    retries={"max_attempts": 1},
)

REGION = "sa-east-1"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ──────────────────────────────────────────────────────────────
# KNOWLEDGE BASES
# ──────────────────────────────────────────────────────────────
section("KNOWLEDGE BASES — sa-east-1")

kb_result = {}
try:
    agent_client = boto3.client("bedrock-agent", region_name=REGION, config=BOTO_CONFIG)
    resp = agent_client.list_knowledge_bases(maxResults=10)
    kbs = resp.get("knowledgeBaseSummaries", [])
    kb_result["list_knowledge_bases"] = "API_ACCESSIBLE"
    kb_result["existing_kbs"] = len(kbs)
    print(f"  list_knowledge_bases : API_ACCESSIBLE | {len(kbs)} KBs existentes")
except ClientError as e:
    code = e.response["Error"]["Code"]
    msg = e.response["Error"]["Message"]
    if "AccessDeniedException" in code:
        kb_result["list_knowledge_bases"] = "PERMISSION_MISSING"
        kb_result["error_code"] = code
        print(f"  list_knowledge_bases : PERMISSION_MISSING | {code}")
    elif "EndpointResolutionError" in str(e) or "Unknown" in str(e):
        kb_result["list_knowledge_bases"] = "NOT_AVAILABLE_IN_REGION"
        print(f"  list_knowledge_bases : NOT_AVAILABLE_IN_REGION")
    else:
        kb_result["list_knowledge_bases"] = f"ERROR_{code}"
        kb_result["message"] = msg[:200]
        print(f"  list_knowledge_bases : ERROR | {code}: {msg[:100]}")
except Exception as e:
    kb_result["list_knowledge_bases"] = "ERROR"
    kb_result["message"] = str(e)[:200]
    print(f"  list_knowledge_bases : ERROR | {e}")

# Retrieve endpoint
try:
    agent_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=BOTO_CONFIG)
    agent_rt.retrieve(
        knowledgeBaseId="probe-nonexistent-id",
        retrievalQuery={"text": "teste regional"},
    )
    kb_result["retrieve_api"] = "ACCESSIBLE"
    print(f"  retrieve_api         : ACCESSIBLE (inesperado — KB não existe)")
except ClientError as e:
    code = e.response["Error"]["Code"]
    if code in ("ValidationException", "ResourceNotFoundException"):
        kb_result["retrieve_api"] = "ENDPOINT_REACHABLE"
        print(f"  retrieve_api         : ENDPOINT_REACHABLE (esperado {code})")
    elif "AccessDeniedException" in code:
        kb_result["retrieve_api"] = "PERMISSION_MISSING"
        print(f"  retrieve_api         : PERMISSION_MISSING | {code}")
    else:
        kb_result["retrieve_api"] = f"ERROR_{code}"
        print(f"  retrieve_api         : ERROR | {code}")
except Exception as e:
    kb_result["retrieve_api"] = "ERROR"
    kb_result["message_rt"] = str(e)[:200]
    print(f"  retrieve_api         : ERROR | {e}")

with open(os.path.join(ARTIFACTS_DIR, "07_knowledge_bases_availability.json"), "w") as f:
    json.dump(kb_result, f, indent=2)
print(f"  [artifact] 07_knowledge_bases_availability.json")


# ──────────────────────────────────────────────────────────────
# S3 VECTORS
# ──────────────────────────────────────────────────────────────
section("S3 VECTORS — sa-east-1")

s3v_result = {}
try:
    s3v_client = boto3.client("s3vectors", region_name=REGION, config=BOTO_CONFIG)
    s3v_result["sdk_client"] = "CREATABLE"
    print("  SDK client s3vectors : CREATABLE")
    try:
        resp = s3v_client.list_vector_buckets()
        s3v_result["status"] = "AVAILABLE_AND_ACCESSIBLE"
        s3v_result["vector_buckets"] = len(resp.get("vectorBuckets", []))
        print(f"  list_vector_buckets  : AVAILABLE_AND_ACCESSIBLE | {s3v_result['vector_buckets']} buckets")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        if "AccessDeniedException" in code:
            s3v_result["status"] = "REGIONALLY_AVAILABLE_ACCOUNT_ACCESS_PENDING"
            s3v_result["error_code"] = code
            print(f"  list_vector_buckets  : PERMISSION_MISSING | {code}")
        else:
            s3v_result["status"] = f"ERROR_{code}"
            s3v_result["message"] = msg[:200]
            print(f"  list_vector_buckets  : ERROR | {code}: {msg[:100]}")
except Exception as e:
    err = str(e)
    if "Unknown service" in err or "s3vectors" in err.lower():
        s3v_result["status"] = "CLI_OR_SDK_NOT_SUPPORTED"
        s3v_result["message"] = err[:200]
        print(f"  s3vectors            : CLI_OR_SDK_NOT_SUPPORTED")
        print(f"  detail               : {err[:120]}")
    else:
        s3v_result["status"] = "ERROR"
        s3v_result["message"] = err[:200]
        print(f"  s3vectors            : ERROR | {err[:120]}")

with open(os.path.join(ARTIFACTS_DIR, "08_s3_vectors_availability.json"), "w") as f:
    json.dump(s3v_result, f, indent=2)
print(f"  [artifact] 08_s3_vectors_availability.json")


# ──────────────────────────────────────────────────────────────
# IAM — PERMISSÕES
# ──────────────────────────────────────────────────────────────
section("IAM — PERMISSÕES")

# Carregar resultados anteriores para inferir permissões
try:
    with open(os.path.join(ARTIFACTS_DIR, "05_embedding_invocation_results.json")) as f:
        embed_results = json.load(f)
except Exception:
    embed_results = {}

try:
    with open(os.path.join(ARTIFACTS_DIR, "06_generation_converse_results.json")) as f:
        gen_results = json.load(f)
except Exception:
    gen_results = {}

embed_ok = any(v.get("status") == "SUCCESS" for v in embed_results.values())
converse_ok = any(v.get("status") == "CONVERSE_ACTIVE_IN_REGION" for v in gen_results.values())
kb_list_ok = kb_result.get("list_knowledge_bases") == "API_ACCESSIBLE"
kb_retrieve_ok = kb_result.get("retrieve_api") in ("ENDPOINT_REACHABLE", "ACCESSIBLE")

checks = [
    ("bedrock:ListFoundationModels",             True),  # prova: 55 modelos listados
    ("bedrock-runtime:InvokeModel (embed)",      embed_ok),
    ("bedrock-runtime:Converse",                 converse_ok),
    ("bedrock-agent:ListKnowledgeBases",         kb_list_ok),
    ("bedrock-agent-runtime:Retrieve (endpoint)",kb_retrieve_ok),
]

iam_findings = {
    "permissions_confirmed": [],
    "permissions_denied_or_unavailable": [],
    "permissions_future_needed": [
        "bedrock-agent:CreateKnowledgeBase",
        "bedrock-agent:CreateDataSource",
        "bedrock-agent:StartIngestionJob",
        "bedrock-agent:GetKnowledgeBase",
        "s3:GetObject (corpus bucket)",
        "s3:PutObject (corpus bucket)",
        "s3:ListBucket (corpus bucket)",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
    ],
}

for perm, ok in checks:
    if ok:
        iam_findings["permissions_confirmed"].append(perm)
        print(f"  OK : {perm}")
    else:
        iam_findings["permissions_denied_or_unavailable"].append(perm)
        print(f"  !! : {perm}")

with open(os.path.join(ARTIFACTS_DIR, "09_iam_findings.json"), "w") as f:
    json.dump(iam_findings, f, indent=2)
print(f"  [artifact] 09_iam_findings.json")


# ──────────────────────────────────────────────────────────────
# ADR-001
# ──────────────────────────────────────────────────────────────
section("ADR-001 — ARMAZENAMENTO VETORIAL")

kb_accessible = kb_result.get("list_knowledge_bases") in ("API_ACCESSIBLE", "PERMISSION_MISSING")
retrieve_reachable = kb_result.get("retrieve_api") in ("ENDPOINT_REACHABLE", "ACCESSIBLE", "PERMISSION_MISSING")
s3v_sdk_ok = s3v_result.get("sdk_client") == "CREATABLE"
s3v_available = s3v_result.get("status") in ("AVAILABLE_AND_ACCESSIBLE", "REGIONALLY_AVAILABLE_ACCOUNT_ACCESS_PENDING")

print(f"\n  Knowledge Bases API acessível : {kb_accessible}")
print(f"  Retrieve endpoint alcançável  : {retrieve_reachable}")
print(f"  S3 Vectors SDK disponível     : {s3v_sdk_ok}")
print(f"  S3 Vectors status             : {s3v_result.get('status')}")

if kb_accessible and retrieve_reachable:
    recommendation = "KNOWLEDGE_BASES"
    reasoning = (
        "bedrock-agent API alcançável em sa-east-1. "
        "Retrieve endpoint responde (sem KB real, retorna erro esperado). "
        "Menor complexidade operacional. Retrieve separado de geração preserva interfaces. "
        "Permissão de criação a ajustar antes do deploy."
    )
elif s3v_available:
    recommendation = "S3_VECTORS"
    reasoning = "Knowledge Bases inacessível. S3 Vectors disponível como alternativa regional."
else:
    recommendation = "PENDING"
    reasoning = "Ambas as opções com restrições. Verificar IAM."

adr = {
    "decision": recommendation,
    "reasoning": reasoning,
    "knowledge_bases_status": kb_result,
    "s3_vectors_status": s3v_result,
    "comparison": {
        "knowledge_bases": {
            "disponibilidade_sa_east_1": kb_accessible,
            "retrieve_sem_retrieve_and_generate": True,
            "vector_store_interno": "OpenSearch Serverless (gerenciado pela AWS)",
            "custo_fixo": "~$0.10/OCU-hora mínimo (OpenSearch Serverless)",
            "custo_por_query_retrieve": "verificar pricing sa-east-1",
            "terraform": "aws_bedrockagent_knowledge_base + aws_bedrockagent_data_source",
            "controle_score": "Retrieve retorna score por chunk, threshold aplicado no cliente",
            "metadata_por_chunk": True,
            "dependencias_adicionais": "OpenSearch Serverless (embutido)",
            "operacao": "Zero administração de índice",
        },
        "s3_vectors": {
            "disponibilidade_sa_east_1": s3v_result.get("status", "UNKNOWN"),
            "sdk_boto3_atual": s3v_result.get("sdk_client", "NOT_CREATABLE"),
            "custo_fixo": "Apenas S3 storage",
            "custo_por_query": "S3 GET + Lambda + embedding por query",
            "terraform": "S3 bucket + IAM (sem recurso vetorial gerenciado)",
            "controle_score": "Total — implementação própria",
            "metadata_por_chunk": True,
            "dependencias_adicionais": "Lambda de ingestão, busca manual",
            "operacao": "Maior complexidade operacional",
        },
    },
}

with open(os.path.join(ARTIFACTS_DIR, "10_adr_001_vector_retrieval.json"), "w") as f:
    json.dump(adr, f, indent=2, ensure_ascii=False)
print(f"\n  Recomendação ADR-001  : {recommendation}")
print(f"  Reasoning             : {reasoning}")
print(f"  [artifact] 10_adr_001_vector_retrieval.json")


# ──────────────────────────────────────────────────────────────
# BLOCKERS + GO/NO-GO
# ──────────────────────────────────────────────────────────────
section("BLOCKERS + GO / NO-GO")

blockers = []

# Embedding
embed_active = [m for m, v in embed_results.items() if v.get("status") == "SUCCESS"]
if not embed_active:
    blockers.append({
        "id": "BLOCKER-EMBED-SA-EAST-1",
        "description": "Nenhum modelo de embedding invocável em sa-east-1",
        "severity": "CRITICAL",
    })

# Geração
converse_active = [m for m, v in gen_results.items() if v.get("status") == "CONVERSE_ACTIVE_IN_REGION"]
if not converse_active:
    blockers.append({
        "id": "BLOCKER-GEN-MODEL-SA-EAST-1",
        "description": "Nenhum modelo de geração com Converse ativo em sa-east-1",
        "severity": "CRITICAL",
    })

# Vector store
if not kb_accessible and not s3v_available:
    blockers.append({
        "id": "BLOCKER-VECTOR-STORE-SA-EAST-1",
        "description": "Nenhuma opção de armazenamento vetorial acessível em sa-east-1",
        "severity": "CRITICAL",
    })

critical = [b for b in blockers if b["severity"] == "CRITICAL"]
high = [b for b in blockers if b["severity"] == "HIGH"]

if not critical and not high:
    decision = "GO_PHASE_3_IMPLEMENTATION"
elif not critical:
    decision = "GO_PHASE_3_WITH_CONDITIONS"
else:
    decision = "NO_GO_PHASE_3_REGIONAL_BLOCKER"

conditions = []
if kb_result.get("list_knowledge_bases") == "PERMISSION_MISSING":
    conditions.append("Adicionar bedrock-agent:CreateKnowledgeBase à role")
if kb_result.get("retrieve_api") == "PERMISSION_MISSING":
    conditions.append("Adicionar bedrock-agent-runtime:Retrieve à role da Lambda")

go_no_go = {
    "decision": decision,
    "region": REGION,
    "embedding_models_active": embed_active,
    "generation_models_converse_active": converse_active,
    "vector_store_recommendation": recommendation,
    "critical_blockers": critical,
    "high_blockers": high,
    "conditions_to_resolve": conditions,
    "cost_estimate_status": "PENDING_MODEL_AND_VECTOR_STORE_SELECTION",
    "retrieval_score_threshold": "0.70_PROPOSED_PENDING_EVALUATION",
    "generation_model_selection": "PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION",
    "next_permitted_step": (
        "Passo 2 — Adicionar DATA_SOURCE_MODE e KNOWLEDGE_MODE ao config.py"
        if decision in ("GO_PHASE_3_IMPLEMENTATION", "GO_PHASE_3_WITH_CONDITIONS")
        else "Resolver bloqueios antes de prosseguir"
    ),
}

with open(os.path.join(ARTIFACTS_DIR, "11_blockers.json"), "w") as f:
    json.dump(blockers, f, indent=2)
with open(os.path.join(ARTIFACTS_DIR, "12_go_no_go.json"), "w") as f:
    json.dump(go_no_go, f, indent=2, ensure_ascii=False)

if blockers:
    for b in blockers:
        print(f"  [{b['severity']}] {b['id']}: {b['description']}")
else:
    print("  Nenhum bloqueio identificado.")

print(f"\n  DECISÃO FINAL : {decision}")
if conditions:
    print("  Condições:")
    for c in conditions:
        print(f"    - {c}")
print(f"  Próximo passo : {go_no_go['next_permitted_step']}")
print(f"\n  [artifact] 11_blockers.json")
print(f"  [artifact] 12_go_no_go.json")

print("\n" + "="*60)
print("  PROBE DE SERVIÇOS CONCLUÍDO")
print("="*60)
