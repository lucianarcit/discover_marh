# 05 — Fluxos por Intenção

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Classificação dos 27 Intents

| Tipo | Qtd | Exemplos | Fluxo |
|---|---|---|---|
| Consultivo (API) | 7 | Consulta de pedidos, saldo, colaboradores | API_ONLY ou HYBRID_RAG_API |
| Informativo (RAG) | 14 | Como cadastrar benefício, política de uso | RAG_ONLY |
| Fora de escopo | 6 | Piadas, previsão do tempo, assuntos pessoais | CLIENT_POLICY / STATIC_RESPONSE |

---

## 2. Fluxo CLIENT_POLICY / STATIC_RESPONSE

**Características:** Sem LLM, sem RAG, sem API.  
**Intents:** OUT-001 a OUT-006 (fora de escopo)

```
Entrada (mensagem do usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ├── Match com padrão fora de escopo?
    │       │
    │       ▼ SIM
    │   [Seleciona mensagem padronizada]
    │       │
    │       ▼
    │   Retorna resposta estática
    │
    └── NÃO → próximo fluxo
```

**Regras:**
- Resposta selecionada de um dicionário de 10 mensagens padronizadas
- Zero chamadas externas
- Latência alvo: < 50ms

**Mensagens padronizadas (exemplos):**
1. "Sou o assistente de RH da Alelo. Posso ajudar com informações sobre benefícios, pedidos e colaboradores."
2. "Essa pergunta está fora do meu escopo. Posso ajudar com dúvidas sobre benefícios Alelo."
3. "Não posso ajudar com esse assunto. Que tal perguntar sobre seus pedidos ou benefícios?"

---

## 3. Fluxo REDIRECT_TO_OFFICIAL_JOURNEY

**Características:** Sem LLM quando determinístico. Resposta direciona o usuário para a jornada oficial no app.

```
Entrada (mensagem do usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ├── Match com intent de redirecionamento?
    │       │
    │       ▼ SIM
    │   [Seleciona mensagem de redirecionamento + deep link]
    │       │
    │       ▼
    │   Retorna resposta com orientação
    │
    └── NÃO → próximo fluxo
```

**Regras:**
- Mensagens pré-definidas com links para jornadas existentes
- Não consome tokens LLM
- Latência alvo: < 50ms

---

## 4. Fluxo RAG_ONLY

**Características:** Uma chamada de retrieval + uma chamada de generation.  
**Intents:** INT-008 a INT-021 (informativos)

```
Entrada (mensagem do usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent informativo
[Bedrock Knowledge Bases — Retrieve]
    │
    ├── Chunks relevantes encontrados? (score > threshold)
    │       │
    │       ▼ SIM
    │   [Monta prompt com contexto dos chunks]
    │       │
    │       ▼
    │   [Bedrock Claude 3.5 Haiku — Generate]
    │       │
    │       ▼
    │   [Validação da resposta]
    │       │
    │       ▼
    │   Retorna resposta ao usuário
    │
    └── NÃO (score < threshold)
            │
            ▼
        [Resposta padronizada: "Não encontrei informação sobre isso"]
```

**Regras:**
- Máximo 5 chunks recuperados (top-k = 5)
- Score mínimo de relevância: 0.7
- Prompt inclui instrução para não inventar informação
- Se nenhum chunk relevante: resposta padronizada (sem LLM)
- Latência alvo: < 3s (P95)

**Composição do prompt:**
```
System: Você é o assistente de RH da Alelo. Responda APENAS com base no contexto fornecido.
Se não houver informação suficiente, diga que não pode responder.

Context: {chunks recuperados}

User: {pergunta original}
```

---

## 5. Fluxo API_ONLY

**Características:** Chamada ao ma-hr-orch + sanitização + LLM para formatação.  
**Intents:** INT-001 a INT-007 (consultivos)

```
Entrada (mensagem do usuário + contexto empresa/usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent consultivo
[Extrai parâmetros da mensagem]
    │
    ▼
[Valida parâmetros obrigatórios]
    │
    ├── Parâmetros insuficientes?
    │       │
    │       ▼ SIM → Fluxo REQUIRES_CLARIFICATION
    │
    └── Parâmetros OK
            │
            ▼
        [HTTP GET → ma-hr-orch]
            │
            ├── Sucesso (200)?
            │       │
            │       ▼
            │   [Sanitização de PII do response]
            │       │
            │       ▼
            │   [Bedrock Claude 3.5 Haiku — Formata resposta]
            │       │
            │       ▼
            │   [Validação final]
            │       │
            │       ▼
            │   Retorna resposta formatada
            │
            └── Erro?
                    │
                    ▼
                [Mapeia erro → mensagem padronizada]
                    │
                    ▼
                Retorna mensagem de erro amigável
```

**Regras:**
- Somente operações GET
- Timeout para ma-hr-orch: 10s
- Sanitização obrigatória antes do LLM (remove CPF, nomes completos, tokens)
- Contexto empresa/usuário vem da API MARH (não do modelo)
- Allowlist de campos por endpoint

**Sanitização (allowlist por tool):**
```python
ALLOWED_FIELDS = {
    "consulta_pedidos": ["order_id", "status", "created_at", "total_value"],
    "consulta_beneficios": ["benefit_name", "balance", "expiry_date"],
    "consulta_colaboradores": ["employee_count", "department", "status"],
}
```

---

## 6. Fluxo HYBRID_RAG_API

**Características:** RAG + API em paralelo quando não há dependência.  
**Intents:** Combinações específicas (ex: consulta de pedido + política de cancelamento)

```
Entrada (mensagem do usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent híbrido
[Análise de dependência]
    │
    ├── Sem dependência entre RAG e API?
    │       │
    │       ▼ SIM — Execução paralela
    │   ┌───────────────────────┐
    │   │  [RAG Retrieve]       │  [HTTP GET → ma-hr-orch]
    │   │       │               │       │
    │   │       ▼               │       ▼
    │   │  [Chunks]             │  [Dados API]
    │   └───────────────────────┘
    │               │
    │               ▼
    │       [Sanitização de PII]
    │               │
    │               ▼
    │       [Monta prompt combinado]
    │               │
    │               ▼
    │       [Bedrock Claude 3.5 Haiku — Generate]
    │               │
    │               ▼
    │       Retorna resposta unificada
    │
    └── Com dependência?
            │
            ▼ Execução sequencial (API primeiro, RAG depois)
```

**Regras:**
- Paralelismo via asyncio quando possível
- Se uma das fontes falha, responde com a outra + disclaimer
- Timeout total: 12s
- Latência alvo: < 5s (P95)

---

## 7. Fluxo REQUIRES_CLARIFICATION

**Características:** Solicita informação adicional ao usuário.

```
Entrada (mensagem do usuário)
    │
    ▼
[Classificador Determinístico]
    │
    ▼ Intent identificado mas parâmetros insuficientes
[Identifica parâmetros faltantes]
    │
    ▼
[Gera pergunta de clarificação]
    │
    ├── Pergunta determinística disponível?
    │       │
    │       ▼ SIM
    │   Retorna pergunta padronizada
    │
    └── NÃO (precisa LLM para formular)
            │
            ▼
        [Bedrock Claude 3.5 Haiku — Gera pergunta contextualizada]
            │
            ▼
        Retorna pergunta ao usuário
```

**Regras:**
- Máximo 1 pergunta de clarificação por turno
- Preferência por perguntas determinísticas (sem LLM)
- Se não houver resposta após clarificação, oferece alternativas

---

## 8. Budget de Latência por Fluxo

| Fluxo | Etapa | P50 | P95 | Timeout |
|---|---|---|---|---|
| **STATIC_RESPONSE** | Total | 20ms | 50ms | 1s |
| **REDIRECT** | Total | 20ms | 50ms | 1s |
| **RAG_ONLY** | Classificação | 5ms | 10ms | — |
| | KB Retrieve | 500ms | 1.5s | 5s |
| | LLM Generate | 800ms | 2s | 8s |
| | **Total** | **1.3s** | **3.5s** | **10s** |
| **API_ONLY** | Classificação | 5ms | 10ms | — |
| | ma-hr-orch GET | 1.5s | 3.3s | 10s |
| | Sanitização | 5ms | 15ms | — |
| | LLM Generate | 800ms | 2s | 8s |
| | **Total** | **2.3s** | **5.3s** | **15s** |
| **HYBRID_RAG_API** | Classificação | 5ms | 10ms | — |
| | Paralelo (RAG + API) | 1.5s | 3.3s | 10s |
| | Sanitização | 5ms | 15ms | — |
| | LLM Generate | 800ms | 2s | 8s |
| | **Total** | **2.3s** | **5.3s** | **15s** |
| **REQUIRES_CLARIFICATION** | Total | 50ms | 1.5s | 8s |

---

## 9. Diagrama de Decisão do Classificador

```
Mensagem do Usuário
    │
    ▼
[Normalização: lowercase, remove acentos, trim]
    │
    ▼
[Match contra padrões fora de escopo]
    ├── SIM → STATIC_RESPONSE
    │
    ▼
[Match contra padrões de redirecionamento]
    ├── SIM → REDIRECT_TO_OFFICIAL_JOURNEY
    │
    ▼
[Match contra padrões consultivos (requer dados)]
    ├── SIM → verifica parâmetros
    │       ├── Completos → API_ONLY ou HYBRID_RAG_API
    │       └── Incompletos → REQUIRES_CLARIFICATION
    │
    ▼
[Match contra padrões informativos]
    ├── SIM → RAG_ONLY
    │
    ▼
[Fallback] → STATIC_RESPONSE (mensagem genérica de escopo)
```

---

## 10. Mapeamento Intent → Fluxo

| Intent ID | Nome | Fluxo | Usa LLM | Usa RAG | Usa API |
|---|---|---|---|---|---|
| INT-001 | Consulta de pedidos | API_ONLY | Sim (format) | Não | Sim |
| INT-002 | Consulta de saldo | API_ONLY | Sim (format) | Não | Sim |
| INT-003 | Consulta de colaboradores | API_ONLY | Sim (format) | Não | Sim |
| INT-004 | Status de pedido | API_ONLY | Sim (format) | Não | Sim |
| INT-005 | Consulta de benefícios | API_ONLY | Sim (format) | Não | Sim |
| INT-006 | Consulta de produtos | API_ONLY | Sim (format) | Não | Sim |
| INT-007 | Dias para crédito | API_ONLY | Sim (format) | Não | Sim |
| INT-008 | Como cadastrar benefício | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-009 | Política de uso | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-010 | Regras de recarga | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-011 | Prazos e datas | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-012 | Tipos de cartão | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-013 | Rede credenciada | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-014 | Legislação trabalhista | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-015 | Processos internos | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-016 | FAQ geral | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-017 | Tutoriais do portal | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-018 | Configurações de conta | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-019 | Relatórios disponíveis | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-020 | Integrações | RAG_ONLY | Sim (gen) | Sim | Não |
| INT-021 | Novidades/Atualizações | RAG_ONLY | Sim (gen) | Sim | Não |
| OUT-001 | Assunto pessoal | STATIC_RESPONSE | Não | Não | Não |
| OUT-002 | Piada/Entretenimento | STATIC_RESPONSE | Não | Não | Não |
| OUT-003 | Outro produto/empresa | STATIC_RESPONSE | Não | Não | Não |
| OUT-004 | Operação de escrita | STATIC_RESPONSE | Não | Não | Não |
| OUT-005 | Informação sensível | STATIC_RESPONSE | Não | Não | Não |
| OUT-006 | Ofensivo/Inadequado | STATIC_RESPONSE | Não | Não | Não |
