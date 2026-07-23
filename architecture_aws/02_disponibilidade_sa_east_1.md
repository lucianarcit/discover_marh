# 02 — Disponibilidade de Serviços em sa-east-1

> **Data da consulta:** 2026-07-23 (revisão corretiva)
> **Fonte:** Documentação oficial da AWS
> **Nota de revisão:** Declarações de disponibilidade de modelos Bedrock e Bedrock Knowledge Bases
> foram marcadas como REQUIRES_ACCOUNT_VALIDATION por exigirem verificação em console ou CLI de conta real.

---

## Princípio desta seção

Uma feature só pode ser declarada `CONFIRMED` quando houver evidência específica para aquela funcionalidade
em `sa-east-1`. Não basta o serviço principal existir na região. Modelos Bedrock, availability de
Knowledge Bases e integração com S3 Vectors requerem confirmação independente, não inferência a partir
de inference profiles.

---

## Matriz de Disponibilidade — Infraestrutura (Confirmada)

| Serviço | Funcionalidade | Disponível em sa-east-1 | Status |
|---|---|---|---|
| AWS Lambda | Runtime Python 3.12 | ✅ Sim | CONFIRMED |
| AWS Lambda | Function URL, X-Ray, ARM64 | ✅ Sim | CONFIRMED |
| Amazon S3 | Buckets, versionamento, KMS, lifecycle | ✅ Sim | CONFIRMED |
| AWS Secrets Manager | Secrets, rotação, KMS | ✅ Sim | CONFIRMED |
| AWS KMS | Chaves simétricas regionais, CMK | ✅ Sim | CONFIRMED |
| Amazon CloudWatch | Logs, Metrics, Alarms, Log Insights | ✅ Sim | CONFIRMED |
| AWS X-Ray | Tracing distribuído, annotations | ✅ Sim | CONFIRMED |
| Amazon Bedrock | Runtime — Converse API | ✅ Sim | CONFIRMED |

---

## Modelos Bedrock — REQUIRES_ACCOUNT_VALIDATION

Modelos só podem ser declarados disponíveis In-Region após verificação no console ou via CLI da conta.
Inference profiles **não** são evidência de disponibilidade In-Region. Um inference profile pode rotear
para outra região.

| Modelo | Model ID | Status | Verificação necessária |
|---|---|---|---|
| Claude 3 Haiku | anthropic.claude-3-haiku-20240307-v1:0 | REQUIRES_ACCOUNT_VALIDATION | Console → Bedrock → Model catalog → sa-east-1 → status ACTIVE |
| Claude 3.5 Sonnet v2 | anthropic.claude-3-5-sonnet-20241022-v2:0 | REQUIRES_ACCOUNT_VALIDATION | Console → Bedrock → Model catalog → sa-east-1 → status ACTIVE |
| Claude 3.5 Haiku | anthropic.claude-3-5-haiku-20241022-v1:0 | REQUIRES_ACCOUNT_VALIDATION | **Não usar** sem confirmação ACTIVE In-Region. Removido da seleção automática. |
| Claude Sonnet 4 | anthropic.claude-sonnet-4-20250514-v1:0 | REQUIRES_ACCOUNT_VALIDATION | Verificar se disponível sem cross-Region inference em sa-east-1 |
| Titan Embed Text v2 | amazon.titan-embed-text-v2:0 | REQUIRES_ACCOUNT_VALIDATION | Console → Bedrock → Model catalog → sa-east-1 → status ACTIVE |

**Procedimento de validação:**
1. Acesse o console AWS na conta alvo, selecione região `sa-east-1`
2. Navegue para Amazon Bedrock → Model catalog
3. Verifique o status de cada modelo: deve ser ACTIVE
4. Confirme que o tipo de inferência é "On-demand" (não inference profile)
5. Confirme que não há indicação de "cross-region routing"
6. Alternativamente: `aws bedrock list-foundation-models --region sa-east-1 --by-inference-type ON_DEMAND`

**Nota sobre Claude 3.5 Haiku:** Removido como seleção automática. Status ACTIVE In-Region em sa-east-1
não foi confirmado por evidência direta.

---

## Bedrock Knowledge Bases — REQUIRES_ACCOUNT_VALIDATION

| Funcionalidade | Status | Evidência necessária |
|---|---|---|
| Knowledge Bases (serviço) | REQUIRES_ACCOUNT_VALIDATION | Página de regiões suportadas na documentação oficial atual |
| Modelo de embedding (qualquer) | REQUIRES_ACCOUNT_VALIDATION | Mesmo procedimento dos modelos acima |
| Integração KB + S3 Vectors | REQUIRES_ACCOUNT_VALIDATION | Documentação oficial: Knowledge Bases with S3 Vectors in sa-east-1 |
| Bedrock Agent Runtime | REQUIRES_ACCOUNT_VALIDATION | Não confundir com Bedrock Agents Classic (descontinuado) |

**Consequência:** Enquanto não houver confirmação, o desenho RAG preferencial para a POC é:

```
Lambda em sa-east-1
  → embedding In-Region (modelo confirmado)
  → consulta direta ao S3 Vectors em sa-east-1
  → recuperação de chunks
  → montagem de contexto mínimo
  → modelo de geração In-Region
```

Bedrock Knowledge Bases gerenciada será considerada **apenas se confirmada com evidência documental oficial específica para sa-east-1**.

---

## Amazon S3 Vectors — REQUIRES_ACCOUNT_VALIDATION

| Funcionalidade | Status | Verificação |
|---|---|---|
| S3 Vectors — bucket criação | REQUIRES_ACCOUNT_VALIDATION | Testar criação de vector bucket em sa-east-1 |
| S3 Vectors — put/query vectors | REQUIRES_ACCOUNT_VALIDATION | Testar API de vetores em sa-east-1 |

---

## Serviços Excluídos da POC

| Serviço | Status | Motivo |
|---|---|---|
| Bedrock Agents Classic | DESCONTINUADO | "no longer open to new customers starting July 30, 2026" |
| Cross-Region Inference | PROIBIDO | Viola restrição de soberania — dados sairiam do Brasil |
| Inference Profile com roteamento | PROIBIDO | Pode rotear para us-east-1 — não usar sem verificação |
| AgentCore Policy (cross-region) | PROIBIDO | Usa cross-Region inference globalmente |
| OpenSearch Serverless | EXCLUÍDO | Custo mínimo ~$700/mês — substituído por S3 Vectors |
| DynamoDB | EXCLUÍDO | POC stateless — não necessário |
| ElastiCache | EXCLUÍDO | Sem cache de dados corporativos |
| API Gateway | EXCLUÍDO da POC | API MARH invoca diretamente |
| NAT Gateway | EXCLUÍDO | Lambda fora de VPC — sem custo de rede |
| VPC | EXCLUÍDO da POC | Sem benefício + $105/mês + cold start adicional |

---

## Quotas — REQUIRES_VALIDATION_IN_ACCOUNT

| Serviço | Quota | Valor padrão | Observação |
|---|---|---|---|
| Lambda | Concurrent executions | 1.000 | Aumento via Service Quotas se necessário |
| Lambda | Memory | Até 10.240 MB | 512 MB suficiente para POC |
| Lambda | Timeout | 15 minutos | Usaremos < 30s |
| Bedrock | RPM do modelo principal | REQUIRES_VALIDATION | Pode ser menor que us-east-1 |
| Bedrock | TPM input | REQUIRES_VALIDATION | Solicitar aumento antes do POC |
| Bedrock | TPM output | REQUIRES_VALIDATION | Solicitar aumento antes do POC |
| S3 Vectors | Vector buckets por conta | REQUIRES_VALIDATION | |
| Secrets Manager | Secrets por conta | 500.000 | Suficiente |
| CloudWatch Logs | Ingest rate | 5 MB/s por log group | Suficiente |

---

## Ações Necessárias Antes do Build

| # | Ação | Urgência |
|---|---|---|
| 1 | Verificar modelos ACTIVE In-Region no console da conta alvo | BLOQUEANTE |
| 2 | Confirmar disponibilidade Bedrock Knowledge Bases em sa-east-1 | BLOQUEANTE para RAG gerenciado |
| 3 | Testar criação de vector bucket S3 Vectors em sa-east-1 | BLOQUEANTE para RAG |
| 4 | Verificar quotas de Bedrock e solicitar aumento | ANTES da Fase 1 |
| 5 | Confirmar que modelo de embedding tem suporte a S3 Vectors | BLOQUEANTE para RAG |

---

*Fontes: Documentação oficial AWS consultada em 2026-07-23. Itens marcados como REQUIRES_ACCOUNT_VALIDATION exigem verificação adicional em conta real.*
