# Checklist de Levantamento — Bot Alelo

Reunião com: ___________________________
Data: ___________________________
Participantes: ___________________________

---

> **Contexto já levantado**
> O bot anterior foi descontinuado por alto custo (modelo caro, mesmo usando cache semântico + Elastic). O novo bot deve ser um **agente consultivo híbrido**: responde dúvidas procedimentais via RAG (22 docs) e também busca dados reais do usuário logado via APIs do portal, respeitando rigorosamente os perfis de acesso. A sessão do usuário deve ser recuperada via cookies.

---

## 1. Canal e Ambiente

> ✅ **Resolvido**

- [x] O bot vive **exclusivamente dentro do aplicativo Meu Alelo** — não há canal externo (WhatsApp, Teams, etc.).
- [x] O usuário sempre estará **autenticado** ao abrir o bot — não há fluxo de login separado.
- [x] O bot deve funcionar em **mobile e web**.
- [x] O comportamento e as permissões do bot variam conforme o **perfil (role) do usuário logado** (Decisão, Gerenciamento, Operação, Financeiro).

---

## 2. Autenticação e Sessão via Cookie

> ✅ **Resolvido** — O app nativo injeta os cookies na webview antes de abri-la. O bot lê esses cookies e monta os headers de cada chamada de API. O ciclo de vida do token é gerenciado inteiramente pelo app nativo.

**Cookies injetados pelo app nativo:**

| Cookie | Descrição |
|---|---|
| `accessToken` | JWT de acesso (expira em ~300s) |
| `refreshToken` | Token de renovação OAuth2 |
| `CLIENT_ID` | Client ID OAuth2 |
| `CLIENT_SECRET` | Client Secret OAuth2 |
| `PLATFORM` | `ANDROID` ou `IOS` |
| `APP_VERSION` | Versão do app nativo |
| `FNP` | Fingerprint do dispositivo |
| `USER_ID` | ID do usuário (fallback se não vier no JWT) |

**Headers obrigatórios em cada chamada de API:**
```
Authorization: Bearer <accessToken>
client_id / x-ibm-client-id: <CLIENT_ID>
x-ibm-client-secret: <CLIENT_SECRET>
X-BASIC-AUTHORIZATION: Basic base64(CLIENT_ID:CLIENT_SECRET)
PLATFORM: <PLATFORM>
APP_VERSION: <APP_VERSION>
USER_ID: <USER_ID>
FNP: <FNP>
auth_type: IS-ALELO
scope-key: appKeyWso2
```

**Gestão de expiração:**
- Não há expiração explícita no cookie — a expiração é detectada via **401 da API**
- Ao receber 401, o bot dispara refresh automático usando `CLIENT_ID` + `CLIENT_SECRET` (fluxo OAuth2)
- A webview **não reescreve** os cookies — quem gerencia o ciclo de vida é o app nativo
- TTL base do token: **300 segundos**

- [x] Qual é o **nome e estrutura do cookie** de sessão? → Ver tabela acima
- [x] O token de sessão é suficiente para as APIs? → Sim, junto com `CLIENT_ID` e `CLIENT_SECRET`
- [x] Como lidar com **sessão expirada**? → Detectar 401 e fazer refresh OAuth2 automaticamente
- [ ] O backend do bot é **server-side** (lê cookies diretamente) ou precisa que o frontend passe os tokens?
- [ ] O bot terá **domínio próprio** ou mesmo domínio do portal? (impacta acesso aos cookies `httpOnly`)
- [ ] Existe endpoint `/profile` ou similar que retorna perfil completo do usuário a partir do `accessToken`? *(candidato: `GET /profile` da base HRM — confirmar campos retornados)*

**Notas:**
```
- Autenticação do MeuAlelo como referência.
- Falar com Carlos para confirmar domínio e acesso server-side aos cookies.


```

---

## 3. Natureza do Agente — RAG, API ou Híbrido

> ✅ **Resolvido** — O processo de RAG será desenhado pelo nosso time. As fontes estão definidas:
> - **RAG**: os 22 arquivos `.md` da pasta `docs` como única fonte de conhecimento procedimental.
> - **API**: apenas os endpoints GET listados na seção 4 como dados complementares em tempo real.
> - **Escrita bloqueada**: o bot opera exclusivamente em modo leitura — sem POST, PUT ou DELETE.

**Comportamento por tipo de pergunta:**

| Tipo de pergunta | Fonte |
|---|---|
| "Como faço um pedido?" (procedural) | RAG |
| "Quais colaboradores eu tenho?" (consulta de dados) | API |
| "Como cadastro um colaborador?" + "Quem já está cadastrado?" | RAG + API |
| "Qual o status do meu último pedido?" | API |
| "Quais benefícios estão ativos?" | API |
| "O que é faturamento descentralizado?" | RAG |

**Estratégia de fallback:**
- Se a API retornar erro ou indisponibilidade → bot informa a situação e oferece a resposta procedimental via RAG quando aplicável.
- O processo de RAG (chunking, embeddings, retrieval, re-ranking) será definido pelo time em fase de design.

---

## 4. Integração com APIs do Portal

> ✅ **Resolvido** — O bot usa **somente GET**. Endpoints definidos e fechados. Nenhuma operação de escrita será executada pelo bot.

**Base URL HML (homologação):** `https://api-ma.homologacaoalelo.com.br/alelo/uat/cardholders-hr-management/v1`

**Headers obrigatórios confirmados via curl real:**
```
Authorization: Bearer {accessToken}
CLIENT_ID: {client_id}
CLIENT_SECRET: {client_secret}
X-BASIC-AUTHORIZATION: Basic {base64(client_id:client_secret)}
APP_VERSION: 8.55.0 (2026071702)
PLATFORM: IOS | ANDROID
FNP: {device_fingerprint}
user_id: {user_id}
x-ibm-client-id: {client_id}
AUTH_TYPE: IS-ALELO
Accept: application/json
Content-Type: application/json
```

**Parâmetro adicional confirmado:** `lang=pt` (query string — define idioma da resposta)

*Pedidos*
| Endpoint | Descrição |
|---|---|
| `GET /orders` | Lista de pedidos |
| `GET /orders/{orderNumber}` | Detalhe do pedido |
| `GET /orders/{orderNumber}/beneficiaries` | Beneficiários do pedido |
| `GET /orders/{orderNumber}/bank-ticket` | Boleto |
| `GET /orders/{orderNumber}/invoice` | Nota fiscal |

*Gestão de Colaboradores*
| Endpoint | Descrição |
|---|---|
| `GET /beneficiaries` | Listar colaboradores (paginado, filtro `nameOrCpf`) |
| `GET /companies` | Empresas do usuário logado |
| `GET /profile` | Perfil do usuário logado |

*Rastreio de Cartões*
| Endpoint | Descrição |
|---|---|
| `GET /tracking` | Lista de pedidos em rastreio |
| `GET /orders/{orderNumber}/tracking` | Rastreio por pedido |
| `GET /orders/{orderNumber}/tracking/{arNumber}/detail` | Detalhe do AR |

*Auxiliares (mesma base HRM)*
| Endpoint | Descrição |
|---|---|
| `GET /benefits` | Tipos de benefício |
| `GET /products` | Produtos disponíveis |
| `GET /places` | Locais de entrega |
| `GET /availability-dates-for-credit` | Datas disponíveis para disponibilização |

*Fora da base HRM*
| Endpoint | Descrição |
|---|---|
| `GET /companies/{companyId}/payment-methods` | Métodos de pagamento da empresa |
| `GET /alelo/uat/places/v2/address?zipCode=` | Consulta de CEP |

- [x] APIs são **REST**, somente **GET** — bot opera em modo leitura
- [x] Swagger disponível — ver `03_api-referencia.md`
- [x] Ambiente de **homologação** confirmado: `api-ma.homologacaoalelo.com.br`
- [x] Credenciais de HML disponíveis — ver `docs/sample/user_hml.txt` e `sample_curl.txt`
- [ ] Existe **rate limiting**? Qual o limite de requisições por minuto/hora?

---

## 5. Guardrails e Controle de Acesso

> ✅ **Decisão do time** — Guardrails atuam em duas camadas independentes: controle de acesso por perfil (lógica de negócio) e Bedrock Guardrails (proteção do modelo).

---

### Camada 1 — Controle de Acesso por Perfil (lógica de negócio)

Implementada no **system prompt do Bedrock Agent**. Antes de qualquer resposta, o bot chama `GET /profile` → obtém `functions[].functionType` → verifica se o módulo solicitado é permitido para aquele perfil.

- [x] O bot aplica guardrails baseados no perfil do usuário logado:

  | Perfil | Acesso no bot |
  |---|---|
  | **Decisão** | Consulta a todos os módulos |
  | **Gerenciamento** | Consulta a todos os módulos |
  | **Operação** | Pedidos, colaboradores, locais de entrega, rastreio, 2ª via, contrato — sem configuração de benefícios |
  | **Financeiro** | Apenas boleto, nota fiscal e relatórios |

- [x] Se o módulo não for permitido para o perfil → bot responde com mensagem de bloqueio **sem buscar no RAG**.

  > Exemplo: usuário com perfil `OPERACAO` pergunta "Como adiciono um novo usuário?"
  > → Bot responde: *"Apenas interlocutores com perfil Decisão podem gerenciar usuários do sistema."*

- [x] O isolamento de dados entre empresas é garantido pela própria API — o token do usuário só retorna dados da sua empresa.
- [x] Qualquer ação de escrita é bloqueada independente do perfil — bot opera somente em consulta.
- [x] As regras são **definidas e mantidas pelo time técnico** — não dependem de configuração do cliente.

---

### Camada 2 — Bedrock Guardrails (proteção do modelo)

Camada **gerenciada pela AWS**, disponível em sa-east-1. Filtra entrada e saída do LLM independente da lógica de negócio. Atua em dois momentos:

```
Mensagem do usuário
        ↓
[Bedrock Guardrails — ENTRADA]
Bloqueia: jailbreak, injeção de prompt, tópicos fora do escopo, conteúdo nocivo
        ↓
[Lógica de perfil — Camada 1]
GET /profile → verifica permissão do módulo
        ↓
[Bedrock Agent — RAG + API]
Busca nos docs e/ou chama endpoint GET
        ↓
[Bedrock Guardrails — SAÍDA]
Mascara PII, verifica grounding, bloqueia invenção
        ↓
Resposta ao usuário
```

**Configuração planejada:**

| Proteção | Regra para este bot |
|---|---|
| **Tópicos bloqueados** | Qualquer assunto fora do portal Meu Alelo (concorrentes, finanças pessoais, RH geral, etc.) |
| **Filtro de conteúdo** | Bloqueia jailbreak, prompt injection e linguagem inadequada |
| **Grounding** | Respostas devem ter base nos docs ou nos dados da API — sem inventar informações |
| **Mascaramento de PII** | CPF exibido de forma parcial (ex: `***.456.**-**`); tokens e secrets nunca expostos na resposta |
| **Fora do escopo** | Se pergunta não tiver relação com o portal → acionar fallback, não tentar responder |

---

### Pendências de definição

| Decisão | Impacto |
|---|---|
| Nível de mascaramento de CPF | Exibir parcial ou não exibir na resposta? |
| Perfil Financeiro em MOD 5 | Pode ver beneficiários de um pedido ou apenas boleto/NF? |
| Comportamento em insistência | Bot repete o bloqueio ou encerra a conversa após N tentativas? |
| Lista fechada de tópicos fora do escopo | A detalhar durante o design |

---

## 6. Infraestrutura AWS — Região São Paulo (sa-east-1)

> ✅ **Confirmado em reunião:** a infraestrutura será na AWS, restrita à região **sa-east-1 (São Paulo)** por requisito de soberania/latência. Isso limita os serviços disponíveis — ver tabelas abaixo.

### Amazon Bedrock — disponível em sa-east-1

| Recurso | Disponível? |
|---|---|
| **Guardrails** | ✅ Sim |
| **Knowledge Bases** (RAG gerenciado) | ✅ Sim |
| **Agents** | ✅ Sim |
| **Provisioned Throughput** | ✅ Sim |
| Model Evaluation | ❌ Não |
| Fine-tuning (custom models) | ❌ Não |
| Continued Pre-training | ❌ Não |

### AgentCore — disponível em sa-east-1

| Recurso | Disponível? |
|---|---|
| **AgentCore Runtime** | ✅ Sim |
| **AgentCore Gateway** | ✅ Sim |
| **AgentCore Identity** | ✅ Sim |
| **AgentCore Built-in Tools** | ✅ Sim |
| **AgentCore Observability** | ✅ Sim |
| AgentCore Harness | ❌ Não |
| AgentCore Memory | ❌ Não |
| AgentCore Evaluations | ❌ Não |
| AgentCore Optimization | ❌ Não |
| Policy in AgentCore | ❌ Não |
| AWS Agent Registry | ❌ Não |

### Implicações para o bot

| Decisão | Impacto da limitação |
|---|---|
| **RAG**: usar Bedrock Knowledge Bases ✅ | Disponível — estratégia viável nativamente |
| **Agente**: usar Bedrock Agents ✅ | Disponível — orquestração de tools nativa |
| **Guardrails**: usar Bedrock Guardrails ✅ | Disponível — solução para guardrails de perfil |
| **Memória de sessão**: AgentCore Memory ❌ | **Indisponível** — precisará de solução alternativa (ex: DynamoDB, ElastiCache) |
| **Avaliação/otimização**: AgentCore Evaluations/Optimization ❌ | **Indisponível** — monitoramento e tuning serão manuais ou via outra ferramenta |
| **Fine-tuning de modelo** ❌ | Indisponível — usar modelos fundacionais (ex: Claude, Titan) sem customização de pesos |

- [ ] Quais **modelos fundacionais** estão disponíveis no Bedrock sa-east-1? (confirmar: Claude Haiku/Sonnet, Titan, Llama)
- [ ] A ausência do **AgentCore Memory** é um bloqueador? Qual alternativa para persistir contexto entre sessões?
- [ ] A ausência do **AgentCore Harness** (testes automatizados de agentes) impacta o processo de QA? Como testar o bot?

**Notas:**
```
Confirmado em reunião: infraestrutura AWS sa-east-1 (São Paulo).


```

---

## 7. Custo e Otimização

> ✅ **Decisão do time** — A estratégia de otimização de custo será definida por nós, aprendendo com os erros do bot anterior (modelo caro + cache insuficiente).

- [x] **Modelo**: adotar hierarquia de custo — **Claude Haiku** para triagem e perguntas simples, **Claude Sonnet** para respostas complexas que exigem RAG + API combinados.
- [x] **Cache**: Bedrock Knowledge Bases oferece cache semântico nativo — substitui a necessidade de Elastic Cache para perguntas procedimentais repetidas. Para dados da API, avaliar TTL curto via ElastiCache.
- [x] **Throughput**: iniciar com **on-demand** no MVP para medir volume real antes de comprometer Provisioned Throughput.
- [x] **AgentCore Observability** (disponível em sa-east-1) será usado para monitorar custo por interação e identificar gargalos.
- [ ] Budget mensal: a definir com o cliente após estimativa de volume de uso.

---

## 8. Redirecionamento para Telas

> ✅ **Decisão do time** — O bot exibirá botões/links de ação ao final de respostas relevantes. A estratégia de deep links será mapeada pelo time durante o desenvolvimento.

- [x] O bot exibe um **botão de ação** ao final da resposta quando a pergunta implica uma ação no portal (ex: "Ver meus pedidos", "Rastrear cartões").
- [x] O link redireciona para a tela correspondente dentro do app — o mapeamento de rotas será levantado pelo time na fase de desenvolvimento.
- [x] O bot omite o link se o usuário não tiver perfil para acessar a tela.
- [x] Para o MVP, o redirecionamento **apenas abre a tela** — pré-preenchimento de dados pode ser avaliado em fases posteriores.

---

## 9. Base de Conhecimento (RAG — Bedrock Knowledge Bases)

> ✅ **Decisão do time** — A estratégia de RAG (chunking, embeddings, retrieval, re-ranking) será desenhada pelo time. Fonte e comportamento de fallback definidos abaixo.

- [x] **Fonte única**: os 22 arquivos `.md` da pasta `docs` — sem outras fontes no MVP.
- [x] **Re-indexação**: será acionada pelo time sempre que um documento for atualizado — processo a ser automatizado em fase posterior.
- [x] O bot responde **estritamente com base nos docs** — sem conhecimento geral externo, para evitar alucinações fora do escopo do portal.
- [x] **Fallback**: quando não encontrar resposta, o bot informa que não sabe e orienta o usuário a contatar o suporte — sem escalada humana automatizada no MVP.

---

## 10. Comportamento e Tom

> ✅ **Decisão do time** — Definições de UX conversacional a serem refinadas durante o design, com base nas diretrizes abaixo.

- [x] **Idioma**: português do Brasil — sem suporte a outros idiomas no MVP.
- [x] **Tom**: objetivo e prestativo — respostas curtas para consultas simples, passo a passo para dúvidas procedimentais.
- [x] **Contexto de sessão**: o bot mantém contexto dentro da mesma conversa (ex: se o usuário mencionou um colaborador, o bot o considera nas próximas perguntas).
- [x] **Histórico entre sessões**: não será persistido no MVP — dado que AgentCore Memory não está disponível em sa-east-1; solução alternativa (ex: DynamoDB) será avaliada em fase posterior.
- [ ] Nome e identidade visual do bot: a definir com o cliente.

---

## 11. Operação, Privacidade e Métricas

> ✅ **Decisão do time** — Monitoramento via AgentCore Observability (disponível em sa-east-1). Privacidade seguirá o princípio de mínimo necessário.

- [x] **Monitoramento**: AgentCore Observability para volume de interações, latência e custo por sessão.
- [x] **Dados de API**: dados de colaboradores e pedidos retornados pela API **não são persistidos** — usados apenas em memória durante a resposta, descartados em seguida (LGPD).
- [x] **Transcrições**: não armazenadas no MVP — apenas logs técnicos anonimizados para debugging.
- [x] **SLA de resposta**: meta de até **5 segundos** para respostas simples; respostas híbridas (RAG + API) podem levar até 10 segundos — a validar com testes de carga.
- [ ] Requisitos específicos de LGPD/auditoria do cliente: a confirmar.

---

## 12. Prazo e Escopo do MVP

> ✅ **Decisão do time** — Fases propostas abaixo. Prazo a confirmar com o cliente.

- [x] **Fase 1 — RAG**: bot responde dúvidas procedimentais com base nos 22 docs. Sem integração de API.
- [x] **Fase 2 — Híbrido**: integração de sessão via cookie + endpoints GET para dados em tempo real (colaboradores, pedidos, rastreio).
- [x] **Fase 3 — Ação**: redirecionamento para telas do portal com botões contextuais.
- [ ] Prazo de cada fase: a confirmar com o cliente.
- [ ] Ponto de contato técnico do cliente para acesso ao ambiente e APIs: **Carlos** (mencionado — confirmar disponibilidade).

---

## Resumo das Decisões

Ao final da reunião, preencher:

| Tema | Decisão |
|---|---|
| Canal do bot | ✅ Dentro do app Meu Alelo (webview) — mobile e web |
| Autenticação | ✅ Cookies injetados pelo app nativo — `accessToken`, `CLIENT_ID`, `CLIENT_SECRET` |
| Expiração de token | ✅ TTL ~300s — refresh automático via 401 + OAuth2 |
| Perfil do usuário | ✅ `GET /profile` → `functions[].functionType` |
| Backend server-side ou client-side | ❓ A confirmar com Carlos |
| Domínio do bot (impacta cookies httpOnly) | ❓ A confirmar com Carlos |
| Guardrails por perfil | ✅ Decisão do time — tabela de acesso definida na seção 5 |
| Escrita bloqueada | ✅ Bot somente GET — sem POST/PUT/DELETE |
| APIs documentadas | ✅ Swagger disponível — ver `03_api-referencia.md` |
| Rate limiting nas APIs | ❓ A confirmar |
| Sandbox/homologação | ❓ A confirmar com Carlos |
| Infraestrutura | ✅ AWS sa-east-1 (São Paulo) |
| RAG | ✅ Bedrock Knowledge Bases — 22 docs `.md` como única fonte |
| Agente | ✅ Bedrock Agents — orquestração nativa |
| Guardrails técnicos | ✅ Bedrock Guardrails |
| Memória entre sessões | ✅ Não persiste no MVP — AgentCore Memory indisponível em sa-east-1 |
| Modelo LLM | ✅ Claude Haiku (triagem) + Claude Sonnet (respostas complexas) |
| Throughput | ✅ On-demand no MVP |
| Monitoramento | ✅ AgentCore Observability |
| Dados de API (LGPD) | ✅ Não persistidos — descartados após a resposta |
| Transcrições | ✅ Não armazenadas no MVP |
| Redirecionamento | ✅ Botão contextual por resposta — rotas mapeadas pelo time |
| Fallback sem resposta | ✅ Informa que não sabe + orienta ao suporte |
| Idioma | ✅ Português do Brasil |
| Fases do MVP | ✅ Fase 1 RAG → Fase 2 Híbrido → Fase 3 Ação |
| Prazo por fase | ❓ A confirmar com o cliente |
| Budget mensal | ❓ A confirmar com o cliente |
| Nome/identidade do bot | ❓ A confirmar com o cliente |
| Ponto de contato técnico | ⚠️ Carlos (confirmar disponibilidade) |

---

## Próximos Passos

- [ ] ___________________________
- [ ] ___________________________
- [ ] ___________________________
