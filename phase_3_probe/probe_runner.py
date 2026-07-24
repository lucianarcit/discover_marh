"""Regional Capability Probe — Fase 3 MARH Agent.

Executa verificações de disponibilidade de serviços AWS em sa-east-1.
Não cria recursos. Não faz deploy. Apenas lê e testa chamadas mínimas.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

BOTO_CONFIG = Config(
    connect_timeout=5,
    read_timeout=30,
    retries={"max_attempts": 1},
)

REGION = "sa-east-1"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

PROBE_TIMESTAMP = datetime.utcnow().isoformat() + "Z"


def mask_account(s: str) -> str:
    """Mascara Account ID em strings."""
    import re
    return re.sub(r"\b(\d{4})\d{4}(\d{2})\b", r"\1****\2", s)


def save_artifact(name: str, data: object) -> None:
    path = os.path.join(ARTIFACTS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [artifact] {path}")


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ──────────────────────────────────────────────────────────────
# 1. IDENTIDADE E REGIÃO
# ──────────────────────────────────────────────────────────────
section("1. IDENTIDADE E REGIÃO")

sts = boto3.client("sts", region_name=REGION, config=BOTO_CONFIG)
try:
    identity = sts.get_caller_identity()
    account_raw = identity["Account"]
    import re
    user_id_raw = identity["UserId"]
    user_id_masked = re.sub(r"([A-Z0-9]{5})[A-Z0-9]+(:)(.{3})[^@]*(@[^@]+)", r"\1****\2\3****\4****", user_id_raw)
    arn_raw = identity["Arn"]
    # Mascarar account, e-mail e role SSO
    arn_masked = mask_account(arn_raw)
    arn_masked = re.sub(r"(AWSReservedSSO_\w+_)[a-f0-9]+", r"\1****", arn_masked)
    arn_masked = re.sub(r"/[^/]+@[^/]+$", "/****@****.***", arn_masked)

    identity_result = {
        "account_masked": mask_account(account_raw),
        "user_id_masked": user_id_masked,
        "arn_masked": arn_masked,
        "region_configured": REGION,
        "status": "OK",
    }
    print(json.dumps(identity_result, indent=2))
except (ClientError, NoCredentialsError) as e:
    identity_result = {"status": "ERROR", "error": str(e)}
    print(identity_result)

save_artifact("01_identity.json", identity_result)


# ──────────────────────────────────────────────────────────────
# 2. INVENTÁRIO DE FOUNDATION MODELS
# ──────────────────────────────────────────────────────────────
section("2. INVENTÁRIO DE FOUNDATION MODELS — sa-east-1")

bedrock = boto3.client("bedrock", region_name=REGION, config=BOTO_CONFIG)
all_models = []
try:
    resp = bedrock.list_foundation_models()
    for m in resp["modelSummaries"]:
        all_models.append({
            "modelId": m.get("modelId"),
            "modelName": m.get("modelName"),
            "providerName": m.get("providerName"),
            "inputModalities": m.get("inputModalities", []),
            "outputModalities": m.get("outputModalities", []),
            "responseStreamingSupported": m.get("responseStreamingSupported"),
            "inferenceTypesSupported": m.get("inferenceTypesSupported", []),
            "modelLifecycle": m.get("modelLifecycle", {}),
        })
    print(f"Total foundation models listados: {len(all_models)}")
    save_artifact("02_all_models_inventory.json", all_models)
except ClientError as e:
    print(f"ERRO ao listar modelos: {e}")
    save_artifact("02_all_models_inventory.json", {"error": str(e)})


# ──────────────────────────────────────────────────────────────
# 3. MODELOS DE EMBEDDING
# ──────────────────────────────────────────────────────────────
section("3. MODELOS DE EMBEDDING")

embed_models = [
    m for m in all_models
    if "EMBEDDING" in m.get("outputModalities", [])
]
print(f"Candidatos a embedding: {len(embed_models)}")
for m in embed_models:
    status = m.get("modelLifecycle", {}).get("status", "UNKNOWN")
    inf = m.get("inferenceTypesSupported", [])
    print(f"  {m['modelId']}")
    print(f"    provider  : {m['providerName']}")
    print(f"    lifecycle : {status}")
    print(f"    inference : {inf}")

# Focar no candidato primário
EMBED_CANDIDATE = "amazon.titan-embed-text-v2:0"
embed_candidate = next((m for m in embed_models if m["modelId"] == EMBED_CANDIDATE), None)
if embed_candidate:
    print(f"\nCandidato primário ENCONTRADO: {EMBED_CANDIDATE}")
    print(f"  lifecycle : {embed_candidate.get('modelLifecycle', {}).get('status')}")
else:
    print(f"\nCandidato primário NÃO ENCONTRADO: {EMBED_CANDIDATE}")

save_artifact("03_embedding_models.json", {
    "all_embedding_candidates": embed_models,
    "primary_candidate": EMBED_CANDIDATE,
    "primary_found_in_list": embed_candidate is not None,
})


# ──────────────────────────────────────────────────────────────
# 4. MODELOS DE GERAÇÃO (excluindo Haiku)
# ──────────────────────────────────────────────────────────────
section("4. MODELOS DE GERAÇÃO (excluindo Haiku)")

EXCLUDED_PATTERNS = ["haiku", "legacy", "eol"]

gen_models = [
    m for m in all_models
    if "TEXT" in m.get("outputModalities", [])
    and "EMBEDDING" not in m.get("outputModalities", [])
    and not any(ex in m["modelId"].lower() for ex in EXCLUDED_PATTERNS)
    and not any(ex in (m.get("modelName") or "").lower() for ex in EXCLUDED_PATTERNS)
    and "ON_DEMAND" in m.get("inferenceTypesSupported", [])
]

print(f"Candidatos a geração (excl. Haiku, ON_DEMAND): {len(gen_models)}")
for m in gen_models:
    status = m.get("modelLifecycle", {}).get("status", "UNKNOWN")
    print(f"  {m['modelId']}")
    print(f"    provider  : {m['providerName']}")
    print(f"    lifecycle : {status}")
    print(f"    streaming : {m.get('responseStreamingSupported')}")

save_artifact("04_generation_models.json", {
    "excluded_patterns": EXCLUDED_PATTERNS,
    "candidates": gen_models,
})


# ──────────────────────────────────────────────────────────────
# 5. INVOCAÇÃO REAL — EMBEDDING
# ──────────────────────────────────────────────────────────────
section("5. INVOCAÇÃO REAL — EMBEDDING")

bedrock_rt = boto3.client("bedrock-runtime", region_name=REGION, config=BOTO_CONFIG)
SYNTHETIC_TEXT = "Teste técnico de disponibilidade regional MARH POC."

embed_invoke_results = {}

for model_id in [m["modelId"] for m in embed_models]:
    print(f"\nTestando: {model_id}")
    try:
        t0 = time.perf_counter()
        body = json.dumps({"inputText": SYNTHETIC_TEXT})
        resp = bedrock_rt.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        result_body = json.loads(resp["body"].read())
        embedding = result_body.get("embedding", [])
        dimension = len(embedding)
        embed_invoke_results[model_id] = {
            "status": "SUCCESS",
            "dimension": dimension,
            "duration_ms": elapsed,
            "region": REGION,
        }
        print(f"  STATUS: SUCCESS | dimension: {dimension} | {elapsed}ms")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        embed_invoke_results[model_id] = {
            "status": "ERROR",
            "error_code": code,
            "message": msg,
        }
        print(f"  STATUS: ERROR | {code}: {msg}")

save_artifact("05_embedding_invocation_results.json", embed_invoke_results)


# ──────────────────────────────────────────────────────────────
# 6. INVOCAÇÃO REAL — GERAÇÃO + CONVERSE
# ──────────────────────────────────────────────────────────────
section("6. INVOCAÇÃO REAL — GERAÇÃO + CONVERSE")

SYNTHETIC_PROMPT = "Responda apenas: OK"
MAX_TOKENS = 10

gen_invoke_results = {}

bedrock_rt2 = boto3.client("bedrock-runtime", region_name=REGION, config=BOTO_CONFIG)

for m in gen_models:
    model_id = m["modelId"]
    print(f"\nTestando: {model_id}")
    result = {"model_id": model_id, "region": REGION}

    # Tentar Converse API
    try:
        t0 = time.perf_counter()
        converse_resp = bedrock_rt2.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": SYNTHETIC_PROMPT}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        usage = converse_resp.get("usage", {})
        result["converse"] = {
            "status": "CONVERSE_ACTIVE_IN_REGION",
            "duration_ms": elapsed,
            "input_tokens": usage.get("inputTokens"),
            "output_tokens": usage.get("outputTokens"),
        }
        print(f"  CONVERSE: SUCCESS | {elapsed}ms | tokens in={usage.get('inputTokens')} out={usage.get('outputTokens')}")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        if "AccessDeniedException" in code or "access" in msg.lower():
            result["converse"] = {"status": "ACCESS_NOT_GRANTED", "error_code": code, "message": msg}
        elif "ValidationException" in code and "cross" in msg.lower():
            result["converse"] = {"status": "CROSS_REGION_REQUIRED", "error_code": code, "message": msg}
        elif "ValidationException" in code:
            result["converse"] = {"status": "NOT_SUPPORTED", "error_code": code, "message": msg}
        else:
            result["converse"] = {"status": "ERROR", "error_code": code, "message": msg}
        print(f"  CONVERSE: {result['converse']['status']} | {code}")
    except Exception as e:
        result["converse"] = {"status": "ERROR", "message": str(e)}
        print(f"  CONVERSE: ERROR | {e}")

    gen_invoke_results[model_id] = result

save_artifact("06_generation_converse_results.json", gen_invoke_results)


# ──────────────────────────────────────────────────────────────
# 7. KNOWLEDGE BASES — disponibilidade
# ──────────────────────────────────────────────────────────────
section("7. BEDROCK KNOWLEDGE BASES — disponibilidade em sa-east-1")

kb_result = {}
try:
    agent_client = boto3.client("bedrock-agent", region_name=REGION)
    resp = agent_client.list_knowledge_bases(maxResults=10)
    kbs = resp.get("knowledgeBaseSummaries", [])
    kb_result = {
        "status": "API_ACCESSIBLE",
        "existing_knowledge_bases": len(kbs),
        "region": REGION,
        "note": "API bedrock-agent acessível — Knowledge Bases disponível na região/conta",
    }
    print(f"  STATUS: API_ACCESSIBLE | {len(kbs)} KBs existentes")
except ClientError as e:
    code = e.response["Error"]["Code"]
    msg = e.response["Error"]["Message"]
    if "AccessDeniedException" in code:
        kb_result = {"status": "API_ACCESSIBLE_PERMISSION_MISSING", "error_code": code, "message": msg}
        print(f"  STATUS: API_ACCESSIBLE mas sem permissão | {code}")
    elif "UnknownServiceException" in str(e) or "EndpointResolutionError" in str(e):
        kb_result = {"status": "NOT_AVAILABLE_IN_REGION", "error_code": code, "message": msg}
        print(f"  STATUS: NOT_AVAILABLE_IN_REGION | {code}")
    else:
        kb_result = {"status": "ERROR", "error_code": code, "message": msg}
        print(f"  STATUS: ERROR | {code}: {msg}")
except Exception as e:
    kb_result = {"status": "ERROR", "message": str(e)}
    print(f"  STATUS: ERROR | {e}")

# Testar bedrock-agent-runtime Retrieve separadamente
try:
    agent_rt = boto3.client("bedrock-agent-runtime", region_name=REGION)
    # Apenas verificar se o endpoint resolve (sem KB real, vai dar ValidationException)
    agent_rt.retrieve(
        knowledgeBaseId="probe-test-nonexistent",
        retrievalQuery={"text": "teste"},
    )
    kb_result["retrieve_api"] = "ACCESSIBLE"
except ClientError as e:
    code = e.response["Error"]["Code"]
    if code in ("ValidationException", "ResourceNotFoundException"):
        kb_result["retrieve_api"] = "ENDPOINT_REACHABLE"
        print(f"  Retrieve endpoint: REACHABLE (esperado {code} sem KB real)")
    elif "AccessDeniedException" in code:
        kb_result["retrieve_api"] = "PERMISSION_MISSING"
        print(f"  Retrieve endpoint: PERMISSION_MISSING | {code}")
    else:
        kb_result["retrieve_api"] = f"ERROR_{code}"
        print(f"  Retrieve endpoint: ERROR | {code}")
except Exception as e:
    kb_result["retrieve_api"] = f"ERROR: {e}"
    print(f"  Retrieve endpoint: ERROR | {e}")

save_artifact("07_knowledge_bases_availability.json", kb_result)


# ──────────────────────────────────────────────────────────────
# 8. S3 VECTORS — disponibilidade
# ──────────────────────────────────────────────────────────────
section("8. S3 VECTORS — disponibilidade em sa-east-1")

s3v_result = {}
try:
    s3 = boto3.client("s3", region_name=REGION)
    # S3 Vectors: verificar se o cliente aceita operações de vector store
    # A API s3vectors ainda não é um serviço separado no boto3 — é s3tables/s3vectors em preview
    # Tentar criar cliente s3vectors
    s3v_client = boto3.client("s3vectors", region_name=REGION)
    s3v_result = {
        "status": "SDK_CLIENT_CREATABLE",
        "note": "Cliente s3vectors criado — endpoint a confirmar",
    }
    print("  s3vectors client: CREATABLE")
    try:
        resp = s3v_client.list_vector_buckets()
        s3v_result["status"] = "AVAILABLE_AND_ACCESSIBLE"
        s3v_result["vector_buckets"] = len(resp.get("vectorBuckets", []))
        print(f"  STATUS: AVAILABLE_AND_ACCESSIBLE")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if "AccessDeniedException" in code:
            s3v_result["status"] = "REGIONALLY_AVAILABLE_ACCOUNT_ACCESS_PENDING"
            s3v_result["error_code"] = code
        else:
            s3v_result["status"] = f"ERROR_{code}"
            s3v_result["message"] = e.response["Error"]["Message"]
        print(f"  list_vector_buckets: {code}")
except Exception as e:
    err_str = str(e)
    if "Unknown service" in err_str or "s3vectors" in err_str.lower():
        s3v_result = {
            "status": "CLI_OR_SDK_NOT_SUPPORTED",
            "message": err_str[:200],
            "note": "s3vectors não disponível nesta versão do boto3 ou não existe como serviço separado",
        }
    else:
        s3v_result = {"status": "ERROR", "message": err_str[:200]}
    print(f"  s3vectors: {s3v_result['status']} | {err_str[:100]}")

save_artifact("08_s3_vectors_availability.json", s3v_result)


# ──────────────────────────────────────────────────────────────
# 9. IAM — verificar permissões atuais e gaps
# ──────────────────────────────────────────────────────────────
section("9. IAM — PERMISSÕES")

iam_findings = {
    "permissions_tested": [],
    "access_denied": [],
    "accessible": [],
    "notes": [],
}

# Testar permissões via chamadas reais já feitas
tests = [
    ("bedrock:ListFoundationModels", len(all_models) > 0),
    ("bedrock-runtime:InvokeModel (embed)", any(v.get("status") == "SUCCESS" for v in embed_invoke_results.values())),
    ("bedrock-runtime:Converse", any(r.get("converse", {}).get("status") == "CONVERSE_ACTIVE_IN_REGION" for r in gen_invoke_results.values())),
    ("bedrock-agent:ListKnowledgeBases", kb_result.get("status") in ("API_ACCESSIBLE", "API_ACCESSIBLE_PERMISSION_MISSING")),
    ("bedrock-agent-runtime:Retrieve", kb_result.get("retrieve_api") in ("ENDPOINT_REACHABLE", "ACCESSIBLE")),
]

for perm, ok in tests:
    entry = {"permission": perm, "status": "ACCESSIBLE" if ok else "ACCESS_DENIED_OR_UNAVAILABLE"}
    iam_findings["permissions_tested"].append(entry)
    if ok:
        iam_findings["accessible"].append(perm)
        print(f"  OK : {perm}")
    else:
        iam_findings["access_denied"].append(perm)
        print(f"  !! : {perm}")

iam_findings["future_permissions_needed"] = [
    "bedrock:InvokeModel",
    "bedrock:Converse",
    "bedrock-agent-runtime:Retrieve",
    "bedrock-agent:CreateKnowledgeBase",
    "bedrock-agent:StartIngestionJob",
    "s3:GetObject (corpus bucket)",
    "s3:PutObject (corpus bucket)",
    "logs:CreateLogGroup",
    "logs:PutLogEvents",
]

save_artifact("09_iam_findings.json", iam_findings)


# ──────────────────────────────────────────────────────────────
# 10. CONSOLIDAÇÃO — candidatos finais
# ──────────────────────────────────────────────────────────────
section("10. CONSOLIDAÇÃO")

# Embedding
embed_active = {k: v for k, v in embed_invoke_results.items() if v.get("status") == "SUCCESS"}
print(f"\nEmbedding models com invocação bem-sucedida: {list(embed_active.keys())}")

# Generation com Converse ativo
converse_active = {
    model_id: r for model_id, r in gen_invoke_results.items()
    if r.get("converse", {}).get("status") == "CONVERSE_ACTIVE_IN_REGION"
}
print(f"Generation models com Converse ativo: {list(converse_active.keys())}")

# Generation sem Converse mas com erro de acesso (acesso pendente)
converse_pending = {
    model_id: r for model_id, r in gen_invoke_results.items()
    if r.get("converse", {}).get("status") == "ACCESS_NOT_GRANTED"
}
print(f"Generation models com Converse (acesso pendente): {list(converse_pending.keys())}")

# Vector store
kb_accessible = kb_result.get("status") in ("API_ACCESSIBLE", "API_ACCESSIBLE_PERMISSION_MISSING")
retrieve_reachable = kb_result.get("retrieve_api") in ("ENDPOINT_REACHABLE", "ACCESSIBLE", "PERMISSION_MISSING")
s3v_available = s3v_result.get("status") in ("AVAILABLE_AND_ACCESSIBLE", "REGIONALLY_AVAILABLE_ACCOUNT_ACCESS_PENDING")

print(f"\nKnowledge Bases API: {kb_result.get('status')}")
print(f"Retrieve endpoint: {kb_result.get('retrieve_api')}")
print(f"S3 Vectors: {s3v_result.get('status')}")

# ──────────────────────────────────────────────────────────────
# 11. ADR-001 — Decisão de armazenamento vetorial
# ──────────────────────────────────────────────────────────────
section("11. ADR-001 — ARMAZENAMENTO VETORIAL")

adr = {
    "knowledge_bases": {
        "api_accessible": kb_accessible,
        "retrieve_reachable": retrieve_reachable,
        "kb_status": kb_result.get("status"),
        "retrieve_api": kb_result.get("retrieve_api"),
        "advantages": [
            "Zero administração de índice vetorial",
            "S3 como data source nativo",
            "Retrieve API retorna chunks + scores",
            "StartIngestionJob para sync do corpus",
            "Terraform: aws_bedrockagent_knowledge_base disponível",
        ],
        "disadvantages": [
            "Depende de permissão bedrock-agent:CreateKnowledgeBase",
            "OpenSearch Serverless embutido tem custo fixo mínimo",
        ],
    },
    "s3_vectors": {
        "status": s3v_result.get("status"),
        "available": s3v_available,
        "advantages": [
            "Controle total da busca e scores",
            "Sem custo fixo de vector store gerenciado",
        ],
        "disadvantages": [
            "SDK boto3 1.43 pode não ter cliente s3vectors",
            "Ingestão manual de embeddings",
            "Mais código de infraestrutura",
        ],
    },
    "recommendation": None,
    "reasoning": None,
}

if kb_accessible and retrieve_reachable:
    adr["recommendation"] = "KNOWLEDGE_BASES"
    adr["reasoning"] = (
        "bedrock-agent API acessível em sa-east-1, Retrieve endpoint reachable. "
        "Menor complexidade operacional, Retrieve separado de geração preserva interfaces. "
        "Permissões de criação a ajustar antes do deploy."
    )
elif s3v_available:
    adr["recommendation"] = "S3_VECTORS"
    adr["reasoning"] = "Knowledge Bases inacessível; S3 Vectors disponível como alternativa."
else:
    adr["recommendation"] = "PENDING_PERMISSIONS"
    adr["reasoning"] = (
        "Knowledge Bases API acessível mas Retrieve com permissão pendente. "
        "S3 Vectors SDK suporte incerto. Recomenda-se ajustar IAM e re-executar probe."
    )

print(f"Recomendação ADR-001: {adr['recommendation']}")
print(f"Reasoning: {adr['reasoning']}")

save_artifact("10_adr_001_vector_retrieval.json", adr)


# ──────────────────────────────────────────────────────────────
# 12. BLOCKERS
# ──────────────────────────────────────────────────────────────
section("12. BLOCKERS")

blockers = []

if not embed_active:
    blockers.append({
        "id": "BLOCKER-EMBED-SA-EAST-1",
        "description": "Nenhum modelo de embedding invocável com sucesso em sa-east-1",
        "severity": "CRITICAL",
    })

if not converse_active and not converse_pending:
    blockers.append({
        "id": "BLOCKER-GEN-MODEL-SA-EAST-1",
        "description": "Nenhum modelo de geração com Converse ativo ou acessível em sa-east-1",
        "severity": "CRITICAL",
    })
elif converse_pending and not converse_active:
    blockers.append({
        "id": "BLOCKER-GEN-MODEL-ACCESS",
        "description": f"Modelos com Converse existem mas acesso não concedido: {list(converse_pending.keys())}",
        "severity": "HIGH",
    })

if not kb_accessible and not s3v_available:
    blockers.append({
        "id": "BLOCKER-VECTOR-STORE-SA-EAST-1",
        "description": "Nenhuma opção de armazenamento vetorial acessível em sa-east-1",
        "severity": "CRITICAL",
    })

if blockers:
    for b in blockers:
        print(f"  [{b['severity']}] {b['id']}: {b['description']}")
else:
    print("  Nenhum bloqueio crítico identificado.")

save_artifact("11_blockers.json", blockers)


# ──────────────────────────────────────────────────────────────
# 13. GO / NO-GO
# ──────────────────────────────────────────────────────────────
section("13. GO / NO-GO")

critical_blockers = [b for b in blockers if b["severity"] == "CRITICAL"]
high_blockers = [b for b in blockers if b["severity"] == "HIGH"]

if not critical_blockers and not high_blockers:
    decision = "GO_PHASE_3_IMPLEMENTATION"
elif not critical_blockers and high_blockers:
    decision = "GO_PHASE_3_WITH_CONDITIONS"
else:
    decision = "NO_GO_PHASE_3_REGIONAL_BLOCKER"

conditions = []
if converse_pending and not converse_active:
    conditions.append("Solicitar acesso aos modelos de geração via AWS Console (Model Access)")
if kb_result.get("retrieve_api") == "PERMISSION_MISSING":
    conditions.append("Adicionar bedrock-agent-runtime:Retrieve à role da Lambda")

go_no_go = {
    "decision": decision,
    "timestamp": PROBE_TIMESTAMP,
    "region": REGION,
    "embedding_model_active": list(embed_active.keys()),
    "generation_model_converse_active": list(converse_active.keys()),
    "generation_model_access_pending": list(converse_pending.keys()),
    "vector_store_recommendation": adr["recommendation"],
    "critical_blockers": critical_blockers,
    "high_blockers": high_blockers,
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

print(f"\n  DECISÃO: {decision}")
if conditions:
    print("  Condições a resolver:")
    for c in conditions:
        print(f"    - {c}")
print(f"  Próximo passo: {go_no_go['next_permitted_step']}")

save_artifact("12_go_no_go.json", go_no_go)

print("\n" + "="*60)
print("  PROBE CONCLUÍDO")
print("="*60)
print(f"  Artefatos em: {ARTIFACTS_DIR}")
print(f"  Timestamp: {PROBE_TIMESTAMP}")
print(f"  Decisão final: {decision}")
