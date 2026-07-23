# 05 — Fluxos por Intenção

**Projeto:** MARH Consultive Agent POC
**Data:** 2026-07-23 (revisão corretiva)
**Região AWS:** sa-east-1
**Fonte:** `discover3/artifacts/intents_catalog.json`, `discover3/artifacts/response_source_matrix.json`

---

## 1. Catálogo Real de Intenções

O agente possui **27 intenções** catalogadas, derivadas exclusivamente de `intents_catalog.json`.

| Grupo | Qtd | Estratégia de resposta |
|---|---|---|
| A — Consultivo (dados em tempo real) | 7 | API_ONLY ou REQUIRES_CLARIFICATION ou NEEDS_CLIENT_VALIDATION |
| B — Informativo MARH | 14 | RAG_ONLY ou CLIENT_POLICY_RESPONSE |
| C — Fora do Escopo | 6 | REDIRECT_TO_OFFICIAL_JOURNEY |

**Intenções não existentes no catálogo — NÃO mapear:**
- Consulta de saldo, legislação trabalhista, novidades, integrações, política de uso, tipos de cartão, regras de recarga, previsão do tempo, FAQ geral, rede credenciada, relatórios disponíveis.

---

## 2. Mapeamento Completo: Intent → Fluxo

| ID | Nome Real | Grupo | Estratégia | Entrada | Fonte | Usa LLM | Usa RAG | Usa API | Cobertura | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| INT-001 | Consultar colaborador por nome | A | API_ONLY | nome (texto) | ma-hr-orch CAP-001 | ❌ | ❌ | ✅ | PARTIALLY_COVERED | CONFIRMED |
| INT-002 | Consultar colaborador por CPF | A | API_ONLY | CPF (transitório) | ma-hr-orch CAP-001 | ❌ | ❌ | ✅ | PARTIALLY_COVERED | CONFIRMED |
| INT-003 | Consultar pedido por número | A | API_ONLY | orderNumber (texto) | ma-hr-orch CAP-003 + CAP-004 | ❌ | ❌ | ✅ | PARTIALLY_COVERED | CONFIRMED |
| INT-004 | Consultar último pedido | A | API_ONLY | — | ma-hr-orch CAP-002 | ❌ | ❌ | ✅ | PARTIALLY_COVERED | CONFIRMED |
| INT-005 | Consultar pedidos por status | A | API_ONLY | status (texto) | ma-hr-orch CAP-002 | ❌ | ❌ | ✅ | PARTIALLY_COVERED | CONFIRMED |
| INT-006 | Rastrear cartão por CPF | A | REQUIRES_CLARIFICATION | CPF (transitório) | fallback → ERR-010 | ❌ | ❌ | ❌ | NOT_VALIDATED | AMBIGUOUS |
| INT-007 | Rastrear cartão por número do pedido | A | NEEDS_CLIENT_VALIDATION | orderNumber | endpoint não inventariado | ❌ | ❌ | ❌ | NOT_VALIDATED | CONFIRMED* |
| INT-008 | O que posso fazer? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-009 | Quais informações posso consultar? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-010 | Como faço para fazer um pedido? | B | RAG_ONLY | — | marh_feature_knowledge.md | ✅ | ✅ | ❌ | COVERED | CONFIRMED |
| INT-011 | Como faço para consultar um pedido? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-012 | Como faço para consultar um colaborador? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-013 | Consigo rastrear cartões? | B | RAG_ONLY (capacidade) | — | marh_feature_knowledge.md | ✅ | ✅ | ❌ | COVERED | CONFIRMED |
| INT-014 | Você consegue cancelar pedido? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md (FORA-002) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-015 | Você consegue alterar dados de um colaborador? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md (FORA-004) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-016 | Você consulta dados de qualquer empresa? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md (SEG-002) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-017 | Preciso selecionar uma empresa para usar o agente? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-018 | O agente substitui o portal web? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-019 | O que é o MARH? | B | RAG_ONLY | — | marh_feature_knowledge.md | ✅ | ✅ | ❌ | PARTIALLY_COVERED | CONFIRMED |
| INT-020 | O que é o Espaço RH? | B | RAG_ONLY | — | marh_feature_knowledge.md | ✅ | ✅ | ❌ | PARTIALLY_COVERED | CONFIRMED |
| INT-021 | Quais tipos de pergunta posso fazer? | B | CLIENT_POLICY_RESPONSE | — | agent_policy.md | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-022 | Cancela o pedido | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-002) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-023 | Altera o endereço do colaborador | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-006) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-024 | Cria um novo pedido | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-001) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-025 | Remove esse colaborador | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-005) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-026 | Paga o pedido | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-010) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |
| INT-027 | Emite um novo cartão | C | REDIRECT_TO_OFFICIAL_JOURNEY | — | agent_policy.md (FORA-007/008) | ❌ | ❌ | ❌ | COVERED | CONFIRMED |

*INT-007: STATUS=CONFIRMED no catálogo significa que o comportamento esperado está documentado, mas o endpoint não está inventariado. Manter como NEEDS_CLIENT_VALIDATION enquanto o contrato não for validado.

---

## 3. Fluxo CLIENT_POLICY_RESPONSE / STATIC_RESPONSE

**Intenções:** INT-008, INT-009, INT-011, INT-012, INT-014 a INT-018, INT-021

**Características:**
- Zero RAG
- Zero chamada de API
- Zero LLM
- Resposta determinística versionada

```
Mensagem do usuário
    │
    ▼
[Classificador Determinístico]
    │
    ├── Match CLIENT_POLICY?
    │       │
    │       ▼ SIM
    │   [Seleciona resposta estática por intent]
    │       │
    │       ▼
    │   Retorna resposta ao usuário
    │
    └── NÃO → próximo fluxo
```

**Fonte das respostas:** `agent_policy.md` — seções de capacidades, escopo, empresa, limitações.

---

## 4. Fluxo REDIRECT_TO_OFFICIAL_JOURNEY

**Intenções:** INT-022 a INT-027

**Características:**
- Zero LLM (mensagem estática definida pelo cliente)
- Zero API transacional
- Resposta: "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH."
- Não inventar deeplink — incluir [list_navigation] somente se DP-003 (AMB-002) for resolvido

```
Mensagem do usuário
    │
    ▼
[Classificador Determinístico]
    │
    ├── Match REDIRECT?
    │       │
    │       ▼ SIM
    │   [Seleciona mensagem padronizada por intent]
    │       │
    │       ▼
    │   Retorna orientação para Espaço RH
    │
    └── NÃO → próximo fluxo
```

---

## 5. Fluxo API_ONLY

**Intenções:** INT-001, INT-002, INT-003, INT-004, INT-005

**Características:**
- Zero LLM — template determinístico
- Sanitização obrigatória antes de construir qualquer resposta
- Allowlist de campos (reais, inventariados)
- Erro específico por código HTTP (ERR-001 a ERR-007)

```
Mensagem (+ contexto empresa/usuário confiável)
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent consultivo identificado
[Extração determinística de parâmetros]
    │
    ├── Empresa ausente → ERR-001 (sem API, sem LLM)
    │
    ├── Parâmetros insuficientes?
    │       │
    │       ▼ SIM → REQUIRES_CLARIFICATION (mensagem padronizada)
    │
    └── Parâmetros OK
            │
            ▼
        [Validação de schema do parâmetro]
            │
            ▼
        [HTTP GET → ma-hr-orch]
            │
            ├── 200 OK
            │       │
            │       ▼
            │   [Validação de schema da resposta]
            │       │
            │       ▼
            │   [Allowlist de campos]
            │       │
            │       ▼
            │   [Sanitização complementar]
            │       │
            │       ▼
            │   [Template determinístico]
            │       │
            │       ▼
            │   [Validação final da resposta]
            │       │
            │       ▼
            │   Retorna ao usuário
            │
            ├── 403 (permissão) → ERR-005 (sem LLM)
            ├── 403 (FNP/prova de vida) → ERR-006 (sem LLM)
            ├── 404 → ERR-002 (colabs) / ERR-003 (pedido) / sem LLM
            ├── 422 → ERR-001 (empresa inválida) / sem LLM
            ├── 429 → retry 1x c/ jitter → ERR-007 (sem LLM)
            ├── 5xx transitório → retry 1x c/ jitter → ERR-007 (sem LLM)
            └── Timeout → ERR-007 (sem LLM)
```

**LLM em API_ONLY:** Não usar LLM para formatar colaborador encontrado, múltiplos colaboradores, pedido por número, último pedido, pedidos por status, erros ou ausência de dados. Toda formatação via template.

**Allowlist de campos reais (por endpoint):**

| Endpoint | Campos permitidos ao usuário |
|---|---|
| GET /v1/beneficiaries | name, placeName, subtype, isHomeDelivery, products |
| GET /v1/orders/{orderNumber} | status (traduzido), orderDate, totalOrder, productInfo.productName, paymentMethod, steps |
| GET /v1/orders | status (traduzido), orderDate, totalOrder, productInfo.productName |
| GET /v1/orders/{orderNumber}/beneficiaries | total (contagem), name (lista) |

**Campos sempre removidos:**
- `documentNumber` (CPF), `email`, `phoneNumber`, `motherName`, `beneficiaryId`, `address`
- `billingDocumentNumber`, `contractNumber`, `idLegalPersonBilling`
- Qualquer campo com conteúdo base64

**Fluxo para múltiplos colaboradores (INT-001):**
- Se `total > 1`: apresentar lista de nomes e solicitar escolha (template determinístico)
- Não enviar lista ao LLM

---

## 6. Fluxo REQUIRES_CLARIFICATION

**Intenções:** INT-006 (fallback definido)

**Comportamento para INT-006:**
- Mensagem recebida com CPF para rastreamento
- Resposta determinística: ERR-010
- "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento."
- Zero LLM, zero API

---

## 7. Fluxo NEEDS_CLIENT_VALIDATION

**Intenções:** INT-007

- Endpoint de rastreamento por orderNumber não inventariado (LAC-001, DP-001)
- Na POC: responder com ERR-007 ("Não consegui consultar essa informação agora. Tente novamente em alguns instantes.")
- **Não** classificar como API_ONLY enquanto o contrato não for validado com o time da ma-hr-orch
- Não inventar campos de resposta

---

## 8. Fluxo RAG_ONLY

**Intenções:** INT-010, INT-013, INT-019, INT-020

**Características:**
- Uma geração de embedding
- Uma consulta vetorial
- Uma chamada de geração
- Nenhum grader LLM adicional na POC
- Fallback sem geração quando não houver evidência suficiente

```
Mensagem do usuário
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent informativo
[Gera embedding da query — modelo In-Region]
    │
    ▼
[Consulta S3 Vectors em sa-east-1]
    │
    ├── Chunks relevantes? (score ≥ threshold — ASSUMPTION_REQUIRES_EVALUATION)
    │       │
    │       ▼ SIM
    │   [Monta contexto com chunks (limite de tokens)]
    │       │
    │       ▼
    │   [Modelo de geração In-Region — uma chamada]
    │       │
    │       ▼
    │   [Validação final (sem PII)]
    │       │
    │       ▼
    │   Retorna resposta
    │
    └── NÃO (score < threshold)
            │
            ▼
        ERR-008: "Ainda não tenho essa informação disponível sobre o MARH."
        (sem LLM)
```

**Fonte da KB:** `discover3/knowledge/marh_feature_knowledge.md` — indexado por seções do markdown.
**Não indexar:** `discover3/agent_policy.md` — fica no código determinístico.

**Parâmetros (ASSUMPTION_REQUIRES_EVALUATION):**
- top-k: valor inicial pequeno (ajustar após avaliação)
- threshold: parâmetro de configuração (não hardcoded)
- Limite de tokens de contexto: a definir

---

## 9. Budget de Latência por Fluxo

| Fluxo | Componentes incluídos | Alvo P95 | Timeout Global |
|---|---|---|---|
| STATIC_RESPONSE / CLIENT_POLICY | Classificação + template | < 100ms | 1s |
| REDIRECT | Classificação + template | < 100ms | 1s |
| API_ONLY (sem LLM) | Classificação + ma-hr-orch + schema + allowlist + template | < 6s | 15s |
| RAG_ONLY | Classificação + embedding + S3 Vectors + geração | ASSUMPTION_REQUIRES_LOAD_TEST | 12s |
| REQUIRES_CLARIFICATION | Template determinístico | < 100ms | 1s |

**Budget API_ONLY coerente:**

| Etapa | Orçamento |
|---|---|
| Classificação + parse | ≤ 20ms |
| ma-hr-orch GET | ≤ 10s (timeout) |
| Schema + allowlist + sanitização | ≤ 20ms |
| Template | ≤ 10ms |
| Total | ≤ 10.1s (dentro do timeout global de 15s) |

**Nota:** 3275ms é uma `single_observed_sample_ms` de `/v1/beneficiaries`. Não representa P50/P95/P99.

---

## 10. Diagrama de Decisão do Classificador

```
Mensagem do usuário
    │
    ▼
[Normalização: lowercase, sem acentos, trim]
    │
    ▼
[Empresa presente no contexto?]
    ├── NÃO → ERR-001 (sem nenhum fluxo)
    │
    ▼ SIM
[Match contra padrões fora de escopo (Grupo C)]
    ├── SIM → REDIRECT_TO_OFFICIAL_JOURNEY
    │
    ▼
[Match contra padrões CLIENT_POLICY (Grupo B — política)]
    ├── SIM → CLIENT_POLICY_RESPONSE
    │
    ▼
[Match contra padrões consultivos (Grupo A)]
    ├── SIM
    │   ├── Parâmetros completos? → API_ONLY (template determinístico)
    │   ├── Parâmetros incompletos? → REQUIRES_CLARIFICATION
    │   └── Endpoint não validado (INT-007)? → NEEDS_CLIENT_VALIDATION
    │
    ▼
[Match contra padrões informativos RAG (Grupo B — KB)]
    ├── SIM → RAG_ONLY
    │
    ▼
[Fallback] → CLIENT_POLICY_RESPONSE (mensagem de escopo genérica)
```

---

## 11. Mensagens de Erro — Catálogo Obrigatório

Usar **exclusivamente** as mensagens ERR-001 a ERR-010 definidas no Discovery.
Não criar mensagens alternativas com textos diferentes.

| ID | Mensagem | Quando usar |
|---|---|---|
| ERR-001 | "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente." | Empresa ausente / 422 |
| ERR-002 | "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." | 404 colaborador |
| ERR-003 | "Não encontrei o pedido informado para a empresa selecionada." | 404 pedido |
| ERR-004 | "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." | Status não reconhecido |
| ERR-005 | "Você não tem permissão para consultar informações dessa empresa no Espaço RH." | 403 permissão |
| ERR-006 | "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente." | 403 FNP/prova de vida |
| ERR-007 | "Não consegui consultar essa informação agora. Tente novamente em alguns instantes." | 5xx, timeout, indisponível |
| ERR-008 | "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões." | KB sem resultado |
| ERR-009 | "Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela." | [list_navigation] falhou |
| ERR-010 | "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." | INT-006 fallback |

---

## 12. Política de Retry por Código HTTP

| Código | Retry | Ação |
|---|---|---|
| 400 | ❌ NUNCA | ERR-001 ou mapeamento correspondente |
| 401 | ❌ NUNCA | Log error + alerta |
| 403 | ❌ NUNCA | ERR-005 ou ERR-006 |
| 404 | ❌ NUNCA | ERR-002 ou ERR-003 |
| 422 | ❌ NUNCA | ERR-001 |
| 429 | ✅ Máximo 1 retry com jitter | Somente se idempotente e dentro do budget |
| 500 | ✅ Máximo 1 retry com jitter | Somente se idempotente e dentro do budget |
| 502/503/504 | ✅ Máximo 1 retry com jitter | Somente se idempotente e dentro do budget |
| Timeout | ✅ Máximo 1 retry | Somente se houver orçamento de latência restante |
