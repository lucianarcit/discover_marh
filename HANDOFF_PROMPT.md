# HANDOFF — Agente Consultivo MARH · Continuação para Versão AWS

**Data de geração:** 2026-07-23  
**Repositório:** `discover_marh` (branch `main`)  
**Projeto local:** `C:\proj\discover_alelo\poc_marh_agent`  
**Status atual:** POC funcional, backend mock local + frontend navegável, 107 testes passando.

---

## 1. CONTEXTO DO PROJETO

### O que é

O **MARH Agent** (Meu Alelo RH) é um assistente consultivo de IA integrado ao app Meu Alelo, destinado a **interlocutores de RH**. Ele responde perguntas sobre colaboradores, pedidos e benefícios Alelo sem substituir o portal web — é somente consultivo.

O agente está hospedado dentro do **Espaço RH**, área do app dedicada a RH. Toda interação pressupõe que o usuário está autenticado com uma empresa selecionada.

### O que foi construído até agora

Foi construída uma **POC completa e funcional** que valida:

- classificação determinística de 27 intenções (sem LLM);
- orquestração independente de framework (FastAPI + Lambda adapter);
- segurança em camadas (contexto confiável, allowlists, sanitização, route catalog);
- sistema visual de cards para as respostas (presentation contract);
- frontend navegável com mock local e toggle para backend real;
- 107 testes automatizados (unit + integração).

---

## 2. ESTADO ATUAL DETALHADO

### 2.1 Estrutura de arquivos

```
poc_marh_agent/
├── backend/
│   ├── pyproject.toml                          # FastAPI + uvicorn + pydantic + pytest
│   ├── .env.example
│   ├── fixtures/
│   │   ├── orders.json                         # 5 pedidos sintéticos (PAID/PENDING/etc.)
│   │   └── collaborators.json                  # 3 colaboradores sintéticos
│   └── src/marh_agent/
│       ├── config.py                           # Env, Mode, WEBVIEW_BASE_URLS
│       ├── api/
│       │   ├── local_api.py                    # FastAPI (só este arquivo depende do framework)
│       │   └── lambda_handler.py               # AWS Lambda adapter (mesmo Orchestrator)
│       ├── application/
│       │   ├── orchestrator.py                 # Pipeline principal (framework-agnóstico)
│       │   └── router.py                       # Dispatch intent → handler → response
│       ├── classification/
│       │   ├── intent_classifier.py            # 27 intenções, regex puro, sem LLM
│       │   ├── entity_extractor.py             # Extrai CPF, número de pedido, nome
│       │   └── status_mapper.py                # Catálogo de status (aliases → api_status)
│       ├── clients/
│       │   ├── ma_hr_orch.py                   # ABC: interface do backend Alelo real
│       │   ├── mock_ma_hr_orch.py              # Implementação mock (lê fixtures JSON)
│       │   ├── knowledge_client.py             # ABC: interface para RAG/Knowledge Base
│       │   └── mock_knowledge_client.py        # 14 tópicos hardcoded (RAG simulado)
│       ├── domain/
│       │   ├── requests.py                     # ChatRequest (Pydantic)
│       │   ├── responses.py                    # ChatResponse + Presentation (Pydantic)
│       │   └── errors.py                       # ERR-001 a ERR-010
│       ├── navigation/
│       │   └── builder.py                      # Catálogo fechado de 7 rotas + deeplink
│       ├── security/
│       │   ├── allowlists.py                   # Filtro de campos por domínio
│       │   ├── trusted_context.py              # Valida company/user/session
│       │   └── sanitization.py                 # Máscara CPF/CNPJ no texto
│       └── templates/
│           ├── collaborators.py                # Templates text para colaboradores
│           ├── orders.py                       # Templates text para pedidos
│           ├── policies.py                     # Respostas estáticas e RAG fallback
│           └── presentation_builder.py         # Construtores do campo presentation
└── frontend/
    ├── index.html                              # Home do Espaço RH (portal de entrada)
    ├── chat-alelo.html                         # ChatAlelo (interface de conversa)
    ├── fixtures/
    │   ├── orders.json
    │   └── collaborators.json
    └── assets/
        ├── css/
        │   ├── common.css                      # Design tokens, reset, header, toast
        │   ├── home.css
        │   ├── chat.css                        # Layout do chat + envelope responsivo
        │   └── agent-response.css              # Cards de presentation (todos os variants)
        └── js/
            ├── config.js                       # CONFIG freeze (USE_MOCK_AGENT, URLs)
            ├── mock-agent.js                   # MockAgent in-browser com presentation
            ├── api-client.js                   # HTTP client (fetch + AbortController)
            ├── message-renderer.js             # Renderer seguro (só DOM APIs)
            └── chat.js                         # Controle de UI (loading, scroll, nav)
```

### 2.2 Contrato de API

#### Request

```json
POST /chat
{
  "company_id": "string (obrigatório, da sessão)",
  "user_id":    "string (obrigatório, da sessão)",
  "session_id": "string (obrigatório, da sessão)",
  "message":    "string (1–2000 chars)",
  "environment": "HML | PRD",
  "correlation_id": "string | null (gerado se ausente)"
}
```

#### Response

```json
{
  "correlation_id": "uuid",
  "intent_id":  "INT-001 | ... | INT-027 | COMPANY_SWITCH | null",
  "flow":       "API_ONLY | RAG_ONLY | STATIC_RESPONSE | REDIRECT_TO_OFFICIAL_JOURNEY | REQUIRES_CLARIFICATION | ERROR",
  "message":    "string (sempre presente, fallback legível)",
  "presentation": {                          // OPCIONAL — ausente quando não há card
    "variant":      "capabilities_list | collaborator_summary | order_summary | order_list | knowledge_answer | informational_notice | warning_notice | transactional_redirect | clarification | error_notice",
    "title":        "string",
    "subtitle":     "string | null",
    "icon":         "string | null",
    "tone":         "neutral | positive | warning | negative | informative",
    "status_label": "string | null",
    "fields": [{ "label": "string", "value": "string", "emphasis": false }],
    "items":  [{ "title": "string", "subtitle": null, "value": null, "badge": null, "tone": null }]
  },
  "navigation": {                            // OPCIONAL
    "type":       "list_navigation",
    "route_id":   "ROUTE-003 | ROUTE-012 | ROUTE-014 | ROUTE-015 | ROUTE-017 | ROUTE-024 | ROUTE-025",
    "label":      "string",
    "deeplink":   "meualelo://app/webview?url=...&isModal=false&showNavbar=false&authRequired=true",
    "webview_url": "https://meualelo-webviews-{hml|prd}.../..."
  },
  "error_code": "ERR-001 | ... | ERR-010 | null",
  "metadata": {
    "mode": "MOCK_LOCAL",
    "data_classification": "SYNTHETIC_TEST_DATA",
    "knowledge_source": "...",          // presente em RAG_ONLY
    "backend_tracking_api_status": "..." // presente em INT-007
  }
}
```

### 2.3 Mapa de intenções

| Grupo | Intenções | Flow | Backend |
|-------|-----------|------|---------|
| **API — Colaboradores** | INT-001 (por nome), INT-002 (por CPF) | API_ONLY | ma-hr-orch |
| **API — Pedidos** | INT-003 (por número), INT-004 (último), INT-005 (por status) | API_ONLY | ma-hr-orch |
| **API — Rastreamento** | INT-006 (CPF→clarification), INT-007 (pedido→warning) | REQUIRES_CLARIFICATION / API_ONLY | — |
| **RAG — Informativas** | INT-008 a INT-021 (14 intenções) | RAG_ONLY | knowledge_client |
| **Transacionais bloqueadas** | INT-022 a INT-027 (cancelar, alterar, criar, etc.) | REDIRECT_TO_OFFICIAL_JOURNEY | — |
| **Troca de empresa** | COMPANY_SWITCH | STATIC_RESPONSE | — |
| **Fora do escopo** | — | STATIC_RESPONSE | — |

### 2.4 Segurança implementada

| Camada | Onde | O que faz |
|--------|------|-----------|
| Contexto confiável | `trusted_context.py` | Rejeita requests sem company/user/session |
| Allowlist de campos | `allowlists.py` | Remove campos não autorizados do response (CPF, email, etc.) |
| Sanitização de texto | `sanitization.py` | Máscara CPF/CNPJ em qualquer texto de resposta |
| Route catalog fechado | `navigation/builder.py` | Só 7 rotas permitidas; orderNumber validado com `^\d{1,10}$`; path traversal bloqueado |
| Frontend host allowlist | `api-client.js` | Só hosts autorizados em `ALLOWED_WEBVIEW_HOSTS` |
| Frontend suffix guard | `api-client.js` | Sufixo de URL validado com `/^\d{1,20}$/` |
| DOM-only rendering | `message-renderer.js` | Nenhum dado do backend passa por innerHTML/eval |

**Gap documentado e não resolvido:** o campo `steps` do pedido (sub-array) passa pelo `filter_order` sem sub-filtragem de campos. Marcado como "risco ALTO" no test #36 de `test_orchestrator.py`. Deve ser resolvido antes de produção.

### 2.5 Testes existentes (107 total — todos passando)

| Arquivo | Quantidade | Cobre |
|---------|-----------|-------|
| `tests/unit/test_orchestrator.py` | 68 | Todos 27 intents, allowlists, deeplinks, status mapper, MockKnowledge |
| `tests/unit/test_presentation.py` | 22 | Todos variants de presentation, CPF ausente, enums, campos vazios |
| `tests/integration/test_api.py` | 17 | HTTP flows, CORS, contrato completo, idOrder fora da resposta |

**Comando para rodar:**
```bash
cd poc_marh_agent/backend
.venv/Scripts/pytest -v          # Windows
# ou
python -m pytest -v              # com venv ativo
```

### 2.6 Frontend

- **Toggle de modo:** `CONFIG.USE_MOCK_AGENT = false` → chama backend real em `localhost:8000`; `true` → MockAgent in-browser sem backend.
- **Para rodar o frontend:** servir `poc_marh_agent/frontend/` em `localhost:8080` (qualquer servidor estático). O backend espera CORS de `localhost:8080`.
- **Para rodar o backend:** `cd poc_marh_agent/backend && uvicorn marh_agent.api.local_api:app --reload --port 8000`

### 2.7 O que o classificador NÃO faz (deliberadamente)

O classificador é regex puro. Ele **não usa LLM** e não entende linguagem natural. Isso é uma decisão de design para a POC — permite auditoria determinística e custo zero. A evolução para LLM está no plano da versão AWS.

---

## 3. O QUE PRECISA SER CONSTRUÍDO

Esta seção descreve o trabalho restante para a **versão AWS de produção**.

### 3.1 Visão geral da arquitetura target

```
[App Meu Alelo]
    │  HTTPS + JWT
    ▼
[API Gateway]
    │
    ▼
[Lambda — marh-agent]
    ├── [Amazon Bedrock — classificação LLM] (Claude 3 Haiku / Titan)
    ├── [Amazon Bedrock Knowledge Bases — RAG] (S3 + embeddings)
    └── [ma-hr-orch — API real Alelo] (VPC / PrivateLink)
```

### 3.2 Componentes a implementar

#### A. Classificador com LLM (substitui regex)

**O que fazer:**
- Implementar `BedrockClassifier` que usa Claude 3 Haiku (ou Titan Text) via `boto3` para classificar a intenção do usuário.
- O classificador deve retornar o mesmo `ClassificationResult` (intent_id, flow, entities) que o classificador regex retorna hoje.
- Manter o regex como fallback ou como primeiro filtro rápido antes do LLM (abordagem híbrida).
- O extrator de entidades (CPF, número de pedido, nome) pode continuar regex — LLM só classifica intenção.

**Interface a respeitar:**
```python
# classification/intent_classifier.py
def classify(message: str) -> ClassificationResult:
    ...
```

**Arquivo a criar:** `classification/bedrock_classifier.py`

---

#### B. Knowledge Base real (substitui MockKnowledgeClient)

**O que fazer:**
- Implementar `BedrockKnowledgeClient` que usa **Amazon Bedrock Knowledge Bases** via `boto3` (API `retrieve` ou `retrieve_and_generate`).
- Respeitar a interface `KnowledgeClient.query(topic: str) -> dict`.
- O retorno deve ser `{"found": bool, "content": str, "source_section": str, "data_classification": str}`.
- Configurar a Knowledge Base com os documentos de política Alelo (MARH, Espaço RH, FAQ).

**Interface existente:**
```python
# clients/knowledge_client.py
class KnowledgeClient(ABC):
    @abstractmethod
    def query(self, topic: str) -> dict: ...
```

**Arquivo a criar:** `clients/bedrock_knowledge_client.py`

---

#### C. Cliente real ma-hr-orch (substitui MockMaHrOrchClient)

**O que fazer:**
- Implementar `HttpMaHrOrchClient` que faz chamadas HTTP reais para a API `ma-hr-orch` da Alelo.
- Respeitar a interface `MaHrOrchClient` com os 5 métodos:
  - `search_collaborator_by_name(company_id, name) -> dict`
  - `search_collaborator_by_document(company_id, cpf) -> dict`
  - `get_order(company_id, order_number) -> dict`
  - `list_orders(company_id) -> dict`
  - `list_orders_by_status(company_id, status) -> dict`
- Mapear erros HTTP para as exceções que o `router.py` já trata:
  - 403 → `PermissionError`
  - 404 → `LookupError`
  - 408/429/503 → `TimeoutError`
  - outros → `RuntimeError`
- Adicionar retry com backoff exponencial (3 tentativas, jitter).
- O token de autenticação deve vir do evento Lambda (não do request do usuário).

**Interface existente:**
```python
# clients/ma_hr_orch.py
class MaHrOrchClient(ABC): ...
```

**Arquivo a criar:** `clients/http_ma_hr_orch.py`

---

#### D. Lambda handler de produção

**O que fazer:**
- Atualizar `api/lambda_handler.py` para usar os clientes reais em vez dos mocks.
- Ler configurações de variáveis de ambiente (não hardcoded):
  - `MA_HR_ORCH_BASE_URL`
  - `BEDROCK_KNOWLEDGE_BASE_ID`
  - `BEDROCK_REGION`
  - `BEDROCK_MODEL_ID`
  - `ENVIRONMENT` (HML | PRD)
- Implementar cold-start cache: instanciar clientes uma vez fora do handler.
- Adicionar X-Ray tracing.
- Manter o Lambda handler atual como fallback de mock para testes locais.

---

#### E. Infraestrutura (IaC)

**O que criar:**
- **AWS CDK** (Python) ou **Terraform** para provisionar:
  - Lambda function (Python 3.12, 512 MB, 30s timeout)
  - API Gateway (REST ou HTTP API) com throttling
  - IAM roles e policies (least privilege)
  - Secrets Manager para credenciais ma-hr-orch
  - Bedrock Knowledge Base + S3 bucket para documentos
  - CloudWatch Log Groups + Alarms
  - VPC/PrivateLink se ma-hr-orch estiver em VPC privada

**Diretório a criar:** `infra/` na raiz do repositório

---

#### F. CI/CD

**O que criar:**
- Pipeline GitHub Actions ou AWS CodePipeline:
  1. `test` — roda `pytest` (107+ testes)
  2. `lint` — ruff/flake8
  3. `build` — empacota Lambda (dependências + src)
  4. `deploy-hml` — deploy automático em HML no push para `main`
  5. `deploy-prd` — deploy manual (aprovação) em PRD

---

#### G. Autenticação real

**O que fazer:**
- O frontend atual usa IDs sintéticos (`empresa-sintetica-001`, etc.).
- Na versão real, `company_id`, `user_id` e `session_id` devem vir da **sessão autenticada do app Meu Alelo** — nunca do input do usuário.
- O API Gateway deve validar o JWT/token do app antes de invocar o Lambda.
- O Lambda deve extrair os IDs do contexto do authorizer, não do body.
- Atualizar `ChatRequest` para marcar esses campos como vindos do contexto, não do request body.

---

#### H. Documentação técnica a criar

Os seguintes documentos precisam ser produzidos:

1. **`docs/architecture.md`** — diagrama e descrição da arquitetura AWS; fluxo de dados de ponta a ponta; decisões de design (por que regex primeiro, por que Bedrock, por que Lambda).

2. **`docs/intent-catalog.md`** — tabela completa dos 27 intents com: ID, descrição, exemplos de input, flow, entidades extraídas, response esperado, navigation gerada.

3. **`docs/security.md`** — modelo de ameaça; camadas de defesa implementadas; gap do campo `steps`; recomendações para produção; política de dados (o que nunca deve aparecer numa resposta).

4. **`docs/api-contract.md`** — especificação completa de request/response com exemplos para cada intent; todos os error codes; campo presentation com todos os variants.

5. **`docs/deployment.md`** — pré-requisitos; variáveis de ambiente; passo a passo de deploy HML e PRD; rollback.

6. **`docs/testing-strategy.md`** — pirâmide de testes atual; o que cada suite cobre; como adicionar testes para novos intents; testes de contrato com ma-hr-orch.

7. **`docs/runbook.md`** — como investigar um erro em produção; mapa de error codes para causa provável; como adicionar um novo intent; como atualizar a Knowledge Base.

8. **`docs/poc-to-production.md`** — diff entre POC e produção; decisões que precisam ser tomadas; riscos conhecidos; o que NÃO mudar (contratos, deeplinks, route catalog).

---

## 4. PLANO DE EXECUÇÃO SUGERIDO

### Fase 1 — Fundação AWS (2–3 semanas)

**Objetivo:** Lambda funcional em HML com mocks, sem LLM ainda.

1. Criar estrutura `infra/` com CDK/Terraform básico (Lambda + API Gateway).
2. Atualizar `lambda_handler.py` para ler config de env vars.
3. Configurar CI/CD básico (test → build → deploy-hml).
4. Validar que os 107 testes passam no pipeline.
5. Criar `docs/deployment.md` e `docs/architecture.md` iniciais.

**Critério de aceite:** Lambda em HML respondendo às mesmas 11 mensagens de validação manual que a POC responde, com mocks.

---

### Fase 2 — Integração ma-hr-orch (2–3 semanas)

**Objetivo:** Dados reais de colaboradores e pedidos.

1. Implementar `HttpMaHrOrchClient` com retry e mapeamento de erros.
2. Criar testes de contrato contra o ambiente de sandbox do ma-hr-orch.
3. Atualizar allowlists se o schema real diferir do mock.
4. Revisar campo `steps` — implementar sub-filtragem (gap de segurança).
5. Criar `docs/security.md`.

**Critério de aceite:** INT-001 a INT-005 funcionando com dados reais em HML; nenhum campo não autorizado na resposta.

---

### Fase 3 — Knowledge Base e RAG (2–3 semanas)

**Objetivo:** Respostas informativas vindas de documentos reais Alelo.

1. Definir e carregar documentos na S3 (políticas MARH, FAQ Espaço RH).
2. Criar Bedrock Knowledge Base com chunking e embedding.
3. Implementar `BedrockKnowledgeClient`.
4. Ajustar o router para passar o texto da pergunta (não só o tópico) ao RAG.
5. Criar testes de qualidade de resposta (não apenas "found=True").
6. Criar `docs/testing-strategy.md`.

**Critério de aceite:** INT-008 a INT-021 respondendo com conteúdo dos documentos reais; sem vazar `source_section` ou metadados internos para o usuário.

---

### Fase 4 — Classificador LLM (2–4 semanas)

**Objetivo:** Classificação mais robusta, menos frágil a variações de linguagem.

1. Criar dataset de avaliação com 200+ pares (input → intent esperado).
2. Implementar `BedrockClassifier` com prompt de classificação.
3. Rodar avaliação: medir accuracy vs. regex atual; identificar regressões.
4. Decidir estratégia: LLM puro vs. regex-first + LLM para casos ambíguos.
5. Atualizar testes — os 68 testes de orquestrador devem continuar passando.
6. Criar `docs/intent-catalog.md` com exemplos de edge cases.

**Critério de aceite:** accuracy ≥ 95% no dataset de avaliação; zero regressões nos 107 testes existentes.

---

### Fase 5 — Autenticação e PRD (1–2 semanas)

**Objetivo:** Integração com sessão real do app; deploy em PRD.

1. Integrar com o authorizer JWT do API Gateway da Alelo.
2. Extrair company_id/user_id/session_id do contexto do authorizer.
3. Remover IDs sintéticos do frontend (usar sessão real).
4. Testes end-to-end no app real em HML.
5. Deploy PRD com aprovação manual.
6. Criar `docs/runbook.md` e `docs/poc-to-production.md`.

**Critério de aceite:** o agente funciona no app Meu Alelo real em HML com usuário de teste; todos os cards de presentation renderizando corretamente; navigation abrindo deeplinks corretos.

---

## 5. RESTRIÇÕES E DECISÕES JÁ TOMADAS

As seguintes decisões foram tomadas e **não devem ser revertidas sem justificativa explícita**:

| Decisão | Razão |
|---------|-------|
| O campo `message` sempre presente no response | Fallback de acessibilidade; leitores de tela; retrocompatibilidade |
| Deeplinks nunca contêm CPF, idOrder ou outros IDs internos | Segurança; esses IDs não devem ser expostos ao app nativo |
| Route catalog fechado (7 rotas) | Previne SSRF; qualquer nova rota precisa de aprovação explícita |
| `steps` no allowlist de pedidos (mas sem sub-filtro) | Gap documentado — resolver na Fase 2 antes de PRD |
| Classificador retorna `ClassificationResult` com intent_id, flow, entities | Interface estável — o router não deve saber como o classificador funciona |
| HTML proibido em campos de presentation | Frontend usa textContent; nenhum dado do backend pode injetar HTML |
| `use_mock_agent = false` é o padrão no frontend | O frontend em produção nunca deve chamar o MockAgent |

---

## 6. CHECKLIST DE QUALIDADE POR FASE

Antes de cada deploy em HML, verificar:

- [ ] `pytest -v` — 107+ testes, 0 falhas
- [ ] Nenhum CPF/CNPJ nos logs de resposta
- [ ] Nenhum `idOrder` ou campo interno no payload de resposta
- [ ] Nenhum campo fora da allowlist no response de colaborador ou pedido
- [ ] `steps` sub-filtrado (a partir da Fase 2)
- [ ] Deeplinks válidos para todos os intents com navigation
- [ ] `error_code` presente quando `message` é de erro
- [ ] `presentation` presente em todos os intents com dados estruturados
- [ ] `message` presente em todos os responses (incluindo erros)
- [ ] CORS configurado para a origem correta (não `*`)
- [ ] X-Ray tracing ativado no Lambda
- [ ] CloudWatch alarms configurados (error rate, latência p99)

---

## 7. EXEMPLOS DE VALIDAÇÃO MANUAL

Executar estas 11 mensagens em qualquer ambiente para validar a cobertura básica:

| Mensagem | Intent esperado | Card esperado | Navigation |
|----------|----------------|---------------|------------|
| `O que posso fazer?` | INT-008 | capabilities_list | — |
| `Consultar colaborador Pessoa Colaboradora A` | INT-001 | collaborator_summary | Ver colaboradores |
| `Consultar CPF 000.000.000-00` | INT-002 | collaborator_summary | Ver colaboradores |
| `Consultar pedido 342671` | INT-003 | order_summary (PAID+) | Ver detalhes do pedido |
| `Qual foi o último pedido?` | INT-004 | order_summary | Ver detalhes do pedido |
| `Pedidos com status pago` | INT-005 | order_list | Ver todos os pedidos |
| `Rastrear cartões pelo CPF` | INT-006 | clarification | — |
| `Rastrear pedido 342671` | INT-007 | warning_notice | Ver rastreamento |
| `Cancele o pedido 342671` | INT-022 | transactional_redirect | (opcional ROUTE-017) |
| `Troque para outra empresa` | COMPANY_SWITCH | informational_notice | — |
| `O que é o MARH?` | INT-019 | knowledge_answer | — |

---

## 8. REFERÊNCIAS TÉCNICAS RELEVANTES

- **Amazon Bedrock Knowledge Bases:** `boto3` client `bedrock-agent-runtime`, método `retrieve` e `retrieve_and_generate`
- **Amazon Bedrock — Claude:** model IDs usados na Alelo: confirmar com time de plataforma (`anthropic.claude-3-haiku-*` ou `anthropic.claude-3-sonnet-*`)
- **ma-hr-orch:** API interna Alelo — documentação disponível no Confluence (solicitar ao time de plataforma)
- **Meu Alelo deeplink schema:** `meualelo://app/webview?url={encoded}&isModal=false&showNavbar=false&authRequired=true` — não alterar sem validação no app nativo
- **Espaço RH webview base URLs:**
  - HML: `https://meualelo-webviews-hml.siteteste.inf.br/`
  - PRD: `https://meualelo-webviews.alelo.com.br/`

---

## 9. O QUE NÃO FAZER

- **Não inventar campos** no response além do contrato documentado.
- **Não colocar CPF, nome completo ou documentos** em deeplinks, URLs ou logs.
- **Não usar `innerHTML`** no frontend com dados vindos do backend (nunca).
- **Não criar CSS ou JS específico por intenção** — os componentes visuais são reutilizáveis por variant.
- **Não alterar os 7 deeplinks do route catalog** sem validação no app nativo.
- **Não alterar o campo `message`** — ele é o fallback universal e deve sempre existir.
- **Não hardcodar credenciais** — usar Secrets Manager ou variáveis de ambiente.
- **Não remover testes existentes** — só acrescentar.
- **Não fazer deploy em PRD** antes de validação completa em HML com usuário real.

---

*Este documento foi gerado automaticamente a partir do estado do repositório em 2026-07-23.*  
*Branch: `main` · Commit mais recente: `b013c68` · Testes: 107/107 passando.*
