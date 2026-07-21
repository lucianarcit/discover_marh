# Plano de Testes — Agente Consultivo MARH

---

## Estratégia

Todos os testes do agente utilizam **mocks ou stubs da ma-hr-orch**. O agente não chama a API HRM diretamente.

Os testes antigos (`docs/tests/test_api.py`, `docs/tests/test_profile_safe.py`) são referência histórica para o time da ma-hr-orch e não fazem parte da suíte do agente.

---

## Cenários de Teste

### Classificação de Intenção

| # | Mensagem | Intenção esperada |
|---|---|---|
| 1 | "consultar colaborador Wesley Fabrete" | CONSULTIVA |
| 2 | "consultar pedido 342671" | CONSULTIVA |
| 3 | "qual foi o último pedido?" | CONSULTIVA |
| 4 | "quais são os últimos pedidos com status pago?" | CONSULTIVA |
| 5 | "rastrear cartão do colaborador 123.456.789-00" | CONSULTIVA |
| 6 | "o que posso fazer?" | INFORMATIVA_MARH |
| 7 | "como faço para fazer um pedido?" | INFORMATIVA_MARH |
| 8 | "você consegue cancelar pedido?" | INFORMATIVA_MARH |
| 9 | "cancela o pedido 342671" | FORA_DO_ESCOPO |
| 10 | "cria um novo pedido" | FORA_DO_ESCOPO |
| 11 | "altera o endereço do colaborador" | FORA_DO_ESCOPO |

### Casos de Uso — ma-hr-orch mockada

| # | Cenário | Mock response | Comportamento esperado |
|---|---|---|---|
| 12 | Colaborador encontrado (único) | `{status: "success", data: {nome, local, produto}}` | Exibe dados + navegação |
| 13 | Múltiplos colaboradores | `{status: "multiple_results", data: [...]}` | Pede escolha ao usuário |
| 14 | Colaborador não encontrado | `{status: "not_found"}` | Mensagem padronizada |
| 15 | Pedido encontrado | `{status: "success", data: {status, data, valor, ...}}` | Exibe dados + navegação |
| 16 | Pedido não encontrado | `{status: "not_found"}` | Mensagem padronizada |
| 17 | Último pedido | `{status: "success", data: {...}}` | Exibe pedido mais recente |
| 18 | Pedidos por status | `{status: "success", data: [...]}` | Lista pedidos filtrados |
| 19 | Status inválido | `{status: "invalid_status"}` | Mensagem orientativa |
| 20 | Rastreio por CPF disponível | `{status: "success", data: {status_entrega, ...}}` | Exibe dados + navegação |
| 21 | Rastreio por CPF indisponível | `{status: "not_found"}` | Solicita nº pedido |

### Erros e Segurança

| # | Cenário | Trigger | Comportamento esperado |
|---|---|---|---|
| 22 | Empresa ausente | `context.selected_company_id` vazio | Erro orientativo imediato |
| 23 | Sem permissão | Mock: `{status: "no_permission"}` | Mensagem padronizada |
| 24 | Segurança não concluída | Mock: `{status: "security_failed"}` | Mensagem padronizada |
| 25 | Timeout da ma-hr-orch | Timeout simulado | Mensagem de indisponibilidade |
| 26 | ma-hr-orch indisponível | Mock retorna 503 | Mensagem de indisponibilidade |
| 27 | Response fora do schema | Mock retorna JSON inválido | Mensagem genérica de erro |
| 28 | Prompt injection | Mensagem maliciosa | Bloqueado na validação de entrada |
| 29 | Tentativa de trocar empresa | "consultar pedidos da empresa CNPJ X" | Usa company_id do context; orienta usuário |

### Markdown

| # | Cenário | Comportamento esperado |
|---|---|---|
| 30 | Conteúdo existe no Markdown | Responde com informação oficial |
| 31 | Conteúdo não existe no Markdown | "Ainda não tenho essa informação..." |

### Output Validator

| # | Cenário | Comportamento esperado |
|---|---|---|
| 32 | Resposta dentro do schema | Passa |
| 33 | Resposta com token/segredo vazado | Bloqueia e sanitiza |
| 34 | Resposta excede tamanho | Trunca ou rejeita |
| 35 | Navegação com type inválido | Remove navegação |

---

## Referência Histórica (fora da suíte do agente)

| Arquivo | Propósito original | Uso atual |
|---|---|---|
| `docs/tests/test_api.py` | Teste direto da API HRM | Referência para time ma-hr-orch |
| `docs/tests/test_profile_safe.py` | Teste seguro GET /profile | Referência para time ma-hr-orch |
| `docs/sample/sample_curl.txt` | Exemplo de headers HRM | Referência de domínio |
