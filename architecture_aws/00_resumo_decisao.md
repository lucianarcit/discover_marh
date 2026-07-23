# 00 — Resumo da Decisão Arquitetural

> **Data:** 2026-07-23 (revisão corretiva)
> **Região:** `sa-east-1` exclusivamente
> **Status:** Desenho — nenhum recurso criado

---

## Alternativa Recomendada

**Alternativa B — AWS Lambda com orquestração própria**

## Justificativa

| Critério | Resultado |
|---|---|
| Prazo de implementação | Menor — sem dependência de novo serviço |
| Latência | Controlável — provisioned concurrency disponível |
| Concorrência | Até 1.000 execuções simultâneas por padrão (aumento via quota) |
| Segurança | IAM nativo, sem secrets em variáveis, KMS integrado |
| Custo variável | Pay-per-use — R$0 quando inativo |
| Custo fixo | Zero (sem NAT, sem container always-on, sem OpenSearch Serverless) |
| Overhead operacional | Mínimo — serverless gerenciado |
| Facilidade de testes | Alta — invocação local, mocks, event-driven |
| Evolução para produção | Direta — adicionar provisioned concurrency, WAF, observabilidade |
| Disponibilidade em sa-east-1 | Confirmada para Lambda, S3, KMS, CloudWatch |
| Risco de lock-in | Baixo — lógica em Python/Node.js, modelo via API padrão |

## Componentes Selecionados

| Componente lógico | Serviço AWS | Justificativa |
|---|---|---|
| Entrada da API | InvokeFunction via AWS SDK (preferencial) ou Function URL AWS_IAM | Sem API Gateway extra — API MARH invoca diretamente |
| Runtime do agente | AWS Lambda (Python 3.12) | Serverless, pay-per-use, escalável |
| Modelo LLM Principal | Amazon Bedrock — PROPOSED_PENDING_ACCOUNT_VALIDATION | Ver seção "Modelo Regional" |
| Modelo alternativo | Amazon Bedrock — PROPOSED_PENDING_ACCOUNT_VALIDATION | Ver seção "Modelo Regional" |
| Modelo de embedding | Amazon Bedrock — PROPOSED_PENDING_ACCOUNT_VALIDATION | Ver seção "Modelo Regional" |
| RAG — Implementação | Lambda → embedding In-Region → S3 Vectors direto (preferencial) | Ver seção "Estratégia RAG" |
| Armazenamento vetorial | Amazon S3 Vectors | Custo mínimo, sem servidor always-on |
| Fonte documental RAG | Amazon S3 (bucket versionado, KMS) | Markdown aprovado — `marh_feature_knowledge.md` |
| Segredos | AWS Secrets Manager | Rotação automática, KMS |
| Estado de sessão | Stateless (contexto na requisição) | Sem DynamoDB na POC — mínimo necessário |
| Observabilidade | CloudWatch Logs + X-Ray | Regional, integrado com Lambda |
| Criptografia | AWS KMS (chave regional) | Criptografia at-rest e in-transit |

---

## Modelo Regional — PROPOSED_PENDING_ACCOUNT_VALIDATION

**Status:** Não é possível confirmar modelo ACTIVE e In-Region em `sa-east-1` sem acesso ao console ou CLI da conta.

Nenhum modelo está declarado como `ACCEPTED` até validação em conta real.

| Papel | Status | Critério de seleção (pós-validação) |
|---|---|---|
| Principal (geração) | PROPOSED_PENDING_ACCOUNT_VALIDATION | ACTIVE + In-Region sa-east-1 + português + tool use + baixa latência |
| Alternativo (qualidade) | PROPOSED_PENDING_ACCOUNT_VALIDATION | ACTIVE + In-Region sa-east-1 + maior raciocínio |
| Embedding | PROPOSED_PENDING_ACCOUNT_VALIDATION | ACTIVE + In-Region sa-east-1 + integração S3 Vectors |

**Candidatos a verificar no console (sem garantia de ACTIVE em sa-east-1):**

| Candidato | Model ID | Verificar |
|---|---|---|
| Claude 3 Haiku | anthropic.claude-3-haiku-20240307-v1:0 | Status ACTIVE + In-Region sa-east-1 |
| Claude 3.5 Sonnet v2 | anthropic.claude-3-5-sonnet-20241022-v2:0 | Status ACTIVE + In-Region sa-east-1 |
| Titan Embed Text v2 | amazon.titan-embed-text-v2:0 | Status ACTIVE + In-Region sa-east-1 |

**Nota:** Claude 3.5 Haiku (`anthropic.claude-3-5-haiku-20241022-v1:0`) foi removido como escolha automática. Disponibilidade In-Region em sa-east-1 não pôde ser confirmada como ACTIVE sem acesso ao console. Não deve ser declarado ACCEPTED sem verificação.

**Nota:** Claude Sonnet 4 referenciado via inference profile implica roteamento cross-Region. Não usar inference profile que roteia para fora de `sa-east-1`.

---

## Estratégia RAG

**Status:** Bedrock Knowledge Bases em `sa-east-1` não está confirmada com evidência oficial específica e atual. Alternativa direta é o desenho preferencial para a POC.

### Desenho preferencial (POC)

```
Lambda em sa-east-1
  → gera embedding da query (modelo In-Region)
  → consulta S3 Vectors diretamente em sa-east-1
  → recupera chunks relevantes
  → monta contexto mínimo
  → chama modelo de geração In-Region em sa-east-1
  → retorna resposta
```

### Fonte documental

- Bucket S3 regional com versionamento, criptografia KMS, metadados, aprovação
- Documento indexado: `discover3/knowledge/marh_feature_knowledge.md`
- **Não indexar:** `discover3/agent_policy.md` — política do agente fica no código/configuração determinística

### Parâmetros RAG (ASSUMPTION_REQUIRES_EVALUATION)

| Parâmetro | Valor inicial | Marcação |
|---|---|---|
| top-k | 3 | ASSUMPTION_REQUIRES_EVALUATION |
| score threshold | parâmetro de configuração | ASSUMPTION_REQUIRES_EVALUATION |
| Limite de tokens por contexto | a definir | ASSUMPTION_REQUIRES_EVALUATION |
| Chunking | por seções do markdown | Ajustar após avaliação |

---

## Fluxos sem LLM (Obrigatório na POC)

| Fluxo | LLM | Justificativa |
|---|---|---|
| CLIENT_POLICY / STATIC_RESPONSE | ❌ Zero | Resposta determinística versionada |
| REDIRECT_TO_OFFICIAL_JOURNEY | ❌ Zero | Mensagem estática definida pelo cliente |
| API_ONLY (colaboradores, pedidos) | ❌ Zero | Template determinístico após allowlist |
| REQUIRES_CLARIFICATION | ❌ Zero (mensagem padronizada) | ERR-010 ou equivalente |
| RAG_ONLY | ✅ Uma geração | Quando há evidência suficiente na KB |

---

## Entrada da POC

### Opção preferencial

```
API MARH → InvokeFunction (AWS SDK) → IAM role + resource-based policy da Lambda
```

Usar quando a API MARH estiver em ambiente AWS e puder assumir uma role.

### Alternativa

```
API MARH → Function URL com AWS_IAM → requisição assinada com SigV4
```

- Sem autenticação anônima
- Sem shared secret
- Não expor Function URL publicamente sem IAM

**Registrar DP-001** enquanto não houver informação sobre onde a API MARH está hospedada.

---

## Custo Estimado (POC) — PRICE_REQUIRES_VALIDATION

Todos os valores de modelo marcados como PRICE_REQUIRES_VALIDATION até confirmação do modelo.

| Item | Custo mensal estimado | Notas |
|---|---|---|
| Lambda | $0 (free tier + pay-per-use) | |
| S3 (documentos) | < $1 | Corpus real < 1 MB |
| S3 Vectors | PRICE_REQUIRES_VALIDATION | Depende de confirmação regional |
| Secrets Manager | ~$1 | 1–2 secrets |
| CloudWatch Logs | ~$2–5 | Retenção curta |
| KMS | ~$1–2 | |
| Bedrock (LLM) | PRICE_REQUIRES_VALIDATION | Depende do modelo |
| Bedrock (embedding) | PRICE_REQUIRES_VALIDATION | Depende do modelo |
| **Total fixo (sem Bedrock)** | **< $10/mês** | |

**Redução significativa vs. versão anterior:** LLM removido das rotas API_ONLY (INT-001 a INT-005). Somente RAG_ONLY (INT-010, INT-019, INT-020) usa LLM para geração.

---

## Latência por Fluxo (ASSUMPTION_REQUIRES_LOAD_TEST)

| Fluxo | Componentes | Alvo P95 |
|---|---|---|
| STATIC_RESPONSE | Classificação + template | < 100ms |
| REDIRECT | Classificação + template | < 100ms |
| API_ONLY | Classificação + ma-hr-orch + schema + allowlist + template | < 6s |
| RAG_ONLY | Classificação + embedding + S3 Vectors + geração | ASSUMPTION_REQUIRES_LOAD_TEST |

**Nota sobre 3275ms:** Esse valor é uma `single_observed_sample_ms` de GET /v1/beneficiaries. Não representa P50, P75, P95 ou P99. Não usar para derivar estatísticas.

---

## Controles de Segurança

- Sanitização determinística de PII APÓS extração de parâmetro, ANTES do modelo
- Allowlist de campos por endpoint (campos reais inventariados)
- Validação de schema na entrada e saída
- Empresa vem do contexto confiável (payload da API MARH) — não pode ser alterada pelo chat
- Autorização delegada à ma-hr-orch — agente não implementa RBAC próprio
- Sem cross-Region — dados permanecem em sa-east-1
- KMS para criptografia at-rest
- TLS 1.2+ para in-transit
- IAM least privilege

---

## Bloqueadores

| Bloqueador | Status |
|---|---|
| Modelo principal não confirmado (ACTIVE In-Region sa-east-1) | ABERTO — requer validação em conta |
| Bedrock Knowledge Bases em sa-east-1 não confirmada | ABERTO — requer evidência oficial |
| S3 Vectors em sa-east-1 — disponibilidade regional | CONFIRMED (documentação oficial AWS) |
| S3 Vectors — acesso, IAM e quotas na conta alvo | ABERTO — requer validação na conta |
| Endpoint de rastreamento por orderNumber não inventariado (INT-007) | ABERTO — DP-001 |
| Invocação da Lambda (SDK vs Function URL) — hospedagem da API MARH desconhecida | ABERTO — DP-001 |
| Conta AWS e permissões | ABERTO — DP-006 |

---

## Escopo Exato da POC

16 cenários de demonstração (ver `12_plano_poc.md`):
1. Resposta estática/política sem LLM
2–4. Perguntas informativas reais da KB
5. Consulta de colaborador por nome
6. Consulta de colaborador por CPF
7. Consulta de pedido por número
8. Consulta do último pedido
9. Consulta de pedidos por status
10. Múltiplos colaboradores — solicitação de escolha
11. Falta de empresa selecionada
12. Tentativa de trocar empresa pelo chat
13. Ausência de dados / permissão negada
14. API indisponível
15. Tentativa de obter PII
16. Prompt injection

---

## ADRs Reabertos

| ADR | Motivo |
|---|---|
| ADR-002 (Modelo) | Claude 3.5 Haiku removido — nova seleção pendente de validação |
| ADR-003 (RAG / Knowledge Bases) | KB gerenciada não confirmada em sa-east-1 — alternativa direta preferida |
| ADR-015 (Entrada) | InvokeFunction vs Function URL AWS_IAM — depende de hospedagem da API MARH |

---

*Decisão baseada em: discovery (2026-07-22), revisão corretiva (2026-07-23), restrição regional sa-east-1*
