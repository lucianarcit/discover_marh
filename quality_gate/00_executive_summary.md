# Quality Gate — Sumário Executivo
**Projeto:** Agente Consultivo MARH — POC  
**Data:** 2026-07-23  
**Versão auditada:** commit `960f042` (branch `main`)  
**Decisão:** GO_WITH_CONDITIONS

---

## Resultado Final

| Métrica | Resultado |
|---|---|
| **Decisão** | ✅ **GO_WITH_CONDITIONS** |
| Arquivos analisados | 498 (excluindo .venv, __pycache__) |
| Requisitos rastreados | 88 (RF, RN, RNF, SEG, ERR, ACE, FORA, AMB) |
| Critérios de aceite | 80 (CA-001 a CA-080) |
| Testes antes das correções | 42/42 ✅ |
| Testes após correções | 57/57 ✅ (+15 novos) |
| BLOCKERs encontrados | 1 → corrigido |
| BLOCKERs restantes | 0 |
| HIGH | 3 (2 documentados como riscos de produção) |
| MEDIUM | 6 |
| LOW | 5 |
| INFO | 4 |
| Correções aplicadas | 6 |

---

## Princípios Críticos — Todos Respeitados ✅

| Princípio | Status |
|---|---|
| Agente exclusivamente consultivo | ✅ |
| Nenhuma operação de escrita | ✅ |
| Empresa imutável pelo chat | ✅ |
| Autorização delegada à ma-hr-orch | ✅ |
| Sem RBAC inventado | ✅ |
| CPF fora da resposta e deeplink | ✅ |
| orderNumber ≠ idOrder | ✅ |
| Sem deeplink individual de colaborador | ✅ |
| Dados de teste 100% sintéticos | ✅ |
| Sem credencial no frontend | ✅ |
| Sem credencial commitada | ✅ (`.env` está no `.gitignore`) |

---

## Blocker Corrigido

**B1 — BUG DE CLASSIFICAÇÃO (BLOCKER → CORRIGIDO)**  
Padrão `cancel[ae]` capturava "cancelados" (particípio passado), redirecionando consultas de status para jornada transacional em vez de listar pedidos por status.  
Correção: regex ajustado para `\bcancelar?\b|\bcancele\b` (forma verbal imperativa/infinitiva).

---

## Condições para GO

As seguintes condições devem ser cumpridas antes de conectar o Bedrock e a API real:

1. **[HIGH]** Adicionar sub-filtro para o campo `steps` na allowlist de pedidos antes de apontar para API real (pode conter `beneficiaryId`, CPF, endereço de entrega).
2. **[HIGH]** Conectar `sanitize_response_text()` ao pipeline de saída antes de usar LLM (atualmente definida mas nunca chamada).
3. **[MEDIUM]** Capturar `LookupError` no router (corrigido nesta auditoria para o mock; validar que a implementação real do cliente lança as mesmas exceções).
4. **[MEDIUM]** Confirmar que a implementação real de `MaHrOrchClient` sempre filtra por `company_id`.

---

## Itens Que Podem Permanecer Pendentes

- Modelo Bedrock não selecionado (etapa futura)
- Conta AWS / deploy não realizado
- S3 Vectors não configurado
- API real da ma-hr-orch não conectada
- Endpoint de rastreamento de cartão não validado (DP-001)
- Aliases de INVOICE e CANCEL_PROCESSING (DP-004)
- Tela padrão de navegação de pedido (DP-003-B)
- Rate limiting no backend
- `docs_url` desabilitado em produção

---

## Comandos para Reproduzir os Testes

```bash
# Backend
cd C:\proj\discover_alelo\poc_marh_agent\backend
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Frontend + Backend local
cd C:\proj\discover_alelo\poc_marh_agent\backend
.\.venv\Scripts\python.exe -m uvicorn marh_agent.api.local_api:app --port 8000
# (outro terminal)
cd C:\proj\discover_alelo\poc_marh_agent\frontend
python -m http.server 8080
```
