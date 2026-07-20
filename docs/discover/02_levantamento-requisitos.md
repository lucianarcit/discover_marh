# Checklist de Levantamento — Bot Alelo

Reunião com: ___________________________
Data: ___________________________
Participantes: ___________________________

---

> **Contexto já levantado**
> O bot anterior foi descontinuado por alto custo (modelo caro, mesmo usando cache semântico + Elastic). O novo bot deve ser um **agente consultivo híbrido**: responde dúvidas procedimentais via RAG (22 docs) e também busca dados reais do usuário logado via APIs do portal, respeitando rigorosamente os perfis de acesso. A sessão do usuário deve ser recuperada via cookies.

---

## 1. Canal e Ambiente

- [ ] O bot vai viver **dentro do portal Alelo** (widget embutido) ou em canal externo (WhatsApp, Teams, página separada)?
- [ ] O usuário já estará **logado no portal** ao abrir o bot, ou o bot precisa autenticar separadamente?
- [ ] O bot precisa funcionar em **mobile**?

**Notas:**
```
Só dentro do aplicativo.  de acordo com perfil (role) de cada usuário.
Sim com o usuário autenticado
Mobile / web


```

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

> Ponto central: o bot não é apenas um FAQ. É um agente consultivo que combina conhecimento dos docs com dados reais do usuário. Precisamos definir quando usa cada fonte.

- [ ] Para cada tipo de pergunta, qual é o comportamento esperado?

  | Tipo de pergunta | Comportamento esperado |
  |---|---|
  | "Como faço um pedido?" (procedural) | Só RAG |
  | "Quais colaboradores eu tenho?" (consulta) | Só API |
  | "Como cadastro um colaborador?" + "Quem já está cadastrado?" | RAG + API |
  | "Qual o status do meu último pedido?" | Só API |

  - [ ] Essa tabela está correta ou há outros comportamentos esperados?

- [ ] Quando RAG e API são usados juntos, qual é a **ordem de apresentação**? (ex: primeiro explica o processo, depois mostra os dados)
- [ ] O bot deve deixar **explícito para o usuário** quando está buscando dados reais vs. explicando um processo?
- [ ] Se a API retornar erro ou estiver fora do ar, o bot responde só com o doc ou informa a indisponibilidade?

**Notas:**
```



```

---

## 4. Integração com APIs do Portal

> ✅ **Parcialmente resolvido** — APIs são REST, somente leitura (GET), base UAT confirmada. Módulos sem endpoint ainda precisam ser verificados.

**Base URL:** `GET /alelo/uat/cardholders-hr-management/v1` (HRM)

**Endpoints confirmados:**

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

- [x] APIs são **REST**
- [x] ⚠️ **A API NÃO é somente leitura** — possui POST, PUT e DELETE confirmados (ver tabela abaixo)
- [ ] Existe **Swagger / Postman collection** com todos os contratos? *(solicitar ao Carlos)*
- [ ] Existe **rate limiting**? Qual o limite de requisições por minuto/hora?
- [ ] Ambiente de **homologação/sandbox** disponível para o bot durante desenvolvimento?
- [ ] Módulos ainda sem endpoint confirmado:

  | Módulo | API disponível? |
  |---|---|
  | Relatórios | A confirmar |
  | Contratos | A confirmar |
  | Interlocutores / Usuários | A confirmar — `GET /profile` pode cobrir? |
  | Locais de entrega / Filiais | Parcial — `GET /places` (confirmar se retorna filiais) |

**Notas:**
```
- Solicitar Postman collection ou Swagger ao Carlos.
- Confirmar se há rate limiting nas APIs.
- Confirmar ambiente de sandbox separado do UAT.


```

---

## 5. Guardrails e Controle de Acesso

> Ponto de alta atenção: o bot precisa respeitar exatamente o que cada perfil pode ver e fazer — nem mais, nem menos.

- [ ] O bot deve aplicar as mesmas restrições de perfil que o portal aplica?
  - Perfil **Financeiro**: só pode ver relatórios e faturas — o bot não deve responder sobre pedidos ou cadastro.
  - Perfil **Operação**: pode fazer pedidos, mas não configura benefícios.
  - Perfil **Gerenciamento** e **Decisão**: acesso amplo.
  - [ ] Essa lógica está correta ou há exceções?

- [ ] Quem **define e mantém** as regras de guardrail? Time técnico, produto ou negócio?
- [ ] O bot deve **explicar ao usuário** por que não pode responder algo? (ex: "Essa ação não está disponível para o seu perfil.")
- [ ] Existe alguma ação que deve ser **completamente bloqueada** no bot, independente do perfil? (ex: excluir colaboradores, cancelar contratos)
- [ ] O bot deve registrar em **log de auditoria** quais dados foram acessados por qual usuário?
- [ ] Se um usuário tentar obter dados de **outro contrato ou empresa** que não é o dele, como o bot deve reagir?
- [ ] Existe necessidade de aprovação humana para alguma ação antes de o bot executá-la?

**Notas:**
```



```

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

> O bot anterior foi descontinuado por alto custo mesmo com cache. Com Bedrock em sa-east-1, a estratégia de otimização muda.

- [ ] Qual é o **budget mensal** aceitável para o bot? Existe um teto de custo por interação?
- [ ] O bot anterior usou **cache semântico + Elastic Cache**. Com Bedrock Knowledge Bases, o cache semântico é nativo — confirmar se substitui a necessidade de Elastic.
- [ ] Qual era o **modelo LLM** do bot anterior? (para evitar repetir o mesmo erro de custo)
- [ ] Qual modelo Bedrock usar? Sugestão de hierarquia por custo: **Claude Haiku** para triagem → **Claude Sonnet** para respostas complexas.
- [ ] O volume esperado de interações é conhecido? (ex: X usuários/dia, Y mensagens/sessão) — impacta diretamente o custo e a escolha de Provisioned Throughput vs. on-demand.
- [ ] Usar **Provisioned Throughput** (disponível em sa-east-1) para cargas previsíveis ou manter on-demand?

**Notas:**
```



```

---

## 8. Redirecionamento para Telas

- [ ] Ao sugerir uma ação, o bot exibe um **botão/link** que leva para a tela correta?
- [ ] Existe uma lista de **deep links / rotas** do portal para cada módulo? (ex: `/pedidos/novo`, `/cartoes/rastreio`)
- [ ] O redirecionamento apenas abre a tela, ou o bot também deve **pré-preencher dados**? (ex: já filtrar pelo colaborador mencionado na conversa)
- [ ] Se o usuário não tiver permissão para acessar a tela, o bot deve **omitir o link** ou exibi-lo com aviso?

**Notas:**
```



```

---

## 9. Base de Conhecimento (RAG — Bedrock Knowledge Bases)

- [ ] Os 22 docs da pasta `docs` são a **única fonte de verdade**, ou há outros materiais (FAQs, e-mails, PDFs, atendimento anterior)?
- [ ] Com que frequência a documentação é **atualizada**? Quem é responsável — time técnico ou negócio?
- [ ] Quando o doc for atualizado, o bot deve ser **re-indexado automaticamente** ou manualmente?
- [ ] O bot pode usar **conhecimento geral** (ex: "o que é boleto bancário") ou responde estritamente pelos docs?
- [ ] Se o bot **não souber responder**, o que deve fazer?
  - [ ] Escalar para atendimento humano
  - [ ] Exibir contato de suporte
  - [ ] Informar que não sabe e encerrar

**Notas:**
```



```

---

## 9. Comportamento e Tom

- [ ] O bot tem **nome e personalidade** definidos ou está em aberto?
- [ ] As respostas devem ser **curtas e diretas** ou detalhadas (passo a passo com contexto)?
- [ ] O bot deve suportar **múltiplos idiomas** ou apenas português?
- [ ] Deve haver **histórico de conversa** persistido entre sessões?
- [ ] O bot deve manter o **contexto dentro de uma sessão**? (ex: usuário mencionou um colaborador antes — o bot lembra nas próximas perguntas)

**Notas:**
```



```

---

## 10. Operação, Privacidade e Métricas

- [ ] Haverá um **painel de monitoramento**? (perguntas sem resposta, satisfação, volume, custo por interação)
- [ ] Existe requisito de **LGPD**: o bot pode armazenar transcrições de conversa? Por quanto tempo?
- [ ] Dados de colaboradores retornados pela API podem ser **logados** para debugging, ou devem ser descartados após a resposta?
- [ ] Há algum **SLA de resposta** esperado? (ex: responder em menos de X segundos — impacta escolha de modelo e estratégia de cache)

**Notas:**
```



```

---

## 11. Prazo e Escopo do MVP

- [ ] Qual é o **prazo** esperado para a primeira entrega?
- [ ] Existe um **MVP definido**? Sugestão de fases para validar:
  - [ ] Fase 1: RAG puro (responde dúvidas procedimentais pelos 22 docs)
  - [ ] Fase 2: integração de sessão + APIs de consulta (ex: listar colaboradores, status de pedido)
  - [ ] Fase 3: redirecionamento para telas com contexto
  - [ ] O cliente concorda com essa sequência ou tem outra ordem de prioridade?
- [ ] Quem é o **responsável técnico** no lado do cliente para acesso às APIs, cookies e ambiente do portal?

**Notas:**
```



```

---

## Resumo das Decisões

Ao final da reunião, preencher:

| Tema | Decisão |
|---|---|
| Canal do bot | ✅ Dentro do app (webview) — mobile e web |
| Cookie / mecanismo de sessão | ✅ App nativo injeta cookies (`accessToken`, `CLIENT_ID`, `CLIENT_SECRET`, etc.) |
| Expiração de token | ✅ TTL ~300s — refresh via 401 + OAuth2 automático |
| Endpoint de validação de sessão | ⚠️ Candidato: `GET /profile` — confirmar campos retornados |
| Backend server-side ou client-side | ❓ A confirmar com Carlos |
| Domínio do bot (impacta cookies httpOnly) | ❓ A confirmar com Carlos |
| Perfis respeitados com guardrails? | ❓ A confirmar |
| Ações bloqueadas independente de perfil | ❓ A confirmar |
| APIs disponíveis e documentadas? | ✅ Swagger confirmado — ver `03_api-referencia.md` |
| Bot lê apenas ou também escreve via API? | ⚠️ API tem POST/PUT/DELETE — definir quais o bot pode usar |
| Rate limiting nas APIs | ❓ A confirmar |
| Sandbox/homologação disponível | ❓ A confirmar |
| Deep links disponíveis? | ❓ A confirmar |
| Fontes além dos 22 docs? | ❓ A confirmar |
| Fallback sem resposta | ❓ A confirmar |
| Budget / teto de custo | ❓ A confirmar |
| Infraestrutura | ✅ AWS sa-east-1 (São Paulo) |
| Bedrock Guardrails disponível? | ✅ Sim — estratégia viável |
| Bedrock Knowledge Bases disponível? | ✅ Sim — RAG nativo |
| Bedrock Agents disponível? | ✅ Sim — orquestração nativa |
| AgentCore Memory disponível? | ❌ Não — solução alternativa necessária |
| Modelo LLM (Bedrock) | ❓ Confirmar quais modelos disponíveis em sa-east-1 |
| Provisioned Throughput vs. on-demand | ❓ A definir com base no volume esperado |
| MVP — fases acordadas | ❓ A confirmar |
| Prazo | ❓ A confirmar |
| Ponto de contato técnico do cliente | ⚠️ Carlos (mencionado) |

---

## Próximos Passos

- [ ] ___________________________
- [ ] ___________________________
- [ ] ___________________________
