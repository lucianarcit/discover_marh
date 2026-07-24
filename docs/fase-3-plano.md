# Plano Técnico — Fase 3 Isolada (Bedrock + RAG)

> **Status:** PLANEJAMENTO — nenhum recurso AWS criado, nenhum código implementado.
> **Data:** 2026-07-23
> **Revisão:** 2026-07-23 (correções pós-aprovação conceitual)
> **Restrição:** não altera ambiente MOCK, não altera Fase 2, não envia dados corporativos ao modelo.
> **Região:** sa-east-1 exclusivamente. Cross-region proibido.

---

## 1. Estado atual relevante

| Item | Estado |
|---|---|
| `KnowledgeClient` (interface ABC) | Existe, contrato `query(topic) → dict` |
| `MockKnowledgeClient` | **15 entradas** no `_KNOWLEDGE` — ver seção 1.1 |
| `_INTENT_KNOWLEDGE_TOPIC` em `router.py` | **14 mapeamentos** INT-xxx → topic |
| `router.py` — fluxo `RAG_ONLY` | Já delega ao `knowledge_client` injetado |
| `orchestrator.py` | Aceita `knowledge_client` via construtor |
| `config.py` — `MODE` | Único enum (MOCK_LOCAL / INTEGRATED) — precisa virar dois eixos ortogonais |
| Corpus aprovado | `discover3/knowledge/marh_feature_knowledge.md` |

O Router **já está preparado** para trocar de implementação de `KnowledgeClient` sem nenhuma alteração. O ponto de mudança está no `config.py` (adicionar eixo `KNOWLEDGE_MODE`) e no `orchestrator.py` / factory (instanciar a implementação correta).

### 1.1 Divergência identificada: 14 tópicos vs. 15 entradas

**Achado:** o `MockKnowledgeClient._KNOWLEDGE` contém 15 entradas, mas o
`_INTENT_KNOWLEDGE_TOPIC` do `router.py` mapeia 14 intenções oficiais.

**Causa:** a entrada `ORDER_STATUS_INFO` foi adicionada ao mock com comentário
`# EV-028` — identificador de caso de avaliação, não um INT-xxx oficial — e
**não está mapeada no router**. Nenhum fluxo `RAG_ONLY` a referencia; ela é
acessível via `knowledge_client.query("ORDER_STATUS_INFO")` apenas se chamada
diretamente.

**Decisão:**

- `ORDER_STATUS_INFO` é um tópico **órfão**: presente no mock, sem intent oficial.
- Não criar nova intenção, não alterar IDs existentes, não remover silenciosamente.
- O tópico deve ser mantido no mock como está e registrado como pendente de
  classificação oficial pelo cliente.
- O dataset de avaliação (seção 10) terá **14 casos funcionais** mapeados às
  intenções oficiais, excluindo `ORDER_STATUS_INFO` até decisão do cliente.
- A tabela `topic_to_query` da Fase 3 conterá apenas os 14 tópicos roteáveis.

**Status:** `ORDER_STATUS_INFO — ORPHAN_TOPIC_PENDING_OFFICIAL_INTENT_ASSIGNMENT`

---

## 2. Configuração ortogonal

**Variáveis de ambiente a criar:**

```
DATA_SOURCE_MODE = MOCK | INTEGRATED      # controla ma-hr-orch
KNOWLEDGE_MODE   = MOCK | BEDROCK_RAG     # controla KnowledgeClient
```

**Retrocompatibilidade:** o `AGENT_MODE` existente continua sendo lido para
derivar `DATA_SOURCE_MODE` como fallback, mas não interfere em `KNOWLEDGE_MODE`.
O ambiente MOCK atual nunca altera — `DATA_SOURCE_MODE=MOCK` +
`KNOWLEDGE_MODE=MOCK` é o comportamento de hoje.

**Combinação da Fase 3:**

```
DATA_SOURCE_MODE=MOCK
KNOWLEDGE_MODE=BEDROCK_RAG
```

Resultado: INT-001 a INT-007 continuam no mock, INT-008 a INT-021 usam RAG real.
Nenhuma API da ma-hr-orch é chamada.

---

## 3. Interfaces a criar

```
KnowledgeClient (já existe — não alterar)
  └── MockKnowledgeClient (já existe — não alterar)
  └── BedrockRagKnowledgeClient (a implementar)

LanguageModelClient (nova interface)
  └── BedrockLanguageModelClient (a implementar)

Retriever (nova interface)
  └── BedrockKnowledgeBaseRetriever (a implementar)
```

**Assinaturas previstas:**

```python
class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        ...

class LanguageModelClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, context_chunks: list[str]) -> str:
        ...

class BedrockRagKnowledgeClient(KnowledgeClient):
    def __init__(self, retriever: Retriever, llm: LanguageModelClient):
        ...
    def query(self, topic: str) -> dict:
        # 1. topic → query_string (mapeamento fixo, não vai ao LLM)
        # 2. retriever.retrieve(query_string)
        # 3. filtrar chunks por score ≥ threshold (ver seção 7)
        # 4. se nenhum chunk aprovado → found=False (sem invenção)
        # 5. llm.generate(prompt_sistema, chunks aprovados)
        # 6. retornar com data_classification=BEDROCK_RAG_GROUNDED
        ...
```

**Regra explícita:** o Router não importa boto3 em nenhum momento. A injeção
ocorre no factory/orchestrator.

**Regra explícita:** `RetrieveAndGenerate` da API do Bedrock Knowledge Bases
**não será utilizado**. O fluxo usa sempre `Retrieve` (recuperação) separado de
`LanguageModelClient.generate` (geração), preservando o controle das interfaces
e a capacidade de trocar implementações independentemente.

---

## 4. Plano de chunking

**Corpus:** `marh_feature_knowledge.md` — estruturado em seções numeradas com
cabeçalhos markdown.

**Estratégia:** chunking hierárquico por seção.

| Nível | Critério | Tamanho alvo |
|---|---|---|
| Seção (`## N.`) | Cabeçalho de segundo nível | ≤ 500 tokens |
| Subseção (`### N.N`) | Cabeçalho de terceiro nível | ≤ 200 tokens |
| Overlap | Entre chunks adjacentes da mesma seção | 50 tokens |

**Metadados por chunk:**

```json
{
  "source_file": "marh_feature_knowledge.md",
  "section_number": "4",
  "section_title": "Pedidos",
  "subsection_title": "Fluxo de criação",
  "chunk_index": 2,
  "approved": true
}
```

**Regra crítica:** nenhum chunk pode conter dados da ma-hr-orch, CPF, pedidos
reais, rotas, deeplinks, schemas ou fixtures. O corpus de origem já respeita
isso — validar durante o processo de ingestão.

---

## 5. Plano de embeddings

**Modelo candidato:** `amazon.titan-embed-text-v2:0`

- Disponível nativamente no Bedrock
- Dimensão: 1024
- Suporte multilingual (PT-BR confirmado para Titan v2)
- Máximo de 8.192 tokens de entrada

**Validação obrigatória antes de qualquer implementação:**

```bash
aws bedrock list-foundation-models --region sa-east-1 \
  --query "modelSummaries[?contains(modelId,'titan-embed')]"
```

**Se `amazon.titan-embed-text-v2:0` não estiver ativo em sa-east-1:**
registrar bloqueio arquitetural `BLOCKER-EMBED-SA-EAST-1` e interromper.
Cross-region é proibido — não usar `us-east-1` como alternativa.

**Status atual:** `EMBEDDING_MODEL=PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION`

---

## 6. Decisão de armazenamento vetorial — ADR-001

### ADR-001: Mecanismo de armazenamento vetorial para Fase 3

**Status:** ABERTO — aguarda resultado do probe de disponibilidade (seção 13).

**Contexto:** a Fase 3 requer recuperação vetorial de chunks do corpus aprovado.
Duas opções são candidatas na região sa-east-1. A decisão impacta Terraform,
permissões IAM, latência e controle da recuperação.

---

#### Opção A — Bedrock Knowledge Bases (gerenciado)

**Como funciona na modalidade correta:**
- Data source: S3
- Sincronização via `StartIngestionJob` (pull do S3)
- Recuperação via `bedrock-agent-runtime:Retrieve` (chunks + scores)
- Geração separada via `LanguageModelClient` (não usa `RetrieveAndGenerate`)
- Índice vetorial interno gerenciado pela AWS (OpenSearch Serverless por padrão)

**Disponibilidade em sa-east-1:** **a confirmar no probe** — Knowledge Bases
foi lançada em regiões selecionadas e sa-east-1 pode ter restrições de
modalidade ou estar em preview.

| Critério | Avaliação |
|---|---|
| Disponibilidade em sa-east-1 | A confirmar — bloqueador se ausente |
| Custo (ingestão) | Negligenciável para corpus pequeno |
| Custo (query/Retrieve) | Por chamada de recuperação — a confirmar pricing sa-east-1 |
| Latência | Gerenciada pela AWS; não controlável |
| Terraform | `aws_bedrockagent_knowledge_base` + `aws_bedrockagent_data_source` |
| Controle da recuperação | Retrieve retorna chunks e scores; threshold aplicado no cliente |
| Operação | Zero administração de índice |
| Risco | Dependência de feature GA em sa-east-1 — verificar antes |

---

#### Opção B — S3 Vectors (acesso direto)

**Como funciona:**
- Corpus pré-processado e vetorizado offline (embedding via Bedrock)
- Vetores armazenados em S3 com metadados
- Retriever implementa busca por similaridade (cosine) sem serviço gerenciado
- Alternativa: usar Aurora pgvector ou OpenSearch Serverless provisionado

**Disponibilidade em sa-east-1:** S3 existe em sa-east-1; S3 Vectors (feature
experimental de busca nativa no S3) está em preview e disponibilidade é incerta.

| Critério | Avaliação |
|---|---|
| Disponibilidade em sa-east-1 | S3 sim; S3 Vectors preview — a confirmar |
| Custo (ingestão) | Lambda de ingestão + S3 storage |
| Custo (query) | Lambda + S3 GET + embedding por query |
| Latência | Controlável, depende da implementação |
| Terraform | S3 bucket + Lambda ingestão + IAM |
| Controle da recuperação | Total — implementação própria |
| Operação | Maior complexidade operacional |
| Risco | S3 Vectors em preview — pode não estar disponível |

---

#### Critério de desempate

Se ambas as opções estiverem disponíveis em sa-east-1, a escolha será:

1. **Knowledge Bases** se `Retrieve` (não `RetrieveAndGenerate`) estiver GA e
   as interfaces `Retriever` / `LanguageModelClient` puderem ser implementadas
   sem acoplamento ao SDK interno da feature.
2. **S3 + Lambda de busca** se Knowledge Bases não estiver disponível ou
   impuser restrição que quebre a separação Retrieve/Generate.

**Decisão final:** PENDENTE — registrar após probe.

---

## 7. Plano de recuperação

**Fluxo `BedrockRagKnowledgeClient.query(topic)`:**

```
topic (ex: "ORDER_PROCESS")
  ↓
topic_to_query(topic) → string em português
  ↓                     (mapeamento fixo em código — 14 tópicos oficiais)
Retriever.retrieve(query, top_k=5)
  ↓
chunks com score ≥ RETRIEVAL_SCORE_THRESHOLD
  ↓ (se nenhum chunk aprovado)
  → found=False, content=None   ← sem invenção
  ↓ (com chunks aprovados)
LanguageModelClient.generate(prompt_sistema, chunks)
  ↓
resposta fundamentada
  ↓
dict com data_classification=BEDROCK_RAG_GROUNDED
```

**Threshold de score:**

```
RETRIEVAL_SCORE_THRESHOLD = 0.70   # PROPOSED_PENDING_EVALUATION
```

- Valor inicial proposto: 0.70
- **Status:** `PROPOSED_PENDING_EVALUATION` — não considerar definitivo.
- Deve ser lido de variável de ambiente para permitir calibração sem redeploy:

```
RETRIEVAL_SCORE_THRESHOLD=0.70   # configurável via env var
```

- Será calibrado executando o dataset de avaliação (seção 10) com valores entre
  0.50 e 0.85 e observando precisão vs. taxa de fallback.

**Mapeamento topic → query (14 tópicos oficiais):**

| Topic | Query string |
|---|---|
| `AGENT_CAPABILITIES` | "O que o agente consultivo MARH consegue fazer?" |
| `CONSULTABLE_INFO` | "Quais informações posso consultar pelo agente?" |
| `ORDER_PROCESS` | "Como criar um pedido no Espaço RH?" |
| `HOW_CONSULT_ORDER` | "Como consultar um pedido pelo agente?" |
| `HOW_CONSULT_COLLABORATOR` | "Como consultar um colaborador pelo agente?" |
| `CARD_TRACKING_INFO` | "Como funciona o rastreamento de cartões?" |
| `CANNOT_CANCEL` | "É possível cancelar um pedido pelo agente?" |
| `CANNOT_EDIT_COLLABORATOR` | "O agente consegue editar dados de colaboradores?" |
| `COMPANY_SCOPE` | "O agente consulta qualquer empresa?" |
| `COMPANY_REQUIRED` | "É necessário selecionar uma empresa para usar o agente?" |
| `AGENT_VS_PORTAL` | "O agente substitui o portal web?" |
| `MARH_OVERVIEW` | "O que é o MARH?" |
| `ESPACO_RH_OVERVIEW` | "O que é o Espaço RH?" |
| `QUESTION_TYPES` | "Que tipo de perguntas posso fazer ao agente?" |

`ORDER_STATUS_INFO` **não está na tabela** — tópico órfão, aguarda decisão
do cliente (ver seção 1.1).

O mapeamento é estático e auditável. Nenhuma query é gerada dinamicamente
por LLM.

---

## 8. Prompt de sistema

```
Você é um assistente consultivo do Meu Alelo RH (MARH).

Responda SOMENTE com base nos trechos de conhecimento fornecidos abaixo.
Não invente informações. Não use conhecimento externo.
Se os trechos não contiverem resposta suficiente, diga que não tem
informação disponível e oriente o usuário a acessar o Espaço RH.

Responda em português brasileiro.
Seja direto, claro e objetivo.
Não mencione que está usando trechos ou documentos.

--- CONHECIMENTO ---
{chunks}
--- FIM DO CONHECIMENTO ---

Pergunta do usuário: {query}
```

**Restrições no prompt:**
- Não mencionar Bedrock, RAG, índice ou embeddings ao usuário
- Não usar dados fora dos chunks fornecidos
- Em caso de ambiguidade, pedir esclarecimento (não inventar)

---

## 9. Modelo de geração

**Status:** `GENERATION_MODEL=PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION`

Nenhum modelo de geração foi selecionado. Claude 3 Haiku e Claude 3.5 Haiku
**não serão utilizados**.

A seleção ocorrerá após o probe (seção 13) confirmar quais modelos de geração
estão ativos em sa-east-1. Critérios de seleção:

- Ativo (não preview) em sa-east-1
- Suporte a PT-BR com qualidade adequada
- Latência compatível com resposta conversacional
- Custo adequado para POC

Se nenhum modelo de geração estiver ativo em sa-east-1:
registrar bloqueio arquitetural `BLOCKER-GEN-MODEL-SA-EAST-1` e interromper.
Cross-region é proibido.

---

## 10. Critérios de groundedness

Para cada resposta gerada, validar:

| Critério | Como verificar |
|---|---|
| Fundamentação | Toda afirmação tem correspondência textual em pelo menos um chunk |
| Sem invenção | Nenhuma informação que não esteja nos chunks recuperados |
| Fallback correto | `found=False` quando score < RETRIEVAL_SCORE_THRESHOLD em todos os chunks |
| Sem dados proibidos | Resposta não contém CPF, pedido real, deeplink, rota interna |
| Corpus exclusivo | Somente `marh_feature_knowledge.md` como origem |

**Groundedness score automático (avaliação):** usar `BedrockRuntime.invoke_model`
com modelo aprovado para verificar se a resposta é suportada pelos chunks —
executado offline no dataset de avaliação, não em produção.

---

## 11. Dataset de avaliação

### Casos funcionais (14 tópicos oficiais)

| ID | Intent | Pergunta de teste | Resultado esperado |
|---|---|---|---|
| EV-RAG-001 | INT-008 | "O que você consegue fazer?" | Lista de capacidades fundamentada no corpus |
| EV-RAG-002 | INT-009 | "Quais informações posso consultar?" | Escopo de consulta |
| EV-RAG-003 | INT-010 | "Como fazer um pedido?" | Fluxo de 5 etapas, boleto — fundamentado no corpus |
| EV-RAG-004 | INT-011 | "Como consultar um pedido?" | Instrução de consulta |
| EV-RAG-005 | INT-012 | "Como consultar um colaborador?" | Instrução por nome ou CPF |
| EV-RAG-006 | INT-013 | "Como rastrear cartões?" | Limitação de rastreamento por CPF |
| EV-RAG-007 | INT-014 | "Você consegue cancelar pedido?" | Negação + redirect |
| EV-RAG-008 | INT-015 | "Pode editar colaborador?" | Negação + redirect |
| EV-RAG-009 | INT-016 | "Consulta qualquer empresa?" | Escopo da empresa selecionada |
| EV-RAG-010 | INT-017 | "Precisa selecionar empresa?" | Confirmação de pré-requisito |
| EV-RAG-011 | INT-018 | "Você substitui o portal?" | Negação + papel consultivo |
| EV-RAG-012 | INT-019 | "O que é o MARH?" | Resposta fundamentada no corpus |
| EV-RAG-013 | INT-020 | "O que é o Espaço RH?" | Resposta fundamentada no corpus |
| EV-RAG-014 | INT-021 | "Que perguntas posso fazer?" | Tipos de consulta |

### Casos de fallback obrigatórios

| ID | Pergunta | Resultado esperado |
|---|---|---|
| EV-RAG-015 | "Qual o CNPJ da Alelo?" | `found=False`, sem invenção |
| EV-RAG-016 | "Quantos colaboradores minha empresa tem?" | `found=False` — dado corporativo real, fora do corpus |
| EV-RAG-017 | "Qual a cotação do dólar hoje?" | `found=False`, sem invenção |

### Casos de regressão (intenções fora do RAG)

| ID | Intent | Verificação |
|---|---|---|
| EV-REG-001 | INT-001 | Não chama KnowledgeClient, usa MockMaHrOrchClient |
| EV-REG-002 | INT-006 | Retorna ERR-010, sem RAG |
| EV-REG-003 | INT-024 | Redirect transacional, sem RAG |

---

## 12. Estimativa de custo

**Status:** `COST_ESTIMATE_STATUS=PENDING_MODEL_AND_VECTOR_STORE_SELECTION`

Estimativas anteriores baseadas em Claude 3 Haiku foram removidas. O modelo de
geração não foi selecionado e o mecanismo de armazenamento vetorial não foi
decidido.

A estimativa será produzida após:
1. probe confirmar modelo de embedding ativo em sa-east-1;
2. probe confirmar modelo de geração ativo em sa-east-1;
3. ADR-001 decidir o mecanismo vetorial;
4. pricing de cada componente ser verificado para sa-east-1.

---

## 13. Probe de disponibilidade — pré-requisito obrigatório

**Nenhuma implementação de código ou Terraform pode ser iniciada antes deste
probe.**

O probe deve produzir um relatório com as seguintes evidências, obtidas por
comandos executados com credenciais reais da conta AWS alvo:

### 13.1 Comandos a executar

```bash
# Modelos de embedding disponíveis em sa-east-1
aws bedrock list-foundation-models --region sa-east-1 \
  --by-inference-type ON_DEMAND \
  --query "modelSummaries[?contains(outputModalities,'EMBEDDING')].{id:modelId,provider:providerName,status:modelLifecycle.status}"

# Modelos de geração de texto disponíveis em sa-east-1
aws bedrock list-foundation-models --region sa-east-1 \
  --by-inference-type ON_DEMAND \
  --query "modelSummaries[?contains(outputModalities,'TEXT') && !contains(outputModalities,'EMBEDDING')].{id:modelId,provider:providerName,status:modelLifecycle.status}"

# Verificar se Knowledge Bases está disponível na conta/região
aws bedrock-agent list-knowledge-bases --region sa-east-1

# Verificar permissões existentes (policy simulada)
aws iam simulate-principal-policy \
  --policy-source-arn <LAMBDA_ROLE_ARN> \
  --action-names bedrock:Retrieve bedrock:InvokeModel \
    bedrock-agent:Retrieve bedrock-agent-runtime:Retrieve \
  --region sa-east-1

# S3 Vectors — verificar se feature está ativa na conta
aws s3api list-bucket-intelligent-tiering-configurations \
  --bucket <qualquer_bucket_existente> --region sa-east-1
```

### 13.2 Itens que o relatório deve responder

| Item | Resposta esperada |
|---|---|
| Titan Embed Text v2 ativo em sa-east-1? | Sim / Não / Preview |
| Outro modelo de embedding disponível? | Listar |
| Modelo de geração (não Haiku) ativo em sa-east-1? | Listar candidatos |
| Bedrock Knowledge Bases GA em sa-east-1? | Sim / Não / Preview |
| `Retrieve` (sem `RetrieveAndGenerate`) disponível? | Sim / Não |
| S3 Vectors disponível na conta/região? | Sim / Não / Preview |
| Permissões existentes na role da Lambda? | Listar gaps |
| Decisão recomendada (ADR-001) | Knowledge Bases ou S3+Lambda |
| Bloqueadores arquiteturais identificados | Listar ou "nenhum" |

### 13.3 Critérios de bloqueio

Se qualquer um dos seguintes for verdadeiro, interromper e registrar bloqueio:

- `amazon.titan-embed-text-v2:0` não está ativo em sa-east-1 → `BLOCKER-EMBED-SA-EAST-1`
- Nenhum modelo de geração aprovado ativo em sa-east-1 → `BLOCKER-GEN-MODEL-SA-EAST-1`
- Bedrock Knowledge Bases não disponível E S3 Vectors não disponível → `BLOCKER-VECTOR-STORE-SA-EAST-1`

---

## 14. Ambiente isolado (plano de implantação)

**Recursos AWS a criar somente após probe aprovado e ADR-001 decidido:**

```
Lambda:         marh-agent-rag-hml
API Gateway:    marh-agent-rag-hml-api
S3 corpus:      marh-agent-rag-hml-knowledge
Knowledge Base: marh-agent-kb-hml         (se ADR-001 = Knowledge Bases)
Frontend:       marh-agent-rag-hml-frontend (CloudFront separado)
Secrets:        /marh-agent/rag-hml/config
CloudWatch:     marh-agent/rag-hml (log group separado)
```

**Variáveis de ambiente da Lambda:**

```
DATA_SOURCE_MODE=MOCK
KNOWLEDGE_MODE=BEDROCK_RAG
BEDROCK_REGION=sa-east-1
BEDROCK_KNOWLEDGE_BASE_ID=<id>           (se ADR-001 = Knowledge Bases)
BEDROCK_MODEL_ID=<decidir após probe>
RETRIEVAL_SCORE_THRESHOLD=0.70           (calibrável — PROPOSED_PENDING_EVALUATION)
ENVIRONMENT=HML
LOG_LEVEL=INFO
```

**Badge do frontend:** `AWS RAG HML` — diferenciado visualmente do ambiente
MOCK e do INTEGRATED.

**Não alterar:**
- Lambda `marh-agent-mock-hml`
- API Gateway do MOCK
- CloudFront `d1vtu9x0di76z9.cloudfront.net`
- Terraform da Fase 1
- Recursos da Fase 2

---

## 15. Sequência de implementação

```
Passo 1  — Executar probe de disponibilidade (seção 13)
           Produzir relatório com evidências dos comandos
           Decidir ADR-001 (armazenamento vetorial)
           Selecionar modelo de embedding e geração
           Registrar bloqueadores se existirem
           *** GATE: não avançar sem relatório aprovado ***

Passo 2  — Adicionar DATA_SOURCE_MODE e KNOWLEDGE_MODE ao config.py
           Adicionar RETRIEVAL_SCORE_THRESHOLD como env var configurável
           Retrocompatível com AGENT_MODE existente

Passo 3  — Criar interfaces Retriever e LanguageModelClient

Passo 4  — Implementar BedrockRagKnowledgeClient
           Stub + testes unitários com mocks das interfaces

Passo 5  — Implementar BedrockKnowledgeBaseRetriever (ou S3Retriever)
           Conforme ADR-001

Passo 6  — Implementar BedrockLanguageModelClient
           Usando modelo selecionado no Passo 1

Passo 7  — Atualizar factory/orchestrator para instanciar conforme KNOWLEDGE_MODE

Passo 8  — Criar Terraform do ambiente RAG HML

Passo 9  — Ingerir corpus no Knowledge Base (ou S3 Vectors)

Passo 10 — Executar dataset de avaliação (20 casos)
           Calibrar RETRIEVAL_SCORE_THRESHOLD

Passo 11 — Deploy da Lambda RAG HML

Passo 12 — Validar frontend com badge AWS RAG HML
```

---

## 16. Resumo das decisões

| Decisão | Estado |
|---|---|
| Armazenamento vetorial | ABERTO — ADR-001 aguarda probe |
| Embeddings | `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION` — Titan Embed v2 candidato |
| Modelo de geração | `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION` — Claude 3 Haiku e 3.5 Haiku excluídos |
| Cross-region | PROIBIDO — sa-east-1 exclusivamente |
| RetrieveAndGenerate | PROIBIDO — usar Retrieve + LanguageModelClient separados |
| Threshold de recuperação | `0.70 — PROPOSED_PENDING_EVALUATION` — configurável por env var |
| Chunking | Hierárquico por seção markdown — APROVADO |
| Invenção permitida | Não — fallback obrigatório (`found=False`) — APROVADO |
| Ponto de injeção | `orchestrator.py` + factory — Router sem alteração — APROVADO |
| Corpus | Somente `marh_feature_knowledge.md` — APROVADO |
| `ORDER_STATUS_INFO` | `ORPHAN_TOPIC_PENDING_OFFICIAL_INTENT_ASSIGNMENT` |
| Estimativa de custo | `PENDING_MODEL_AND_VECTOR_STORE_SELECTION` |
| Ambientes MOCK e Fase 2 | Intocados — CONFIRMADO |

---

## 17. Restrições absolutas da Fase 3

Não adicionar ao corpus:
- dados da ma-hr-orch
- pedidos ou colaboradores reais
- CPF
- rotas ou deeplinks
- regras de autorização
- catálogo de erros
- schemas de API
- decisões de infraestrutura
- fixtures

Não fazer antes do probe (Passo 1):
- selecionar modelo definitivo
- criar recurso AWS
- fazer deploy
- conectar dados reais
- alterar templates API_ONLY
- criar fluxo híbrido
- modificar INT-001 a INT-007

Nunca:
- usar cross-region
- usar `RetrieveAndGenerate`
- usar Claude 3 Haiku ou Claude 3.5 Haiku
- fazer fallback silencioso para mock em modo BEDROCK_RAG
- fazer commit ou push sem autorização
