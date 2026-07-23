# Configuração GitHub Actions → AWS (OIDC)

Este guia conecta o GitHub Actions à sua conta AWS **sem access keys** (mais seguro).

## Passo 1 — Criar o Identity Provider no IAM

No console AWS (IAM → Identity providers → Add provider):

| Campo | Valor |
|-------|-------|
| Provider type | OpenID Connect |
| Provider URL | `https://token.actions.githubusercontent.com` |
| Audience | `sts.amazonaws.com` |

## Passo 2 — Criar a IAM Role para deploy

Criar uma role com a trust policy abaixo. Substitua `SEU_USUARIO/SEU_REPO` pelo caminho do seu repo no GitHub.

### Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:SEU_USUARIO/SEU_REPO:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### Permissions Policy

Anexar a policy `AdministratorAccess` temporariamente (para CDK deploy).  
Depois do primeiro deploy, restringir para:
- `cloudformation:*`
- `lambda:*`
- `apigateway:*`
- `iam:*` (com condição no path `/marh-agent-*`)
- `logs:*`
- `secretsmanager:*`
- `s3:*` (bucket do CDK bootstrap)
- `xray:*`

## Passo 3 — Configurar o secret no GitHub

No repositório GitHub → Settings → Secrets and variables → Actions:

| Secret | Valor |
|--------|-------|
| `AWS_DEPLOY_ROLE_ARN` | `arn:aws:iam::ACCOUNT_ID:role/NOME_DA_ROLE_CRIADA` |

## Passo 4 — Criar o environment "hml"

No repositório GitHub → Settings → Environments → New environment:

- Nome: `hml`
- (Opcional) Adicionar reviewers se quiser aprovação antes do deploy

## Passo 5 — Bootstrap do CDK

Rodar uma vez (localmente ou no CloudShell):

```bash
cdk bootstrap aws://ACCOUNT_ID/sa-east-1
```

## Passo 6 — Testar

Fazer push para `main`. O pipeline deve:
1. ✅ Rodar testes (107 passando)
2. ✅ Lint (ruff)
3. ✅ Build (zip do Lambda)
4. ✅ Deploy CDK em HML

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | Trust policy incorreta | Verificar `sub` condition no passo 2 |
| `CDK bootstrap not found` | Não fez bootstrap | Rodar `cdk bootstrap` (passo 5) |
| `Permission denied` na role | Policy muito restritiva | Usar AdministratorAccess no primeiro deploy |
