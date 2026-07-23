# Step 2.0 — Autenticação, Identidade e Contexto Confiável

**Status:** DOCUMENTADO — aguardando confirmação de mecanismo de produção  
**Data:** 2026-07-23  
**Baseado em:** `.env.example`, `api_capability_map.json`, responses reais em `.local/api_runs/`

---

## 1. De onde vem o token do usuário

### Ambiente de testes (descoberto nos runs de 2026-07-22)

O sistema de autenticação da Alelo usa **OAuth2** com os seguintes componentes:

```
Endpoint de token: https://api.homologacaoalelo.com.br/alelo/uat/identity-server-auth/v1/oauth2/token
Tipo: IS-ALELO (Identity Server Alelo)
```

**Duas formas de obter o access token:**
1. **Via refresh_token** → chama o endpoint OAuth2 e recebe um Bearer token
2. **Via token direto** → token já obtido do app/Postman, usado sem chamar OAuth2

### Arquitetura real (app Meu Alelo)

Na produção, o fluxo é:
1. Usuário faz login no app Meu Alelo
2. App obtém JWT/access_token do Identity Server
3. Ao abrir o chat, o app envia o token no header `Authorization: Bearer {token}`
4. API Gateway (ou ma-hr-orch) valida o token

**Conclusão:** O token vem da sessão autenticada do app. O agente/Lambda nunca emite tokens — apenas os recebe e propaga.

---

## 2. Quem valida o token

**A ma-hr-orch** é responsável por validar:
- Token do usuário (Bearer OAuth2)
- Permissão de interlocutor de RH
- FNP (fingerprint do dispositivo)
- Prova de vida (se aplicável)

O agente **não valida tokens**. Se o token for inválido, a ma-hr-orch retorna 403 e o agente mapeia para ERR-005/ERR-006.

**Referência:** `agent_policy.md` seção 12 — "Responsabilidades da ma-hr-orch (não do agente)"

---

## 3. Como company_id e user_id são obtidos de fonte confiável

### POC / Testes locais (ambiente MOCK)

- `company_id`, `user_id`, `session_id` vêm no body JSON do request
- São valores sintéticos fixos (`empresa-sintetica-001`, etc.)
- Aceitos sem validação adicional (contexto de desenvolvimento)

### Ambiente INTEGRATED em HML (proposta)

Para o frontend de teste integrado, duas opções:

**Opção A — Simulação controlada (recomendada para POC integrada):**
- O frontend integrado envia IDs fixos de teste no body (como hoje)
- A Lambda propaga esses IDs nos headers para a ma-hr-orch
- A ma-hr-orch valida se esses IDs existem no ambiente UAT
- **Risco:** IDs vêm do browser, podem ser alterados. Aceitável em HML de teste.

**Opção B — JWT real (requer integração com o app):**
- API Gateway com JWT Authorizer valida o token
- Lambda extrai company_id/user_id do `event.requestContext.authorizer`
- Implementação da Fase 5

**Decisão para Fase 2:** Usar **Opção A** para viabilizar testes integrados. Documentar que o frontend integrado é de uso interno/teste apenas. Não publicar acesso anônimo.

---

## 4. Headers obrigatórios na ma-hr-orch

Confirmados pela documentação e pelos testes reais:

| Header | Valor | Origem |
|--------|-------|--------|
| `Authorization` | `Bearer {access_token}` | Token OAuth2 (sessão do usuário ou credencial técnica) |
| `APP_VERSION` | `8.55.0 (2026072003)` | Fixo por release do agente |
| `client_id` | Credencial da aplicação | Secrets Manager |
| `FNP` | Fingerprint do dispositivo | Contexto confiável (ou valor técnico) |
| `PLATFORM` | `IOS` ou `ANDROID` | Fixo por configuração |
| `Content-Type` | `application/json` | Sempre |
| `X-BASIC-AUTHORIZATION` | `Basic {base64}` | Credencial de aplicação (Secrets Manager) |
| `USER_ID` | ID do usuário autenticado | Contexto confiável (request body na POC) |

---

## 5. Token propagado ou trocado por credencial técnica

### Descoberta dos testes

O `.env.example` mostra **dois mecanismos**:
1. `ALELO_ACCESS_TOKEN` — token direto (Bearer do usuário) — **CONFIRMED_WORKING_MECHANISM**
2. `ALELO_REFRESH_TOKEN` → usado para gerar access_token via OAuth2 — **NOT_VALIDATED**

### Decisão confirmada

```
AUTH_TOKEN_ACQUISITION       = MANUAL_FROM_TEST_APP
ALELO_ACCESS_TOKEN           = CONFIRMED_WORKING_MECHANISM
AUTOMATIC_TOKEN_REFRESH      = NOT_VALIDATED
SERVICE_ACCOUNT              = NOT_VALIDATED
```

Para a POC integrada HML:
- O token é obtido **manualmente** do app de teste da Alelo
- Colado em `ALELO_ACCESS_TOKEN` no `.env` local (para diagnóstico)
- Para a Lambda: armazenado no Secrets Manager (atualizado manualmente quando expirar)
- Em produção (Fase 5): o token do usuário real virá do JWT via API Gateway Authorizer

**Procedimento completo:** ver `docs/procedimento-atualizar-access-token.md`

---

## 6. Expiração e renovação

| Credencial | Expiração | Renovação |
|------------|-----------|-----------|
| Access token (Bearer) | Curta (~30min a 2h) | **Manual** — obter novo token no app de teste |
| Refresh token | Não validado | NOT_VALIDATED |
| client_id / client_secret | Não expira (rotação manual) | Manual via Secrets Manager |
| X-BASIC-AUTHORIZATION | Não expira (rotação manual) | Manual via Secrets Manager |

**Para a Lambda integrada (quando implementada):**
- O token será armazenado no Secrets Manager
- Atualizado manualmente quando expirar
- Em produção (Fase 5): token do usuário virá do app via JWT Authorizer

**Procedimento de renovação:** ver `docs/procedimento-atualizar-access-token.md`

---

## 7. Frontend integrado pode funcionar fora do app?

**Sim, mas com restrições:**

- O frontend integrado é um site estático servido via CloudFront (HTTPS)
- Qualquer pessoa com a URL pode acessar a interface
- Porém, as chamadas à API usam credenciais técnicas (não do visitante)
- **Risco:** Se público, qualquer pessoa poderia consultar dados da empresa de teste

**Decisão:** O frontend integrado **NÃO será publicado** com URL pública indexável. Opções de proteção:
1. ~~Autenticação CloudFront (Lambda@Edge)~~ — complexo para POC
2. **IP allowlist no API Gateway** — restringir acesso a IPs do time
3. **URL não divulgada + sem indexação** — segurança por obscuridade (aceitável para HML de teste)

**Recomendação:** Opção 3 para a POC integrada (URL não divulgada). Adicionar header `X-Robots-Tag: noindex` no CloudFront.

---

## 8. Usuários e empresas de teste em HML

### Confirmado nos runs de API (2026-07-22)

| Dado | Valor | Status |
|------|-------|--------|
| **Base URL** | `https://api-ma.homologacaoalelo.com.br/alelo/uat` | CONFIRMED |
| **Empresa de teste** | 30 colaboradores retornados, pedidos disponíveis | CONFIRMED |
| **Usuário de teste** | Configurado via `ALELO_USER_ID` + `ALELO_FNP` | CONFIRMED |
| **Colaboradores disponíveis** | 30 (paginados, 10 por página) | CONFIRMED |
| **Pedidos disponíveis** | 32+ | CONFIRMED |

### IDs de teste (do .env — não commitar)

Os valores reais estão no `.env` local. Para a Lambda integrada, serão armazenados no Secrets Manager com o seguinte schema:

```json
{
  "client_id": "...",
  "client_secret": "...",
  "basic_auth": "Basic ...",
  "refresh_token": "...",
  "user_id": "...",
  "fnp": "...",
  "company_context": "implícito no token/sessão"
}
```

---

## Decisões Registradas

| # | Decisão | Justificativa |
|---|---------|---------------|
| 1 | Token obtido **manualmente** do app de teste | Refresh automático não validado; token direto é o mecanismo confirmado |
| 2 | company_id vem do body (Fase 2) → authorizer (Fase 5) | Viabiliza testes; será reforçado em produção |
| 3 | Frontend integrado não publicado | Usa dados reais; sem autenticação de visitante |
| 4 | Credenciais no Secrets Manager (Lambda) / .env (local) | Nunca em código, env versionado ou logs |
| 5 | Headers propagados conforme documentação | Authorization, client_id, FNP, USER_ID, etc. |
| 6 | Token atualizado manualmente quando expirar | Procedimento documentado em `procedimento-atualizar-access-token.md` |
| 7 | ma-hr-orch valida autorização | Agente não duplica validação |
| 8 | Opção A (IDs no body) para Fase 2 | JWT Authorizer é Fase 5 |

---

## Bloqueadores Identificados

| # | Item | Status | Ação |
|---|------|--------|------|
| 1 | Refresh token de teste válido | ✅ Existe no .env local | Transferir para Secrets Manager da Lambda integrada |
| 2 | Empresa de teste com dados | ✅ 30 colaboradores + 32 pedidos | Usar como está |
| 3 | Expiração do refresh token | ⚠️ Pode expirar entre sessões | Monitorar; renovar manualmente se necessário |
| 4 | FNP de teste | ✅ Configurado no .env | Transferir para Secrets Manager |

---

## Próximo passo permitido

Com o contexto de autenticação documentado, o **Step 2.1** pode ser iniciado:
- Criar Integration DTOs baseados nos responses reais observados
- Criar Domain Models com campos necessários para INT-001 a INT-005
- Não conectar APIs ainda (apenas definir os modelos)
