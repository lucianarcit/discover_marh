# ─── IAM — Role da Knowledge Base ────────────────────────────────────────────
# Menor privilégio: apenas as permissões necessárias para ingestão e recuperação.

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "knowledge_base_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:knowledge-base/*"]
    }
  }
}

resource "aws_iam_role" "knowledge_base" {
  name               = "${local.prefix}-kb-role"
  assume_role_policy = data.aws_iam_policy_document.knowledge_base_assume_role.json
  description        = "Role da Knowledge Base RAG HML - menor privilegio"
}

resource "aws_iam_role_policy" "knowledge_base_permissions" {
  name   = "kb-permissions"
  role   = aws_iam_role.knowledge_base.id
  policy = data.aws_iam_policy_document.knowledge_base_permissions.json
}

data "aws_iam_policy_document" "knowledge_base_permissions" {
  statement {
    sid    = "ReadCorpusBucket"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.corpus.arn,
      "${aws_s3_bucket.corpus.arn}/*",
    ]
  }

  statement {
    sid    = "S3VectorsIndexOperations"
    effect = "Allow"
    actions = [
      "s3vectors:PutVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors",
      "s3vectors:QueryVectors",
      "s3vectors:ListVectors",
    ]
    resources = [
      "${aws_s3vectors_vector_bucket.rag.vector_bucket_arn}/index/*",
    ]
  }

  statement {
    sid    = "InvokeEmbeddingModel"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
    ]
    resources = [
      local.embed_model_arn,
    ]
  }
}
