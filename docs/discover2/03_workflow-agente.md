# Workflow do Agente — Fluxos Detalhados

---

## Diagrama Geral

```mermaid
flowchart TD
    REQ[API MARH envia request] --> VAL[Validação de Entrada]
    VAL -->|empresa ausente| ERR_EMP[Erro: empresa não identificada]
    VAL -->|válido| INTENT{Classificar Intenção}

    INTENT -->|CONSULTIVA| ORCH[Tool: ma-hr-orch]
    INTENT -->|INFORMATIVA_MARH| MD[Tool: Markdown]
    INTENT -->|FORA_DO_ESCOPO| FORA[Resposta orientativa]

    ORCH -->|sucesso| RESP[Formatar resposta + navegação]
    ORCH -->|erro padronizado| ERR[Mensagem de erro]
    MD -->|encontrado| RESP
    MD -->|não encontrado| ERR_MD[Info não disponível]

    RESP --> OUT[Output Validator]
    ERR --> OUT
    ERR_MD --> OUT
    ERR_EMP --> OUT
    FORA --> OUT
    OUT --> RET[Retorna para API MARH]
```

---

## Fluxos por Caso de Uso

### Consultar colaborador por nome

```mermaid
sequenceDiagram
    participant MARH as API MARH
    participant AG as Agente
    participant ORCH as ma-hr-orch

    MARH->>AG: {context: {company_id}, message: "consultar colaborador Wesley Fabrete"}
    AG->>AG: classifica → CONSULTIVA
    AG->>ORCH: {operation: "search_collaborator", params: {name: "Wesley Fabrete"}, context: {company_id}}
    ORCH-->>AG: {status: "success", data: {nome, local_entrega, produto}}
    AG->>AG: formata resposta + navegação
    AG-->>MARH: {message: "Encontrei o colaborador...", navigation: {...}}
```

### Consultar colaborador por CPF

Mesmo fluxo, com `params: {cpf: "123.456.789-00"}`.

### Múltiplos colaboradores encontrados

```
ORCH retorna: {status: "multiple_results", data: [{nome, cpf_parcial}, ...]}
Agente: "Encontrei mais de um colaborador. Qual destes você gostaria de consultar?"
  - Lista os resultados
  - Aguarda escolha do usuário
```

### Colaborador não encontrado

```
ORCH retorna: {status: "not_found"}
Agente: "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada."
```

### Consultar pedido por número

```mermaid
sequenceDiagram
    participant MARH as API MARH
    participant AG as Agente
    participant ORCH as ma-hr-orch

    MARH->>AG: {context: {company_id}, message: "consultar pedido 342671"}
    AG->>AG: classifica → CONSULTIVA, extrai order_number=342671
    AG->>ORCH: {operation: "get_order", params: {order_number: "342671"}, context: {company_id}}
    ORCH-->>AG: {status: "success", data: {status, data, produto, valor, colaboradores, cartoes, etapas}}
    AG->>AG: formata resposta + navegação
    AG-->>MARH: resposta estruturada
```

### Pedido não encontrado

```
ORCH retorna: {status: "not_found"}
Agente: "Não encontrei o pedido informado para a empresa selecionada."
```

### Consultar último pedido

```
message: "qual foi o último pedido?"
operation: "get_latest_order"
params: {}
```

### Consultar pedidos por status

```
message: "quais são os últimos pedidos com status pago?"
operation: "list_orders_by_status"
params: {status: "pago"}
```

### Status inválido

```
ORCH retorna: {status: "invalid_status"}
Agente: "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento."
```

### Rastrear cartão por CPF

```mermaid
sequenceDiagram
    participant MARH as API MARH
    participant AG as Agente
    participant ORCH as ma-hr-orch

    MARH->>AG: {message: "rastrear cartão do colaborador 123.456.789-00"}
    AG->>AG: classifica → CONSULTIVA
    AG->>ORCH: {operation: "track_card", params: {cpf: "123.456.789-00"}, context: {company_id}}
    alt CPF disponível
        ORCH-->>AG: {status: "success", data: {status_entrega, data_atualizacao, endereco, codigo_rastreio}}
        AG-->>MARH: resposta com dados + navegação
    else CPF indisponível
        ORCH-->>AG: {status: "not_found", error_message: "rastreio por CPF indisponível"}
        AG-->>MARH: "Ainda não consigo rastrear o cartão diretamente apenas pelo CPF. Informe o número do pedido..."
    end
```

### Pergunta informativa (existe no Markdown)

```
message: "o que posso fazer?"
Classifica → INFORMATIVA_MARH
Consulta Markdown → encontra conteúdo
Responde com base no Markdown
```

### Pergunta informativa (não existe no Markdown)

```
Markdown sem resultado
Agente: "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões."
```

### Operação transacional recusada

```
message: "cancela o pedido 342671"
Classifica → FORA_DO_ESCOPO
Agente: "No momento eu consigo apenas consultar informações. Para realizar essa ação, acesse a jornada correspondente no Espaço RH."
+ navegação quando aplicável
```

### Empresa selecionada ausente

```
Validação de Entrada detecta: selected_company_id vazio ou ausente
Agente: "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente."
Sem tool call.
```

### Sem permissão

```
ORCH retorna: {status: "no_permission"}
Agente: "Você não tem permissão para consultar informações dessa empresa no Espaço RH."
```

### Falha de segurança

```
ORCH retorna: {status: "security_failed"}
Agente: "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente."
```

### Indisponibilidade / timeout

```
ORCH retorna: {status: "unavailable"} ou timeout
Agente: "Não consegui consultar essa informação agora. Tente novamente em alguns instantes."
```

### Tentativa de trocar empresa pelo chat

```
message: "consultar pedidos da empresa CNPJ 12.345.678/0001-99"
Agente usa selected_company_id do contexto confiável (ignora CNPJ da mensagem)
Agente: "A consulta considera apenas a empresa selecionada no app. Para consultar outra empresa, selecione-a no Espaço RH."
```
