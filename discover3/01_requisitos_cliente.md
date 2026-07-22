# 01 — Requisitos do Cliente: Agente Consultivo MARH

> **Princípio:** Este documento contém **exclusivamente** requisitos, regras, critérios de aceite, tratamento de erros, segurança e itens fora do escopo extraídos de:
>
> `docs\cliente\00_Agente_Consultivo_MARH.html`
>
> Nenhum conteúdo cuja única fonte seja `docs\kb`, documentação de API, inventários ou relatórios técnicos está presente aqui.

---

## Legenda de componentes responsáveis

| Valor | Significado |
|---|---|
| AGENTE | Lógica implementada no agente de IA |
| MA_HR_ORCH | Microserviço orquestrador `ma-hr-orch` |
| API_MARH | API que conecta o app ao agente |
| FRONTEND | Camada de frontend (renderização e navegação) |
| APP_MEU_ALELO | App mobile Meu Alelo (cliente final) |
| RESPONSABILIDADE_COMPARTILHADA | Mais de um componente envolvido |
| A_DEFINIR | Não definido na especificação — decisão técnica pendente |

## Legenda de prioridade

| Valor | Significado |
|---|---|
| MUST | Obrigatório — a POC não está completa sem este item |
| SHOULD | Desejável — importante, mas a POC pode operar sem ele |
| COULD | Opcional — entrega de valor adicional |
| NOT_APPLICABLE | Não se aplica (ex.: itens fora do escopo) |
| NOT_DEFINED | Prioridade não estabelecida na especificação |

---

## 1. Requisitos Funcionais (RF)

| ID | Requisito normalizado | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| RF-001 | O agente deve responder perguntas consultivas sobre colaboradores, pedidos, rastreamento de cartão e dúvidas sobre a feature MARH. | 00_Agente_Consultivo_MARH.html | Seção 1 — Objetivo | "O agente deve responder apenas perguntas consultivas sobre: Colaboradores. Pedidos. Último pedido. Pedidos por status. Rastreamento de cartão de colaborador. Dúvidas sobre a feature MARH." | AGENTE | MUST | CONFIRMED |
| RF-002 | O agente deve classificar a intenção de cada mensagem antes de responder: consultiva, informativa sobre MARH ou fora do escopo. | 00_Agente_Consultivo_MARH.html | Seção 7 — Classificação de intenção | "Antes de responder, o agente deve classificar a intenção da mensagem do usuário." | AGENTE | MUST | CONFIRMED |
| RF-003 | Para intenção consultiva, o agente deve chamar a `ma-hr-orch`, responder com base nos dados retornados e tratar ausência de dados sem inventar informações. | 00_Agente_Consultivo_MARH.html | Seção 7.1 — Intenção consultiva | "Chamar a ma-hr-orch. Responder com base nos dados retornados. Tratar ausência de dados. Não executar ações transacionais." | AGENTE | MUST | CONFIRMED |
| RF-004 | Para intenção informativa sobre a feature MARH, o agente deve responder exclusivamente com base no arquivo markdown de conhecimento, sem consultar a `ma-hr-orch`. | 00_Agente_Consultivo_MARH.html | Seções 6 e 7.2 | "Se a intenção for uma dúvida sobre a feature MARH, deve responder usando o arquivo markdown de conhecimento." | AGENTE | MUST | CONFIRMED |
| RF-005 | Para intenção fora do escopo, o agente deve orientar o usuário a acessar a jornada correspondente no Espaço RH, sem executar a ação. | 00_Agente_Consultivo_MARH.html | Seção 7.3 — Intenção fora do escopo | "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH." | AGENTE | MUST | CONFIRMED |
| RF-006 | O agente deve estar disponível por meio de uma API REST para ser consumido pelo app Meu Alelo dentro da jornada do Espaço RH. | 00_Agente_Consultivo_MARH.html | Seção 3 — Disponibilização do agente | "O agente deve estar disponível por meio de uma API REST, para ser consumido pelo app Meu Alelo dentro da jornada do Espaço RH." | RESPONSABILIDADE_COMPARTILHADA | MUST | CONFIRMED |
| RF-007 | O agente deve usar a empresa selecionada no app como contexto obrigatório em todas as consultas. O usuário não pode trocar a empresa digitando outro CNPJ, contrato ou nome no chat. | 00_Agente_Consultivo_MARH.html | Seção 5 — Contexto obrigatório | "O agente deve considerar sempre a empresa selecionada recebida pela API MARH. O usuário não deve conseguir trocar a empresa da consulta digitando outro CNPJ, contrato ou nome de empresa no chat." | AGENTE | MUST | CONFIRMED |
| RF-008 | A API MARH deve enviar ao agente: identificador da empresa selecionada, identificador do contrato (quando necessário), identificador do usuário/interlocutor (quando necessário) e a mensagem do usuário. | 00_Agente_Consultivo_MARH.html | Seção 5 — Parâmetros esperados | "Parâmetros esperados: Identificador da empresa selecionada. Identificador do contrato, quando necessário. Identificador do usuário/interlocutor autenticado, quando necessário. Mensagem enviada pelo usuário." | API_MARH | MUST | CONFIRMED |
| RF-009 | O agente deve repassar o contexto da empresa selecionada para a `ma-hr-orch` em todas as consultas. | 00_Agente_Consultivo_MARH.html | Seção 5 | "O agente deve repassar o contexto da empresa selecionada para a ma-hr-orch." | AGENTE | MUST | CONFIRMED |
| RF-010 | O agente deve possuir um arquivo markdown de conhecimento que cubra todas as informações que está autorizado a responder sobre a feature MARH. Este arquivo deve ser versionado e revisado a cada alteração de escopo. | 00_Agente_Consultivo_MARH.html | Seção 6 — Fonte de conhecimento em Markdown | "O markdown deve conter todas as informações que o agente está autorizado a responder sobre a feature MARH. O markdown deve ser versionado junto com a evolução da feature." | AGENTE | MUST | CONFIRMED |
| RF-011 | O agente deve consultar colaboradores por nome ou CPF na empresa selecionada. Se houver mais de um resultado, deve pedir ao usuário que escolha. Se não encontrar nenhum, deve informar. | 00_Agente_Consultivo_MARH.html | Seção 8.1 — Consultar colaborador | "O usuário pode consultar um colaborador pelo nome ou CPF. Se houver mais de um resultado, pedir para o usuário escolher. Se não encontrar, informar que nenhum colaborador foi localizado." | AGENTE | MUST | CONFIRMED |
| RF-012 | O agente deve consultar um pedido específico pelo número. Deve exibir, quando disponíveis: status, data, produto, valor, quantidade de colaboradores, cartões e etapas. Não deve permitir ações como cancelar, pagar ou alterar. | 00_Agente_Consultivo_MARH.html | Seção 8.2 — Consultar pedido | "O usuário pode consultar um pedido específico pelo número. Exibir status atual, data, produto, valor, quantidade de colaboradores e cartões quando disponíveis. Não permitir ações como cancelar, pagar ou alterar pedido." | AGENTE | MUST | CONFIRMED |
| RF-013 | O agente deve retornar o último pedido disponível da empresa selecionada. Se não houver ordenação confiável nos dados, deve informar que está exibindo o pedido mais recente retornado pela consulta. | 00_Agente_Consultivo_MARH.html | Seção 8.3 — Consultar último pedido | "Se não houver ordenação confiável nos dados, informar que está exibindo o pedido mais recente retornado pela consulta." | AGENTE | MUST | CONFIRMED |
| RF-014 | O agente deve listar os últimos pedidos filtrando por status informado pelo usuário. Se o status não for reconhecido, deve pedir esclarecimento. Se não houver pedidos no status, deve responder de forma amigável. | 00_Agente_Consultivo_MARH.html | Seção 8.4 — Consultar últimos pedidos por status | "Identificar o status informado pelo usuário. Se o status não for reconhecido, pedir esclarecimento. Se não houver pedidos no status informado, responder de forma amigável." | AGENTE | MUST | CONFIRMED |
| RF-015 | O agente deve apresentar informações de rastreamento quando a `ma-hr-orch` disponibilizar dados para a consulta, exibindo somente os campos definidos no documento (status, data da última atualização, endereço de entrega, código de rastreio), sem inventar prazo, transportadora ou status. | 00_Agente_Consultivo_MARH.html | Seção 8.5 — Rastrear cartão do colaborador | "Quando houver fonte disponível por meio da ma-hr-orch, buscar rastreamento do cartão vinculado ao colaborador. Exibir status, data da última atualização, endereço de entrega e código de rastreio quando disponíveis. Não inventar prazo, transportadora ou status." | RESPONSABILIDADE_COMPARTILHADA | MUST | CONFIRMED |
| RF-016 | A possibilidade de consultar rastreamento de cartão diretamente pelo CPF do colaborador depende de validação técnica da `ma-hr-orch`. O endpoint de consulta por CPF ainda não foi confirmado. | 00_Agente_Consultivo_MARH.html | Seção 8.5 | "Avaliar, junto ao time técnico, se a ma-hr-orch consegue disponibilizar uma consulta de rastreamento por CPF do colaborador." | MA_HR_ORCH | MUST | NOT_VALIDATED |
| RF-017 | Quando a consulta de rastreamento por CPF não estiver disponível na `ma-hr-orch`, o agente deve solicitar o número do pedido ao usuário para continuar o rastreamento. | 00_Agente_Consultivo_MARH.html | Seção 8.5 | "Caso a consulta direta por CPF não esteja disponível, o agente deve solicitar uma informação complementar, como o número do pedido." | AGENTE | MUST | CONFIRMED |
| RF-018 | Nas respostas em que fizer sentido, o agente pode retornar um elemento de navegação `[list_navigation]` com deeplink para o app Meu Alelo (`meualelo://app/webview`), permitindo ao frontend renderizar um acesso rápido à tela relacionada. | 00_Agente_Consultivo_MARH.html | Seção 9 — Elemento de navegação para o frontend | "Nas respostas em que fizer sentido, o agente poderá retornar um elemento de navegação para que o frontend identifique e renderize um componente visual de acesso rápido." | RESPONSABILIDADE_COMPARTILHADA | SHOULD | CONFIRMED |

---

## 2. Regras de Negócio (RN)

| ID | Requisito normalizado | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| RN-001 | O agente não deve criar, alterar, cancelar, excluir, aprovar, reprovar ou executar qualquer ação transacional. Sua função é exclusivamente consultiva neste primeiro momento. | 00_Agente_Consultivo_MARH.html | Seção 1 — Objetivo | "O agente não deve criar, alterar, cancelar, excluir, aprovar, reprovar ou executar qualquer ação transacional." | AGENTE | MUST | CONFIRMED |
| RN-002 | O agente não deve inventar capacidades que não estejam descritas no markdown de conhecimento. | 00_Agente_Consultivo_MARH.html | Seção 6 | "O agente não deve inventar capacidades que não estejam descritas no markdown." | AGENTE | MUST | CONFIRMED |
| RN-003 | O agente não deve inventar prazo, transportadora ou status de rastreamento de cartão. | 00_Agente_Consultivo_MARH.html | Seção 8.5 | "Não inventar prazo, transportadora ou status." | AGENTE | MUST | CONFIRMED |
| RN-004 | O agente não deve implementar diretamente regras de autorização, permissão, validação de token ou validações técnicas dos sistemas internos. Essas são responsabilidade exclusiva da `ma-hr-orch`. | 00_Agente_Consultivo_MARH.html | Seção 4 — Responsabilidades da API ma-hr-orch | "O agente não deve implementar diretamente regras de autorização, permissão, validação de token ou validações técnicas dos sistemas internos." | MA_HR_ORCH | MUST | CONFIRMED |
| RN-005 | O elemento `[list_navigation]` deve ser retornado apenas quando houver relação direta com a resposta e o identificador necessário estiver disponível. O agente não deve inventar identificadores. | 00_Agente_Consultivo_MARH.html | Seção 9 | "O elemento de navegação deve ser retornado apenas quando houver relação direta com a resposta. O link só deve ser retornado quando o identificador necessário estiver disponível. O agente não deve inventar identificadores." | AGENTE | MUST | CONFIRMED |
| RN-006 | O elemento `[list_navigation]` não deve executar ações transacionais automaticamente. Deve apenas direcionar o usuário para uma tela onde ele possa consultar ou continuar uma jornada oficial. | 00_Agente_Consultivo_MARH.html | Seção 9 | "O elemento de navegação não deve executar ações transacionais automaticamente. O elemento deve apenas direcionar o usuário para uma tela onde ele possa consultar ou continuar uma jornada oficial." | AGENTE | MUST | CONFIRMED |
| RN-007 | O texto da resposta deve continuar compreensível mesmo que o frontend não renderize o componente visual do elemento `[list_navigation]`. | 00_Agente_Consultivo_MARH.html | Seção 9 | "O texto da resposta deve continuar compreensível mesmo que o frontend não renderize o componente visual." | AGENTE | MUST | CONFIRMED |
| RN-008 | Links para ações transacionais só devem abrir a jornada oficial no Espaço RH, sem executar a ação automaticamente. | 00_Agente_Consultivo_MARH.html | Seção 9 | "Links para ações transacionais só devem abrir a jornada oficial, sem executar a ação automaticamente." | AGENTE | MUST | CONFIRMED |
| RN-009 | A `ma-hr-orch` deve orquestrar chamadas para os sistemas necessários e retornar ao agente apenas as informações que podem ser exibidas ao usuário. | 00_Agente_Consultivo_MARH.html | Seção 4 — Responsabilidades da API ma-hr-orch | "Orquestrar chamadas para os sistemas necessários. Retornar ao agente apenas as informações que podem ser exibidas ao usuário." | MA_HR_ORCH | MUST | CONFIRMED |
| RN-010 | A `ma-hr-orch` deve padronizar erros de permissão, segurança, ausência de dados e indisponibilidade. | 00_Agente_Consultivo_MARH.html | Seção 4 — Responsabilidades da API ma-hr-orch | "Padronizar erros de permissão, segurança, ausência de dados e indisponibilidade." | MA_HR_ORCH | MUST | CONFIRMED |
| RN-011 | Se a empresa selecionada não for enviada ao agente, ele deve retornar erro orientativo ao usuário. | 00_Agente_Consultivo_MARH.html | Seção 5 | "Se a empresa selecionada não for enviada, o agente deve retornar erro orientativo." | AGENTE | MUST | CONFIRMED |
| RN-012 | Se o usuário solicitar dados de outra empresa, o agente deve orientar que a consulta considera apenas a empresa selecionada no app. | 00_Agente_Consultivo_MARH.html | Seção 5 | "Se o usuário solicitar dados de outra empresa, o agente deve orientar que a consulta considera apenas a empresa selecionada no app." | AGENTE | MUST | CONFIRMED |
| RN-013 | Se a pergunta não estiver contemplada no markdown de conhecimento, o agente deve informar que não possui essa informação (sem inventar). | 00_Agente_Consultivo_MARH.html | Seção 6 | "Se a pergunta não estiver contemplada no markdown, o agente deve informar que não possui essa informação." | AGENTE | MUST | CONFIRMED |
| RN-014 | Enquanto a disponibilidade do endpoint de rastreamento por CPF não for validada com o time técnico, o comportamento padrão é: quando o usuário informar somente o CPF, o agente solicita o número do pedido. Este comportamento é o único caminho confirmado para rastreamento. | 00_Agente_Consultivo_MARH.html | Seção 8.5 | "Avaliar, junto ao time técnico, se a ma-hr-orch consegue disponibilizar uma consulta de rastreamento por CPF do colaborador. Caso a consulta direta por CPF não esteja disponível, o agente deve solicitar uma informação complementar, como o número do pedido." | RESPONSABILIDADE_COMPARTILHADA | MUST | CONFIRMED |

---

## 3. Requisitos Não Funcionais (RNF)

| ID | Requisito normalizado | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| RNF-001 | O agente deve estar disponível via API REST. | 00_Agente_Consultivo_MARH.html | Seção 3 e Seção 14 | "O agente deve estar disponível por meio de uma API REST." | RESPONSABILIDADE_COMPARTILHADA | MUST | CONFIRMED |
| RNF-002 | O arquivo markdown de conhecimento deve conter todas as informações que o agente está autorizado a responder sobre a feature MARH, e deve ser mantido atualizado a cada evolução do escopo. | 00_Agente_Consultivo_MARH.html | Seção 6 | "O markdown deve conter todas as informações que o agente está autorizado a responder sobre a feature MARH. O markdown deve ser versionado e revisado." | AGENTE | MUST | CONFIRMED |
| RNF-003 | A URL da webview no elemento `[list_navigation]` deve ser enviada em formato URL encoded. | 00_Agente_Consultivo_MARH.html | Seção 9 | "A URL da webview deve ser enviada em formato URL encoded." | A_DEFINIR | SHOULD | CONFIRMED |
| RNF-004 | A URL final da webview deve ser definida pela API MARH, pelo frontend ou pela camada responsável pela navegação, conforme estratégia técnica a ser definida. | 00_Agente_Consultivo_MARH.html | Seção 9 | "A URL final da webview deve ser definida pela API MARH, pelo frontend ou pela camada responsável pela navegação, conforme estratégia técnica." | A_DEFINIR | SHOULD | AMBIGUOUS |

---

## 4. Segurança (SEG)

| ID | Requisito normalizado | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| SEG-001 | A `ma-hr-orch` é responsável por validar: token do usuário, se o usuário é interlocutor da empresa, permissão de acesso aos dados da empresa selecionada, FNP e prova de vida. | 00_Agente_Consultivo_MARH.html | Seção 4 — Responsabilidades da API ma-hr-orch | "Validar o token do usuário. Validar se o usuário é interlocutor da empresa. Validar FNP, prova de vida ou demais validações de segurança aplicáveis." | MA_HR_ORCH | MUST | CONFIRMED |
| SEG-002 | O agente não deve permitir consulta de outra empresa por CNPJ, pedido ou CPF digitado manualmente no chat. | 00_Agente_Consultivo_MARH.html | Seções 5 e 11 | "O usuário não deve conseguir trocar a empresa da consulta digitando outro CNPJ, contrato ou nome de empresa no chat. Não permitir consulta de outra empresa por CNPJ, pedido ou CPF digitado manualmente." | AGENTE | MUST | CONFIRMED |
| SEG-003 | O agente não deve expor informações técnicas, tokens, integrações internas ou dados sensíveis desnecessários ao usuário. | 00_Agente_Consultivo_MARH.html | Seção 11 — Regras de segurança | "Não expor informações técnicas, tokens, integrações internas ou dados sensíveis desnecessários." | AGENTE | MUST | CONFIRMED |
| SEG-004 | O elemento `[list_navigation]` deve apontar apenas para telas permitidas no contexto do Espaço RH. | 00_Agente_Consultivo_MARH.html | Seções 11 e 9 | "Retornar elementos de navegação apenas para telas permitidas no contexto do Espaço RH." | AGENTE | MUST | CONFIRMED |
| SEG-005 | O deeplink do elemento `[list_navigation]` deve exigir usuário autenticado para abrir a webview (`authRequired=true`). | 00_Agente_Consultivo_MARH.html | Seção 9 | "authRequired=true indica que a abertura exige usuário autenticado." | APP_MEU_ALELO | MUST | CONFIRMED |
| SEG-006 | O agente deve consultar dados apenas da empresa selecionada, usando a `ma-hr-orch` como única fonte consultiva para dados da empresa. | 00_Agente_Consultivo_MARH.html | Seção 11 | "Consultar apenas dados da empresa selecionada. Usar a ma-hr-orch como fonte consultiva para dados da empresa." | AGENTE | MUST | CONFIRMED |
| SEG-007 | O agente não deve usar elementos `[list_navigation]` para acionar operações transacionais automaticamente. | 00_Agente_Consultivo_MARH.html | Seção 11 | "Não usar elementos de navegação para acionar operações transacionais automaticamente." | AGENTE | MUST | CONFIRMED |

---

## 5. Tratamento de Erros (ERR)

| ID | Requisito normalizado | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| ERR-001 | Quando a empresa selecionada não for identificada: "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente." | 00_Agente_Consultivo_MARH.html | Seções 5 e 13 | Mensagem explícita definida na seção 5 e confirmada na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-002 | Quando o colaborador não for encontrado: "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-003 | Quando o pedido não for encontrado: "Não encontrei o pedido informado para a empresa selecionada." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-004 | Quando o status informado não for reconhecido: "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-005 | Quando o usuário não tiver permissão: "Você não tem permissão para consultar informações dessa empresa no Espaço RH." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-006 | Quando a validação de segurança (FNP/prova de vida) não for concluída: "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-007 | Quando a consulta estiver indisponível: "Não consegui consultar essa informação agora. Tente novamente em alguns instantes." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-008 | Quando a informação não estiver disponível no markdown: "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões." | 00_Agente_Consultivo_MARH.html | Seções 6 e 13 | Mensagem definida na seção 6 e confirmada na seção 13. | AGENTE | MUST | CONFIRMED |
| ERR-009 | Quando o elemento `[list_navigation]` não puder ser gerado: "Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela." | 00_Agente_Consultivo_MARH.html | Seção 13 | Mensagem de erro explícita na seção 13. | AGENTE | SHOULD | CONFIRMED |
| ERR-010 | Quando o agente precisar do número do pedido para rastrear cartão (CPF insuficiente): "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." | 00_Agente_Consultivo_MARH.html | Seção 8.5 | Mensagem explícita na seção 8.5. | AGENTE | MUST | CONFIRMED |

---

## 6. Critérios de Aceite (ACE)

| ID | Critério verificável | Fonte | Seção | Evidência | Componente responsável | Prioridade | Requisitos relacionados | Status |
|---|---|---|---|---|---|---|---|---|
| ACE-001 | O agente responde a requisições HTTP enviadas pela API MARH. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | RESPONSABILIDADE_COMPARTILHADA | MUST | RF-006, RNF-001 | CONFIRMED |
| ACE-002 | O app Meu Alelo envia mensagens do usuário ao agente por meio da API MARH. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | APP_MEU_ALELO / API_MARH | MUST | RF-006, RF-008 | CONFIRMED |
| ACE-003 | A API MARH inclui o identificador da empresa selecionada em todas as requisições ao agente. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | API_MARH | MUST | RF-008 | CONFIRMED |
| ACE-004 | O agente usa o identificador da empresa recebido em todas as chamadas à `ma-hr-orch`, sem permitir substituição pelo usuário. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-007, RF-009 | CONFIRMED |
| ACE-005 | O agente chama a `ma-hr-orch` para todas as consultas de dados da empresa. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-003, RF-009 | CONFIRMED |
| ACE-006 | A `ma-hr-orch` rejeita com erro padronizado requisições com token inválido, FNP NOK ou prova de vida NOK. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | MA_HR_ORCH | MUST | SEG-001, RN-010 | CONFIRMED |
| ACE-007 | O agente possui um arquivo markdown de conhecimento carregado e acessível em tempo de execução. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-010, RNF-002 | CONFIRMED |
| ACE-008 | Para perguntas sobre o funcionamento do MARH, o agente responde com base apenas no markdown de conhecimento, sem chamar a `ma-hr-orch`. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-004 | CONFIRMED |
| ACE-009 | O agente classifica corretamente as três intenções: consultiva, informativa sobre MARH e fora do escopo. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-002 | CONFIRMED |
| ACE-010 | O agente retorna dados de colaborador quando consultado por nome ou CPF válidos para a empresa selecionada. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-011 | CONFIRMED |
| ACE-011 | O agente retorna dados de pedido quando consultado por número de pedido válido para a empresa selecionada. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-012 | CONFIRMED |
| ACE-012 | O agente retorna o pedido mais recente disponível quando solicitado o "último pedido" da empresa selecionada. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-013 | CONFIRMED |
| ACE-013 | O agente retorna lista de pedidos filtrada pelo status informado pelo usuário. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-014 | CONFIRMED |
| ACE-014 | Quando o usuário informa um status não reconhecido, o agente solicita esclarecimento com exemplos de status válidos. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RF-014, ERR-004 | CONFIRMED |
| ACE-015 | Quando uma consulta não retorna dados, o agente informa com a mensagem correspondente sem inventar informações. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | ERR-002, ERR-003 | CONFIRMED |
| ACE-016 | O agente não executa nenhuma operação de escrita, criação, alteração ou cancelamento em resposta a qualquer mensagem do usuário. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE | MUST | RN-001 | CONFIRMED |
| ACE-017 | Dado que o rastreamento direto por CPF não está disponível, quando o usuário solicitar rastreamento informando apenas o CPF do colaborador, o agente deve solicitar o número do pedido e não deve inventar informações de rastreamento. | 00_Agente_Consultivo_MARH.html | Seções 8.5 e 14 | "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF do colaborador. Informe o número do pedido para eu consultar as informações disponíveis de rastreamento." | AGENTE | MUST | RF-017, ERR-010, RN-014 | CONFIRMED |
| ACE-018 | Quando o agente retornar elemento `[list_navigation]`, a resposta textual permanece compreensível independentemente de o frontend renderizar o componente. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE / FRONTEND | SHOULD | RF-018, RN-007 | CONFIRMED |
| ACE-019 | O frontend identifica a marcação `[list_navigation]` na resposta do agente, abre o deeplink `meualelo://app/webview` e carrega a URL encoded da webview correspondente. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | FRONTEND | SHOULD | RF-018, RNF-003 | CONFIRMED |
| ACE-020 | O elemento `[list_navigation]` não dispara nenhuma ação transacional automaticamente ao ser aberto. | 00_Agente_Consultivo_MARH.html | Seção 14 | Item explícito da seção 14. | AGENTE / APP_MEU_ALELO | MUST | RN-006, SEG-007 | CONFIRMED |

---

## 7. Fora do Escopo (FORA)

| ID | Ação proibida | Fonte | Seção | Evidência | Componente responsável | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| FORA-001 | O agente não deve criar pedido. | 00_Agente_Consultivo_MARH.html | Seção 12 — Fora de escopo | "O agente não deve: Criar pedido." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-002 | O agente não deve cancelar pedido. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Cancelar pedido." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-003 | O agente não deve alterar pedido. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Alterar pedido." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-004 | O agente não deve editar colaborador. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Editar colaborador." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-005 | O agente não deve excluir colaborador. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Excluir colaborador." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-006 | O agente não deve alterar endereço de entrega. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Alterar endereço de entrega." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-007 | O agente não deve solicitar segunda via de cartão. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Solicitar segunda via de cartão." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-008 | O agente não deve reemitir cartão. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Reemitir cartão." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-009 | O agente não deve alterar status de pedido ou entrega. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Alterar status de pedido ou entrega." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-010 | O agente não deve realizar pagamento. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Realizar pagamento." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-011 | O agente não deve consultar empresa sem permissão. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Consultar empresa sem permissão." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-012 | O agente não deve responder sobre capacidades não previstas no markdown de conhecimento. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Responder informações sobre capacidades que não estejam previstas no markdown de conhecimento." | AGENTE | NOT_APPLICABLE | CONFIRMED |
| FORA-013 | O agente não deve retornar `[list_navigation]` apontando para telas fora do contexto autorizado do Espaço RH. | 00_Agente_Consultivo_MARH.html | Seção 12 | "Retornar link de navegação para telas fora do contexto autorizado do Espaço RH." | AGENTE | NOT_APPLICABLE | CONFIRMED |

---

## 8. Ambiguidades e Decisões Técnicas Pendentes (AMB)

### AMB-001 — Rastreamento direto por CPF do colaborador

| Campo | Conteúdo |
|---|---|
| **ID** | AMB-001 |
| **Descrição** | O rastreamento de cartão por CPF é listado como escopo do MVP, mas o documento indica explicitamente que é necessário avaliar com o time técnico se a `ma-hr-orch` consegue disponibilizar esse tipo de consulta. Não há confirmação de que o endpoint existe. |
| **Fonte** | 00_Agente_Consultivo_MARH.html — Seção 8.5 |
| **Evidência** | "Avaliar, junto ao time técnico, se a ma-hr-orch consegue disponibilizar uma consulta de rastreamento por CPF do colaborador." |
| **Status** | AMBIGUOUS |
| **Decisão necessária** | Confirmar com o time técnico se a `ma-hr-orch` expõe ou pode expor endpoint de rastreamento por CPF. Se sim: especificar contrato da API. Se não: formalizar que o fallback por `orderNumber` é o comportamento permanente. |
| **Responsável sugerido** | MA_HR_ORCH / Time técnico de integração |
| **Impacto no MVP** | Afeta apenas a jornada de rastreamento iniciada por CPF. A jornada de rastreamento iniciada por número do pedido está confirmada (RF-015, RF-017, ERR-010). |
| **Bloqueia POC** | **NÃO** — O fallback por `orderNumber` está CONFIRMED e é suficiente para a POC. As demais consultas (colaborador, pedido, último pedido, pedidos por status) não são afetadas. |
| **Requisitos relacionados** | RF-015, RF-016, RF-017, RN-014, ERR-010, ACE-017 |

---

### AMB-002 — Camada responsável pela URL final da webview

| Campo | Conteúdo |
|---|---|
| **ID** | AMB-002 |
| **Descrição** | A especificação não define qual camada (API MARH, frontend ou outra) é responsável por compor a URL final da webview que o elemento `[list_navigation]` deve carregar. |
| **Fonte** | 00_Agente_Consultivo_MARH.html — Seção 9 |
| **Evidência** | "A URL final da webview deve ser definida pela API MARH, pelo frontend ou pela camada responsável pela navegação, conforme estratégia técnica." |
| **Status** | AMBIGUOUS |
| **Decisão necessária** | Definir qual componente (API MARH, frontend ou camada de BFF) é responsável por compor e entregar a URL da webview no formato correto para o deeplink. |
| **Responsável sugerido** | A_DEFINIR — frontend + API MARH (decisão de arquitetura) |
| **Impacto no MVP** | Afeta apenas a entrega do componente visual `[list_navigation]`. O fluxo textual do agente funciona independentemente (RN-007). |
| **Bloqueia POC** | **NÃO** — O agente pode responder consultas sem o elemento de navegação. A entrega textual é completa e compreensível sem o componente visual. Bloqueia apenas a entrega final do SHOULD `[list_navigation]`. |
| **Requisitos relacionados** | RF-018, RNF-004, ACE-018, ACE-019 |

---

## Contagem de itens

| Categoria | Prefixo | Qtd |
|---|---|---|
| Requisitos Funcionais | RF | 18 |
| Regras de Negócio | RN | 14 |
| Requisitos Não Funcionais | RNF | 4 |
| Segurança | SEG | 7 |
| Tratamento de Erros | ERR | 10 |
| Critérios de Aceite | ACE | 20 |
| Fora do Escopo | FORA | 13 |
| Ambiguidades | AMB | 2 |
| **Total** | | **88** |

---

## Resumo de prioridades

| Prioridade | Qtd | Exemplos |
|---|---|---|
| MUST | 75 | Todo o núcleo consultivo (RF-001 a RF-017), segurança, erros, fora do escopo |
| SHOULD | 7 | RF-018, RNF-003, RNF-004, RN-005*, ACE-018, ACE-019, ERR-009 |
| NOT_APPLICABLE | 13 | Todos os itens FORA |

> *RN-005 marcado como MUST por conter regra de segurança explícita ("não deve inventar identificadores"). O item SHOULD se refere à existência do elemento; a restrição é MUST.

## Resumo de responsabilidades por componente

| Componente | Responsável por |
|---|---|
| **AGENTE** | Classificação de intenção; consultas via ma-hr-orch; respostas informativas via markdown; fallback de rastreamento; mensagens de erro; restrições de escopo; geração do elemento [list_navigation] |
| **MA_HR_ORCH** | Validação de token, FNP e prova de vida; verificação de interlocutor; orquestração de sistemas; padronização de erros; (futura) disponibilização do endpoint de rastreamento por CPF |
| **API_MARH** | Envio do contexto da empresa selecionada ao agente; encaminhamento de mensagens do app |
| **FRONTEND** | Renderização do componente [list_navigation]; abertura do deeplink |
| **APP_MEU_ALELO** | Consumo do agente via API MARH; aplicação de authRequired na abertura do deeplink |
| **A_DEFINIR** | Composição da URL final da webview; formato URL encoded para o deeplink |

## Itens que bloqueiam a POC

| Bloqueia | Itens |
|---|---|
| **SIM** | Ausência de: RF-001 a RF-017 (núcleo consultivo), SEG-001 a SEG-007, ERR-001 a ERR-008, ERR-010 |
| **NÃO** | AMB-001 (rastreamento por CPF — fallback disponível); AMB-002 (URL webview — fluxo textual funciona sem); RF-018 e [list_navigation] em geral |

---

*Fonte única: `docs\cliente\00_Agente_Consultivo_MARH.html` · Revisado em 2026-07-22*
