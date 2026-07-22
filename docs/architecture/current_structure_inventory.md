# Inventário da Estrutura Atual

**Gerado em:** 2026-07-22  
**Projeto:** discover_alelo  
**Raiz:** `C:\proj\discover_alelo`

---

## 1. Estrutura Atual

```
C:\proj\discover_alelo\
├── .claude/                        # Config local do Claude Code
├── .git/
├── .gitignore
├── .venv/                          # Virtual environment (Python)
└── docs/
    ├── cliente/                    # Documentação HTML do cliente
    │   ├── 00_Agente_Consultivo_MARH.html
    │   ├── brief_kiro_apis_rotas_marh.md
    │   ├── Gestao_de_Colaboradores.html
    │   ├── Gestao_de_Pedidos.html
    │   └── Rotas_hr_space.html
    ├── desenhos/                   # Diagramas de arquitetura (drawio, PNG)
    │   ├── arq1.png, arq2.png, arq3.png
    │   ├── arq3.xml
    │   └── *.drawio.xml (5 arquivos)
    ├── discover/                   # Primeira versão da documentação de discovery
    │   ├── 00_Agente_Consultivo_MARH.html
    │   ├── 01_INDICE.md a 05_infraestrutura-aws-mvp.md
    │   └── README.md
    ├── discover2/                  # Segunda versão do discovery (mais recente)
    │   └── 00_INDICE.md a 07_decisoes-pendentes.md
    ├── kb/                         # Knowledge Base de procedimentos do portal Alelo
    │   └── 22 arquivos .md (manuais de operação)
    ├── sample/                     # Exemplos de requisição e dados de teste
    │   ├── Gestao_de_Colaboradores.html
    │   ├── Gestao_de_Pedidos.html
    │   ├── sample_curl.txt
    │   └── user_hml.txt            ⚠️ CONTÉM CREDENCIAIS
    ├── tests/                      # Scripts de teste existentes
    │   ├── apis/
    │   │   ├── .env.example
    │   │   └── get_token.txt       ⚠️ CONTÉM CREDENCIAIS (Basic Auth, refresh_token)
    │   ├── request_sample.txt      ⚠️ CONTÉM CREDENCIAIS (Bearer token, client_secret)
    │   ├── response.json           # Resposta de API capturada (contém IDs de cartão)
    │   └── test_ma_hr_orchi.py     # Script Python de teste funcional
    └── _referencia_alelo_faq_ciandt/  # Projeto de referência completo (FAQ CIandT)
        ├── .env                    ⚠️ CONTÉM CREDENCIAIS
        ├── .env.example
        ├── .env.lambda
        └── api/                    # Código Python de referência
```

---

## 2. Finalidade Provável de Cada Pasta

| Pasta | Finalidade |
|-------|-----------|
| `docs/cliente/` | Documentação HTML oficial entregue pelo cliente Alelo |
| `docs/desenhos/` | Diagramas de arquitetura do bot/agente |
| `docs/discover/` | Primeira iteração do discovery técnico |
| `docs/discover2/` | Segunda iteração (mais completa, com plano de testes e decisões) |
| `docs/kb/` | Base de conhecimento para o agente consultivo (manuais do portal) |
| `docs/sample/` | Dados de exemplo para testes manuais |
| `docs/tests/` | Scripts e dados para testes de integração com as APIs |
| `docs/_referencia_alelo_faq_ciandt/` | Projeto de referência (FAQ anterior da CIandT) |

---

## 3. Arquivos com Possíveis Segredos

| Arquivo | Conteúdo Sensível | Rastreado pelo Git? |
|---------|-------------------|---------------------|
| `docs/tests/apis/get_token.txt` | Basic Auth base64, refresh_token, client_id, FNP | **NÃO** |
| `docs/tests/request_sample.txt` | Bearer token, CLIENT_SECRET, user_id | **NÃO** (no .gitignore) |
| `docs/sample/user_hml.txt` | CPF e senha de homologação | **NÃO** (pasta no .gitignore) |
| `docs/_referencia_alelo_faq_ciandt/.env` | Credenciais AWS/OpenAI | **NÃO** (pasta no .gitignore) |
| `docs/tests/response.json` | cardId, contractNumber, JWT interno | **NÃO** (no .gitignore) |

---

## 4. Arquivos Duplicados ou Mal Posicionados

| Arquivo | Localização Atual | Observação |
|---------|-------------------|-----------|
| `Gestao_de_Colaboradores.html` | `docs/cliente/` e `docs/sample/` | Possível duplicata |
| `Gestao_de_Pedidos.html` | `docs/cliente/` e `docs/sample/` | Possível duplicata |
| `00_Agente_Consultivo_MARH.html` | `docs/cliente/` e `docs/discover/` | Duplicata entre pastas |

---

## 5. Scripts Python Existentes

| Arquivo | Descrição |
|---------|-----------|
| `docs/tests/test_ma_hr_orchi.py` | Parser básico de cURL + chamada HTTP com requests |

---

## 6. Dependências Identificadas

- `requests` (usada em `test_ma_hr_orchi.py`)
- `python-dotenv` (referenciada no `.env.example`)
- Nenhum `requirements.txt` ou `pyproject.toml` na raiz do projeto

---

## 7. Riscos Identificados

1. **Credenciais em arquivos TXT** — Embora não estejam rastreados, ficam acessíveis localmente sem proteção.
2. **Ausência de `.env` formal** — Variáveis de ambiente não centralizadas.
3. **Sem estrutura `src/`** — Código de teste misturado com documentação.
4. **Sem `requirements.txt` na raiz** — Dependências não formalizadas.
5. **JWT e IDs internos em `response.json`** — Dados potencialmente sensíveis armazenados.
6. **Projeto de referência completo na árvore** — `_referencia_alelo_faq_ciandt` aumenta o tamanho sem necessidade.

---

## 8. Proposta de Migração (Origem → Destino)

| Origem | Destino | Ação |
|--------|---------|------|
| `docs/cliente/Gestao_de_Colaboradores.html` | `docs/client/Gestao_de_Colaboradores.html` | COPIAR |
| `docs/cliente/*.html` (outros) | `docs/client/` | COPIAR |
| `docs/tests/apis/get_token.txt` | `.local/curls/get_token.txt` | COPIAR |
| `docs/tests/request_sample.txt` | `.local/curls/request_sample.txt` | COPIAR |
| `docs/sample/user_hml.txt` | `.local/user_hml.txt` | COPIAR |
| `docs/tests/test_ma_hr_orchi.py` | Referência apenas (será substituído) | MANTER |
| `docs/discover/` | `docs/architecture/legacy/discover/` | MANTER (referência) |
| `docs/discover2/` | `docs/architecture/legacy/discover2/` | MANTER (referência) |
| `docs/desenhos/` | `docs/architecture/diagrams/` | MANTER (referência) |
| `docs/kb/` | `docs/kb/` (sem mudança) | MANTER |
| `docs/_referencia_alelo_faq_ciandt/` | Sem migração | MANTER (já no .gitignore) |

---

## 9. Observações

- Nenhum arquivo será excluído nesta fase.
- A migração será feita por cópia, preservando os originais até validação.
- O `.gitignore` será atualizado para cobrir a nova estrutura.
