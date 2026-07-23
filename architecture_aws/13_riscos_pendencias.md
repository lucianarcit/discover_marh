# 13 — Riscos e Pendências

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Riscos Regionais (sa-east-1)

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-01 | Quotas de Bedrock menores que us-east-1 | Alta | Alto | Solicitar aumento antes do POC; validar quotas reais | Platform |
| R-02 | Modelo Claude 3.5 Haiku indisponível na região | Baixa | Crítico | Verificar disponibilidade; fallback para outro modelo | Arquitetura |
| R-03 | S3 Vectors não disponível em sa-east-1 | Baixa | Alto | Verificar GA; alternativa: FAISS em Lambda layer | Arquitetura |
| R-04 | Latência regional maior que us-east-1 | Média | Baixo | Budget de latência já considera overhead; aceitável | Dev |
| R-05 | Knowledge Bases com limitações regionais | Baixa | Médio | Verificar feature parity com us-east-1 | Platform |
| R-06 | Titan Embeddings indisponível para KB | Baixa | Alto | Verificar; alternativa: Cohere Embed | Arquitetura |

---

## 2. Riscos de Integração

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-07 | ma-hr-orch latência P95 > 3.3s em horário de pico | Alta | Alto | Timeout agressivo (10s); circuit breaker; fallback message | Dev |
| R-08 | ma-hr-orch indisponível durante desenvolvimento | Média | Médio | Mock server para desenvolvimento local | Dev |
| R-09 | Formato de resposta do ma-hr-orch muda sem aviso | Média | Alto | Schema validation; contrato versionado; alertas | Dev + ma-hr-orch team |
| R-10 | Sanitização de PII insuficiente (campo novo não mapeado) | Média | Crítico | Allowlist (whitelist) approach — só passa o que está listado | Dev |
| R-11 | ma-hr-orch retorna PII inesperado em campos novos | Média | Alto | Allowlist garante que campos novos são ignorados | Dev |
| R-12 | Credenciais do ma-hr-orch expiram durante POC | Baixa | Médio | Rotação automática via Secrets Manager | Platform |

---

## 3. Riscos de Modelo (LLM)

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-13 | Alucinação: modelo inventa dados não existentes | Alta | Alto | System prompt restritivo; validação de output; RAG com threshold | Dev |
| R-14 | Prompt injection via input do usuário | Média | Alto | Separação system/user; sanitização; instrução anti-injection | Dev |
| R-15 | Modelo revela system prompt | Baixa | Médio | Instrução anti-leak; detecção de patterns | Dev |
| R-16 | Modelo gera conteúdo inadequado | Baixa | Alto | Prompt restritivo; validação de output; Guardrails (produção) | Dev |
| R-17 | Indirect prompt injection via documentos KB | Baixa | Médio | Documentos curados internamente; review antes de indexar | Conteúdo |
| R-18 | Modelo tenta operações de escrita | Baixa | Baixo | Apenas GET implementado; não há tools de escrita | Dev |
| R-19 | Custo de tokens excede orçamento | Média | Médio | Monitorar custo/request; alertas; prompts curtos | Dev |

---

## 4. Riscos Operacionais

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-20 | Cold start afeta experiência do usuário | Média | Baixo | Warm-up via CloudWatch Events; aceitável para POC (~300ms) | Dev |
| R-21 | Lambda throttling em pico | Baixa | Médio | Reserved concurrency = 100; monitorar | Platform |
| R-22 | Logs com PII vazam acidentalmente | Baixa | Crítico | Sanitização antes de log; code review; testes | Dev |
| R-23 | Secrets expostos em código/log | Baixa | Crítico | Secrets Manager; .gitignore; code review | Dev |
| R-24 | Custo AWS excede orçamento do POC | Baixa | Médio | Budget alerts; monitorar diariamente | Platform |
| R-25 | Documentos KB desatualizados | Média | Baixo | Processo de atualização; versionamento S3 | Conteúdo |

---

## 5. Decisões Pendentes

### DP-001: Formato de Invocação da Lambda

| Campo | Valor |
|---|---|
| **Pergunta** | API MARH invocará via Function URL (HTTPS) ou via AWS SDK (invoke)? |
| **Impacto** | Define autenticação, formato de payload, métricas disponíveis |
| **Opções** | A) Function URL com IAM Auth / B) AWS SDK invoke direto / C) Function URL com shared secret |
| **Recomendação** | B (AWS SDK invoke) — menor overhead, sem expor endpoint público |
| **Status** | ❓ AGUARDANDO decisão da equipe API MARH |
| **Deadline** | Antes do início da Fase 1 |

### DP-002: Modelo de Embedding para Knowledge Base

| Campo | Valor |
|---|---|
| **Pergunta** | Qual modelo de embedding usar: Titan Embeddings v2 ou Cohere Embed? |
| **Impacto** | Qualidade do retrieval, custo, disponibilidade regional |
| **Opções** | A) Titan Embeddings v2 / B) Cohere Embed v3 |
| **Recomendação** | A (Titan) — nativo AWS, integração mais simples com KB |
| **Status** | ❓ AGUARDANDO verificação de disponibilidade em sa-east-1 |
| **Deadline** | Antes do início da Fase 3 |

### DP-003: Endpoints Exatos do ma-hr-orch

| Campo | Valor |
|---|---|
| **Pergunta** | Quais são os endpoints exatos (URL base, paths, parâmetros)? |
| **Impacto** | Implementação da integração, testes |
| **Opções** | Documentação da API |
| **Recomendação** | Obter OpenAPI/Swagger spec |
| **Status** | ❓ AGUARDANDO documentação da equipe ma-hr-orch |
| **Deadline** | Antes do início da Fase 4 |

### DP-004: Conteúdo dos Documentos da Knowledge Base

| Campo | Valor |
|---|---|
| **Pergunta** | Quem produz e valida os ~50 documentos markdown para RAG? |
| **Impacto** | Qualidade das respostas informativas |
| **Opções** | A) Equipe de produto / B) Equipe técnica / C) Ambos |
| **Recomendação** | C — Produto define conteúdo, técnico formata para RAG |
| **Status** | ❓ AGUARDANDO definição de responsável |
| **Deadline** | Antes do início da Fase 3 |

### DP-005: Ambiente Sandbox do ma-hr-orch

| Campo | Valor |
|---|---|
| **Pergunta** | Existe ambiente sandbox/staging do ma-hr-orch para testes? |
| **Impacto** | Testes de integração sem afetar produção |
| **Opções** | A) Sandbox existente / B) Mock server / C) Ambiente de dev |
| **Recomendação** | A ou C — ambiente real para validar comportamento |
| **Status** | ❓ AGUARDANDO confirmação |
| **Deadline** | Antes do início da Fase 4 |

### DP-006: Conta AWS e Permissões

| Campo | Valor |
|---|---|
| **Pergunta** | Qual conta AWS será usada? Quem cria IAM roles? |
| **Impacto** | Bloqueia TODA a implementação |
| **Opções** | A) Conta existente / B) Nova conta dedicada / C) Sandbox |
| **Recomendação** | B — conta dedicada para isolamento |
| **Status** | ❓ AGUARDANDO — **BLOQUEANTE PRINCIPAL** |
| **Deadline** | IMEDIATO (bloqueia Fase 1) |

### DP-007: Rate Limits do ma-hr-orch

| Campo | Valor |
|---|---|
| **Pergunta** | Quais são os rate limits do ma-hr-orch? Há throttling? |
| **Impacto** | Dimensionamento do circuit breaker e retry policy |
| **Opções** | Documentação do serviço |
| **Recomendação** | Obter limites documentados |
| **Status** | ❓ AGUARDANDO informação da equipe ma-hr-orch |
| **Deadline** | Antes do início da Fase 4 |

### DP-008: Orçamento Máximo do POC

| Campo | Valor |
|---|---|
| **Pergunta** | Qual o orçamento máximo mensal aceitável para o POC? |
| **Impacto** | Define limites de teste e uso |
| **Opções** | A) $50/mês / B) $100/mês / C) $200/mês |
| **Recomendação** | B ($100/mês) — permite 1000 req/dia com margem |
| **Status** | ❓ AGUARDANDO aprovação |
| **Deadline** | Antes do início da Fase 1 |

---

## 6. Matriz de Prioridade das Pendências

| Prioridade | Decisão | Justificativa |
|---|---|---|
| 🔴 P0 (Bloqueante) | DP-006 (Conta AWS) | Sem conta = sem trabalho |
| 🔴 P0 (Bloqueante) | DP-001 (Formato invocação) | Define arquitetura de entrada |
| 🟡 P1 (Antes da fase) | DP-003 (Endpoints ma-hr-orch) | Necessário para Fase 4 |
| 🟡 P1 (Antes da fase) | DP-005 (Sandbox) | Necessário para testes |
| 🟡 P1 (Antes da fase) | DP-004 (Conteúdo KB) | Necessário para Fase 3 |
| 🟢 P2 (Desejável) | DP-002 (Embedding model) | Default: Titan |
| 🟢 P2 (Desejável) | DP-007 (Rate limits) | Default: conservador |
| 🟢 P2 (Desejável) | DP-008 (Orçamento) | Default: $100/mês |

---

## 7. Plano de Mitigação Consolidado

| Risco | Probabilidade × Impacto | Ação | Responsável | Prazo |
|---|---|---|---|---|
| R-01 (Quotas sa-east-1) | Alta × Alto | Solicitar quotas antes do início | Platform | Semana 0 |
| R-07 (ma-hr-orch latência) | Alta × Alto | Implementar circuit breaker robusto | Dev | Fase 4 |
| R-10 (PII sanitização) | Média × Crítico | Allowlist + testes extensivos | Dev | Fase 4 |
| R-13 (Alucinação) | Alta × Alto | Prompt restritivo + RAG threshold | Dev | Fase 3-4 |
| R-22 (PII em logs) | Baixa × Crítico | Sanitização pré-log + auditoria | Dev | Fase 1 |
| DP-006 (Conta AWS) | — | Escalar para gestão | Líder técnico | Imediato |
