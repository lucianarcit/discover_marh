# 13 — Riscos e Pendências

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1

---

## 1. Riscos Regionais (sa-east-1)

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-01 | Quotas de Bedrock menores que us-east-1 | Alta | Alto | Verificar quotas reais no console; solicitar aumento antes do POC | Platform |
| R-02 | Nenhum modelo ACTIVE In-Region disponível em sa-east-1 | Média | Crítico | Verificar no console da conta alvo antes de qualquer implementação | Arquitetura |
| R-03 | S3 Vectors não disponível em sa-east-1 | Média | Alto | Testar criação de vector bucket; alternativa: FAISS em Lambda layer | Arquitetura |
| R-04 | Bedrock Knowledge Bases não disponível em sa-east-1 | Alta | Médio | Já mitigado: desenho preferencial usa S3 Vectors direto | Arquitetura |
| R-05 | Modelo de embedding não disponível In-Region | Média | Alto | Verificar no console; alternativa: embedding via modelo alternativo | Arquitetura |
| R-06 | Integração direta S3 Vectors + embedding não validada | Média | Alto | Testar end-to-end em Fase 3 | Dev |

---

## 2. Riscos de Integração

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-07 | ma-hr-orch latência alta em horário de pico | Alta | Alto | Timeout configurado (10s); fallback ERR-007 | Dev |
| R-08 | ma-hr-orch indisponível durante desenvolvimento | Média | Médio | Mock server para desenvolvimento local | Dev |
| R-09 | Formato de resposta do ma-hr-orch muda sem aviso | Média | Alto | Schema validation; allowlist garante que campos novos são ignorados | Dev |
| R-10 | Sanitização PII insuficiente (campo novo não mapeado) | Média | Crítico | Allowlist approach — só passa o que está listado | Dev |
| R-11 | Endpoint de rastreamento (INT-007) não inventariado | Alta | Médio | POC usa fallback ERR-007 para INT-007; não bloqueia demonstração | Dev |
| R-12 | Credenciais do ma-hr-orch expiram durante POC | Baixa | Médio | Rotação automática via Secrets Manager | Platform |

---

## 3. Riscos de Modelo (LLM)

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-13 | Alucinação em RAG_ONLY | Alta | Médio | System prompt restritivo; RAG com threshold; fallback ERR-008 | Dev |
| R-14 | Prompt injection via input do usuário | Média | Alto | Separação system/user; instrução fixa; validação de output | Dev |
| R-15 | Modelo revela system prompt | Baixa | Médio | Instrução anti-leak; detecção de patterns | Dev |
| R-16 | Indirect injection via documentos KB | Baixa | Médio | Documentos curados e versionados internamente | Conteúdo |
| R-17 | Custo de tokens excede orçamento | Baixa | Médio | LLM somente em RAG_ONLY (~30% dos requests) | Dev |

---

## 4. Riscos Operacionais

| # | Risco | Prob. | Impacto | Mitigação | Owner |
|---|---|---|---|---|---|
| R-18 | Cold start afeta primeiras requisições | Média | Baixo | Warm-up via CloudWatch Events; ~300ms aceitável | Dev |
| R-19 | Lambda throttling em pico | Baixa | Médio | Reserved concurrency configurado | Platform |
| R-20 | Logs com PII vazam acidentalmente | Baixa | Crítico | Sanitização antes do log; code review; testes | Dev |
| R-21 | Secrets expostos em código/log | Baixa | Crítico | Secrets Manager; .gitignore; code review | Dev |
| R-22 | Custo AWS excede orçamento | Baixa | Médio | Budget alerts; LLM somente em RAG_ONLY | Platform |
| R-23 | marh_feature_knowledge.md desatualizado | Média | Baixo | Processo de atualização; versionamento S3 | Conteúdo |

---

## 5. Decisões Pendentes

### DP-001: Formato de Invocação da Lambda

| Campo | Valor |
|---|---|
| **Pergunta** | API MARH invocará via InvokeFunction (AWS SDK) ou Function URL AWS_IAM? |
| **Impacto** | Define autenticação, formato de payload, métricas disponíveis |
| **Opções** | A) InvokeFunction via AWS SDK (preferencial — API MARH em AWS) / B) Function URL com AWS_IAM + SigV4 |
| **Descartado** | Shared secret — removido da arquitetura |
| **Recomendação** | A se API MARH estiver em AWS e puder assumir role; B caso contrário |
| **Status** | ❓ AGUARDANDO — depende de onde a API MARH está hospedada |
| **Deadline** | Antes da Fase 1 |

### DP-002: Modelo ACTIVE In-Region sa-east-1

| Campo | Valor |
|---|---|
| **Pergunta** | Qual modelo está ACTIVE In-Region em sa-east-1 na conta alvo? |
| **Impacto** | Bloqueante — sem modelo confirmado, RAG_ONLY não pode ser implementado |
| **Opções** | A verificar no console: Claude 3 Haiku, Claude 3.5 Sonnet v2, outros |
| **Recomendação** | Menor modelo ACTIVE com tool use e português — verificar no console |
| **Status** | ❓ AGUARDANDO validação no console da conta — **BLOQUEANTE** |
| **Deadline** | Antes da Fase 1 |

### DP-003: S3 Vectors disponível em sa-east-1

| Campo | Valor |
|---|---|
| **Pergunta** | S3 Vectors está disponível em sa-east-1 na conta alvo? |
| **Impacto** | Define a estratégia RAG — direto via S3 Vectors ou alternativa |
| **Opções** | A) S3 Vectors direto / B) FAISS em Lambda layer |
| **Recomendação** | Testar criação de vector bucket antes da Fase 3 |
| **Status** | ❓ AGUARDANDO — **BLOQUEANTE para Fase 3** |
| **Deadline** | Antes da Fase 3 |

### DP-004: Bedrock Knowledge Bases em sa-east-1

| Campo | Valor |
|---|---|
| **Pergunta** | Bedrock Knowledge Bases está disponível em sa-east-1 com S3 Vectors? |
| **Impacto** | Determina se usa KB gerenciada ou RAG direto |
| **Opções** | A) KB gerenciada (se confirmada) / B) RAG direto via S3 Vectors (preferencial para POC) |
| **Recomendação** | B — RAG direto elimina dependência de KB gerenciada não confirmada |
| **Status** | DEFINIDO — usar RAG direto enquanto KB não for confirmada com evidência oficial |
| **Deadline** | N/A para POC |

### DP-005: Conta AWS e Permissões

| Campo | Valor |
|---|---|
| **Pergunta** | Qual conta AWS? Quem cria IAM roles? Bedrock habilitado em sa-east-1? |
| **Impacto** | Bloqueia TODA a implementação |
| **Status** | ❓ AGUARDANDO — **BLOQUEANTE PRINCIPAL** |
| **Deadline** | IMEDIATO |

### DP-006: Ambiente Sandbox do ma-hr-orch

| Campo | Valor |
|---|---|
| **Pergunta** | Existe sandbox/staging do ma-hr-orch para testes? |
| **Impacto** | Testes de integração sem afetar produção |
| **Opções** | A) Sandbox existente / B) Mock server / C) Ambiente de dev |
| **Status** | ❓ AGUARDANDO |
| **Deadline** | Antes da Fase 4 |

### DP-007: Aprovação do marh_feature_knowledge.md

| Campo | Valor |
|---|---|
| **Pergunta** | O cliente aprovou o conteúdo do marh_feature_knowledge.md para indexação? |
| **Impacto** | Sem aprovação, indexar pode gerar respostas incorretas |
| **Status** | ❓ AGUARDANDO revisão e aprovação |
| **Deadline** | Antes da Fase 3 |

### DP-008: Orçamento Máximo do POC

| Campo | Valor |
|---|---|
| **Pergunta** | Qual o orçamento máximo mensal aceitável? |
| **Impacto** | Define limites de teste |
| **Recomendação** | < $20/mês para escopo mínimo (fixo) + custo Bedrock validado |
| **Status** | ❓ AGUARDANDO aprovação |
| **Deadline** | Antes da Fase 1 |

---

## 6. Matriz de Prioridade

| Prioridade | Decisão/Risco | Justificativa |
|---|---|---|
| 🔴 P0 (Bloqueante) | DP-005 (Conta AWS) | Sem conta = sem trabalho |
| 🔴 P0 (Bloqueante) | DP-002 (Modelo ACTIVE) | Sem modelo = sem RAG_ONLY |
| 🔴 P0 (Bloqueante) | DP-001 (Formato invocação) | Define entrada da Lambda |
| 🟡 P1 (Antes da fase) | DP-003 (S3 Vectors) | Necessário para Fase 3 |
| 🟡 P1 (Antes da fase) | DP-007 (Aprovação KB) | Necessário para Fase 3 |
| 🟡 P1 (Antes da fase) | DP-006 (Sandbox ma-hr-orch) | Necessário para Fase 4 |
| 🟢 P2 (Desejável) | DP-004 (Bedrock KB) | Definido: RAG direto |
| 🟢 P2 (Desejável) | DP-008 (Orçamento) | Default: < $20/mês |
