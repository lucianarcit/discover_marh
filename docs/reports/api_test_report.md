# Relatório de Testes de API - Gestão de Colaboradores

**Gerado em:** 2026-07-22 10:35:48
**Execução:** `20260722_103354`
**Ambiente:** homologacao
**Autenticação:** OAuth2 Bearer Token (refresh_token grant)

---

## Resumo por Categoria

| Categoria | Total | Sucesso | Falha | Bloqueado | Ignorado |
|-----------|-------|---------|-------|-----------|----------|
| Testes unitários | 64 | 64 | 0 | 0 | 0 |
| Classificação de erro | 4 | 4 | 0 | 0 | 0 |
| Integração real (GET) | 1 | 0 | 0 | 1 | 0 |
| Operações mutáveis | 3 | 0 | 0 | 0 | 3 |

> ⚠️ **ATENÇÃO:** Nenhuma API foi validada com resposta real.
> Os testes de integração reais foram **bloqueados pela autenticação**.
> Isso NÃO pode ser considerado como integração aprovada.

---

## Resumo de Execução

| Métrica | Valor |
|---------|-------|
| Total de operações | 4 |
| APIs realmente executadas com sucesso | 0 |
| APIs bloqueadas por auth | 1 |
| Falhas (erros HTTP reais) | 0 |
| Ignoradas (segurança) | 3 |
| Duração total | 0ms |
| Status codes encontrados | [] |

---

## APIs Bloqueadas por Autenticação

| Operação | Método | Auth Status | Detalhe |
|----------|--------|-------------|---------|
| Consulta dos colaboradores | GET | AUTH_TOKEN_INVALID | HTTP 401. Código: ''. Detalhe: '' |

---

## APIs Não Executadas (Segurança)

| Operação | Método | Motivo |
|----------|--------|--------|
| Cadastro de colaborador | POST | Método POST pode alterar dados. Requer análise manual antes da execução. |
| Atualização de colaborador | PUT | Método PUT pode alterar dados. Requer análise manual antes da execução. |
| Exclusão de colaborador | DELETE | Método DELETE pode alterar dados. Requer análise manual antes da execução. |

---

## Localização dos Artefatos

- Resumo: `artifacts/api_runs/20260722_103354/execution_summary.json`
- Respostas sanitizadas: `artifacts/api_runs/20260722_103354/sanitized_responses.json`
- Schemas: `artifacts/api_runs/20260722_103354/schemas.json`
- Individual: `artifacts/api_runs/20260722_103354/individual/`
