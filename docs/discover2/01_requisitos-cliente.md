# Requisitos — Agente Consultivo MARH

Consolidação fiel da especificação do cliente:
`docs/cliente/00_Agente_Consultivo_MARH.html`

Cada requisito referencia a seção correspondente da especificação (Spec §N).

**Categorias de conteúdo:**
- **Requisito confirmado** — textual da especificação
- **Exemplo do cliente** — apresentado como exemplo, não como regra fechada
- **Resposta padronizada** — mensagem aprovada pelo cliente
- **Decisão pendente** — não definida pelo cliente
- **Proposta técnica** — não originada na especificação
- **Inferência** — derivada indiretamente do texto

---

## 1. Objetivo (Spec §1)

**Requisito confirmado:**

Permitir que o interlocutor de RH consulte informações da empresa selecionada no Espaço RH por meio de um agente de IA conversacional.

O objetivo principal do agente é entregar valor ao usuário por meio de consultas rápidas, simples e contextualizadas, reduzindo a necessidade de navegação manual em diferentes telas do MARH.

O agente deve responder apenas perguntas consultivas sobre:

- Colaboradores.
- Pedidos.
- Último pedido.
- Pedidos por status.
- Rastreamento de cartão de colaborador.
- Dúvidas sobre a feature MARH.

O agente não deve criar, alterar, cancelar, excluir, aprovar, reprovar ou executar qualquer ação transacional.

---

## 2. Referências (Spec §2)

**Requisito confirmado:**

As documentações abaixo devem ser usadas como referência de domínio e entendimento das jornadas existentes:

- MARH: Espaço RH no app Meu Alelo.
- API `ma-hr-orch`.
- Gestão de Pedidos MARH.
- Gestão de Colaboradores MARH.

Importante:

- O agente deve consumir a API `ma-hr-orch`.
- A API `ma-hr-orch` será responsável por orquestrar as integrações necessárias.
- A API `ma-hr-orch` será responsável por validar token, permissão do interlocutor, empresa selecionada e demais validações de segurança aplicáveis.
- O agente deve permanecer consultivo neste primeiro momento, focando em entregar respostas úteis para o usuário sem executar ações transacionais.

---

## 3. Disponibilização do agente (Spec §3)

**Requisito confirmado:**

O agente deve estar disponível por meio de uma API REST, para ser consumido pelo app Meu Alelo dentro da jornada do Espaço RH.

Fluxo esperado:

```
App Meu Alelo → API MARH → Agente IA MARH → ma-hr-orch (ou Markdown) → Agente → API MARH → App
```

Responsabilidades:

- O app envia a mensagem do usuário para a API MARH.
- A API MARH encaminha a solicitação para o agente.
- O agente interpreta a intenção do usuário.
- O agente identifica se a mensagem exige uma consulta ou apenas uma resposta informativa.
- Quando a intenção for consultiva, o agente consulta a API `ma-hr-orch`.
- Quando a intenção for informativa sobre a feature MARH, o agente consulta o arquivo Markdown de conhecimento.
- A resposta retorna para a API MARH e depois para o app.

---

## 4. Responsabilidades da API ma-hr-orch (Spec §4)

**Requisito confirmado:**

A API `ma-hr-orch` será a camada responsável por centralizar as regras técnicas e de segurança das consultas realizadas pelo agente.

Responsabilidades esperadas:

- Validar o token do usuário.
- Validar se o usuário é interlocutor da empresa.
- Validar se o usuário possui permissão para acessar os dados da empresa selecionada.
- Validar FNP, prova de vida ou demais validações de segurança aplicáveis.
- Garantir que a consulta seja feita no contexto da empresa selecionada.
- Orquestrar chamadas para os sistemas necessários.
- Retornar ao agente apenas as informações que podem ser exibidas ao usuário.
- Padronizar erros de permissão, segurança, ausência de dados e indisponibilidade.

O agente não deve implementar diretamente regras de autorização, permissão, validação de token ou validações técnicas dos sistemas internos.

---

## 5. Contexto obrigatório da empresa selecionada (Spec §5)

**Requisito confirmado:**

A API MARH deve enviar para o agente o contexto da empresa selecionada pelo usuário no app.

Esse contexto deve ser usado em todas as consultas.

Parâmetros esperados:

- Identificador da empresa selecionada.
- Identificador do contrato, quando necessário.
- Identificador do usuário/interlocutor autenticado, quando necessário.
- Mensagem enviada pelo usuário.
- Dados mínimos necessários para garantir que a consulta seja feita no contexto correto.

Regras:

- O agente não deve decidir sozinho qual empresa consultar.
- O agente deve considerar sempre a empresa selecionada recebida pela API MARH.
- O agente deve repassar o contexto da empresa selecionada para a `ma-hr-orch`.
- O usuário não deve conseguir trocar a empresa da consulta digitando outro CNPJ, contrato ou nome de empresa no chat.
- Se a empresa selecionada não for enviada, o agente deve retornar erro orientativo.
- Se o usuário solicitar dados de outra empresa, o agente deve orientar que a consulta considera apenas a empresa selecionada no app.

**Resposta padronizada** quando faltar empresa selecionada:

> Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente.

---

## 6. Fonte de conhecimento em Markdown (Spec §6)

**Requisito confirmado:**

O agente deve possuir um arquivo Markdown de conhecimento para responder dúvidas sobre a feature MARH e sobre o funcionamento do próprio agente.

Esse arquivo deve ser usado como fonte oficial para respostas informativas, quando a pergunta do usuário não exigir consulta a dados da empresa.

**Exemplos do cliente** — perguntas respondidas com base no Markdown:

- "O que posso fazer?"
- "Quais informações posso consultar?"
- "Como faço para fazer um pedido?"
- "Como faço para consultar um pedido?"
- "Como faço para consultar um colaborador?"
- "Consigo rastrear cartões?"
- "Você consegue cancelar pedido?"
- "Você consegue alterar dados de um colaborador?"
- "Você consulta dados de qualquer empresa?"
- "Preciso selecionar uma empresa para usar o agente?"
- "O agente substitui o portal web?"
- "O que é o MARH?"
- "O que é o Espaço RH?"
- "Quais tipos de pergunta posso fazer?"

Regras:

- O agente deve identificar a intenção da mensagem do usuário.
- Se a intenção for consultiva, deve realizar a consulta na `ma-hr-orch`.
- Se a intenção for uma dúvida sobre a feature MARH, deve responder usando o arquivo Markdown de conhecimento.
- Se a pergunta não estiver contemplada no Markdown, o agente deve informar que não possui essa informação.
- O agente não deve inventar capacidades que não estejam descritas no Markdown.
- O Markdown deve conter todas as informações que o agente está autorizado a responder sobre a feature MARH.
- O Markdown deve ser versionado junto com a evolução da feature.
- O Markdown deve ser revisado sempre que o escopo do agente for alterado.

**Resposta padronizada** quando a informação não existir no Markdown:

> Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões.

---

## 7. Classificação de intenção (Spec §7)

**Requisito confirmado:**

Antes de responder, o agente deve classificar a intenção da mensagem do usuário.

### 7.1 Intenção CONSULTIVA

Quando o usuário deseja consultar dados da empresa selecionada.

**Exemplos do cliente:**

- "Consultar colaborador Wesley Fabrete."
- "Consultar pedido 342671."
- "Qual foi o último pedido?"
- "Quais são os últimos pedidos com status pago?"
- "Rastrear cartão do colaborador 123.456.789-00."

Comportamento esperado:

- Identificar a intenção.
- Identificar os dados necessários para a consulta.
- Chamar a `ma-hr-orch`.
- Responder com base nos dados retornados.
- Tratar ausência de dados.
- Não executar ações transacionais.

### 7.2 Intenção INFORMATIVA_MARH

Quando o usuário pergunta sobre o que o agente faz, como funciona ou quais são suas limitações.

**Exemplos do cliente:**

- "O que posso fazer?"
- "Como faço para fazer um pedido?"
- "Você pode cancelar pedido?"
- "Você consegue alterar um colaborador?"
- "Quais perguntas posso fazer?"
- "Você consulta qualquer empresa?"

Comportamento esperado:

- Responder com base no arquivo Markdown de conhecimento.
- Explicar capacidades e limitações.
- Não consultar a `ma-hr-orch` se a pergunta for apenas informativa.

### 7.3 Intenção FORA_DO_ESCOPO

Quando o usuário pede algo que o agente não pode fazer.

**Exemplos do cliente:**

- "Cancela o pedido 342671."
- "Altera o endereço do colaborador."
- "Cria um novo pedido."
- "Remove esse colaborador."
- "Paga o pedido."
- "Emite um novo cartão."

**Resposta padronizada:**

> No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH.

---

## 8. Escopo do MVP (Spec §8)

### 8.1 Consultar colaborador

**Requisito confirmado:**

O usuário pode consultar um colaborador pelo nome ou CPF.

**Exemplo do cliente:**

> Consultar colaborador Wesley Fabrete.

Comportamento esperado:

- Buscar colaborador na empresa selecionada por meio da `ma-hr-orch`.
- Exibir os principais dados disponíveis.
- Se houver mais de um resultado, pedir para o usuário escolher.
- Se não encontrar, informar que nenhum colaborador foi localizado.
- Quando fizer sentido, retornar um elemento de navegação para a tela do colaborador.

**Exemplo de resposta do cliente:**

```markdown
Encontrei o colaborador **Wesley Fabrete**.

Local de entrega: **empresa**
Produto: **Alelo Pod**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_COLLABORATOR_DETAIL}&isModal=false&showNavbar=false&authRequired=true)
```

### 8.2 Consultar pedido

**Requisito confirmado:**

O usuário pode consultar um pedido específico pelo número.

**Exemplo do cliente:**

> Consultar pedido 342671.

Comportamento esperado:

- Buscar informações do pedido na empresa selecionada por meio da `ma-hr-orch`.
- Exibir status atual, data, produto, valor, quantidade de colaboradores e cartões quando disponíveis.
- Exibir etapas do pedido quando disponíveis.
- Não permitir ações como cancelar, pagar ou alterar pedido.
- Quando fizer sentido, retornar um elemento de navegação para a tela do pedido.

**Exemplo de resposta do cliente:**

```markdown
Encontrei o pedido **342671**.

Status: **Pago**
Data do pedido: **dd/mm/aaaa**
Produto: **Alelo Pod**
Colaboradores: **6**
Cartões: **6**
Valor total: **R$ 90,00**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_DETAIL}&isModal=false&showNavbar=false&authRequired=true)
```

### 8.3 Consultar último pedido

**Requisito confirmado:**

O usuário pode perguntar qual foi o último pedido da empresa selecionada.

**Exemplo do cliente:**

> Qual foi o último pedido?

Comportamento esperado:

- Consultar os pedidos da empresa selecionada por meio da `ma-hr-orch`.
- Retornar o pedido mais recente disponível.
- Se não houver ordenação confiável nos dados, informar que está exibindo o pedido mais recente retornado pela consulta.
- Quando fizer sentido, retornar um elemento de navegação para a tela do pedido.

**Exemplo de resposta do cliente:**

```markdown
O último pedido encontrado foi o **342671**.

Status: **Pago**
Data do pedido: **dd/mm/aaaa**
Produto: **Alelo Pod**
Valor total: **R$ 90,00**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_DETAIL}&isModal=false&showNavbar=false&authRequired=true)
```

### 8.4 Consultar últimos pedidos por status

**Requisito confirmado:**

O usuário pode consultar pedidos filtrando por status.

**Exemplo do cliente:**

> Quais são os últimos pedidos com status pago?

Também deve aceitar variações como:

- "Quais são os últimos pedidos pendentes?"
- "Mostre os últimos pedidos cancelados."
- "Quais pedidos estão em processamento?"

Comportamento esperado:

- Identificar o status informado pelo usuário.
- Consultar os pedidos da empresa selecionada por meio da `ma-hr-orch`.
- Listar os últimos pedidos com aquele status.
- Se o status não for reconhecido, pedir esclarecimento.
- Se não houver pedidos no status informado, responder de forma amigável.
- Quando fizer sentido, retornar um elemento de navegação para a lista de pedidos filtrada ou para pedidos específicos.

> **Inferência — não textual da especificação:** os status apresentados são exemplos e não constituem enumeração técnica definitiva, pendente do contrato da ma-hr-orch.

**Exemplo de resposta do cliente:**

```markdown
Encontrei **3 pedidos** com status **pago**.

1. Pedido **342671** — dd/mm/aaaa — R$ 90,00
2. Pedido **342650** — dd/mm/aaaa — R$ 120,00
3. Pedido **342610** — dd/mm/aaaa — R$ 80,00

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_LIST_WITH_STATUS_FILTER}&isModal=false&showNavbar=false&authRequired=true)
```

> **Nota editorial — não textual da especificação:** os valores são exemplos conceituais e não representam dados reais.

### 8.5 Rastrear cartão do colaborador

**Requisito confirmado:**

O usuário pode solicitar o rastreamento do cartão de um colaborador pelo CPF.

**Exemplo do cliente:**

> Rastrear cartão do colaborador 123.456.789-00.

Comportamento esperado:

- Avaliar, junto ao time técnico, se a `ma-hr-orch` consegue disponibilizar uma consulta de rastreamento por CPF do colaborador.
- Caso a consulta direta por CPF não esteja disponível, o agente deve solicitar uma informação complementar, como o número do pedido.
- Quando houver fonte disponível por meio da `ma-hr-orch`, buscar rastreamento do cartão vinculado ao colaborador.
- Exibir status, data da última atualização, endereço de entrega e código de rastreio quando disponíveis.
- Não inventar prazo, transportadora ou status.
- Quando fizer sentido, retornar um elemento de navegação para a tela de rastreamento.

**Resposta padronizada** quando precisar do número do pedido:

> Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento.

**Exemplo de resposta do cliente** com rastreamento:

```markdown
Encontrei informações de rastreamento para o pedido **342671**.

Status: **Entrega em andamento**
Última atualização: **dd/mm/aaaa**
Código de rastreio: **123456789**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_CARD_TRACKING}&isModal=false&showNavbar=false&authRequired=true)
```

---

## 9. Desejável: elemento de navegação para o frontend (Spec §9)

**Requisito confirmado:**

Nas respostas em que fizer sentido, o agente poderá retornar um elemento de navegação para que o frontend identifique e renderize um componente visual de acesso rápido.

Esse elemento deve permitir direcionar o usuário para uma tela relacionada ao resultado da consulta, como:

- Detalhe do pedido.
- Detalhe do colaborador.
- Lista de pedidos.
- Lista de pedidos filtrada por status.
- Rastreamento de cartões.
- Jornada de criação de pedido, quando a resposta for apenas orientativa.

O elemento de navegação deve usar o formato:

```markdown
[list_navigation](meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true)
```

Onde:

- `meualelo://app/webview` é o deeplink responsável por abrir uma webview dentro do app.
- `url={URL_ENCODED}` deve receber a URL da webview em formato URL encoded.
- `isModal=false` indica que a webview não será aberta como modal.
- `showNavbar=false` indica que a navbar nativa não será exibida.
- `authRequired=true` indica que a abertura exige usuário autenticado.

**Exemplo do cliente** — URL original:

```text
https://meualelo-webviews.alelo.com.br/#/card-tracking
```

**Exemplo do cliente** — mesma URL em formato encoded:

```text
https%3A%2F%2Fmeualelo-webviews.alelo.com.br%2F%23%2Fcard-tracking
```

**Exemplo do cliente** — elemento final de navegação:

```markdown
[list_navigation](meualelo://app/webview?url=https%3A%2F%2Fmeualelo-webviews.alelo.com.br%2F%23%2Fcard-tracking&isModal=false&showNavbar=false&authRequired=true)
```

Regras:

- O elemento de navegação deve ser retornado apenas quando houver relação direta com a resposta.
- O texto da resposta deve continuar compreensível mesmo que o frontend não renderize o componente visual.
- O frontend deve interpretar o elemento `[list_navigation]` e decidir qual componente visual será exibido.
- O deeplink deve abrir uma webview no app Meu Alelo.
- A URL da webview deve ser enviada em formato URL encoded.
- O agente não deve inventar identificadores.
- O link só deve ser retornado quando o identificador necessário estiver disponível.
- A URL final da webview deve ser definida pela API MARH, pelo frontend ou pela camada responsável pela navegação, conforme estratégia técnica.
- O elemento de navegação não deve executar ações transacionais automaticamente.
- O elemento deve apenas direcionar o usuário para uma tela onde ele possa consultar ou continuar uma jornada oficial.
- Links para ações transacionais só devem abrir a jornada oficial, sem executar a ação automaticamente.

**Requisito confirmado pelo cliente:**

A URL final da webview deve ser definida pela API MARH, pelo frontend ou pela camada responsável pela navegação, conforme a estratégia técnica adotada.

**Alternativas previstas pelo cliente:**

- API MARH.
- Frontend.
- Camada responsável pela navegação.

**Decisão pendente:**

Definir qual das camadas previstas será responsável pela URL final.

**Proposta técnica interna — não definida pelo cliente:**

- Uso de templates determinísticos, caso a camada selecionada seja o agente.
- Detalhes de implementação e validação dos templates.

**Exemplos conceituais do cliente** — seis destinos de navegação:

```markdown
[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_DETAIL}&isModal=false&showNavbar=false&authRequired=true)

[list_navigation](meualelo://app/webview?url={URL_ENCODED_COLLABORATOR_DETAIL}&isModal=false&showNavbar=false&authRequired=true)

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_LIST}&isModal=false&showNavbar=false&authRequired=true)

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_LIST_WITH_STATUS_FILTER}&isModal=false&showNavbar=false&authRequired=true)

[list_navigation](meualelo://app/webview?url={URL_ENCODED_CARD_TRACKING}&isModal=false&showNavbar=false&authRequired=true)

[list_navigation](meualelo://app/webview?url={URL_ENCODED_NEW_ORDER}&isModal=false&showNavbar=false&authRequired=true)
```

**Exemplo de resposta do cliente** — navegação para pedido:

```markdown
Encontrei o pedido **342671**.

Status: **Pago**
Data do pedido: **dd/mm/aaaa**
Valor total: **R$ 90,00**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_ORDER_DETAIL}&isModal=false&showNavbar=false&authRequired=true)
```

**Exemplo de resposta do cliente** — navegação para colaborador:

```markdown
Encontrei o colaborador **Wesley Fabrete**.

Local de entrega: **empresa**
Produto: **Alelo Pod**

[list_navigation](meualelo://app/webview?url={URL_ENCODED_COLLABORATOR_DETAIL}&isModal=false&showNavbar=false&authRequired=true)
```

**Exemplo de resposta do cliente** — navegação para rastreamento de cartões:

```markdown
Encontrei informações de rastreamento para o pedido **342671**.

Status: **Entrega em andamento**
Última atualização: **dd/mm/aaaa**

[list_navigation](meualelo://app/webview?url=https%3A%2F%2Fmeualelo-webviews.alelo.com.br%2F%23%2Fcard-tracking&isModal=false&showNavbar=false&authRequired=true)
```

**Exemplo de resposta do cliente** — navegação orientativa para criação de pedido:

```markdown
Eu não consigo criar pedidos pelo chat, mas você pode fazer isso pela jornada oficial do Espaço RH.

[list_navigation](meualelo://app/webview?url={URL_ENCODED_NEW_ORDER}&isModal=false&showNavbar=false&authRequired=true)
```

---

## 10. Principais perguntas suportadas (Spec §10)

**Exemplos do cliente:**

1. Consultar colaborador Wesley Fabrete.
2. Consultar pedido 342671.
3. Qual foi o último pedido?
4. Quais são os últimos pedidos com status XXXX?
5. Rastrear cartão do colaborador 123.456.789-00.
6. O que posso fazer?
7. Como faço para fazer um pedido?
8. Como faço para consultar um colaborador?
9. Consigo rastrear cartões?
10. Você consegue cancelar pedido?

> **Interpretação funcional — não textual da especificação:** as perguntas são exemplos representativos. A aceitação de formulações semanticamente equivalentes deverá ser validada nos testes.

> **Proposta técnica:** utilizar esses exemplos como dataset inicial de avaliação para testes de classificação, testes funcionais e regressão.

---

## 11. Regras de segurança (Spec §11)

**Requisito confirmado:**

O agente deve:

- Consultar apenas dados da empresa selecionada.
- Usar a `ma-hr-orch` como fonte consultiva para dados da empresa.
- Não implementar validação própria de token, permissão de interlocutor, FNP ou prova de vida.
- Considerar que as validações de token, permissão, interlocutor e empresa selecionada são responsabilidade da `ma-hr-orch`.
- Não permitir consulta de outra empresa por CNPJ, pedido ou CPF digitado manualmente.
- Não expor informações técnicas, tokens, integrações internas ou dados sensíveis desnecessários.
- Responder dúvidas sobre a feature MARH apenas com base no Markdown de conhecimento.
- Retornar elementos de navegação apenas para telas permitidas no contexto do Espaço RH.
- Não usar elementos de navegação para acionar operações transacionais automaticamente.

---

## 12. Fora de escopo (Spec §12)

**Requisito confirmado:**

O agente não deve:

1. Criar pedido.
2. Cancelar pedido.
3. Alterar pedido.
4. Editar colaborador.
5. Excluir colaborador.
6. Alterar endereço de entrega.
7. Solicitar segunda via de cartão.
8. Reemitir cartão.
9. Alterar status de pedido ou entrega.
10. Realizar pagamento.
11. Consultar empresa sem permissão.
12. Responder informações sobre capacidades que não estejam previstas no Markdown de conhecimento.
13. Retornar link de navegação para telas fora do contexto autorizado do Espaço RH.

---

## 13. Tratamento de erros (Spec §13)

**Respostas padronizadas pelo cliente:**

### Colaborador não encontrado

> Não encontrei nenhum colaborador com os dados informados para a empresa selecionada.

### Pedido não encontrado

> Não encontrei o pedido informado para a empresa selecionada.

### Status não reconhecido

> Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento.

### Empresa selecionada ausente

> Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente.

### Sem permissão

> Você não tem permissão para consultar informações dessa empresa no Espaço RH.

### Validação de segurança não concluída

> Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente.

### Consulta indisponível

> Não consegui consultar essa informação agora. Tente novamente em alguns instantes.

### Informação não disponível no Markdown

> Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões.

### Navegação indisponível

> Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela.

---

## 14. Critérios de aceite (Spec §14)

| ID | Critério | Seção de origem | Evidência de teste futura |
|---|---|---|---|
| AC-01 | O agente está disponível para consumo via API REST. | §3 | A definir |
| AC-02 | O app consome o agente por meio da API MARH. | §3 | A definir |
| AC-03 | A API MARH envia a empresa selecionada para o agente. | §5 | A definir |
| AC-04 | O agente utiliza a empresa selecionada como contexto obrigatório em todas as consultas. | §5 | A definir |
| AC-05 | O agente consulta dados da empresa por meio da `ma-hr-orch`. | §3, §4 | A definir |
| AC-06 | A `ma-hr-orch` é responsável por validar token, permissão do interlocutor, empresa selecionada e validações de segurança aplicáveis. | §4 | A definir |
| AC-07 | O agente possui um arquivo Markdown de conhecimento sobre a feature MARH. | §6 | A definir |
| AC-08 | O agente responde dúvidas sobre a feature MARH com base no Markdown de conhecimento. | §6 | A definir |
| AC-09 | O agente identifica se a intenção do usuário é consultiva, informativa ou fora do escopo. | §7 | A definir |
| AC-10 | O agente consulta colaborador por nome ou CPF. | §8.1 | A definir |
| AC-11 | O agente consulta pedido por número. | §8.2 | A definir |
| AC-12 | O agente retorna o último pedido disponível da empresa selecionada. | §8.3 | A definir |
| AC-13 | O agente lista últimos pedidos por status. | §8.4 | A definir |
| AC-14 | O agente trata status inválido ou não reconhecido. | §8.4 | A definir |
| AC-15 | O agente informa quando não encontrar dados. | §13 | A definir |
| AC-16 | O agente não executa ações transacionais. | §1, §12 | A definir |
| AC-17 | O agente avalia a possibilidade de rastrear cartão pelo CPF por meio da `ma-hr-orch`. | §8.5 | A definir |
| AC-18 | O agente pode retornar elemento de navegação quando houver destino relacionado à resposta. | §9 | A definir |
| AC-19 | O frontend consegue identificar o elemento `[list_navigation]`, abrir o deeplink `meualelo://app/webview` e carregar a URL encoded da webview correspondente. | §9 | A definir |
| AC-20 | O elemento de navegação não executa ações transacionais automaticamente. | §9 | A definir |
