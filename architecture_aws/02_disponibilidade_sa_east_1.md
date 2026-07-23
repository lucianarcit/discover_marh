# 02 — Disponibilidade de Serviços em sa-east-1

> **Data da consulta:** 2026-07-23  
> **Fonte:** Documentação oficial da AWS

---

## Matriz de Disponibilidade

| Serviço | Funcionalidade | Disponível em sa-east-1 | Evidência oficial | Alternativa regional |
|---|---|---|---|---|
| AWS Lambda | Runtime Python 3.12 | ✅ Sim | [AWS Lambda endpoints](https://docs.aws.amazon.com/general/latest/gr/lambda-service.html) | N/A |
| Amazon Bedrock | Runtime (Converse API) | ✅ Sim | [Bedrock regional endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints-region-availability.html) | N/A |
| Amazon Bedrock | Claude 3.5 Haiku (In-Region) | ✅ Sim | [Bedrock models region compatibility](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html) | N/A |
| Amazon Bedrock | Claude Sonnet 4 (In-Region) | ✅ Sim | [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) — sa-east-1 listado | N/A |
| Amazon Bedrock | Claude 3 Haiku (In-Region) | ✅ Sim | Documentação do modelo | N/A |
| Amazon Bedrock | Titan Text Embeddings V2 | ✅ Sim | [KB supported models](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html) | N/A |
| Amazon Bedrock | Knowledge Bases | ✅ Sim | [KB regions](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html) | N/A |
| Amazon Bedrock | Guardrails | ✅ Sim | [Guardrails supported regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported.html) — sa-east-1 listado | N/A |
| Amazon Bedrock | AgentCore Runtime | ✅ Sim | [AWS announcement maio 2026](https://aws.amazon.com/about-aws/whats-new/2026/05/agentcore-sao-paulo-region/) | N/A |
| Amazon S3 | Buckets, versionamento, KMS | ✅ Sim | Serviço global com endpoints regionais | N/A |
| Amazon S3 Vectors | Vector buckets | ✅ Sim | [S3 Vectors expansion março 2026](https://aws.amazon.com/about-aws/whats-new/2026/03/s3-vectors-expands-17-regions/) | N/A |
| Amazon OpenSearch Serverless | Coleções vetoriais | ✅ Sim | [OpenSearch Serverless endpoints](https://docs.aws.amazon.com/general/latest/gr/opensearch-service.html) | S3 Vectors (menor custo) |
| Amazon Aurora PostgreSQL | pgvector | ✅ Sim | [Aurora regions](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.RegionsAndAvailabilityZones.html) | S3 Vectors |
| Amazon DynamoDB | On-demand, TTL, KMS | ✅ Sim | Serviço regional padrão | N/A |
| AWS Secrets Manager | Secrets, rotação | ✅ Sim | Serviço regional padrão | N/A |
| AWS KMS | Chaves simétricas regionais | ✅ Sim | Serviço regional padrão | N/A |
| Amazon CloudWatch | Logs, Metrics, Alarms | ✅ Sim | Serviço regional padrão | N/A |
| AWS X-Ray | Tracing distribuído | ✅ Sim | Serviço regional padrão | N/A |
| Amazon API Gateway | HTTP API | ✅ Sim | Serviço regional padrão | Integração direta |
| AWS WAF | Proteção de API | ✅ Sim | [WAF endpoints](https://docs.aws.amazon.com/general/latest/gr/waf.html) | N/A |
| Amazon VPC | VPC, subnets, security groups | ✅ Sim | Serviço regional padrão | N/A |
| NAT Gateway | Saída de VPC | ✅ Sim | Serviço regional padrão | Lambda fora de VPC |
| VPC Endpoints (PrivateLink) | Bedrock, S3, Secrets Manager | ✅ Sim | Documentação de cada serviço | N/A |

## Modelos Bedrock Disponíveis em sa-east-1 (In-Region)

| Modelo | Provider | Model ID | Tool Use | Streaming | Contexto |
|---|---|---|---|---|---|
| Claude 3.5 Haiku | Anthropic | anthropic.claude-3-5-haiku-20241022-v1:0 | ✅ | ✅ | 200K |
| Claude 3 Haiku | Anthropic | anthropic.claude-3-haiku-20240307-v1:0 | ✅ | ✅ | 200K |
| Claude Sonnet 4 | Anthropic | anthropic.claude-sonnet-4-20250514-v1:0 | ✅ | ✅ | 200K |
| Claude 3.5 Sonnet v2 | Anthropic | anthropic.claude-3-5-sonnet-20241022-v2:0 | ✅ | ✅ | 200K |
| Titan Text Embeddings V2 | Amazon | amazon.titan-embed-text-v2:0 | N/A | N/A | 8K |
| OpenAI open weight models | OpenAI | Vários | ✅ | ✅ | Variável |

> **Nota:** Modelos listados com base em anúncios oficiais da AWS para sa-east-1 até julho 2026. Verificar disponibilidade exata no console antes do build.

## Serviços NÃO Disponíveis ou com Restrições em sa-east-1

| Serviço/Feature | Status | Impacto | Mitigação |
|---|---|---|---|
| Bedrock Agents Classic | Descontinuado para novos clientes (jul 2026) | Não pode ser usado | Usar Lambda + Converse API |
| AgentCore Policy (cross-region) | Usa cross-Region inference globalmente | Viola restrição regional | Não usar AgentCore Policy |
| Bedrock Guardrails Image Filters | Apenas us-east-1, us-west-2, eu-central-1, ap-northeast-1 | Sem impacto (texto only) | N/A |

## Bloqueadores Regionais

| Serviço | Funcionalidade | Status |
|---|---|---|
| — | — | **NENHUM BLOQUEADOR IDENTIFICADO** |

Todos os serviços necessários para a arquitetura proposta estão disponíveis em sa-east-1.

## Quotas Relevantes em sa-east-1

| Serviço | Quota | Valor padrão | Nota |
|---|---|---|---|
| Lambda | Concurrent executions | 1.000 | Aumento via Service Quotas |
| Lambda | Memory | Até 10.240 MB | Suficiente |
| Lambda | Timeout | 15 minutos | Suficiente (usaremos < 30s) |
| Bedrock | Requests por minuto (Claude 3.5 Haiku) | Verificar no console | Pode ser menor que us-east-1 |
| Bedrock | Tokens por minuto (input) | Verificar no console | Pode requerer aumento |
| Bedrock | Tokens por minuto (output) | Verificar no console | Pode requerer aumento |
| S3 Vectors | Vector buckets por conta | 1.000 | Suficiente |
| S3 Vectors | Vectors por bucket | 50 milhões | Muito acima do necessário |
| Secrets Manager | Secrets por conta | 500.000 | Suficiente |
| CloudWatch Logs | Ingest rate | 5 MB/s por log group | Suficiente |

> **AÇÃO REQUERIDA:** Antes de iniciar o build, consultar as quotas exatas de Bedrock em sa-east-1 para o modelo selecionado e solicitar aumento se necessário.

---

*Fontes: Documentação oficial AWS consultada em 2026-07-23*
