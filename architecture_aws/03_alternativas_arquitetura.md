# 03 — Alternativas de Arquitetura

---

## Alternativa A — Amazon Bedrock AgentCore

### Descrição

- API MARH → Lambda de entrada (adaptador) → AgentCore Runtime
- AgentCore Runtime gerencia: modelo, tools, sessão
- Tools definidas para ma-hr-orch
- Bedrock Knowledge Bases para RAG
- S3 Vectors como armazenamento vetorial

### Vantagens

- Gerenciamento de sessão nativo
- Framework de tools integrado
- Observabilidade nativa (quando disponível)
- Evolução simplificada para recursos futuros do AgentCore

### Desvantagens

- Serviço recém-lançado em sa-east-1 (maio 2026) — maturidade limitada
- AgentCore Policy usa cross-Region inference (viola restrição)
- Menor controle sobre o fluxo de orquestração
- Classificação determinística difícil de implementar sem chamada ao LLM
- Overhead de abstração pode dificultar otimizações de latência
- Documentação e exemplos limitados para sa-east-1
- Risco de quotas restritivas em região nova

### Pontuação

| Critério | Peso | Nota (1-5) | Justificativa |
|---|---|---|---|
| Prazo de implementação | Alto | 3 | Curva de aprendizado do novo serviço |
| Latência | Alto | 3 | Overhead do runtime gerenciado |
| Concorrência | Alto | 3 | Quotas não documentadas em sa-east-1 |
| Segurança | Alto | 4 | IAM + tools gerenciadas |
| Custo variável | Alto | 3 | Pay-per-use mas pricing opaco |
| Custo fixo | Alto | 4 | Sem sempre-on |
| Overhead operacional | Alto | 4 | Gerenciado |
| Facilidade de testes | Médio | 2 | Difícil testar localmente |
| Evolução para produção | Alto | 4 | Framework maduro a longo prazo |
| Disponibilidade em sa-east-1 | Eliminatório | ✅ | Disponível (maio 2026) |
| Risco de lock-in | Médio | 2 | Alto lock-in ao AgentCore |
| **Total ponderado** | | **3.1** | |

---

## Alternativa B — Lambda com orquestração própria (RECOMENDADA)

### Descrição

- API MARH → AWS Lambda (Python 3.12)
- Lambda orquestra: classificação, roteamento, sanitização
- Amazon Bedrock Converse API para LLM
- Bedrock Knowledge Bases + S3 Vectors para RAG
- Cliente HTTP para ma-hr-orch
- Stateless — contexto na requisição

### Vantagens

- Controle total sobre o fluxo de execução
- Classificação determinística sem chamar LLM
- Sanitização custom antes do modelo
- Testável localmente (SAM, moto, pytest)
- Zero custo fixo
- Documentação madura e ampla
- Todas as otimizações de latência sob controle
- Provisioned concurrency para eliminar cold start
- Código reutilizável em produção

### Desvantagens

- Toda orquestração é código próprio
- Gerenciamento de sessão precisa ser implementado (se necessário)
- Limite de 15 minutos (irrelevante — requests < 30s)
- Cold start (mitigável)

### Pontuação

| Critério | Peso | Nota (1-5) | Justificativa |
|---|---|---|---|
| Prazo de implementação | Alto | 5 | Stack conhecida, sem curva de aprendizado |
| Latência | Alto | 5 | Controle total, provisioned concurrency |
| Concorrência | Alto | 4 | 1.000 concurrent padrão, escalável |
| Segurança | Alto | 5 | IAM granular, sem dados em memória permanente |
| Custo variável | Alto | 5 | $0 quando inativo, pay-per-invocation |
| Custo fixo | Alto | 5 | Zero |
| Overhead operacional | Alto | 4 | Serverless — deploy via SAM/CDK |
| Facilidade de testes | Médio | 5 | pytest, SAM local, mocks |
| Evolução para produção | Alto | 4 | Adicionar layers progressivamente |
| Disponibilidade em sa-east-1 | Eliminatório | ✅ | Disponível (desde 2014) |
| Risco de lock-in | Médio | 4 | Lógica em Python, modelo via API |
| **Total ponderado** | | **4.6** | |

---

## Alternativa C — Container gerenciado (ECS Fargate)

### Descrição

- API MARH → Application Load Balancer → ECS Fargate (FastAPI/Python)
- Container always-on (mínimo 1 task)
- Amazon Bedrock para LLM
- Bedrock Knowledge Bases + S3 Vectors para RAG
- Cliente HTTP para ma-hr-orch

### Vantagens

- Sem limite de 15 minutos (irrelevante para este caso)
- Framework web tradicional (FastAPI, Flask)
- Sem cold start
- Útil se streaming bidirecional for necessário

### Desvantagens

- **Custo fixo sempre-on**: mínimo ~$30–50/mês (1 task Fargate 0.5 vCPU / 1GB)
- Necessita ALB (~$22/mês fixo)
- Escalabilidade mais lenta que Lambda
- Requer gerenciar imagens Docker, ECR, deploys
- Complexidade operacional maior
- NAT Gateway necessário para acesso à internet ($45/mês + dados)
- Overhead de VPC obrigatório

### Pontuação

| Critério | Peso | Nota (1-5) | Justificativa |
|---|---|---|---|
| Prazo de implementação | Alto | 3 | Docker, ECR, ALB, VPC, subnets |
| Latência | Alto | 5 | Sem cold start |
| Concorrência | Alto | 4 | Autoscaling horizontal |
| Segurança | Alto | 4 | VPC, security groups |
| Custo variável | Alto | 3 | Paga sempre-on mesmo sem uso |
| Custo fixo | Alto | 2 | ALB + Fargate + NAT = ~$100/mês mínimo |
| Overhead operacional | Alto | 3 | Docker, deploys, health checks |
| Facilidade de testes | Médio | 4 | Container local |
| Evolução para produção | Alto | 4 | Horizontal scaling natural |
| Disponibilidade em sa-east-1 | Eliminatório | ✅ | Disponível |
| Risco de lock-in | Médio | 4 | Container portátil |
| **Total ponderado** | | **3.5** | |

---

## Referência — Bedrock Agents Classic

### Status

**DESCONTINUADO para novos clientes a partir de 30/07/2026.** Não recomendado.

- Documentação oficial: "Amazon Bedrock Agents (launched November 2023) is now 'Amazon Bedrock Agents Classic' and will no longer be open to new customers starting on July 30, 2026."
- Migração recomendada para AgentCore

### Motivo de rejeição

- Não estará disponível para novas implementações na data prevista do build
- Sem evolução futura
- Lock-in em serviço legado

---

## Comparação Visual

| Critério | A (AgentCore) | B (Lambda) | C (Fargate) |
|---|---|---|---|
| Prazo | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Latência | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Concorrência | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Segurança | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Custo variável | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Custo fixo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Operacional | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Testes | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Evolução | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Lock-in | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **TOTAL** | **3.1** | **4.6** | **3.5** |

## Decisão

**Alternativa B — Lambda com orquestração própria.**

A menor arquitetura que atende todos os requisitos, com o menor custo, maior facilidade de teste e controle total sobre otimizações de latência e segurança.

---

*Análise realizada em 2026-07-23 com base na documentação oficial da AWS*
