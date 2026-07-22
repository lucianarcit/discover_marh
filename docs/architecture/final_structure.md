# Estrutura Final do Projeto

**Data:** 2026-07-22

---

## Árvore

```
C:\proj\discover_alelo\
│
├── .env                            # Credenciais locais (NÃO versionado)
├── .env.example                    # Template de configuração (versionado)
├── .gitignore                      # Regras de versionamento
├── README.md                       # Documentação principal
├── requirements.txt                # Dependências Python
│
├── src/
│   └── discover_alelo/
│       ├── __init__.py             # Package init
│       ├── config.py               # Carregamento de .env e validação
│       ├── auth.py                 # Autenticação OAuth2
│       ├── api_client.py           # Cliente HTTP reutilizável
│       ├── curl_parser.py          # Parser de cURL
│       ├── html_api_parser.py      # Parser de HTML da documentação
│       ├── sanitization.py         # Sanitização de dados sensíveis
│       ├── response_recorder.py    # Gravação de resultados
│       └── models.py               # Dataclasses de resultado
│
├── scripts/
│   ├── bootstrap_env.py            # Valida ambiente e testa auth
│   ├── inventory_client_apis.py    # Extrai APIs do HTML
│   ├── run_api_tests.py            # Executa testes de integração
│   └── generate_api_report.py      # Gera relatórios consolidados
│
├── tests/
│   ├── unit/
│   │   ├── test_curl_parser.py     # 27 testes do parser cURL
│   │   ├── test_html_api_parser.py # 11 testes do parser HTML
│   │   └── test_sanitization.py    # 26 testes de sanitização
│   ├── integration/
│   │   └── test_gestao_colaboradores_api.py  # Testes reais
│   └── fixtures/
│       ├── curls/                  # cURLs de teste (sanitizados)
│       └── payloads/              # Payloads de exemplo
│
├── docs/
│   ├── cliente/                    # HTMLs originais do cliente
│   │   ├── Gestao_de_Colaboradores.html
│   │   ├── Gestao_de_Pedidos.html
│   │   └── ...
│   ├── architecture/
│   │   ├── current_structure_inventory.md
│   │   ├── migration_plan.md
│   │   └── final_structure.md
│   ├── reports/
│   │   ├── api_inventory.md
│   │   ├── api_test_report.md
│   │   └── model_consumption_assessment.md
│   ├── discover/                   # Discovery v1 (histórico)
│   ├── discover2/                  # Discovery v2 (histórico)
│   ├── kb/                         # Knowledge base (ativa)
│   └── desenhos/                   # Diagramas (histórico)
│
├── artifacts/
│   ├── api_inventory/
│   │   ├── gestao_colaboradores_apis.json
│   │   └── model_data_catalog.json
│   └── api_runs/                   # NÃO versionado
│       └── YYYYMMDD_HHMMSS/
│           ├── execution_summary.json
│           ├── sanitized_responses.json
│           ├── schemas.json
│           └── individual/
│
└── .local/                         # NÃO versionado
    ├── curls/
    │   └── get_token.txt
    └── api_runs/                   # Respostas brutas (debug)
```

---

## Responsabilidade de Cada Pasta

| Pasta | Responsabilidade |
|-------|-----------------|
| `src/discover_alelo/` | Código-fonte reutilizável do framework |
| `scripts/` | Scripts de execução standalone (CLI) |
| `tests/unit/` | Testes sem rede, rápidos, executáveis em CI |
| `tests/integration/` | Testes contra API real (requer .env e VPN) |
| `docs/cliente/` | Documentação HTML original do cliente |
| `docs/architecture/` | Documentação da migração e estrutura |
| `docs/reports/` | Relatórios gerados pelo framework |
| `docs/kb/` | Knowledge base para o agente consultivo |
| `artifacts/api_inventory/` | Inventário estruturado (versionável) |
| `artifacts/api_runs/` | Resultados de execução (NÃO versionável) |
| `.local/` | Dados sensíveis locais (NÃO versionável) |

---

## Como Executar

```powershell
cd C:\proj\discover_alelo
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# 1. Validar ambiente
python .\scripts\bootstrap_env.py

# 2. Inventariar APIs
python .\scripts\inventory_client_apis.py

# 3. Executar testes
python .\scripts\run_api_tests.py

# 4. Gerar relatórios
python .\scripts\generate_api_report.py

# 5. Rodar testes unitários
python -m pytest .\tests -v
```

---

## Como Atualizar o Token

1. O `refresh_token` expira periodicamente.
2. Obtenha um novo via app móvel ou Postman.
3. Atualize `ALELO_REFRESH_TOKEN` no `.env`.
4. Valide com `python scripts/bootstrap_env.py`.

---

## Como Adicionar uma Nova API

1. Obtenha o HTML de documentação do cliente.
2. Salve em `docs/cliente/`.
3. Crie um novo script ou atualize `inventory_client_apis.py`.
4. Execute o inventário.
5. Crie testes de integração em `tests/integration/`.
6. Execute e gere relatórios.

---

## Como Regenerar Relatórios

```powershell
python .\scripts\generate_api_report.py
```

---

## Pastas que NÃO Devem Ser Versionadas

| Pasta/Arquivo | Motivo |
|---------------|--------|
| `.env` | Credenciais reais |
| `.local/` | Dados sensíveis e respostas brutas |
| `artifacts/api_runs/` | Execuções com dados potencialmente sensíveis |
| `.venv/` | Ambiente virtual |
| `__pycache__/` | Cache Python |
| `.pytest_cache/` | Cache de testes |
