# ─── S3 Bucket do corpus ─────────────────────────────────────────────────────
# Armazena somente o corpus aprovado: marh_feature_knowledge.md
# Corpus adicional requer aprovação do cliente antes de ser adicionado.

resource "aws_s3_bucket" "corpus" {
  bucket = "${local.prefix}-corpus"
}

resource "aws_s3_bucket_versioning" "corpus" {
  bucket = aws_s3_bucket.corpus.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "corpus" {
  bucket = aws_s3_bucket.corpus.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "corpus" {
  bucket = aws_s3_bucket.corpus.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Política: permite apenas a role da Knowledge Base ler o corpus
resource "aws_s3_bucket_policy" "corpus" {
  bucket = aws_s3_bucket.corpus.id
  policy = data.aws_iam_policy_document.corpus_bucket_policy.json

  depends_on = [aws_s3_bucket_public_access_block.corpus]
}

data "aws_iam_policy_document" "corpus_bucket_policy" {
  statement {
    sid    = "AllowKnowledgeBaseRead"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.knowledge_base.arn]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.corpus.arn,
      "${aws_s3_bucket.corpus.arn}/*",
    ]
  }

  # Deny qualquer acesso não-HTTPS
  statement {
    sid    = "DenyNonHTTPS"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.corpus.arn,
      "${aws_s3_bucket.corpus.arn}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

# Upload do corpus aprovado
# O arquivo é lido do repositório local — nunca de fontes externas.
resource "aws_s3_object" "corpus_knowledge" {
  bucket = aws_s3_bucket.corpus.id
  key    = local.corpus_s3_key
  source = "${path.module}/../discover3/knowledge/marh_feature_knowledge.md"

  # Reprocessar ingestão quando o corpus mudar
  source_hash = filemd5("${path.module}/../discover3/knowledge/marh_feature_knowledge.md")

  content_type = "text/markdown"
}
