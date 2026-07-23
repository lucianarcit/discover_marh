# ─── Amplify Hosting (Frontend) ──────────────────────────────────────────────
# 
# NOTA: O Amplify é configurado via console AWS (OAuth com GitHub)
# pois tokens fine-grained do GitHub não suportam webhooks para Amplify.
#
# Alternativa usada: deploy manual via CLI ou S3.
# Veja docs/deployment.md para instruções.
#
# Para criar via console:
# 1. AWS Console → Amplify → New app → Host web app
# 2. Selecionar GitHub → Autorizar
# 3. Repo: lucianarcit/discover_marh
# 4. Branch: main
# 5. Build settings: baseDirectory = poc_marh_agent/frontend
# 6. Deploy

# S3 bucket para hosting estático (alternativa simples ao Amplify)
resource "aws_s3_bucket" "frontend" {
  bucket = "marh-agent-frontend-${local.env_lower}"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}
