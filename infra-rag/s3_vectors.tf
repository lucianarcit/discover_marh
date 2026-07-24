# ─── S3 Vectors ──────────────────────────────────────────────────────────────
# Recursos nativos do provider hashicorp/aws v6.56.
# Configuração validada no gate Passo 8A:
#   dimension=1024, cosine, float32
#   nonFilterableMetadataKeys: AMAZON_BEDROCK_TEXT, AMAZON_BEDROCK_METADATA

resource "aws_s3vectors_vector_bucket" "rag" {
  vector_bucket_name = "${local.prefix}-vectors"
}

resource "aws_s3vectors_index" "rag" {
  vector_bucket_name = aws_s3vectors_vector_bucket.rag.vector_bucket_name
  index_name         = "${local.prefix}-index"

  data_type       = local.vector_data_type
  dimension       = local.vector_dimension
  distance_metric = local.vector_distance

  metadata_configuration {
    non_filterable_metadata_keys = local.non_filterable_keys
  }
}
