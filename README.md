# Discover Alelo

Framework de descoberta, teste e documentação das APIs Alelo para consumo por modelo de IA.

---

## Objetivo

1. Ler cURLs de autenticação existentes e extrair credenciais.
2. Obter tokens OAuth2 dinamicamente.
3. Analisar documentação HTML do cliente e inventariar APIs.
4. Executar testes de integração contra ambiente de homologação.
5. Registrar respostas de forma sanitizada.
6. Gerar relatórios de viabilidade para consumo por modelo de IA.

---

## Pré-requisitos

- Python 3.11+
- Acesso à VPN/rede para APIs de homologação Alelo
- Arquivo `.env` configurado (veja `.env.example`)

---

## Setup Rápido (PowerShell)

```powershell
cd C:\proj\discover_alelo
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## Configuração

1. Copie `.env.example` para `.env`
2. Preencha os valores reais (credenciais de homologação)
3. Valide com:

```powershell
python .\scripts\bootstrap_env.py
```

---

## Execução

### 1. Validar ambiente
```powershell
python .\scripts\bootstrap_env.py
```

### 2. Inventariar APIs do HTML do cliente
```powershell
python .\scripts\inventory_client_apis.py
```

### 3. Executar testes de integração
```powershell
python .\scripts\run_api_tests.py
```

### 4. Gerar relatórios
```powershell
python .\scripts\generate_api_report.py
```

### 5. Executar testes unitários
```powershell
python -m pytest .\tests -v
```

---

## Estrutura do Projeto

```
├── .env                    # Credenciais locais (NÃO versionado)
├── .env.example            # Template de configuração
├── .gitignore
├── README.md
├── requirements.txt
│
├── src/discover_alelo/     # Código-fonte principal
│   ├── __init__.py
│   ├── config.py           # Carregamento de variáveis de ambiente
│   ├── auth.py             # Autenticação OAuth2
│   ├── api_client.py       # Cliente HTTP reutilizável
│   ├── curl_parser.py      # Parser de comandos cURL
│   ├── html_api_parser.py  # Parser de HTML de documentação
│   ├── sanitization.py     # Sanitização de dados sensíveis
│   ├── response_recorder.py # Registro de respostas
│   └── models.py           # Modelos de dados
│
├── scripts/                # Scripts de execução
│   ├── bootstrap_env.py
│   ├── inventory_client_apis.py
│   ├── run_api_tests.py
│   └── generate_api_report.py
│
├── tests/                  # Testes
│   ├── unit/               # Testes unitários (sem rede)
│   ├── integration/        # Testes de integração (chamadas reais)
│   └── fixtures/           # Dados de teste
│
├── docs/                   # Documentação
│   ├── client/             # HTML original do cliente
│   ├── architecture/       # Inventário e plano de migração
│   └── reports/            # Relatórios gerados
│
├── artifacts/              # Artefatos gerados
│   ├── api_inventory/      # Inventário estruturado das APIs
│   └── api_runs/           # Resultados de execução (NÃO versionado)
│
└── .local/                 # Dados locais sensíveis (NÃO versionado)
    └── curls/              # cURLs com credenciais
```

---

## Segurança

- **Tokens** permanecem somente em memória durante a execução.
- **`.env`** nunca é versionado.
- **Respostas brutas** ficam em `.local/` (ignorado pelo Git).
- **Relatórios** contêm apenas dados sanitizados.
- **Operações mutáveis** (POST/PUT/DELETE) não são executadas automaticamente.
- **URLs** são validadas para confirmar ambiente de homologação antes de qualquer chamada.

---

## Atualizar Token

Quando o `refresh_token` expirar:

1. Obtenha um novo token na aplicação móvel ou via Postman.
2. Atualize `ALELO_REFRESH_TOKEN` no `.env`.
3. Execute `python scripts/bootstrap_env.py` para validar.

---

## Adicionar Nova API

1. Adicione o HTML da nova API em `docs/client/`.
2. Atualize `scripts/inventory_client_apis.py` para incluir o novo arquivo.
3. Execute `python scripts/inventory_client_apis.py` para gerar inventário.
4. Crie testes em `tests/integration/`.
5. Execute `python scripts/run_api_tests.py`.
6. Gere relatórios com `python scripts/generate_api_report.py`.

---

## Pastas que NÃO devem ser versionadas

| Pasta/Arquivo | Motivo |
|---------------|--------|
| `.env` | Credenciais reais |
| `.local/` | Respostas brutas e cURLs com credenciais |
| `artifacts/api_runs/` | Respostas de API (podem conter dados sensíveis) |
| `.venv/` | Virtual environment |
| `__pycache__/` | Bytecode Python |
