# Probe — 08. Permissões IAM

**Região:** sa-east-1
**Role:** SSO AdministratorAccess (mascarada)

## Nota sobre nomes de permissões do Bedrock

| API chamada | Permissão IAM real |
|---|---|
| `bedrock-runtime:InvokeModel` | `bedrock:InvokeModel` |
| `bedrock-runtime:Converse` | `bedrock:InvokeModel` |
| `bedrock-runtime:ConverseStream` | `bedrock:InvokeModelWithResponseStream` |
| `bedrock-agent:ListKnowledgeBases` | `bedrock:ListFoundationModels` não cobre — é `bedrock-agent:ListKnowledgeBases` |
| `bedrock-agent-runtime:Retrieve` | `bedrock-agent-runtime:Retrieve` |

**Importante:** `bedrock:Converse` e `bedrock-runtime:Converse` **não existem como permissões IAM**. A Converse API usa `bedrock:InvokeModel`. Erros anteriores nesta documentação foram corrigidos.

## Permissões confirmadas por chamadas reais

| Permissão IAM real | Evidência | Status |
|---|---|---|
| `bedrock:ListFoundationModels` | 55 modelos listados | **CONFIRMADA** |
| `bedrock:InvokeModel` | Titan Embed invocado com sucesso; Converse funcionou | **CONFIRMADA** |
| `bedrock-agent:ListKnowledgeBases` | API retornou lista sem erro de acesso | **CONFIRMADA** |
| `bedrock-agent-runtime:Retrieve` | Endpoint alcançável, ValidationException esperado | **CONFIRMADA** |

## Permissões futuras necessárias (não ampliar agora)

Para a Lambda do ambiente RAG HML (Passo 8):

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream",
    "bedrock-agent-runtime:Retrieve",
    "bedrock-agent:CreateKnowledgeBase",
    "bedrock-agent:CreateDataSource",
    "bedrock-agent:StartIngestionJob",
    "bedrock-agent:GetKnowledgeBase",
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket",
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": [
    "arn:aws:bedrock:sa-east-1::foundation-model/*",
    "arn:aws:bedrock:sa-east-1:<account-id>:knowledge-base/*",
    "arn:aws:s3:::marh-agent-rag-hml-knowledge/*",
    "arn:aws:logs:sa-east-1:<account-id>:log-group:/marh-agent/rag-hml:*"
  ]
}
```

`<account-id>` a preencher no Terraform. Não registrar valor real neste documento.

## Gaps identificados

Nenhum para o probe atual. Gaps futuros resolvidos no Passo 8 (Terraform + IAM da Lambda).

## Observação de segurança

A role de probe é AdministratorAccess — permissiva demais para produção. A role da Lambda RAG HML deve seguir princípio de menor privilégio com a política acima.
