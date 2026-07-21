# Contratos — Agente Consultivo MARH

> ⚠️ Os contratos abaixo são **propostas**. O contrato real da ma-hr-orch é um bloqueador de implementação e depende da equipe Alelo.

---

## 1. Request: API MARH → Agente

```json
{
  "context": {
    "selected_company_id": "string (obrigatório)",
    "contract_id": "string | null",
    "interlocutor_id": "string | null",
    "session_id": "string (obrigatório)",
    "correlation_id": "string (obrigatório)"
  },
  "message": "string (entrada não confiável)"
}
```

### Regras

- `context` é confiável — enviado pela API MARH, previamente validado
- `message` é não confiável — texto livre do usuário
- `selected_company_id` ausente → erro orientativo imediato
- `correlation_id` propagado em todos os logs e chamadas downstream
- Valores da mensagem nunca sobrescrevem o contexto

---

## 2. Response: Agente → API MARH

```json
{
  "response": {
    "message": "string (compreensível sem renderização)",
    "intent": "CONSULTIVA | INFORMATIVA_MARH | FORA_DO_ESCOPO",
    "sources": ["string (identificador do Markdown ou operação)"],
    "navigation": {
      "type": "order_detail | collaborator_detail | order_list | card_tracking | journey | null",
      "resource_id": "string | null",
      "deeplink": "string | null"
    },
    "error": {
      "code": "string | null",
      "user_message": "string | null"
    }
  },
  "metadata": {
    "correlation_id": "string",
    "model_calls": 1,
    "latency_ms": 1200
  }
}
```

### Regras

- `navigation.deeplink` pode ser null (decisão pendente: quem constrói)
- `error.code` usa códigos padronizados (ver seção 5)
- `metadata` para observabilidade — não exposto ao usuário final
- `message` deve funcionar mesmo sem renderização de `navigation`

---

## 3. Contrato Conceitual: Agente → ma-hr-orch

> ⚠️ **Este contrato é candidato.** Operações e schemas reais dependem da documentação da equipe Alelo.

### Request (proposta)

```json
{
  "operation": "string",
  "params": {},
  "context": {
    "selected_company_id": "string",
    "contract_id": "string | null",
    "interlocutor_id": "string | null",
    "correlation_id": "string"
  }
}
```

### Operações candidatas (não confirmadas)

| Operação | Parâmetros candidatos | Retorno esperado |
|---|---|---|
| `search_collaborator` | `{name?: str, cpf?: str}` | Dados do colaborador ou lista |
| `get_order` | `{order_number: str}` | Dados do pedido |
| `get_latest_order` | `{}` | Pedido mais recente |
| `list_orders_by_status` | `{status: str}` | Lista de pedidos |
| `track_card` | `{cpf?: str, order_number?: str}` | Dados de rastreio |

### Response (proposta)

```json
{
  "status": "success | not_found | multiple_results | invalid_status | no_permission | security_failed | unavailable",
  "data": {},
  "error_message": "string | null"
}
```

---

## 4. Contexto Confiável vs. Não Confiável

| Campo | Origem | Confiável? | Pode ser alterado pela mensagem? |
|---|---|---|---|
| `selected_company_id` | API MARH | ✅ Sim | ❌ Nunca |
| `contract_id` | API MARH | ✅ Sim | ❌ Nunca |
| `interlocutor_id` | API MARH | ✅ Sim | ❌ Nunca |
| `session_id` | API MARH | ✅ Sim | ❌ Nunca |
| `correlation_id` | API MARH | ✅ Sim | ❌ Nunca |
| nome do colaborador | mensagem | ❌ Não | — (extraído) |
| CPF | mensagem | ❌ Não | — (extraído) |
| nº do pedido | mensagem | ❌ Não | — (extraído) |
| status | mensagem | ❌ Não | — (extraído) |

---

## 5. Códigos de Erro Padronizados

| Código | Cenário | Mensagem ao usuário |
|---|---|---|
| `company_missing` | Empresa ausente no context | "Não consegui identificar a empresa selecionada..." |
| `not_found_collaborator` | Colaborador não encontrado | "Não encontrei nenhum colaborador..." |
| `not_found_order` | Pedido não encontrado | "Não encontrei o pedido informado..." |
| `invalid_status` | Status não reconhecido | "Não reconheci o status informado..." |
| `no_permission` | Sem permissão | "Você não tem permissão..." |
| `security_failed` | Validação de segurança | "...validação de segurança não foi concluída..." |
| `unavailable` | Indisponibilidade ou timeout | "Não consegui consultar essa informação agora..." |
| `info_not_found` | Markdown sem resposta | "Ainda não tenho essa informação..." |
| `navigation_unavailable` | Link não gerado | "...não consegui gerar o atalho de navegação..." |
| `out_of_scope` | Operação transacional | "No momento eu consigo apenas consultar..." |

---

## 6. Navegação (decisão pendente)

Proposta de resposta estruturada:

```json
"navigation": {
  "type": "order_detail",
  "resource_id": "342671",
  "deeplink": null
}
```

**Decisão pendente:** qual camada constrói `deeplink`:
- ma-hr-orch retorna URL junto com dados
- API MARH constrói com base em type + resource_id
- Frontend resolve
- Agente com templates fixos (menor preferência — LLM não deve inventar URLs)

---

## 7. Decisões Bloqueadoras deste Contrato

| # | Decisão | Status |
|---|---|---|
| 1 | Base URL e rota da ma-hr-orch | Pendente |
| 2 | Mecanismo de auth (agente → ma-hr-orch) | Pendente |
| 3 | Schema exato da response por operação | Pendente |
| 4 | Timeout | Pendente |
| 5 | Códigos HTTP vs. status no body | Pendente |
| 6 | Correlation ID (header ou body?) | Pendente |
| 7 | Versionamento da API | Pendente |
| 8 | Limites de payload | Pendente |
| 9 | Idempotência | Pendente |
| 10 | Construção do deeplink | Pendente |
