# Fase 2 — Plano de Execução

**Objetivo:** Integrar INT-001 a INT-005 com a ma-hr-orch real em sandbox/HML, preservando todas as demais intenções e mantendo o ambiente AWS MOCK atual funcionando.

**Restrições absolutas:**
- Não conectar Bedrock
- Não implementar RAG real
- Não criar embeddings
- Não modificar regras de negócio
- Não alterar o frontend visual
- Não substituir o ambiente MOCK público
- AGENT_MODE=INTEGRATED nunca faz fallback silencioso para MockMaHrOrchClient

---

## Estratégia de Ambiente

| Ambiente | Lambda | API Gateway | Frontend | AGENT_MODE |
|----------|--------|-------------|----------|------------|
| **MOCK (existente)** | `marh-agent-hml` | `pzn843po3h` | `d1vtu9x0di76z9.cloudfront.net` | MOCK_LOCAL |
| **INTEGRATED (novo)** | `marh-agent-integrated-hml` | Novo HTTP API dedicado | Novo CloudFront + S3 separado | INTEGRATED |

Princípios:
- Segunda Lambda com código compartilhado, modo diferente
- Segundo API Gateway HTTP dedicado
- Frontend integrado separado com badge "AWS INTEGRATED HML"
- Logs, variáveis e secrets separados
- Reutilização dos mesmos módulos Terraform (parametrizados)

---

## Steps

### 2.0 — Autenticação, Identidade e Contexto Confiável

Documentar e confirmar:
1. De onde vem o token do usuário
2. Quem valida o token
3. Como company_id e user_id são obtidos de fonte confiável
4. Quais headers são obrigatórios na ma-hr-orch
5. Se o token do usuário é propagado ou trocado por credencial técnica
6. Como expiração e renovação funcionam
7. Se o frontend integrado pode funcionar fora do app
8. Quais usuários e empresas de teste podem acessar HML

**Regra:** No ambiente integrado, company_id e user_id não podem ser confiados apenas porque vieram no JSON do navegador. O frontend integrado não pode ser publicado para acesso anônimo com dados reais enquanto o fluxo de autenticação não estiver confirmado.

**Saída:** Documento `docs/fase-2-step-0-auth.md` com decisões registradas.

---

### 2.1 — Modelos Integration DTO + Domain Models

Duas camadas:
- **Integration DTOs:** representam o contrato externo da ma-hr-orch (tolerantes, campos extras ignorados)
- **Domain Models:** representam somente os dados necessários ao agente (estritos)

Fluxo: `response HTTP → Integration DTO → Domain Model → Presentation → frontend`

Regras:
- Baseados em documentação oficial + inventário + responses observados em HML
- Validar campos essenciais nos DTOs
- Tolerar campos adicionais compatíveis
- Tratar ausência de campos obrigatórios como erro de contrato
- Documentar diferenças entre documentação e payload real
- Não usar DTOs diretamente nos templates
- Criar fixtures sintéticas equivalentes ao schema (nunca commitar payloads reais)

---

### 2.2 — Exceções de Domínio e Mapeamento HTTP

Mapeamento centralizado de HTTP status → exceções → ERR codes:
- 401 → erro técnico de integração (não expor ao usuário)
- 403 → PermissionError → ERR-005 / ERR-006
- 404 → LookupError → ERR-003
- 408 → TimeoutError → ERR-007
- 422 → contrato/parâmetro inválido
- 429 → indisponibilidade temporária (após esgotar retries)
- 5xx → indisponibilidade → ERR-007

---

### 2.3 — HttpMaHrOrchClient

Implementar `src/marh_agent/clients/http_ma_hr_orch.py`:
- httpx com conexão reutilizável
- Timeout explícito
- Headers técnicos confirmados
- correlation_id propagado
- Autenticação conforme contrato real
- Retry: apenas em transitórios (timeout, 429, 502, 503, 504)
- Sem retry: 400, 401, 403, 404, 409, 422
- Máximo 3 tentativas, backoff exponencial com jitter
- Sem regra de negócio no cliente

---

### 2.4 — Secrets e Autenticação Técnica

- Ler credenciais do Secrets Manager no cold-start
- Cache seguro durante a vida da instância Lambda
- Validar: nome do secret, formato, permissão, ausência
- Nunca imprimir o secret
- Token obtido manualmente do app de teste (MANUAL_FROM_TEST_APP)
- Refresh automático NOT_VALIDATED — não implementar nesta fase
- Se token expirar durante execução: retornar ERR-007 (indisponibilidade)
- Procedimento de renovação: `docs/procedimento-atualizar-access-token.md`

---

### 2.5 — Seleção Explícita do Modo INTEGRATED

- `_build_orchestrator` instancia HttpMaHrOrchClient quando INTEGRATED
- MockKnowledgeClient permanece para INT-008 a INT-021 (sem Bedrock)
- Nunca faz fallback para mock se ma-hr-orch falhar
- Erro controlado com correlation_id preservado

---

### 2.6 — Testes Unitários

25+ novos testes cobrindo:
1. Sucesso em cada método HTTP
2. Contexto de empresa enviado
3. correlation_id enviado
4. Timeout
5. Erro de conexão
6. Retry em 429, 502, 503, 504
7. Ausência de retry em 400, 401, 403, 404, 422
8. Limite de tentativas
9. Backoff configurável
10. Resposta inválida / JSON inválido
11. Campos obrigatórios ausentes
12. Secret ausente
13. Nenhuma credencial em logs
14. company_id digitado no chat ignorado
15. Seleção mock/integrated
16. Regressão de todas as intenções

Todos os 107 testes anteriores devem continuar passando.

---

### 2.7 — Testes de Contrato

- Marker: `@pytest.mark.contract`
- Apontam para sandbox/HML
- Empresa e usuário de teste autorizados
- Validam: status HTTP, schema, campos obrigatórios, paginação, erros esperados
- Não rodam automaticamente em PRs sem credenciais
- Comando separado: `python -m pytest -m contract`

---

### 2.8 — Infraestrutura Isolada

Terraform parametrizado para criar segundo ambiente:
- Lambda `marh-agent-integrated-hml`
- API Gateway HTTP dedicado
- S3 + CloudFront separados (frontend integrado)
- Log groups separados
- Secret separado (ou reutilizado com permissão)
- Mesmo módulo Terraform, variáveis diferentes

---

### 2.9 — Smoke Tests em HML

16 cenários documentados no prompt, confirmando:
- INT-001 a INT-005 usam ma-hr-orch real
- Outras intenções preservam comportamento anterior
- Nenhum Bedrock chamado
- Nenhum dado completo em logs
- Frontend renderiza mesmos componentes
- Navigation permanece válida
- Erros não exibem detalhes internos

---

### 2.10 — Quality Gate

Diretório `phase_2_gate/` com 10 documentos + decisão GO/NO-GO.

---

## Decisão DP-006 Vigente

**RESOLVED_UPSTREAM_SANITIZATION** — A ma-hr-orch realiza autorização e sanitização. O agente:
- Valida schema técnico
- Converte respostas em modelos internos
- Utiliza campos necessários aos templates
- Rejeita respostas estruturalmente inválidas
- Não registra payload completo
- Não envia dados ao LLM nesta fase
- Não duplica política de autorização da ma-hr-orch
