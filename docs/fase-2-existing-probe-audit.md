# Auditoria do Probe Existente — Fase 2

**Data:** 2026-07-23  
**Status:** AUTH_TOKEN_INVALID_OR_EXPIRED  
**Decisão:** EXISTING_PROBE_READY_WITH_ADJUSTMENTS

---

## 1. Inventário do Código Existente

| Arquivo | Responsabilidade | Reutilizável | Alteração necessária |
|---------|------------------|:---:|---|
| `config.py` | Carrega .env, valida vars obrigatórias, timeouts | ✅ | Nenhuma |
| `auth.py` | OAuth2 (refresh_token) + token direto do .env | ✅ | Nenhuma (já suporta token direto) |
| `api_client.py` | Cliente HTTP GET com retry, headers, redaction | ✅ | Nenhuma |
| `models.py` | ApiResult, ApiOperation, ExecutionSummary | ✅ | Nenhuma |
| `response_recorder.py` | Salva resultados sanitizados + brutos locais | ✅ | Nenhuma |
| `sanitization.py` | Mascara PII, tokens, headers nos relatórios | ✅ | Nenhuma |
| `network_diagnostic.py` | DNS, TCP, HTTPS sem credenciais | ✅ | Nenhuma |
| `curl_parser.py` | Parseia cURL commands para componentes | ⚠️ | Não necessário para Fase 2 |
| `html_api_parser.py` | Extrai operações de HTML da documentação | ⚠️ | Não necessário para Fase 2 |

---

## 2. Comandos Encontrados

| Comando | O que faz |
|---------|-----------|
| `python scripts/run_api_tests.py` | Executa GET colaboradores (inventário) |
| `python scripts/run_pedidos_tests.py` | Executa GET pedidos com encadeamento (orderNumber) |
| `python scripts/inventory_client_apis.py` | Gera inventário de APIs a partir dos HTMLs |
| `python scripts/generate_api_report.py` | Gera relatório de capacidades |
| `python scripts/dry_run_probe.py` | Mostra config sem executar chamadas |

---

## 3. Mecanismo de Autenticação Real

### auth.py — análise detalhada

| Questão | Resposta |
|---------|----------|
| Aceita access token direto? | **SIM** — se `ALELO_ACCESS_TOKEN` está preenchido, usa sem chamar OAuth2 |
| Tenta refresh_token? | Sim, mas **apenas se** `ALELO_ACCESS_TOKEN` estiver vazio |
| Qual fluxo tem precedência? | Token direto > refresh_token > erro |
| Chama algum endpoint OAuth? | Sim, `ALELO_AUTH_URL` com grant_type=refresh_token (só quando necessário) |
| Possível desabilitar refresh? | **Sim** — basta preencher `ALELO_ACCESS_TOKEN` no .env |

### Decisão de autenticação

```
AUTH_TOKEN_ACQUISITION = MANUAL_FROM_TEST_APP
ALELO_ACCESS_TOKEN = CONFIRMED_WORKING_MECHANISM (quando token válido)
AUTOMATIC_REFRESH = NOT_VALIDATED (refresh_token pode estar expirado)
SERVICE_ACCOUNT = NOT_VALIDATED
```

**Modo recomendado para Fase 2:** `ALELO_ACCESS_TOKEN` direto, obtido manualmente do app de teste.

---

## 4. Operações Já Disponíveis

### Colaboradores (run_api_tests.py)
- `GET /v1/beneficiaries` — lista paginada com filtro `nameOrCpf`

### Pedidos (run_pedidos_tests.py)
- `GET /v1/orders` — lista paginada
- `GET /v1/orders/{orderNumber}` — detalhe por número
- `GET /v1/orders/{orderNumber}/beneficiaries` — colaboradores do pedido
- `GET /v1/orders/{orderNumber}/invoice` — nota fiscal
- `GET /v1/orders/{orderNumber}/bank-ticket` — boleto
- `GET /v1/products` — catálogo de produtos
- `GET /v1/benefits` — benefícios disponíveis
- `GET /v1/availability-dates-for-credit` — datas de crédito

---

## 5. Testes Existentes

**Não existem testes unitários** no pacote `src/discover_alelo/tests/` — o diretório não existe.

Os "testes" são na verdade **runners de integração** (scripts/) que chamam a API real.

---

## 6. Gaps Identificados

| # | Gap | Impacto |
|---|-----|---------|
| 1 | Sem testes unitários do pacote | Não há validação sem API real |
| 2 | Sem filtro por nome/CPF no runner de colaboradores | run_api_tests.py faz apenas listagem sem params |
| 3 | Sem filtro por status no runner de pedidos | run_pedidos_tests.py não filtra por status |
| 4 | Token expirado (resultado do teste) | Precisa token fresco para validar |
| 5 | Sem modo STATIC_ACCESS_TOKEN explícito | Já funciona pelo precedência do auth.py, mas sem env var de controle |

---

## 7. Resultados da Execução

### Dry-run
```
Base URL:    https://api-ma.homologacaoalelo.com.br/alelo/uat
Is HML:      True
Auth mode:   STATIC_ACCESS_TOKEN (direto do .env)
Platform:    IOS
Operações:   1 GET (colaboradores) + 8 GET (pedidos)
```

### Probe real (run_api_tests.py)
```
Resultado:   0 sucesso | 1 falha | 0 bloqueadas
Causa:       HTTP 401 — Token rejeitado (expirado)
Duração:     494ms
Classificação: AUTH_TOKEN_INVALID_OR_EXPIRED
```

### Verificação .env
```
ALELO_API_BASE_URL:    CONFIGURED
ALELO_ACCESS_TOKEN:    CONFIGURED (mas expirado)
ALELO_CLIENT_ID:       CONFIGURED
ALELO_BASIC_AUTH:      CONFIGURED
ALELO_FNP:            CONFIGURED
ALELO_USER_ID:        CONFIGURED
ALELO_APP_VERSION:    CONFIGURED
ALELO_PLATFORM:       CONFIGURED
ALELO_REFRESH_TOKEN:  CONFIGURED
ALELO_AUTH_URL:        CONFIGURED
```

### git check-ignore .env
```
.env — IGNORADO ✅
```

---

## 8. Estratégia de Reaproveitamento

### Recomendação: **C — Extrair somente componentes comprovados**

| Componente | Ação | Justificativa |
|------------|------|---------------|
| `auth.py` | Reutilizar como ferramenta de diagnóstico | Suporta token direto; funciona para validação |
| `api_client.py` | Referência para `HttpMaHrOrchClient` | Headers, retry, session, timeouts são modelo comprovado |
| `config.py` | Manter no pacote discover_alelo | Usado pelos runners de diagnóstico |
| `models.py` | Manter no pacote discover_alelo | ApiResult útil para runners |
| `sanitization.py` | Manter no pacote discover_alelo | Para sanitização de relatórios (não do agente) |
| `response_recorder.py` | Manter no pacote discover_alelo | Para gravar resultados de probe |
| `network_diagnostic.py` | Manter como ferramenta de troubleshooting | DNS/TCP/HTTPS check |

### Por que NÃO importar diretamente no backend:

1. O pacote `discover_alelo` usa `requests` — o backend usa `pydantic` + será `httpx`
2. `discover_alelo` é ferramenta de diagnóstico com print/stdout — backend é Lambda
3. Misturar dependências de diagnóstico com runtime aumenta superfície de ataque
4. Os headers e auth do `api_client.py` são modelo, não código final

### O que o `HttpMaHrOrchClient` vai copiar (como referência):

- Lista de headers de `_build_headers()`
- Lógica de retry de `api_client.py`
- Pattern de session reutilizável
- Timeout separado (connect/read)
- Classificação de erros transitórios

---

## 9. Decisão

```
EXISTING_PROBE_READY_WITH_ADJUSTMENTS
```

### O que já existia e funciona:
- Runner de colaboradores: `scripts/run_api_tests.py`
- Runner de pedidos: `scripts/run_pedidos_tests.py`
- Auth com token direto: `auth.py` (ALELO_ACCESS_TOKEN tem precedência)
- Headers confirmados: `api_client.py._build_headers()`
- Retry para 502/503/504: `api_client.py`
- Sanitização de relatórios: `sanitization.py`
- Gravação de resultados: `response_recorder.py`

### Arquivo runner atual:
- `scripts/run_api_tests.py` (colaboradores)
- `scripts/run_pedidos_tests.py` (pedidos com encadeamento)

### Comando exato para executar:
```bash
python scripts/run_api_tests.py        # colaboradores
python scripts/run_pedidos_tests.py    # pedidos
```

### Autenticação utilizada:
`ALELO_ACCESS_TOKEN` direto do .env (36 chars, atualmente EXPIRADO)

### Chamadas aprovadas:
Todas — quando token válido (comprovado nos runs de 2026-07-22)

### Chamadas falhas:
1/1 — HTTP 401 (token expirado, não erro de infraestrutura)

### Arquivos alterados:
- Criado: `scripts/dry_run_probe.py` (utilidade pura, sem lógica nova)

### Necessidade de novo script:
**NÃO** — os runners existentes cobrem todas as operações necessárias para INT-001 a INT-005.

### Estratégia de reaproveitamento:
**C** — `discover_alelo` permanece como ferramenta de diagnóstico. O `HttpMaHrOrchClient` será implementado usando os mesmos headers e patterns como referência, mas como código independente no backend.

---

## Próximo passo

1. **Obter token fresco** do app de teste (ver `docs/procedimento-atualizar-access-token.md`)
2. **Colar** em `ALELO_ACCESS_TOKEN` no `.env`
3. **Re-executar** `python scripts/run_api_tests.py` e `python scripts/run_pedidos_tests.py`
4. **Confirmar** que as chamadas passam com token válido
5. **Iniciar Step 2.1** — Integration DTOs baseados nos responses confirmados
