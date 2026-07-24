"""
PASSO 8A — Gate End-to-End Descartável (Fase 3 RAG)

Cria recursos AWS temporários, executa ingestão e Retrieve reais,
depois remove exclusivamente os recursos criados aqui.

Região: sa-east-1 (obrigatória — sem cross-region)
Corpus: discover3/knowledge/marh_feature_knowledge.md

Uso:
    cd C:\\proj\\discover_alelo
    python phase_3_e2e_gate/gate_runner.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# ──────────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────────

REGION = "sa-east-1"
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
CORPUS_PATH = Path(__file__).parent.parent / "discover3" / "knowledge" / "marh_feature_knowledge.md"
GATE_DIR = Path(__file__).parent
ARTIFACTS_DIR = GATE_DIR / "artifacts"
MANIFEST_PATH = GATE_DIR / "resource_manifest.json"
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Sufixo único baseado em timestamp curto
TS = datetime.now(timezone.utc).strftime("%m%d%H%M")
PREFIX = f"marh-rag-e2e-{TS}"

TAGS = [
    {"key": "Project", "value": "marh-agent"},
    {"key": "Environment", "value": "e2e-probe"},
    {"key": "Purpose", "value": "phase-3-gate"},
    {"key": "Temporary", "value": "true"},
]

BOTO_CFG = Config(connect_timeout=10, read_timeout=60, retries={"max_attempts": 2, "mode": "standard"})

# top_k para o gate
TOP_K = 5
SCORE_THRESHOLD = 0.70

# ──────────────────────────────────────────────────────────────
# Manifesto de recursos
# ──────────────────────────────────────────────────────────────

manifest: dict = {}


def save_manifest() -> None:
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, default=str)


def mask(s: str) -> str:
    """Mascara Account ID e ARNs em strings."""
    import re
    s = re.sub(r"\b(\d{4})\d{4}(\d{2})\b", r"\1****\2", s)
    s = re.sub(r"arn:aws[^\"'\s]+", lambda m: m.group()[:20] + "****", s)
    return s


def section(title: str) -> None:
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


def log(msg: str) -> None:
    print(f"  {msg}")


# ──────────────────────────────────────────────────────────────
# 1. PREFLIGHT
# ──────────────────────────────────────────────────────────────


def preflight() -> dict:
    section("1. PREFLIGHT")
    result: dict = {}

    # Identidade
    sts = boto3.client("sts", region_name=REGION, config=BOTO_CFG)
    identity = sts.get_caller_identity()
    account = identity["Account"]
    result["account_masked"] = mask(account)[:4] + "****" + mask(account)[-2:]
    result["region"] = REGION
    log(f"Account: {result['account_masked']}")
    log(f"Region : {REGION}")

    # Corpus
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus não encontrado: {CORPUS_PATH}")
    corpus_bytes = CORPUS_PATH.read_bytes()
    sha256 = hashlib.sha256(corpus_bytes).hexdigest()
    result["corpus_path"] = str(CORPUS_PATH)
    result["corpus_size_bytes"] = len(corpus_bytes)
    result["corpus_sha256"] = sha256
    log(f"Corpus : {CORPUS_PATH.name} ({len(corpus_bytes)} bytes, sha256={sha256[:16]}...)")

    # Clientes boto3
    clients_ok = []
    for svc in ["s3", "s3vectors", "bedrock", "bedrock-agent", "bedrock-agent-runtime", "iam"]:
        try:
            boto3.client(svc, region_name=REGION, config=BOTO_CFG)
            clients_ok.append(svc)
        except Exception as e:
            raise RuntimeError(f"Não foi possível criar cliente {svc}: {e}")
    result["clients_ok"] = clients_ok
    log(f"Clientes OK: {clients_ok}")

    result["status"] = "PASSED"
    log("PREFLIGHT_STATUS=PASSED")
    return result


# ──────────────────────────────────────────────────────────────
# 2. BUCKET S3 DO CORPUS
# ──────────────────────────────────────────────────────────────


def create_s3_bucket(account: str) -> str:
    section("2. BUCKET S3 DO CORPUS")
    s3 = boto3.client("s3", region_name=REGION, config=BOTO_CFG)
    bucket_name = f"{PREFIX}-corpus"
    log(f"Criando bucket: {bucket_name}")

    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": REGION},
    )
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
        },
    )

    # Upload corpus
    s3_key = "knowledge/marh_feature_knowledge.md"
    s3.upload_file(str(CORPUS_PATH), bucket_name, s3_key)
    log(f"Upload: s3://{bucket_name}/{s3_key}")

    manifest["s3_bucket"] = bucket_name
    manifest["s3_key"] = s3_key
    save_manifest()
    return bucket_name


# ──────────────────────────────────────────────────────────────
# 3. S3 VECTORS
# ──────────────────────────────────────────────────────────────


def create_s3_vectors() -> tuple[str, str]:
    section("3. S3 VECTORS")
    s3v = boto3.client("s3vectors", region_name=REGION, config=BOTO_CFG)

    vbucket_name = f"{PREFIX}-vbucket"
    vindex_name = f"{PREFIX}-vindex"

    log(f"Criando vector bucket: {vbucket_name}")
    s3v.create_vector_bucket(vectorBucketName=vbucket_name)
    manifest["vector_bucket"] = vbucket_name
    save_manifest()

    log(f"Criando vector index: {vindex_name} (dim=1024, cosine, float32)")
    s3v.create_index(
        vectorBucketName=vbucket_name,
        indexName=vindex_name,
        dataType="float32",
        dimension=1024,
        distanceMetric="cosine",
    )
    manifest["vector_index"] = vindex_name
    save_manifest()
    return vbucket_name, vindex_name


# ──────────────────────────────────────────────────────────────
# 4. IAM TEMPORÁRIO
# ──────────────────────────────────────────────────────────────


def create_iam_role(account: str, bucket_name: str, vbucket_name: str) -> str:
    section("4. IAM TEMPORÁRIO")
    iam = boto3.client("iam", region_name=REGION, config=BOTO_CFG)
    role_name = f"{PREFIX}-kb-role"

    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": account},
                "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock:{REGION}:{account}:knowledge-base/*"},
            },
        }],
    }

    resp = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust),
        Description="Temporary role for MARH e2e gate - Fase 3",
        Tags=[{"Key": t["key"], "Value": t["value"]} for t in TAGS],
    )
    role_arn = resp["Role"]["Arn"]
    manifest["iam_role_name"] = role_name
    manifest["iam_role_arn_masked"] = mask(role_arn)
    save_manifest()
    log(f"Role criada: {mask(role_arn)}")

    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:DeleteVectors",
                    "s3vectors:QueryVectors",
                    "s3vectors:ListVectors",
                ],
                "Resource": f"arn:aws:s3vectors:{REGION}:{account}:bucket/{vbucket_name}/index/*",
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": f"arn:aws:bedrock:{REGION}::foundation-model/{EMBED_MODEL_ID}",
            },
        ],
    }
    policy_name = f"{PREFIX}-kb-policy"
    policy_resp = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_doc),
        Description="Temporary policy for MARH e2e gate - Fase 3",
        Tags=[{"Key": t["key"], "Value": t["value"]} for t in TAGS],
    )
    policy_arn = policy_resp["Policy"]["Arn"]
    manifest["iam_policy_arn_masked"] = mask(policy_arn)
    manifest["iam_policy_name"] = policy_name
    save_manifest()

    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    log(f"Policy criada e anexada: {policy_name}")

    # Aguardar propagação IAM
    log("Aguardando propagação IAM (10s)...")
    time.sleep(10)
    return role_arn


# ──────────────────────────────────────────────────────────────
# 5. KNOWLEDGE BASE
# ──────────────────────────────────────────────────────────────


def create_knowledge_base(role_arn: str, account: str,
                           vbucket_name: str, vindex_name: str) -> str:
    section("5. KNOWLEDGE BASE")
    ba = boto3.client("bedrock-agent", region_name=REGION, config=BOTO_CFG)
    kb_name = f"{PREFIX}-kb"

    resp = ba.create_knowledge_base(
        name=kb_name,
        description="MARH Agent Fase 3 — e2e gate temporário",
        roleArn=role_arn,
        knowledgeBaseConfiguration={
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": f"arn:aws:bedrock:{REGION}::foundation-model/{EMBED_MODEL_ID}",
            },
        },
        storageConfiguration={
            "type": "S3_VECTORS",
            "s3VectorsConfiguration": {
                "vectorBucketName": vbucket_name,
                "indexName": vindex_name,
            },
        },
        tags={t["key"]: t["value"] for t in TAGS},
    )
    kb_id = resp["knowledgeBase"]["knowledgeBaseId"]
    manifest["knowledge_base_id"] = kb_id
    save_manifest()
    log(f"KB criada: {kb_id[:8]}****")

    # Aguardar estado ACTIVE
    log("Aguardando KB ficar ACTIVE...")
    for _ in range(30):
        time.sleep(10)
        status_resp = ba.get_knowledge_base(knowledgeBaseId=kb_id)
        status = status_resp["knowledgeBase"]["status"]
        log(f"  KB status: {status}")
        if status == "ACTIVE":
            break
        if status in ("FAILED", "DELETE_UNSUCCESSFUL"):
            raise RuntimeError(f"KB entrou em estado: {status}")

    log("KNOWLEDGE_BASE_CREATED=CONFIRMED")
    return kb_id


# ──────────────────────────────────────────────────────────────
# 6. DATA SOURCE + INGESTÃO
# ──────────────────────────────────────────────────────────────


def create_data_source_and_ingest(kb_id: str, bucket_name: str) -> dict:
    section("6. DATA SOURCE + INGESTÃO")
    ba = boto3.client("bedrock-agent", region_name=REGION, config=BOTO_CFG)
    ds_name = f"{PREFIX}-ds"

    resp = ba.create_data_source(
        knowledgeBaseId=kb_id,
        name=ds_name,
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{bucket_name}",
                "inclusionPrefixes": ["knowledge/"],
            },
        },
        vectorIngestionConfiguration={
            "chunkingConfiguration": {
                "chunkingStrategy": "HIERARCHICAL",
                "hierarchicalChunkingConfiguration": {
                    "levelConfigurations": [
                        {"maxTokens": 500},  # parent
                        {"maxTokens": 200},  # child
                    ],
                    "overlapTokens": 50,
                },
            },
        },
    )
    ds_id = resp["dataSource"]["dataSourceId"]
    manifest["data_source_id"] = ds_id
    save_manifest()
    log(f"Data source: {ds_id[:8]}****")

    # Iniciar ingestão
    job_resp = ba.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=ds_id)
    job_id = job_resp["ingestionJob"]["ingestionJobId"]
    manifest["ingestion_job_id"] = job_id
    save_manifest()
    log(f"Ingestion job iniciado: {job_id[:8]}****")

    t0 = time.time()
    ingestion_result: dict = {}
    for _ in range(60):
        time.sleep(10)
        status_resp = ba.get_ingestion_job(
            knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
        )
        job = status_resp["ingestionJob"]
        status = job["status"]
        elapsed = round(time.time() - t0)
        stats = job.get("statistics", {})
        log(f"  Ingestão status={status} docs_ok={stats.get('numberOfDocumentsScanned', 0)} "
            f"docs_fail={stats.get('numberOfDocumentsFailed', 0)} ({elapsed}s)")
        if status == "COMPLETE":
            ingestion_result = {
                "status": "COMPLETE",
                "duration_s": elapsed,
                "docs_scanned": stats.get("numberOfDocumentsScanned", 0),
                "docs_failed": stats.get("numberOfDocumentsFailed", 0),
                "docs_deleted": stats.get("numberOfDocumentsDeleted", 0),
            }
            break
        if status in ("FAILED", "STOPPED"):
            raise RuntimeError(f"Ingestão terminou com status: {status}")

    log(f"INGESTION_STATUS={ingestion_result.get('status', 'UNKNOWN')}")
    with open(ARTIFACTS_DIR / "ingestion_result.json", "w") as f:
        json.dump(ingestion_result, f, indent=2)
    return ingestion_result


# ──────────────────────────────────────────────────────────────
# 7. RETRIEVE REAL
# ──────────────────────────────────────────────────────────────


def run_retrieve(kb_id: str) -> dict:
    section("7. RETRIEVE REAL")

    # Importar o componente real de produção
    sys.path.insert(0, str(Path(__file__).parent.parent / "poc_marh_agent" / "backend" / "src"))
    from marh_agent.clients.bedrock_knowledge_base_retriever import BedrockKnowledgeBaseRetriever
    from marh_agent.clients.bedrock_rag_knowledge_client import _DEFAULT_TOPIC_QUERY_MAP

    retriever = BedrockKnowledgeBaseRetriever(
        knowledge_base_id=kb_id,
        region_name=REGION,
    )

    all_scores: list[float] = []
    positive_results: list[dict] = []
    negative_results: list[dict] = []

    # Casos positivos — 14 tópicos oficiais
    log("Casos positivos (14 tópicos oficiais):")
    for topic, query in _DEFAULT_TOPIC_QUERY_MAP.items():
        t0 = time.perf_counter()
        chunks = retriever.retrieve(query, top_k=TOP_K)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        scores = [c.score for c in chunks if c.score is not None]
        all_scores.extend(scores)
        result = {
            "case_id": f"POS-{topic}",
            "topic": topic,
            "top_k": TOP_K,
            "results_returned": len(chunks),
            "scores": scores,
            "max_score": max(scores) if scores else None,
            "min_score": min(scores) if scores else None,
            "source_files": list({c.source_file for c in chunks if c.source_file}),
            "section_titles": list({c.section_title for c in chunks if c.section_title}),
            "duration_ms": elapsed_ms,
        }
        positive_results.append(result)
        log(f"  {topic}: {len(chunks)} resultados, scores={[round(s,3) for s in scores[:3]]}, {elapsed_ms}ms")

    # Casos negativos
    negative_queries = [
        ("NEG-001", "Qual é a cotação do dólar hoje?"),
        ("NEG-002", "Quantos colaboradores minha empresa possui?"),
        ("NEG-003", "Qual é o CNPJ da Alelo?"),
    ]
    log("\nCasos negativos (3):")
    for case_id, query in negative_queries:
        t0 = time.perf_counter()
        chunks = retriever.retrieve(query, top_k=TOP_K)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        scores = [c.score for c in chunks if c.score is not None]
        result = {
            "case_id": case_id,
            "top_k": TOP_K,
            "results_returned": len(chunks),
            "scores": scores,
            "max_score": max(scores) if scores else None,
            "duration_ms": elapsed_ms,
        }
        negative_results.append(result)
        log(f"  {case_id}: {len(chunks)} resultados, scores={[round(s,3) for s in scores[:3]]}, {elapsed_ms}ms")

    retrieve_scores = {
        "positive_cases": positive_results,
        "negative_cases": negative_results,
        "all_positive_scores": all_scores,
    }
    with open(ARTIFACTS_DIR / "retrieve_scores.json", "w") as f:
        json.dump(retrieve_scores, f, indent=2, default=str)

    return retrieve_scores


# ──────────────────────────────────────────────────────────────
# 8. ANÁLISE DO THRESHOLD
# ──────────────────────────────────────────────────────────────


def analyze_threshold(retrieve_scores: dict) -> dict:
    section("8. ANÁLISE DO THRESHOLD")

    pos_scores = retrieve_scores["all_positive_scores"]
    neg_scores = [
        s for case in retrieve_scores["negative_cases"]
        for s in case["scores"]
    ]

    thresholds = [0.50, 0.60, 0.65, 0.70, 0.75, 0.80]
    comparison = []

    for t in thresholds:
        pos_approved = sum(1 for s in pos_scores if s >= t)
        pos_rejected = sum(1 for s in pos_scores if s < t)
        neg_approved = sum(1 for s in neg_scores if s >= t)
        neg_rejected = sum(1 for s in neg_scores if s < t)
        comparison.append({
            "threshold": t,
            "positives_approved": pos_approved,
            "positives_rejected": pos_rejected,
            "negatives_approved": neg_approved,
            "negatives_rejected": neg_rejected,
        })
        log(f"  t={t}: pos_ok={pos_approved} pos_rej={pos_rejected} "
            f"neg_ok={neg_approved} neg_rej={neg_rejected}")

    # Estatísticas dos positivos
    if pos_scores:
        sorted_pos = sorted(pos_scores)
        n = len(sorted_pos)
        median_pos = sorted_pos[n // 2]
        min_pos = sorted_pos[0]
        max_pos = sorted_pos[-1]
    else:
        median_pos = min_pos = max_pos = None

    max_neg = max(neg_scores) if neg_scores else None

    # Recomendação: menor threshold onde neg_approved == 0 e pos_approved é razoável
    recommendation = 0.70
    status = "KEEP_0_70"
    for row in comparison:
        if row["negatives_approved"] == 0 and row["positives_rejected"] == 0:
            recommendation = row["threshold"]
            status = "KEEP_0_70" if recommendation == 0.70 else "ADJUST_THRESHOLD"
            break
    if not pos_scores:
        status = "DATASET_INSUFFICIENT"

    log(f"\n  Scores positivos: min={min_pos} median={median_pos} max={max_pos}")
    log(f"  Score máx negativos: {max_neg}")
    log(f"  RETRIEVAL_SCORE_THRESHOLD_RECOMMENDATION={recommendation}")
    log(f"  STATUS={status}")

    analysis = {
        "positive_score_stats": {"min": min_pos, "median": median_pos, "max": max_pos},
        "negative_score_max": max_neg,
        "threshold_comparison": comparison,
        "recommendation": recommendation,
        "status": status,
    }
    with open(ARTIFACTS_DIR / "threshold_comparison.json", "w") as f:
        json.dump(analysis, f, indent=2)
    return analysis


# ──────────────────────────────────────────────────────────────
# 9. SMOKE DO PIPELINE COMPLETO
# ──────────────────────────────────────────────────────────────


def run_pipeline_smoke(kb_id: str, temp_model_id: str) -> dict:
    section("9. SMOKE DO PIPELINE COMPLETO")
    sys.path.insert(0, str(Path(__file__).parent.parent / "poc_marh_agent" / "backend" / "src"))
    from marh_agent.clients.bedrock_knowledge_base_retriever import BedrockKnowledgeBaseRetriever
    from marh_agent.clients.bedrock_language_model_client import BedrockLanguageModelClient
    from marh_agent.clients.bedrock_rag_knowledge_client import BedrockRagKnowledgeClient

    retriever = BedrockKnowledgeBaseRetriever(knowledge_base_id=kb_id, region_name=REGION)
    llm = BedrockLanguageModelClient(model_id=temp_model_id, region_name=REGION)
    rag = BedrockRagKnowledgeClient(
        retriever=retriever,
        language_model_client=llm,
        score_threshold=SCORE_THRESHOLD,
    )

    smoke_results = []

    # Caso 1 — pergunta com evidência
    log("Caso 1 — com evidência (MARH_OVERVIEW):")
    t0 = time.perf_counter()
    r1 = rag.query("MARH_OVERVIEW")
    d1 = round((time.perf_counter() - t0) * 1000, 1)
    log(f"  found={r1['found']}, flow_detail={r1.get('metadata', {}).get('flow_detail')}, {d1}ms")
    smoke_results.append({
        "case": "com_evidencia",
        "topic": "MARH_OVERVIEW",
        "found": r1["found"],
        "content_len": len(r1.get("content") or ""),
        "source_section": r1.get("source_section"),
        "flow_detail": r1.get("metadata", {}).get("flow_detail"),
        "data_classification": r1.get("data_classification"),
        "duration_ms": d1,
    })

    # Caso 2 — sem evidência (query inexistente)
    log("Caso 2 — sem evidência (tópico desconhecido):")
    t0 = time.perf_counter()
    r2 = rag.query("TOPICO_NAO_MAPEADO_GATE")
    d2 = round((time.perf_counter() - t0) * 1000, 1)
    log(f"  found={r2['found']}, reason={r2.get('metadata', {}).get('reason')}, {d2}ms")
    smoke_results.append({
        "case": "sem_evidencia",
        "topic": "TOPICO_NAO_MAPEADO_GATE",
        "found": r2["found"],
        "content": r2["content"],
        "reason": r2.get("metadata", {}).get("reason"),
        "duration_ms": d2,
    })

    # Caso 3 — múltiplos chunks (ORDER_PROCESS — corpus mais rico)
    log("Caso 3 — múltiplos chunks (ORDER_PROCESS):")
    t0 = time.perf_counter()
    r3 = rag.query("ORDER_PROCESS")
    d3 = round((time.perf_counter() - t0) * 1000, 1)
    log(f"  found={r3['found']}, approved_chunks={r3.get('metadata', {}).get('approved_chunks')}, {d3}ms")
    smoke_results.append({
        "case": "multiplos_chunks",
        "topic": "ORDER_PROCESS",
        "found": r3["found"],
        "content_len": len(r3.get("content") or ""),
        "approved_chunks": r3.get("metadata", {}).get("approved_chunks"),
        "duration_ms": d3,
    })

    # Validações
    assert r1["found"] is True, "Caso 1: esperava found=True"
    assert r1.get("metadata", {}).get("flow_detail") == "BEDROCK_RAG", "flow_detail incorreto"
    assert r1.get("data_classification") == "BEDROCK_RAG_GROUNDED"
    assert r2["found"] is False, "Caso 2: esperava found=False (tópico desconhecido)"
    assert r2["content"] is None
    log("  Validações PASSARAM")

    pipeline_smoke = {"results": smoke_results, "temporary_model": temp_model_id}
    with open(ARTIFACTS_DIR / "pipeline_smoke.json", "w") as f:
        json.dump(pipeline_smoke, f, indent=2, default=str)
    return pipeline_smoke


# ──────────────────────────────────────────────────────────────
# 10. TEARDOWN
# ──────────────────────────────────────────────────────────────


def teardown() -> dict:
    section("10. TEARDOWN")
    result: dict = {"actions": [], "errors": []}

    if not MANIFEST_PATH.exists():
        log("Manifesto não encontrado — nada a destruir.")
        return result

    with open(MANIFEST_PATH) as f:
        m = json.load(f)

    ba = boto3.client("bedrock-agent", region_name=REGION, config=BOTO_CFG)
    s3 = boto3.client("s3", region_name=REGION, config=BOTO_CFG)
    iam = boto3.client("iam", region_name=REGION, config=BOTO_CFG)

    # 1. Data source
    if "data_source_id" in m and "knowledge_base_id" in m:
        try:
            ba.delete_data_source(knowledgeBaseId=m["knowledge_base_id"], dataSourceId=m["data_source_id"])
            log(f"Data source removido: {m['data_source_id'][:8]}****")
            result["actions"].append("data_source_deleted")
        except Exception as e:
            log(f"  AVISO data source: {type(e).__name__}")
            result["errors"].append(f"data_source: {type(e).__name__}")

    # 2. Knowledge Base
    if "knowledge_base_id" in m:
        try:
            ba.delete_knowledge_base(knowledgeBaseId=m["knowledge_base_id"])
            log(f"Knowledge Base removida: {m['knowledge_base_id'][:8]}****")
            # Aguardar exclusão
            for _ in range(20):
                time.sleep(10)
                try:
                    status = ba.get_knowledge_base(knowledgeBaseId=m["knowledge_base_id"])
                    s = status["knowledgeBase"]["status"]
                    log(f"  KB status: {s}")
                    if s == "DELETE_UNSUCCESSFUL":
                        break
                except ClientError as e:
                    if "ResourceNotFoundException" in str(e):
                        break
            result["actions"].append("knowledge_base_deleted")
        except Exception as e:
            log(f"  AVISO KB: {type(e).__name__}")
            result["errors"].append(f"knowledge_base: {type(e).__name__}")

    # 3. S3 Vectors index
    if "vector_index" in m and "vector_bucket" in m:
        try:
            s3v = boto3.client("s3vectors", region_name=REGION, config=BOTO_CFG)
            s3v.delete_index(vectorBucketName=m["vector_bucket"], indexName=m["vector_index"])
            log(f"Vector index removido: {m['vector_index']}")
            result["actions"].append("vector_index_deleted")
        except Exception as e:
            log(f"  AVISO vector index: {type(e).__name__}")
            result["errors"].append(f"vector_index: {type(e).__name__}")

    # 4. S3 Vectors bucket
    if "vector_bucket" in m:
        try:
            s3v = boto3.client("s3vectors", region_name=REGION, config=BOTO_CFG)
            s3v.delete_vector_bucket(vectorBucketName=m["vector_bucket"])
            log(f"Vector bucket removido: {m['vector_bucket']}")
            result["actions"].append("vector_bucket_deleted")
        except Exception as e:
            log(f"  AVISO vector bucket: {type(e).__name__}")
            result["errors"].append(f"vector_bucket: {type(e).__name__}")

    # 5. Objeto S3
    if "s3_bucket" in m and "s3_key" in m:
        try:
            s3.delete_object(Bucket=m["s3_bucket"], Key=m["s3_key"])
            log(f"Objeto S3 removido: {m['s3_key']}")
            result["actions"].append("s3_object_deleted")
        except Exception as e:
            log(f"  AVISO objeto S3: {type(e).__name__}")
            result["errors"].append(f"s3_object: {type(e).__name__}")

    # 6. Bucket S3
    if "s3_bucket" in m:
        try:
            s3.delete_bucket(Bucket=m["s3_bucket"])
            log(f"Bucket S3 removido: {m['s3_bucket']}")
            result["actions"].append("s3_bucket_deleted")
        except Exception as e:
            log(f"  AVISO bucket S3: {type(e).__name__}")
            result["errors"].append(f"s3_bucket: {type(e).__name__}")

    # 7. Política IAM
    if "iam_policy_name" in m:
        try:
            # Encontrar ARN pelo nome
            policies = iam.list_policies(Scope="Local")["Policies"]
            policy_arn = next((p["Arn"] for p in policies if p["PolicyName"] == m["iam_policy_name"]), None)
            if policy_arn:
                if "iam_role_name" in m:
                    try:
                        iam.detach_role_policy(RoleName=m["iam_role_name"], PolicyArn=policy_arn)
                    except Exception:
                        pass
                iam.delete_policy(PolicyArn=policy_arn)
                log(f"Policy IAM removida: {m['iam_policy_name']}")
                result["actions"].append("iam_policy_deleted")
        except Exception as e:
            log(f"  AVISO policy IAM: {type(e).__name__}")
            result["errors"].append(f"iam_policy: {type(e).__name__}")

    # 8. Role IAM
    if "iam_role_name" in m:
        try:
            iam.delete_role(RoleName=m["iam_role_name"])
            log(f"Role IAM removida: {m['iam_role_name']}")
            result["actions"].append("iam_role_deleted")
        except Exception as e:
            log(f"  AVISO role IAM: {type(e).__name__}")
            result["errors"].append(f"iam_role: {type(e).__name__}")

    result["residual"] = len(result["errors"])
    result["status"] = "COMPLETE" if not result["errors"] else "PARTIAL"
    log(f"TEARDOWN_STATUS={result['status']}")
    log(f"RESIDUAL_TEMPORARY_RESOURCES={result['residual']}")

    with open(ARTIFACTS_DIR / "teardown_verification.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    # Modelo temporário para o smoke — um dos candidatos validados no probe regional
    # Não é o modelo definitivo — seleção no Passo 10
    TEMP_MODEL_ID = os.getenv("GATE_MODEL_ID", "mistral.magistral-small-2509")

    gate_result: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "region": REGION,
        "prefix": PREFIX,
        "temporary_model": TEMP_MODEL_ID,
    }
    teardown_result: dict = {}
    account: str = ""

    try:
        # Preflight
        preflight_result = preflight()
        gate_result["preflight"] = preflight_result
        account = preflight_result["account_masked"].replace("****", "")
        # Recuperar account real para ARNs
        sts = boto3.client("sts", region_name=REGION, config=BOTO_CFG)
        account = sts.get_caller_identity()["Account"]

        # Recursos
        bucket_name = create_s3_bucket(account)
        vbucket_name, vindex_name = create_s3_vectors()
        role_arn = create_iam_role(account, bucket_name, vbucket_name)
        kb_id = create_knowledge_base(role_arn, account, vbucket_name, vindex_name)
        ingestion_result = create_data_source_and_ingest(kb_id, bucket_name)
        gate_result["ingestion"] = ingestion_result

        if ingestion_result.get("status") != "COMPLETE":
            raise RuntimeError("Ingestão não completou — abortando.")

        # Retrieve
        retrieve_scores = run_retrieve(kb_id)
        gate_result["retrieve"] = {
            "positive_cases": len(retrieve_scores["positive_cases"]),
            "negative_cases": len(retrieve_scores["negative_cases"]),
        }

        # Threshold
        threshold_analysis = analyze_threshold(retrieve_scores)
        gate_result["threshold"] = threshold_analysis

        # Smoke
        smoke = run_pipeline_smoke(kb_id, TEMP_MODEL_ID)
        gate_result["smoke"] = smoke

        gate_result["decision"] = "GO_PHASE_3_INFRA" if not threshold_analysis.get("negatives_approved_at_070") else "GO_PHASE_3_INFRA_WITH_CONDITIONS"

    except Exception as e:
        gate_result["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        gate_result["decision"] = "NO_GO_PHASE_3_INFRA"
        print(f"\n  ERRO: {e}", file=sys.stderr)
    finally:
        teardown_result = teardown()
        gate_result["teardown"] = teardown_result

    # Salvar summary
    gate_result["finished_at"] = datetime.now(timezone.utc).isoformat()
    with open(ARTIFACTS_DIR / "gate_summary.json", "w") as f:
        json.dump(gate_result, f, indent=2, default=str)

    section("RESULTADO FINAL")
    log(f"Decisão: {gate_result.get('decision', 'N/A')}")
    log(f"Teardown: {teardown_result.get('status', 'N/A')}")
    log(f"Residuais: {teardown_result.get('residual', '?')}")
    log(f"Artefatos: {ARTIFACTS_DIR}")
    print()


if __name__ == "__main__":
    main()
