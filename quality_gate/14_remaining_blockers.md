# Quality Gate — Bloqueadores Restantes
**Data:** 2026-07-23

---

## Bloqueadores de Avançar para Bedrock/API Real

### Nenhum BLOCKER permanece aberto.

O único BLOCKER identificado (F-001 — bug de classificação "cancelados") foi corrigido e validado com 57/57 testes passando.

---

## Condições para GO (não são blockers da POC atual, mas bloqueiam produção)

### COND-1 — Sub-filtro para `steps` [HIGH — F-002]
**Quando bloqueia:** Antes de conectar a API real da ma-hr-orch que pode popular `steps` com dados PII.  
**O que fazer:** Definir `ORDER_STEPS_FIELDS` e sub-filtrar em `filter_order()`.  
**Estimativa:** 1 hora de implementação + 30 min de testes.

### COND-2 — `sanitize_response_text()` conectada [HIGH — F-003]
**Quando bloqueia:** Antes de usar o LLM para gerar texto baseado nos dados da API.  
**O que fazer:** Chamar `sanitize_response_text(response.message)` no orchestrator.  
**Estimativa:** 30 minutos.

---

## Decisões Pendentes do Cliente (não bloqueiam a POC técnica)

| ID | Decisão | Impacto se não resolvida |
|---|---|---|
| DP-001 | Endpoint de rastreamento por orderNumber | Agente usa fallback ERR-007. Rastreamento não funciona. |
| DP-002 | Rastreamento por CPF na ma-hr-orch | Agente usa ERR-010. Fallback funcional. |
| DP-003-B | Tela padrão: order-detail vs. order-request-group | POC usa ROUTE-014. Pode não ser a tela correta para todos os casos. |
| DP-004 | Aliases INVOICE e CANCEL_PROCESSING | ERR-004 para esses status. Experiência subótima. |
| DP-005 | Estratégia de paginação para filtro de status | Lista pode ser incompleta para empresas grandes. |
| DP-006 | Sanitização de PII na ma-hr-orch | Crítico antes de produção — verificar implementação real. |

---

## Decisões Técnicas Internas Pendentes

| Item | Status | Impacto |
|---|---|---|
| Modelo Bedrock (Claude 3.x) | Não selecionado | Etapa futura — não bloqueia integração inicial |
| Sub-filtro de `steps` | Não implementado | Risco de PII em produção |
| `sanitize_response_text()` | Não conectada | Risco de PII se LLM gerar texto com dados |
| Rate limiting | Não implementado | Produção apenas |
| `docs_url=None` | Ativo em local_api.py | Produção apenas |
| Ferramentas de qualidade estática (ruff, mypy) | Não configuradas | Melhoria futura |

---

## Checklist Final Antes de Integrar com Bedrock

```
[ ] COND-1: sub-filtrar steps na allowlist de pedidos
[ ] COND-2: conectar sanitize_response_text() ao pipeline
[ ] Validar que MaHrOrchClient real sempre usa company_id nas queries
[ ] Confirmar que ma-hr-orch remove PII antes de retornar ao agente (DP-006)
[ ] Executar pytest (deve manter 57+ aprovados)
[ ] Verificar integrações end-to-end com backend local (USE_MOCK_AGENT=false)
[ ] Selecionar modelo Bedrock (recomendado: claude-haiku-4-5 para POC)
```
