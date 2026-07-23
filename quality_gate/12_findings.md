# Quality Gate — Achados (Findings)
**Data:** 2026-07-23

---

## Legenda

| Severidade | Descrição |
|---|---|
| BLOCKER | Impede avançar para integração real |
| HIGH | Risco alto — deve ser resolvido antes de produção |
| MEDIUM | Inconsistência relevante |
| LOW | Melhoria de qualidade |
| INFO | Observação ou dívida futura |

---

## BLOCKER

### F-001 — Bug de classificação: "pedidos cancelados" → INT-022 em vez de INT-005
| Campo | Valor |
|---|---|
| **ID** | F-001 |
| **Severidade** | BLOCKER |
| **Categoria** | Lógica de negócio / Classificação |
| **Arquivo** | `src/marh_agent/classification/intent_classifier.py` |
| **Linha** | 27 |
| **Descrição** | Padrão `cancel[ae]` na regex de intenções transacionais capturava a substring "cancela" em "cancelados", redirecionando consultas de status de pedido ("pedidos cancelados") para a jornada transacional de cancelamento (INT-022 / REDIRECT_TO_OFFICIAL_JOURNEY) em vez de listar pedidos por status CANCELLED (INT-005). |
| **Evidência** | `re.search(r"cancel[ae]", "cancelados", re.IGNORECASE)` → match em posição 0. |
| **Impacto** | Usuário consultando pedidos cancelados receberia resposta "Para realizar essa ação, acesse o Espaço RH" em vez da lista de pedidos. Violação do comportamento esperado do INT-005. |
| **Correção recomendada** | Alterar regex para `\bcancelar?\b|\bcancele\b` (forma verbal imperativa/infinitiva). |
| **Correção aplicada** | ✅ SIM — regex corrigido na linha 30. Teste `test_cancelled_status_query_not_transactional` adicionado e passando. |

---

## HIGH

### F-002 — `steps` na allowlist de pedidos sem sub-filtro de campos internos
| Campo | Valor |
|---|---|
| **ID** | F-002 |
| **Severidade** | ~~HIGH~~ → **NOT_APPLICABLE_BY_CLIENT_DECISION** |
| **Decisão** | DP-006 RESOLVED_UPSTREAM_SANITIZATION (2026-07-23) |
| **Novo status** | A ma-hr-orch garante que apenas dados autorizados chegam ao agente. Sub-filtro de `steps` por visibilidade não é responsabilidade do agente. O agente continua validando schema/contrato técnico. |
| **Ação** | Manter `steps` na allowlist de schema. Não criar sub-filtro por campo de autorização. |
| **Histórico** | Anteriormente classificado como HIGH pois a responsabilidade de sanitização não estava confirmada. Com DP-006 resolvido, o risco é assumido upstream. |

### F-003 — `sanitize_response_text()` definida mas nunca chamada
| Campo | Valor |
|---|---|
| **ID** | F-003 |
| **Severidade** | ~~HIGH~~ → **NOT_APPLICABLE_FOR_API_ONLY** |
| **Decisão** | DP-006 RESOLVED_UPSTREAM_SANITIZATION (2026-07-23) |
| **Novo status** | Em fluxos API_ONLY sem LLM, o texto da resposta é gerado por templates determinísticos — não há output de modelo a sanitizar. `sanitize_response_text()` será relevante apenas na etapa de integração RAG/LLM, fora do escopo desta POC. |
| **Ação** | Manter `sanitization.py` no projeto para uso futuro. Não conectar ao pipeline API_ONLY. |
| **Histórico** | Anteriormente classificado como HIGH pois havia risco de PII escapar de allowlist não completa. Com DP-006 resolvido, a responsabilidade de filtragem upstream está confirmada. |

### F-004 — `LookupError` (404 backend) não capturada no router
| Campo | Valor |
|---|---|
| **ID** | F-004 |
| **Severidade** | HIGH → CORRIGIDO |
| **Categoria** | Resiliência / Tratamento de erros |
| **Arquivo** | `src/marh_agent/application/router.py` |
| **Linha** | 239-265 |
| **Descrição** | O `MockMaHrOrchClient` lança `LookupError("404")` quando `simulate_error = 404`. O bloco `try/except` no router capturava `PermissionError`, `TimeoutError`, `RuntimeError`, `ConnectionError` — mas não `LookupError`. A exceção propagaria como 500 sem `correlation_id`. |
| **Evidência** | `except (RuntimeError, ConnectionError)` sem `LookupError`. `_check_simulated_errors()` linha 37: `raise LookupError("404")`. |
| **Impacto** | Simulação de 404 no backend causaria exceção não tratada, resultando em HTTP 500 sem resposta estruturada. |
| **Correção aplicada** | ✅ SIM — `except LookupError` adicionado retornando ERR-003. Teste `test_lookup_error_handled_gracefully` adicionado e passando. |

---

## MEDIUM

### F-005 — `get_display_label()` expõe valor técnico da API para status desconhecido
| Campo | Valor |
|---|---|
| **ID** | F-005 |
| **Severidade** | MEDIUM → CORRIGIDO |
| **Categoria** | UX / Segurança |
| **Arquivo** | `src/marh_agent/classification/status_mapper.py` |
| **Linha** | 155-159 |
| **Descrição** | Se a API retornasse um status desconhecido (ex: `"SUSPENDED_BY_FRAUD"`), `get_display_label()` retornaria a string técnica da API diretamente ao usuário. Adicionalmente, `PARTIAL_REFUNDED` com `label_completed=None` retornaria `"PARTIAL_REFUNDED"`. |
| **Correção aplicada** | ✅ SIM — Função retorna `"Status desconhecido"` para status não catalogados e `"Status não disponível"` para labels pendentes de confirmação. |

### F-006 — Regex de cancelamento muito ampla (corrigido em F-001, mas regex geral merece atenção)
| Campo | Valor |
|---|---|
| **ID** | F-006 |
| **Severidade** | MEDIUM |
| **Categoria** | Lógica de classificação |
| **Arquivo** | `src/marh_agent/classification/intent_classifier.py` |
| **Linha** | 27-33 |
| **Descrição** | Outros padrões transacionais também podem ter falsos positivos. Ex: `remov` capturaria "removido" (estado de pedido hipotético). Recomenda-se revisão com word-boundaries em todos os padrões. |
| **Impacto** | Baixo na POC atual — nenhum status da fixture usa esses termos. |
| **Correção aplicada** | ⚠️ Parcial — somente cancelamento corrigido. Outros padrões documentados para revisão futura. |

### F-007 — Dead code: `_CATALOG_PATH` em status_mapper
| Campo | Valor |
|---|---|
| **ID** | F-007 |
| **Severidade** | MEDIUM → CORRIGIDO |
| **Categoria** | Qualidade de código |
| **Arquivo** | `src/marh_agent/classification/status_mapper.py` |
| **Linha** | 29-33 |
| **Descrição** | `_CATALOG_PATH` apontava para `fixtures/order_status_catalog.json` que não existe. O catálogo é inline. Dead code criava confusão sobre a fonte dos dados. |
| **Correção aplicada** | ✅ SIM — Dead code removido, comentário explícito sobre fonte inline adicionado. |

### F-008 — Import `extract_name` dentro de função (inline import)
| Campo | Valor |
|---|---|
| **ID** | F-008 |
| **Severidade** | MEDIUM → CORRIGIDO |
| **Categoria** | Qualidade de código |
| **Arquivo** | `src/marh_agent/classification/intent_classifier.py` |
| **Linha** | 183 |
| **Descrição** | `from marh_agent.classification.entity_extractor import extract_name` era importado dentro da função `classify()` a cada chamada. |
| **Correção aplicada** | ✅ SIM — Import movido para o topo do arquivo. |

### F-009 — ERR-001 enganoso quando user_id/session_id ausente
| Campo | Valor |
|---|---|
| **ID** | F-009 |
| **Severidade** | MEDIUM |
| **Categoria** | UX / Mensagens de erro |
| **Arquivo** | `src/marh_agent/security/trusted_context.py` |
| **Linha** | 17-23 |
| **Descrição** | `validate_trusted_context()` retorna ERR-001 ("Selecione uma empresa no Espaço RH") também quando `user_id` ou `session_id` estão ausentes. A mensagem é enganosa — o problema pode ser sessão expirada, não empresa ausente. |
| **Impacto** | Experiência confusa para o usuário em casos de sessão expirada. |
| **Correção aplicada** | ⚠️ NÃO — Requer decisão de produto sobre mensagem a exibir. Registrado para próxima iteração. |

### F-010 — Teste 29 com condição OR fraca
| Campo | Valor |
|---|---|
| **ID** | F-010 |
| **Severidade** | MEDIUM → CORRIGIDO (indiretamente) |
| **Categoria** | Qualidade de testes |
| **Arquivo** | `tests/unit/test_orchestrator.py` |
| **Linha** | 279 |
| **Descrição** | `assert "000" not in resp.navigation.deeplink or "employees" in resp.navigation.deeplink` — condição OR fraca que passaria mesmo com CPF no deeplink. |
| **Correção aplicada** | ✅ SIM — Testes `test_cpf_not_in_deeplink` e `test_deeplink_no_sensitive_ids` complementados com verificação mais precisa. |

---

## LOW

### F-011 — `format_date_ptbr()` expõe string inválida em falha de parse
| Campo | Valor |
|---|---|
| **ID** | F-011 |
| **Severidade** | LOW |
| **Arquivo** | `src/marh_agent/templates/orders.py` linha 16 |
| **Descrição** | Em falha de parse de data, retorna a string original que pode ser lixo técnico. Recomendado retornar `""`. |
| **Correção aplicada** | ⚠️ NÃO — Risco real muito baixo com fixture sintética. Documentado para produção. |

### F-012 — `docs_url="/docs"` ativo em FastAPI
| Campo | Valor |
|---|---|
| **ID** | F-012 |
| **Severidade** | LOW |
| **Arquivo** | `src/marh_agent/api/local_api.py` linha 36 |
| **Descrição** | Swagger UI expõe contrato da API em `/docs`. Aceitável para POC local, deve ser desabilitado em produção. |
| **Correção aplicada** | ⚠️ NÃO — POC local. Deve ser `docs_url=None` em produção. |

### F-013 — innerHTML em home.js com dados sintéticos (não risco real na POC)
| Campo | Valor |
|---|---|
| **ID** | F-013 |
| **Severidade** | LOW |
| **Arquivo** | `poc_marh_agent/frontend/assets/js/home.js` linhas 61, 88 |
| **Descrição** | `innerHTML` usado com dados de fixture sintética escapados via `_escText()`. Não há risco real na POC. Em chat.js linha 298, SVG estático hardcoded via innerHTML — também sem risco. Boa prática seria usar `textContent` + DOM building, mas dado o escaping presente e os dados sintéticos, classificado como LOW. |
| **Correção aplicada** | ⚠️ NÃO — Dados são sintéticos e escapados. Risco real inexistente na POC. |

### F-014 — ROUTE-015 no catálogo do builder mas nunca chamada
| Campo | Valor |
|---|---|
| **ID** | F-014 |
| **Severidade** | LOW |
| **Arquivo** | `src/marh_agent/navigation/builder.py` linha 30 |
| **Descrição** | `ROUTE-015` (`#/order-detail/{orderNumber}/beneficiaries`) presente no catálogo fechado mas nunca invocada em `router.py`. Feature planejada mas não implementada. |
| **Correção aplicada** | ⚠️ NÃO — Rota está no catálogo por design (pode ser invocada no futuro). Não representa risco. |

### F-015 — Ausência de ferramentas de qualidade estática
| Campo | Valor |
|---|---|
| **ID** | F-015 |
| **Severidade** | LOW |
| **Arquivo** | `pyproject.toml` |
| **Descrição** | Sem `ruff`, `mypy`, `bandit` nas dev dependencies. Sem configuração de cobertura mínima. Sem `[tool.coverage]`. |
| **Correção aplicada** | ⚠️ NÃO — Escopo de melhoria futura. Não bloqueia a POC. |

---

## INFO

### F-016 — Arquivo vazio `artifacts/api_inventory/cardholders-hr-management`
| Campo | Valor |
|---|---|
| **ID** | F-016 |
| **Severidade** | INFO |
| **Descrição** | Arquivo de 0 bytes sem extensão. Provavelmente artifact de teste incompleto. |

### F-017 — HTMLs duplicados (~21 MB extras)
| Campo | Valor |
|---|---|
| **ID** | F-017 |
| **Severidade** | INFO |
| **Descrição** | `00_Agente_Consultivo_MARH.html`, `Gestao_de_Colaboradores.html`, `Gestao_de_Pedidos.html` existem em 2 cópias cada (docs/cliente/ e docs/sample/ ou docs/discover/). Impacto só em tamanho do repo. |

### F-018 — `.env` raiz com credenciais HML não commitado (OK, mas risco de vazar)
| Campo | Valor |
|---|---|
| **ID** | F-018 |
| **Severidade** | INFO |
| **Descrição** | O `.env` raiz contém credenciais reais de HML (client_id, client_secret, access_token, refresh_token). O arquivo **não está commitado** (`.gitignore` cobre `.env`). Verificado via `git check-ignore -v .env`. O risco é de vazar localmente ou ser compartilhado acidentalmente. Recomendado rotacionar tokens após o Discovery. |

### F-019 — Salto de numeração nos documentos do Discovery (06 → 12)
| Campo | Valor |
|---|---|
| **ID** | F-019 |
| **Severidade** | INFO |
| **Descrição** | Documentos 07 a 11 não existem no `discover3/`. O salto é intencional mas pode confundir novos membros da equipe. |

---

## Resumo por Severidade

| Severidade | Total | Corrigidos | Restantes |
|---|---|---|---|
| BLOCKER | 1 | 1 | **0** |
| HIGH | 3 | 1 | 2 (condições de GO) |
| MEDIUM | 6 | 4 | 2 (requerem decisão) |
| LOW | 5 | 0 | 5 (melhoria futura) |
| INFO | 4 | 0 | 4 (observações) |
| **Total** | **19** | **6** | **13** |
