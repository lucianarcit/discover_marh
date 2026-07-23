# Quality Gate — Decisão GO / NO-GO
**Data:** 2026-07-23  
**Projeto:** Agente Consultivo MARH — POC

---

## ✅ GO_WITH_CONDITIONS

O projeto pode avançar para a próxima etapa (integração com Bedrock e ma-hr-orch real), **desde que as condições abaixo sejam cumpridas antes da primeira chamada com dados reais**.

---

## Critérios Mínimos de GO — Verificação

| Critério | Status | Evidência |
|---|---|---|
| Zero BLOCKER | ✅ | F-001 corrigido (57/57 testes) |
| Zero vazamento de PII | ✅ | `documentNumber`, `beneficiaryId`, `email`, `motherName`, `address` bloqueados pela allowlist. CPF não aparece em resposta nem deeplink (test_cpf_not_in_response_fields). |
| Zero segredo commitado | ✅ | `.env` no `.gitignore`. Verificado via `git check-ignore`. Nenhum segredo em código. |
| Contratos front/back compatíveis | ✅ | Frontend envia `company_id`, `user_id`, `session_id`, `message`, `environment`. Backend valida via Pydantic. Campos de resposta: `correlation_id`, `intent_id`, `flow`, `message`, `navigation`, `error_code`, `metadata` — idênticos nos dois lados. |
| Testes centrais aprovados | ✅ | 57/57 — inclui allowlist, deeplinks, PII, erros, empresa imutável. |
| Deeplinks válidos | ✅ | Catálogo fechado, URL encoding correto, casing `isModal`/`showNavbar`/`authRequired`, sem idOrder, sem beneficiaryId. |
| `orderNumber` usado corretamente | ✅ | `idOrder` bloqueado pela allowlist. `orderNumber` usado no PATH da rota. |
| Colaborador sem deeplink individual | ✅ | ROUTE-003 é `#/employees` sem parâmetro de id. ROUTE-008 não está no catálogo do builder. |
| Empresa imutável pelo chat | ✅ | `COMPANY_SWITCH` classificado antes de qualquer outra intenção. `company_id` vem do contexto trusted. |
| Allowlists funcionando | ✅ | `filter_order()` remove idOrder, billingDocumentNumber, contractNumber, idLegalPersonBilling. `filter_collaborator()` remove documentNumber, email, phoneNumber, motherName, beneficiaryId, address. |
| Dados de teste sintéticos | ✅ | Fixtures com nomes genéricos, CPFs inválidos (000.000.000-00), IDs marcados como "sintetico". |
| Arquitetura respeitada | ✅ | Lambda sem FastAPI, núcleo reutilizável, sem Redis/banco/VPC/Bedrock/RAG. |

---

## Condições Para Avançar com Bedrock

As condições abaixo devem ser implementadas **antes** da primeira chamada real ao LLM:

### Condição 1 — Sub-filtro para `steps` [HIGH — F-002]
Antes de conectar a API real da ma-hr-orch, adicionar `ORDER_STEPS_FIELDS` e sub-filtrar `steps` em `filter_order()`. O campo `steps` pode conter `beneficiaryId`, CPF e endereços de entrega na resposta real da API.

**Ação:** Definir os campos seguros de `steps` e implementar sub-filtro análogo ao `productInfo`.

### Condição 2 — Conectar `sanitize_response_text()` ao pipeline [HIGH — F-003]
Antes do LLM gerar texto baseado nos dados da API, adicionar uma camada de sanitização no output final. Atualmente, `sanitize_response_text()` está definida mas nunca chamada.

**Ação:** Chamar `sanitize_response_text(response.message)` no orchestrator após o `route()`.

### Condição 3 — Validar que implementação real do MaHrOrchClient sempre usa `company_id` [MEDIUM]
O `MockMaHrOrchClient` ignora o `company_id` nas queries por design da POC. Garantir que a implementação real aplique sempre o filtro de empresa em todas as chamadas à ma-hr-orch.

**Ação:** Code review da implementação real do client antes do merge.

---

## Itens Que Podem Permanecer Pendentes

Os seguintes itens **não bloqueiam** o avanço para a próxima etapa:

| Item | Motivo |
|---|---|
| Modelo Bedrock não selecionado | Decisão de etapa futura (DP pendente) |
| Conta AWS / deploy | Não necessário para integração local |
| S3 Vectors | Etapa de RAG posterior |
| API real da ma-hr-orch | Pode ser conectada gradualmente |
| Endpoint de rastreamento (DP-001) | Funciona com fallback ERR-010 |
| Aliases INVOICE / CANCEL_PROCESSING (DP-004) | Retorna ERR-004 corretamente |
| Tela padrão de navegação de pedido (DP-003-B) | POC usa ROUTE-014 — funcional |
| Rate limiting | Não necessário em testes locais |
| `docs_url=None` em produção | Só relevante em deploy |

---

## Próximo Passo Recomendado

1. Resolver Condição 1 (sub-filtro de `steps`) — estimado 1h
2. Conectar `sanitize_response_text()` — estimado 30min
3. Re-executar `pytest` (deve passar tudo)
4. Integrar com Bedrock via `ConversationAgent` ou `InvokeModel`
5. Substituir `MockMaHrOrchClient` por `RealMaHrOrchClient` apontando para ma-hr-orch HML
6. Executar os 15 cenários de teste end-to-end do plano de avaliação (`evaluation_dataset.json`)
