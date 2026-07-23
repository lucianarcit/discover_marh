# 04 — Arquitetura Recomendada

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1 (São Paulo)  
**Status:** DRAFT

---

## 1. Visão Geral

A arquitetura do Agente Consultivo MARH foi desenhada para operar exclusivamente na região `sa-east-1`, sem VPC, sem API Gateway e sem estado persistente (stateless). O agente é invocado diretamente pela API MARH via Function URL ou AWS SDK.

---

## 2. Tabela de Componentes

| Componente Lógico | Serviço AWS | Responsabilidade | Justificativa | Alternativa Rejeitada |
|---|---|---|---|---|
| Runtime do Agente | AWS Lambda (Python 3.12) | Execução da lógica do agente, classificação, orquestração | Serverless, sem gestão de infra, custo por execução, cold start aceitável | ECS Fargate (over-engineering para POC), EC2 (custo fixo desnecessário) |
| Modelo LLM Principal | Amazon Bedrock — Claude 3.5 Haiku | Geração de respostas naturais, síntese de dados | Baixa latência, custo reduzido, disponível em sa-east-1 | Claude Sonnet 4 (custo 10x maior), GPT-4o (fora do ecossistema AWS) |
| Modelo LLM Alternativo | Amazon Bedrock — Claude Sonnet 4 | Fallback para respostas complexas (futuro) | Maior capacidade de raciocínio | — |
| Base de Conhecimento | Bedrock Knowledge Bases | Indexação e recuperação de documentos markdown | Gerenciado, integração nativa com Bedrock | LangChain + FAISS (mais código, menos gerenciável) |
| Vector Store | S3 Vectors | Armazenamento de embeddings para RAG | Custo ~$5/mês, sem servidor, sem cluster | OpenSearch Serverless ($700/mês mínimo), Pinecone (vendor lock-in externo) |
| Armazenamento de Docs | Amazon S3 (KMS + Versioning) | Documentos fonte para RAG (markdown) | Durável, versionado, criptografado, baixo custo | EFS (desnecessário para docs estáticos) |
| Gerenciamento de Segredos | AWS Secrets Manager | Armazenar tokens, chaves de API, configurações sensíveis | Rotação automática, auditoria, integração IAM | SSM Parameter Store SecureString (menos auditável) |
| Criptografia | AWS KMS | Chaves de criptografia para S3 e Secrets Manager | CMK gerenciada, auditoria via CloudTrail | Chaves default S3 (menor controle) |
| Logs | Amazon CloudWatch Logs | Logs estruturados da Lambda e métricas custom | Nativo, sem setup adicional | ELK Stack (over-engineering) |
| Métricas | Amazon CloudWatch Metrics | Latência, erros, tokens consumidos, custo por rota | Nativo, alarmes integrados | Datadog (custo adicional desnecessário para POC) |
| Tracing | AWS X-Ray | Rastreamento distribuído de requisições | Correlação de chamadas Lambda → Bedrock → ma-hr-orch | Jaeger (infra adicional) |
| Integração Externa | HTTP Client (httpx/requests) | Chamadas GET ao ma-hr-orch | Simples, direto, sem overhead | SDK customizado (desnecessário) |
| Invocação | Lambda Function URL / AWS SDK | API MARH invoca o agente | Sem API Gateway, sem custo adicional, autenticação IAM | API Gateway ($3.50/M requests + custo desnecessário) |

---

## 3. Arquitetura POC vs. Alvo Produção

### 3.1 Arquitetura POC (Escopo Atual)

```
API MARH → Lambda Function URL → Lambda (Python 3.12)
                                      ├── Classificador Determinístico
                                      ├── Bedrock (Claude 3.5 Haiku)
                                      ├── Bedrock Knowledge Bases + S3 Vectors
                                      ├── HTTP → ma-hr-orch (GET only)
                                      ├── Secrets Manager
                                      └── CloudWatch + X-Ray
```

**Características POC:**
- Stateless (sem DynamoDB)
- Sem cache de dados corporativos
- Sem VPC / NAT Gateway
- Sem API Gateway
- Sem multi-agent
- Classificador determinístico (sem LLM para classificação)
- 12 cenários de demonstração
- Dados sintéticos para testes

### 3.2 Arquitetura Alvo Produção (Futuro)

```
API MARH → API Gateway → Lambda (Python 3.12)
                              ├── Classificador (pode evoluir para LLM)
                              ├── Bedrock (Claude 3.5 Haiku / Sonnet 4)
                              ├── Bedrock Knowledge Bases + S3 Vectors
                              ├── HTTP → ma-hr-orch
                              ├── DynamoDB (sessão + histórico)
                              ├── ElastiCache (cache de dados frequentes)
                              ├── Secrets Manager
                              ├── CloudWatch + X-Ray
                              ├── Bedrock Guardrails
                              └── WAF + Shield
```

---

## 4. Diferenças entre POC e Produção

| Aspecto | POC | Produção |
|---|---|---|
| Estado de sessão | Stateless | DynamoDB (TTL 24h) |
| Cache | Nenhum | ElastiCache Redis |
| Proteção de entrada | Function URL + IAM | API Gateway + WAF + Shield |
| Guardrails LLM | Prompt engineering | Bedrock Guardrails |
| Rate limiting | Throttling Lambda | API Gateway throttling + WAF |
| Monitoramento | CloudWatch básico | CloudWatch + dashboards + alarmes + PagerDuty |
| Multi-tenant | Single company | Multi-company isolation |
| Classificador | Determinístico (regex + keywords) | Pode evoluir para LLM-based |
| Documentação RAG | ~50 documentos | Centenas de documentos |
| Região | sa-east-1 only | sa-east-1 only (sem cross-region) |

---

## 5. Componentes a Adicionar Posteriormente

| Componente | Serviço | Quando | Motivo |
|---|---|---|---|
| Sessão/Histórico | DynamoDB | Pós-POC | Contexto multi-turno |
| Cache corporativo | ElastiCache Redis | Pós-POC | Reduzir chamadas ao ma-hr-orch |
| API Management | API Gateway | Produção | Rate limiting, throttling, métricas |
| Proteção DDoS | AWS WAF + Shield | Produção | Segurança de borda |
| Guardrails nativos | Bedrock Guardrails | Produção | Proteção contra prompt injection nativa |
| CI/CD | CodePipeline + CodeBuild | Pós-POC | Automação de deploy |
| IaC | AWS CDK (Python) | Produção | Infraestrutura como código |
| Auditoria | CloudTrail + Config | Produção | Compliance |
| Backup de KB | AWS Backup | Produção | Disaster recovery |
| Notificações | SNS + Lambda | Produção | Alertas de erro |

---

## 6. Componentes NÃO Implementar Agora

| Componente | Motivo da Exclusão |
|---|---|
| VPC + NAT Gateway | Custo de $45/mês sem benefício para POC; ma-hr-orch acessível via HTTPS público |
| API Gateway | API MARH invoca diretamente; sem necessidade de gestão de API pública |
| DynamoDB | POC é stateless; sessão não é requisito |
| OpenSearch Serverless | Custo mínimo $700/mês; S3 Vectors atende o POC por ~$5/mês |
| Multi-Agent | Complexidade desnecessária; um agente com classificação atende 27 intenções |
| Cross-Region Inference | Não permitido por requisito; somente sa-east-1 |
| Bedrock Agents (Classic) | Abstração excessiva, menor controle sobre orquestração e sanitização de PII |
| ElastiCache | Sem cache de dados corporativos no POC (dado pode estar desatualizado) |
| Step Functions | Fluxo simples demais para orquestração com máquina de estados |
| SQS/SNS | Processamento síncrono; sem necessidade de filas no POC |

---

## 7. Decisões de Design Fundamentais

1. **Classificação Determinística** — Nenhuma chamada LLM para classificar a intenção. Usa regex, keywords e regras para mapear para os 27 intents.

2. **PII Never Reaches Model** — Sanitização obrigatória antes de qualquer chamada ao Bedrock. Dados pessoais substituídos por placeholders.

3. **Somente GET** — Nenhuma operação de escrita via ma-hr-orch. Agente é read-only.

4. **10 Mensagens Padronizadas de Erro** — Respostas de erro consistentes e user-friendly, sem expor detalhes técnicos.

5. **Sem Cache de Dados Corporativos** — Cada consulta busca dados frescos do ma-hr-orch. Evita inconsistência.

6. **Region Lock** — Todos os serviços em sa-east-1. Sem inferência cross-region. Sem replicação.
