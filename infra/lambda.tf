# ─── IAM Role ────────────────────────────────────────────────────────────────

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
  name               = "marh-agent-${local.env_lower}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Permissões: logs + X-Ray
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

# Permissão: ler secrets
resource "aws_iam_role_policy" "lambda_secrets" {
  name = "secrets-read"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [aws_secretsmanager_secret.ma_hr_orch.arn]
      }
    ]
  })
}

# Permissão: Bedrock (preparada para Fase 3+)
resource "aws_iam_role_policy" "lambda_bedrock" {
  name = "bedrock-invoke"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:Retrieve",
          "bedrock:RetrieveAndGenerate"
        ]
        Resource = ["*"] # Restringir ao model/KB específico na Fase 3
      }
    ]
  })
}

# ─── CloudWatch Log Group ────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/marh-agent-${local.env_lower}"
  retention_in_days = var.log_retention_days
}

# ─── Lambda Layer (dependências Python) ──────────────────────────────────────

resource "aws_lambda_layer_version" "deps" {
  layer_name          = "marh-agent-${local.env_lower}-deps"
  description         = "Dependências Python (pydantic, etc.)"
  filename            = "${path.module}/.build/layer.zip"
  source_code_hash    = filebase64sha256("${path.module}/.build/layer.zip")
  compatible_runtimes = ["python3.12"]
}

# ─── Lambda Function ─────────────────────────────────────────────────────────

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
  function_name = "marh-agent-${local.env_lower}"
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
      AGENT_MODE                 = var.agent_mode
      ENVIRONMENT                = var.environment
      LOG_LEVEL                  = "INFO"
      MAX_MESSAGE_LENGTH         = "2000"
      MA_HR_ORCH_BASE_URL        = ""
      MA_HR_ORCH_TIMEOUT_SECONDS = "10"
      BEDROCK_REGION             = var.aws_region
      BEDROCK_MODEL_ID           = "anthropic.claude-3-haiku-20240307-v1:0"
      BEDROCK_KNOWLEDGE_BASE_ID  = ""
      CORS_ALLOWED_ORIGINS       = join(",", var.cors_allowed_origins)
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_basic,
  ]
}
