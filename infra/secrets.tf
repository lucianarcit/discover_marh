# ─── Secrets Manager ─────────────────────────────────────────────────────────

resource "aws_secretsmanager_secret" "ma_hr_orch" {
  name        = "marh-agent/${local.env_lower}/ma-hr-orch-credentials"
  description = "Credenciais para API ma-hr-orch (preenchidas manualmente)"
}

resource "aws_secretsmanager_secret_version" "ma_hr_orch" {
  secret_id = aws_secretsmanager_secret.ma_hr_orch.id
  secret_string = jsonencode({
    api_key  = "PLACEHOLDER"
    base_url = "PLACEHOLDER"
  })

  # Ignorar mudanças — o valor real é preenchido manualmente
  lifecycle {
    ignore_changes = [secret_string]
  }
}
