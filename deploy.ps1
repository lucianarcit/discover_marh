# deploy.ps1 — Script de deploy completo (test → commit → push → AWS)
# Uso: .\deploy.ps1 "mensagem do commit"
# Exemplo: .\deploy.ps1 "fix: corrigir classificação de INT-005"

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MARH Agent — Deploy Pipeline" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Testes ────────────────────────────────────────────────────────────────
Write-Host "[1/5] Rodando testes..." -ForegroundColor Yellow
Push-Location "$Root\poc_marh_agent\backend"
$testResult = python -m pytest -q 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "FALHOU — testes não passaram:" -ForegroundColor Red
    Write-Host $testResult
    Pop-Location
    exit 1
}
$testCount = ($testResult | Select-String "passed").ToString().Trim()
Write-Host "  OK — $testCount" -ForegroundColor Green
Pop-Location

# ─── 2. Git add + commit ─────────────────────────────────────────────────────
Write-Host "[2/5] Commitando..." -ForegroundColor Yellow
Push-Location $Root
git add -A
$status = git status --porcelain
if (-not $status) {
    Write-Host "  Nada para commitar — continuando deploy..." -ForegroundColor DarkYellow
} else {
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FALHOU — git commit" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "  OK — commitado" -ForegroundColor Green
}
Pop-Location

# ─── 3. Git push ─────────────────────────────────────────────────────────────
Write-Host "[3/5] Pushando para GitHub..." -ForegroundColor Yellow
Push-Location $Root
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "FALHOU — git push" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "  OK — pushed" -ForegroundColor Green
Pop-Location

# ─── 4. Terraform apply (Lambda + infra) ─────────────────────────────────────
Write-Host "[4/5] Atualizando Lambda na AWS (terraform apply)..." -ForegroundColor Yellow
Push-Location "$Root\infra"
terraform apply -auto-approve
if ($LASTEXITCODE -ne 0) {
    Write-Host "FALHOU — terraform apply" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "  OK — Lambda atualizada" -ForegroundColor Green
Pop-Location

# ─── 5. Frontend sync (S3) ───────────────────────────────────────────────────
Write-Host "[5/5] Sincronizando frontend no S3..." -ForegroundColor Yellow
aws s3 sync "$Root\poc_marh_agent\frontend" s3://marh-agent-frontend-hml/ --delete
if ($LASTEXITCODE -ne 0) {
    Write-Host "FALHOU — s3 sync" -ForegroundColor Red
    exit 1
}
Write-Host "  OK — frontend atualizado" -ForegroundColor Green

# ─── Resumo ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  API:      https://pzn843po3h.execute-api.sa-east-1.amazonaws.com" -ForegroundColor White
Write-Host "  Frontend: http://marh-agent-frontend-hml.s3-website-sa-east-1.amazonaws.com" -ForegroundColor White
Write-Host ""
