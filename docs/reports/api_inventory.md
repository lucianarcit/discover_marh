# Inventário de APIs - Gestão de Colaboradores

**Gerado em:** 2026-07-22 10:00:59
**Fonte:** `docs/cliente/Gestao_de_Colaboradores.html`
**Total de operações:** 4

---

## Operações Identificadas

| # | Operação | Método | Endpoint | Tipo | Parâmetros | Token | Risco Alteração | Exemplo no HTML | Situação |
|---|----------|--------|----------|------|-----------|-------|-----------------|----------------|----------|
| 1 | Consulta dos colaboradores | `GET` | `cardholders-hr-management/v1/beneficiaries` | Consulta | nameOrCpf, page | Sim | 🟢 Baixo | ✅ | Apta |
| 2 | Cadastro de colaborador | `POST` | `/v1/beneficiaries` | Mutação | N/A | Sim | 🔴 Alto | ✅ | SKIPPED_SAFETY |
| 3 | Atualização de colaborador | `PUT` | `/v1/beneficiaries/{beneficiaryId}` | Mutação | beneficiaryId | Sim | 🔴 Alto | ✅ | SKIPPED_SAFETY |
| 4 | Exclusão de colaborador | `DELETE` | `/v1/beneficiaries/{beneficiaryId}` | Mutação | beneficiaryId | Sim | 🔴 Alto | ❌ | SKIPPED_SAFETY |

---

## Detalhes por Operação

### Consulta dos colaboradores

- **Método:** `GET`
- **Path:** `cardholders-hr-management/v1/beneficiaries`
- **Segura para execução:** Sim
- **Motivo:** Operação de consulta (GET) segura para execução.
- **Headers obrigatórios:** Authorization, APP_VERSION, client_id, FNP, PLATFORM, Content-Type, X-BASIC-AUTHORIZATION, USER_ID
- **Status codes:** 204 No Content, 200 Sucesso, 403 Sem permissão, ou FNP, ou prova de vida NOK, 422 ID da empresa inválido

### Cadastro de colaborador

- **Método:** `POST`
- **Path:** `/v1/beneficiaries`
- **Segura para execução:** Não
- **Motivo:** Método POST pode alterar dados. Requer análise manual antes da execução.
- **Headers obrigatórios:** Authorization, APP_VERSION, client_id, FNP, PLATFORM, Content-Type, X-BASIC-AUTHORIZATION, USER_ID
- **Status codes:** 201 Criado, 400 Erro de preenchimento, 403 Sem permissão, ou FNP ou prova de vida NOK, 422 ID da empresa inválido

### Atualização de colaborador

- **Método:** `PUT`
- **Path:** `/v1/beneficiaries/{beneficiaryId}`
- **Segura para execução:** Não
- **Motivo:** Método PUT pode alterar dados. Requer análise manual antes da execução.
- **Headers obrigatórios:** Authorization, APP_VERSION, client_id, FNP, PLATFORM, Content-Type, X-BASIC-AUTHORIZATION, USER_ID
- **Status codes:** 204 No Content, 400 Erro de preenchimento, 403 Sem permissão, ou FNP ou prova de vida NOK, 422 ID da empresa inválido

### Exclusão de colaborador

- **Método:** `DELETE`
- **Path:** `/v1/beneficiaries/{beneficiaryId}`
- **Segura para execução:** Não
- **Motivo:** Método DELETE pode alterar dados. Requer análise manual antes da execução.
- **Headers obrigatórios:** Authorization, APP_VERSION, client_id, FNP, PLATFORM, Content-Type, X-BASIC-AUTHORIZATION, USER_ID
- **Status codes:** 204 No Content, 400 Erro de preenchimento, 403 Sem permissão, 422 ID da empresa inválido
