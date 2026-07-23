# 14 — Architecture Decision Records (ADRs)

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## ADR-001: Runtime Choice — AWS Lambda

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O agente consultivo precisa de um runtime para executar a lógica de classificação, orquestração e integração. O runtime deve suportar Python 3.12, escalar automaticamente e ter custo proporcional ao uso.

### Decisão

Utilizar **AWS Lambda (Python 3.12)** como runtime do agente.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| ECS Fargate | Sem cold start, containers flexíveis | Custo fixo ~$35/mês, over-engineering para POC | Custo fixo desnecessário |
| EC2 | Controle total | Custo fixo, gestão de servidor, patching | Over-engineering |
| App Runner | Simples, auto-scaling | Menos controle, custo mínimo fixo | Menos maduro |
| Bedrock Agents | Gerenciado, sem código de orquestração | Menos controle sobre sanitização, classificação e fluxos | Controle insuficiente (ADR-013) |

### Consequências

- ✅ Zero custo fixo (pay per invocation)
- ✅ Auto-scaling nativo (0 a 1000+ concorrentes)
- ✅ Sem gestão de infraestrutura
- ✅ Integração nativa com CloudWatch e X-Ray
- ⚠️ Cold start (~300ms) aceitável para o caso de uso
- ⚠️ Timeout máximo 15min (mais que suficiente)
- ⚠️ Memory máximo 10GB (512MB suficiente)

### Riscos

- Cold start pode afetar primeiras requisições após período inativo
- Limite de 1000 concorrências default (pode solicitar aumento)

### Custo

- POC (100 req/dia): ~$0.08/mês (free tier)
- Produção (10000 req/dia): ~$7.50/mês

---

## ADR-002: Model Choice — Claude 3.5 Haiku

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O agente precisa de um LLM para gerar respostas naturais a partir de dados da API e chunks do RAG. O modelo deve equilibrar qualidade, latência e custo.

### Decisão

Utilizar **Claude 3.5 Haiku** como modelo principal via Amazon Bedrock.  
**Claude Sonnet 4** como alternativa para respostas complexas (futuro).

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| Claude Sonnet 4 | Melhor raciocínio | 12x mais caro, maior latência | Custo proibitivo para volume |
| Claude 3.5 Sonnet | Bom equilíbrio | 5x mais caro que Haiku | Haiku suficiente para o caso |
| Llama 3 (Bedrock) | Open source, barato | Menor qualidade em português | Qualidade insuficiente |
| GPT-4o (via API) | Alta qualidade | Fora do ecossistema AWS, dependência externa | Vendor lock-in externo |
| Mistral Large | Bom custo-benefício | Menos testado em português | Risco de qualidade |

### Consequências

- ✅ Custo baixo ($0.001/request estimado)
- ✅ Baixa latência (~600ms P50)
- ✅ Boa qualidade para tarefas de formatação e síntese
- ✅ Nativo no Bedrock (sem dependência externa)
- ⚠️ Pode não ser suficiente para raciocínios complexos
- ⚠️ Qualidade em português pode variar

### Riscos

- Modelo pode alucinar (mitigação: RAG + prompt restritivo)
- Qualidade em português pode ser inferior ao inglês
- Disponibilidade em sa-east-1 deve ser confirmada

### Custo

- Input: $0.25/1M tokens
- Output: $1.25/1M tokens
- ~$0.001 por request (1500 in + 500 out tokens)

---

## ADR-003: RAG Strategy — Bedrock Knowledge Bases + S3 Vectors

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O agente precisa responder 14 intenções informativas com base em documentos internos (markdown). Necessita de um sistema de RAG (Retrieval-Augmented Generation).

### Decisão

Utilizar **Bedrock Knowledge Bases** com **S3 Vectors** como vector store.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| LangChain + FAISS | Flexível, local | Mais código, gerenciamento manual de índice | Complexidade operacional |
| LangChain + Pinecone | Boa performance | Vendor lock-in externo, custo | Dependência externa |
| Custom RAG (embeddings manuais) | Controle total | Muito código, manutenção | Over-engineering |
| Bedrock KB + OpenSearch | Melhor performance | $700/mês mínimo | Custo (ADR-004) |

### Consequências

- ✅ Gerenciado (zero infra para RAG)
- ✅ Integração nativa com Bedrock models
- ✅ Baixo custo (~$5/mês)
- ✅ Chunking automático de documentos
- ✅ Suporta markdown nativamente
- ⚠️ Menos controle sobre chunking strategy
- ⚠️ Performance pode ser inferior a OpenSearch

### Riscos

- Qualidade do retrieval depende da qualidade dos documentos
- Chunking automático pode não ser ideal para todos os docs
- Disponibilidade do serviço em sa-east-1

### Custo

- S3 Vectors: ~$5/mês
- KB queries: incluso no custo de embedding
- S3 storage: ~$0.50/mês

---

## ADR-004: Vector Store — S3 Vectors (over OpenSearch Serverless)

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O Bedrock Knowledge Bases suporta múltiplos vector stores. Para o POC, precisamos do mais simples e econômico.

### Decisão

Utilizar **S3 Vectors** como vector store para o Knowledge Base.

### Alternativas Consideradas

| Alternativa | Custo Mínimo | Performance (P95) | Complexidade | Motivo da Rejeição |
|---|---|---|---|---|
| OpenSearch Serverless | $700/mês | ~200ms | Média | Custo absurdo para POC |
| Aurora pgvector | $50/mês | ~300ms | Alta | Requer RDS, over-engineering |
| Pinecone | $70/mês | ~150ms | Baixa | Vendor externo |
| Redis (ElastiCache) | $30/mês | ~50ms | Média | Não integra com KB nativamente |
| **S3 Vectors** | **~$5/mês** | **~500ms** | **Muito baixa** | ✅ ESCOLHIDO |

### Consequências

- ✅ Economia de $695/mês vs. OpenSearch Serverless
- ✅ Zero gerenciamento (serverless)
- ✅ Integração nativa com Bedrock KB
- ⚠️ Latência ligeiramente maior (~500ms vs ~200ms)
- ⚠️ Serviço relativamente novo (verificar GA em sa-east-1)

### Riscos

- Serviço pode não estar disponível em sa-east-1 (verificar)
- Performance pode degradar com volume muito alto de vetores
- Menos features que OpenSearch (sem filtros complexos)

### Custo

- S3 Vectors: ~$5/mês (20GB estimado)
- vs. OpenSearch Serverless: ~$700/mês
- **Economia: $695/mês ($8.340/ano)**

---

## ADR-005: No VPC

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

Lambda pode executar dentro ou fora de uma VPC. VPC adiciona isolamento de rede mas também custo e complexidade.

### Decisão

Lambda executará **fora de VPC** no POC.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| Lambda em VPC | Isolamento de rede, controle de egress | +$105/mês, +1-2s cold start, complexidade | Custo e complexidade sem benefício para POC |

### Consequências

- ✅ Zero custo de rede
- ✅ Sem impacto em cold start (sem ENI attachment)
- ✅ Simplicidade operacional
- ✅ Todos os serviços acessíveis via HTTPS
- ⚠️ Sem controle de egress por IP/port
- ⚠️ Não atende compliance PCI-DSS (avaliar para produção)

### Riscos

- Se ma-hr-orch migrar para rede privada, precisará de VPC
- Se compliance exigir VPC, migration será necessária

### Custo

- Economia: $105/mês ($1.260/ano) vs. Lambda em VPC

---

## ADR-006: No NAT Gateway

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

NAT Gateway é necessário quando Lambda em VPC precisa acessar internet. Como Lambda está fora de VPC (ADR-005), NAT Gateway não é necessário.

### Decisão

**Não utilizar NAT Gateway.**

### Consequências

- ✅ Economia de $45-90/mês
- ✅ Sem ponto de falha adicional
- ✅ Sem limite de bandwidth do NAT
- ✅ Decorrência direta do ADR-005

### Custo

- Economia: $45/mês (mínimo) = $540/ano

---

## ADR-007: Session State — Stateless

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O agente pode ser stateful (manter contexto entre turnos) ou stateless (cada request é independente).

### Decisão

POC será **stateless**. Cada requisição é processada independentemente, sem histórico de conversa.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| DynamoDB (sessão) | Contexto multi-turno, melhor UX | Custo, complexidade, gestão de TTL | Desnecessário para POC |
| ElastiCache Redis | Rápido, TTL nativo | Custo fixo ~$30/mês | Over-engineering |
| Lambda memory (dict) | Zero custo | Perde entre invocações | Não funciona |

### Consequências

- ✅ Simplicidade máxima
- ✅ Zero custo de storage
- ✅ Sem gerenciamento de TTL/expiração
- ✅ Cada request é autocontido
- ⚠️ Sem contexto de conversa (usuário precisa repetir informações)
- ⚠️ Sem personalização baseada em histórico

### Riscos

- UX pode ser impactada (sem "memória" da conversa)
- Aceitável para POC; evoluir para stateful se necessário

### Custo

- $0 (vs. ~$5-30/mês com DynamoDB/ElastiCache)

---

## ADR-008: Deterministic Responses — No LLM for Static/Policy

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

Para intents fora de escopo (6) e redirecionamentos, podemos usar respostas determinísticas (hardcoded) ou gerar via LLM.

### Decisão

Intents OUT-001 a OUT-006 e redirecionamentos utilizam **respostas determinísticas** (sem chamada LLM).

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| LLM para todas as respostas | Tom mais natural, variado | Custo desnecessário, latência, risco de alucinação | Overhead sem benefício |

### Consequências

- ✅ Latência ~20ms (vs. ~800ms com LLM)
- ✅ Zero custo de tokens para ~30% das requisições
- ✅ Respostas 100% previsíveis e controladas
- ✅ Sem risco de alucinação ou conteúdo inadequado
- ⚠️ Respostas podem parecer "robóticas" (aceitável)
- ⚠️ Menos variação (sempre a mesma resposta)

### Custo

- Economia: ~30% dos tokens totais não são gastos

---

## ADR-009: Cache Policy — No Cache of Corporate Data

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

Dados corporativos do ma-hr-orch (pedidos, saldos, colaboradores) poderiam ser cacheados para reduzir latência e chamadas.

### Decisão

**Não cachear dados corporativos** no POC. Cada consulta busca dados frescos do ma-hr-orch.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| ElastiCache Redis | Reduz latência, menos chamadas | Dados podem estar desatualizados, custo $30/mês, complexidade de invalidação | Risco de dados stale |
| Lambda memory cache | Zero custo | Efêmero, inconsistente entre instâncias | Não confiável |
| DynamoDB cache | Durável, TTL | Custo, complexidade | Over-engineering |

### Consequências

- ✅ Dados sempre frescos/atualizados
- ✅ Sem complexidade de invalidação de cache
- ✅ Sem risco de mostrar dados desatualizados
- ✅ Simplicidade
- ⚠️ Maior latência (sempre chama ma-hr-orch)
- ⚠️ Mais carga no ma-hr-orch

### Riscos

- ma-hr-orch pode sofrer com volume se escalar muito
- Aceitável para POC; avaliar cache para produção

### Custo

- $0 (economia de $30/mês vs. ElastiCache)

---

## ADR-010: Observability — CloudWatch + X-Ray

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

O agente precisa de observabilidade para monitorar performance, erros e custo.

### Decisão

Utilizar **CloudWatch** (logs + metrics) + **AWS X-Ray** (tracing distribuído).

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| Datadog | Dashboard superior, APM completo | $15-30/host/mês, vendor externo | Custo desnecessário para POC |
| New Relic | Bom free tier, APM | Vendor externo, complexidade | Desnecessário |
| ELK Stack | Open source, poderoso | Infra para gerenciar, custo Elastic | Over-engineering |
| OpenTelemetry + Grafana | Vendor-neutral | Infra adicional | Over-engineering para POC |

### Consequências

- ✅ Nativo AWS (zero setup adicional)
- ✅ Integração automática com Lambda
- ✅ Custo proporcional ao uso
- ✅ X-Ray trace completo (Lambda → Bedrock → ma-hr-orch)
- ⚠️ Dashboards menos sofisticados que Datadog
- ⚠️ Alertas mais limitados (suficiente para POC)

### Custo

- CloudWatch: ~$5/mês (POC)
- X-Ray: ~$0.50/mês (free tier 100K traces)

---

## ADR-011: Region Restriction — sa-east-1 Only

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Requisito de Negócio |

### Contexto

Por requisitos de soberania de dados e compliance, todos os dados devem permanecer no Brasil.

### Decisão

Todos os serviços AWS operam **exclusivamente em sa-east-1** (São Paulo).

### Consequências

- ✅ Dados permanecem no Brasil
- ✅ Compliance com LGPD (localidade)
- ✅ Menor latência para usuários brasileiros
- ⚠️ Quotas podem ser menores
- ⚠️ Alguns serviços podem não estar disponíveis
- ⚠️ Sem redundância multi-região

### Riscos

- Se sa-east-1 tiver outage, agente fica indisponível
- Quotas de Bedrock podem ser restritivas
- Alguns modelos podem não estar disponíveis

---

## ADR-012: No Cross-Region Inference

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Requisito de Negócio |

### Contexto

Bedrock oferece cross-region inference para melhor disponibilidade e throughput, roteando requests para outras regiões automaticamente.

### Decisão

**Não utilizar cross-region inference.** Todas as inferências devem ser processadas em sa-east-1.

### Alternativas Consideradas

| Alternativa | Prós | Contras | Motivo da Rejeição |
|---|---|---|---|
| Cross-region inference | Maior throughput, melhor disponibilidade | Dados saem do Brasil, compliance | Viola requisito de soberania |

### Consequências

- ✅ Dados nunca saem de sa-east-1
- ✅ Compliance com soberania de dados
- ⚠️ Throughput limitado à capacidade da região
- ⚠️ Sem failover automático para outra região
- ⚠️ Pode ter throttling em picos

### Riscos

- Throttling em sa-east-1 durante picos (sem overflow para outra região)
- Mitigação: monitorar quotas, solicitar aumento antecipado

---

## ADR-013: Bedrock Agents Classic — Rejected

| Campo | Valor |
|---|---|
| **Status** | ACCEPTED |
| **Data** | 2026-07-23 |
| **Deciders** | Equipe de Arquitetura |

### Contexto

Bedrock Agents oferece orquestração gerenciada com tool use, conversação e memória. Avaliamos se atende aos requisitos do agente MARH.

### Decisão

**Rejeitar Bedrock Agents Classic** em favor de orquestração custom em Lambda.

### Motivos da Rejeição

| Requisito | Bedrock Agents | Lambda Custom | Vencedor |
|---|---|---|---|
| Classificação determinística (sem LLM) | ❌ Sempre usa LLM para classificar | ✅ Regex/rules sem custo | Lambda |
| Sanitização PII antes do modelo | ⚠️ Difícil controlar | ✅ Controle total | Lambda |
| Respostas estáticas sem LLM | ❌ Sempre passa pelo modelo | ✅ Retorno direto | Lambda |
| Allowlist de campos por endpoint | ⚠️ Complexo de implementar | ✅ Total controle | Lambda |
| 10 mensagens padronizadas de erro | ⚠️ Mensagens do agent são genéricas | ✅ Mensagens custom | Lambda |
| Circuit breaker / retry custom | ❌ Não suporta | ✅ Implementação livre | Lambda |
| Custo (classificação) | ❌ LLM call para cada classificação | ✅ $0 (regex) | Lambda |
| Observabilidade custom | ⚠️ Limitada | ✅ Total controle | Lambda |

### Consequências

- ✅ Controle total sobre fluxo de dados
- ✅ PII nunca alcança o modelo (garantia arquitetural)
- ✅ ~30% das requests não gastam tokens (respostas estáticas)
- ✅ Tratamento de erro customizado
- ⚠️ Mais código para manter
- ⚠️ Sem memory/session gerenciado (aceitável: stateless)

### Custo

- Economia em tokens de classificação: ~$0.0003/request × volume
- Mais custo de desenvolvimento (one-time)
