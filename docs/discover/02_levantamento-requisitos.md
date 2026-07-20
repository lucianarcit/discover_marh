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

> Ponto crítico: o bot deve recuperar o usuário logado via cookies, mas ainda não está claro como isso funciona tecnicamente.

- [ ] Qual é o **nome e estrutura do cookie** de sessão do portal? (ex: `session_token`, JWT, etc.)
- [ ] O backend do bot é **server-side** (pode ler cookies diretamente) ou client-side (precisa que o frontend passe o token)?
- [ ] Existe um **endpoint de validação de sessão** que, dado o cookie, retorna os dados do usuário (id, perfil, contratos)?
- [ ] O token de sessão é suficiente para chamar todas as APIs do portal, ou são necessárias credenciais adicionais para o bot?
- [ ] Como lidar com **sessão expirada** durante uma conversa? O bot deve pedir novo login ou encerrar?
- [ ] O bot terá um **domínio próprio** ou será servido no mesmo domínio do portal? (impacta se o cookie é acessível via `httpOnly`, `SameSite`, etc.)

**Notas:**
```
- Ver como ta autenticação do MeuAlelo, copiar os cookies de la.
- Autenticação já está tratada no outro.
-Falar com Carlos (essas dúvidas)


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

- [ ] Existe uma **API documentada** do portal? (Swagger, Postman collection, ambiente de sandbox?)
- [ ] Quem será o **ponto de contato técnico** do lado do cliente para esclarecer e liberar acesso às APIs?
- [ ] Quais módulos têm API disponível? Confirmar cada um:

  | Módulo | API disponível? | Endpoint conhecido? |
  |---|---|---|
  | Colaboradores (listar, buscar por CPF) | | |
  | Pedidos (listar, status, detalhe) | | |
  | Cartões (rastreio, 2ª via) | | |
  | Relatórios | | |
  | Contratos | | |
  | Interlocutores / Usuários | | |
  | Locais de entrega / Filiais | | |

- [ ] As APIs são **REST**? Existe GraphQL, gRPC ou outro padrão?
- [ ] Existe **rate limiting** nas APIs? (importante para estimar cache necessário)
- [ ] O bot pode apenas **ler** dados via API, ou também pode **escrever** (ex: iniciar um pedido, emitir 2ª via)?
- [ ] Existe ambiente de **homologação/sandbox** separado do produção para o bot usar durante o desenvolvimento?

**Notas:**
```



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

## 6. Custo e Otimização

> O bot anterior foi descontinuado por alto custo mesmo com cache. Precisamos entender os limites e estratégias esperadas.

- [ ] Qual é o **budget mensal** aceitável para o bot? Existe um teto de custo por interação?
- [ ] O bot anterior usou **cache semântico + Elastic Cache**. Essas estratégias devem ser mantidas, aprimoradas ou substituídas?
- [ ] Qual era o **modelo LLM** do bot anterior? (para evitar repetir o mesmo erro de custo)
- [ ] Existe preferência por algum provedor de LLM? (OpenAI, Anthropic, Azure OpenAI, modelo open-source auto-hospedado)
- [ ] O volume esperado de interações é conhecido? (ex: X usuários/dia, Y mensagens/sessão) — impacta diretamente o custo.
- [ ] Perguntas repetidas e frequentes devem ser identificadas e tratadas com cache. **Quem define** o que é "frequente" — monitoramento automático ou lista manual?
- [ ] O cliente tem infraestrutura própria (ex: AWS, Azure) onde o bot será hospedado, ou será um serviço gerenciado?

**Notas:**
```



```

---

## 7. Redirecionamento para Telas

- [ ] Ao sugerir uma ação, o bot exibe um **botão/link** que leva para a tela correta?
- [ ] Existe uma lista de **deep links / rotas** do portal para cada módulo? (ex: `/pedidos/novo`, `/cartoes/rastreio`)
- [ ] O redirecionamento apenas abre a tela, ou o bot também deve **pré-preencher dados**? (ex: já filtrar pelo colaborador mencionado na conversa)
- [ ] Se o usuário não tiver permissão para acessar a tela, o bot deve **omitir o link** ou exibi-lo com aviso?

**Notas:**
```



```

---

## 8. Base de Conhecimento (RAG)

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
| Canal do bot | |
| Cookie / mecanismo de sessão | |
| Endpoint de validação de sessão existe? | |
| Perfis respeitados com guardrails? | |
| Ações bloqueadas independente de perfil | |
| APIs disponíveis e documentadas? | |
| Bot lê apenas ou também escreve via API? | |
| Deep links disponíveis? | |
| Fontes além dos 22 docs? | |
| Fallback sem resposta | |
| Budget / teto de custo | |
| Provedor LLM preferido | |
| MVP — fases acordadas | |
| Prazo | |
| Ponto de contato técnico do cliente | |

---

## Próximos Passos

- [ ] ___________________________
- [ ] ___________________________
- [ ] ___________________________
