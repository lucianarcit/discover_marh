# ─── IAM Role da Lambda RAG HML ──────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.prefix}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  description        = "Role da Lambda RAG HML - menor privilegio"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

# Permissões específicas do RAG (menor privilégio)
resource "aws_iam_role_policy" "lambda_rag" {
  name = "rag-permissions"
  role = aws_iam_role.lambda.id

  policy = data.aws_iam_policy_document.lambda_rag_permissions.json
}

data "aws_iam_policy_document" "lambda_rag_permissions" {
  # Retrieve via Knowledge Base (NÃO RetrieveAndGenerate)
  statement {
    sid    = "BedrockKBRetrieve"
    effect = "Allow"
    actions = [
      "bedrock-agent-runtime:Retrieve",
    ]
    resources = [
      aws_bedrockagent_knowledge_base.rag.arn,
    ]
  }

  # Invocação do modelo de geração via Converse API
  # Permissão IAM: bedrock:InvokeModel (Converse usa InvokeModel, não bedrock:Converse)
  statement {
    sid    = "BedrockInvokeGenerationModel"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = [
      "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}",
    ]
  }

  # Leitura da configuração RAG do Secrets Manager
  statement {
    sid    = "ReadRagConfig"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
    ]
    resources = [
      aws_secretsmanager_secret.rag_config.arn,
    ]
  }
}

# ─── CloudWatch Log Group ─────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.prefix}"
  retention_in_days = var.log_retention_days
}

# ─── Lambda Layer (dependências Python) ───────────────────────────────────────
# O layer deve incluir: boto3, pydantic, fastapi (se necessário).
# Construir com: cd infra-rag && ./scripts/build_layer.sh

resource "aws_lambda_layer_version" "deps" {
  layer_name          = "${local.prefix}-deps"
  description         = "Dependencias Python para Lambda RAG HML"
  filename            = "${path.module}/.build/layer.zip"
  source_code_hash    = fileexists("${path.module}/.build/layer.zip") ? filebase64sha256("${path.module}/.build/layer.zip") : ""
  compatible_runtimes = ["python3.12"]
  # Construir antes do apply: cd infra-rag && bash scripts/build_layer.sh
}

# ─── Lambda Function ──────────────────────────────────────────────────────────

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../poc_marh_agent/backend/src"
  output_path = "${path.module}/.build/lambda.zip"

  excludes = [
    "**/__pycache__/**",
    "*.pyc",
    "*.egg-info/**",
  ]
}

resource "aws_lambda_function" "agent" {
  function_name = local.prefix
  role          = aws_iam_role.lambda.arn
  handler       = "marh_agent.api.lambda_handler.lambda_handler"
  runtime       = "python3.12"
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  layers = [aws_lambda_layer_version.deps.arn]

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      # Eixos ortogonais — Fase 3 isolada
      DATA_SOURCE_MODE = "MOCK"
      KNOWLEDGE_MODE   = "BEDROCK_RAG"

      # Configuração do RAG
      BEDROCK_REGION            = var.aws_region
      BEDROCK_KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.rag.id
      BEDROCK_MODEL_ID          = var.bedrock_model_id
      BEDROCK_EMBED_MODEL_ID    = local.embed_model_id
      RETRIEVAL_SCORE_THRESHOLD = tostring(var.retrieval_score_threshold)

      # Ambiente e log
      ENVIRONMENT        = var.environment
      LOG_LEVEL          = "INFO"
      MAX_MESSAGE_LENGTH = "2000"

      # CORS
      CORS_ALLOWED_ORIGINS = join(",", var.cors_allowed_origins)

      # Legado — retrocompatibilidade
      AGENT_MODE = "MOCK_LOCAL"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_basic,
    aws_bedrockagent_knowledge_base.rag,
  ]
}
