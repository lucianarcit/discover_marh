# ─── Bedrock Knowledge Base ───────────────────────────────────────────────────
# Recursos nativos do provider hashicorp/aws v6.56.
# Embedding: amazon.titan-embed-text-v2:0 (confirmado ativo em sa-east-1).
# Storage: S3 Vectors — recursos nativos, sem null_resource/local-exec.
# Retrieve separado da geração — RetrieveAndGenerate não é usado.

resource "aws_bedrockagent_knowledge_base" "rag" {
  name        = "${local.prefix}-kb"
  description = "Knowledge Base RAG HML - corpus MARH aprovado"
  role_arn    = aws_iam_role.knowledge_base.arn

  knowledge_base_configuration {
    type = "VECTOR"

    vector_knowledge_base_configuration {
      embedding_model_arn = local.embed_model_arn
    }
  }

  storage_configuration {
    type = "S3_VECTORS"

    s3_vectors_configuration {
      vector_bucket_arn = aws_s3vectors_vector_bucket.rag.vector_bucket_arn
      index_arn         = aws_s3vectors_index.rag.index_arn
    }
  }

  depends_on = [
    aws_iam_role_policy.knowledge_base_permissions,
    aws_s3vectors_index.rag,
  ]
}

# ─── Data Source ─────────────────────────────────────────────────────────────
# Conecta o bucket S3 do corpus à Knowledge Base.
# Chunking HIERARCHICAL — validado no gate (parent=500t, child=200t, overlap=50t).

resource "aws_bedrockagent_data_source" "corpus" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.rag.id
  name              = "${local.prefix}-corpus-ds"

  data_source_configuration {
    type = "S3"

    s3_configuration {
      bucket_arn         = aws_s3_bucket.corpus.arn
      inclusion_prefixes = ["knowledge/"]
    }
  }

  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "HIERARCHICAL"

      hierarchical_chunking_configuration {
        level_configuration {
          max_tokens = var.knowledge_base_chunking_parent_tokens
        }

        level_configuration {
          max_tokens = var.knowledge_base_chunking_child_tokens
        }

        overlap_tokens = var.knowledge_base_chunking_overlap_tokens
      }
    }
  }

  depends_on = [aws_bedrockagent_knowledge_base.rag]
}
