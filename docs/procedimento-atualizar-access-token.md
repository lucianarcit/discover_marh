# Procedimento para Atualizar o Access Token da Alelo em Ambiente Local

## Objetivo

Atualizar manualmente o access token utilizado pelos scripts de diagnóstico e testes das APIs da ma-hr-orch em HML/UAT.

## Contexto

Atualmente, o access token é obtido manualmente por meio do app de teste da Alelo. Após copiar o token, ele deve ser inserido no arquivo local de configuração do projeto.

## Importante

O token é uma credencial sensível e não deve ser:

- enviado por e-mail ou mensagem
- incluído em prints
- registrado em documentação
- adicionado ao código-fonte
- commitado no Git
- colocado no arquivo `.env.example`
- exibido em logs

---

## 1. Obter o token

Acesse o app de teste da Alelo e realize o fluxo necessário para obter um access token válido.

Copie somente o valor do access token.

---

## 2. Abrir o arquivo de configuração local

No VS Code, abra o arquivo:

```
C:\proj\discover_alelo\.env
```

O arquivo `.env` fica na raiz do projeto.

**Não editar o arquivo:**

```
C:\proj\discover_alelo\src\discover_alelo\config.py
```

O `config.py` apenas lê as variáveis definidas no arquivo `.env`.

---

## 3. Atualizar o token

Localize a variável:

```
ALELO_ACCESS_TOKEN=
```

Substitua o valor existente pelo token novo:

```
ALELO_ACCESS_TOKEN=TOKEN_OBTIDO_NO_APP_DE_TESTE
```

Normalmente, deve ser inserido somente o valor do token, sem acrescentar a palavra `Bearer`.

O código monta o header da chamada no formato:

```
Authorization: Bearer {ALELO_ACCESS_TOKEN}
```

Não utilizar aspas, espaços antes ou depois do token ou quebra de linha no meio do valor.

---

## 4. Salvar o arquivo

Salve o arquivo `.env` no VS Code.

Caso algum script, servidor local ou processo Python já esteja em execução, finalize-o e inicie novamente para que o novo token seja carregado.

---

## 5. Confirmar que o .env está protegido pelo Git

No terminal, execute:

```powershell
cd C:\proj\discover_alelo
git check-ignore .env
```

**Resultado esperado:**

```
.env
```

Esse resultado confirma que o arquivo está listado no `.gitignore` e não será incluído em commits.

Também é possível conferir com:

```powershell
git status
```

O arquivo `.env` não deve aparecer entre os arquivos alterados ou não rastreados.

---

## 6. Executar o teste

Com o ambiente virtual ativado, execute o diagnóstico ou script de teste definido para a API.

```powershell
cd C:\proj\discover_alelo
.\.venv\Scripts\Activate.ps1
```

Depois execute o comando de teste correspondente:

```powershell
python scripts/run_api_tests.py          # colaboradores
python scripts/run_pedidos_tests.py      # pedidos
python scripts/dry_run_probe.py          # dry-run (sem chamadas HTTP)
```

---

## 7. Resultados possíveis

| Resultado | Significado |
|-----------|-------------|
| `AUTHENTICATED` / `SUCCESS` | Token válido, headers corretos, API respondeu |
| `ACCESS_TOKEN_INVALID_OR_EXPIRED` / `AUTH_TOKEN_INVALID` | Token inválido ou expirado |
| `FORBIDDEN_OR_CONTEXT_INVALID` / `HTTP_403` | Token aceito, mas sem permissão ou contexto incorreto |
| `TIMEOUT` | Timeout de conexão ou leitura |
| `UPSTREAM_UNAVAILABLE` / `CONNECTION_ERROR` | API fora do ar ou inalcançável |

---

## 8. Quando o token expirar

Repita o procedimento:

1. Obter um novo token no app de teste
2. Copiar o access token
3. Atualizar `ALELO_ACCESS_TOKEN` no arquivo `.env`
4. Salvar
5. Reiniciar o processo Python
6. Executar novamente o teste

---

## Observação

Nesta fase, a obtenção e a renovação do token são manuais.

Não estão confirmados atualmente:

- refresh automático pela Lambda
- client_credentials
- service account
- renovação automática fora do app
- geração automática de token pelo agente

### Status atual da autenticação

```
AUTH_TOKEN_ACQUISITION       = MANUAL_FROM_TEST_APP
AUTOMATIC_TOKEN_REFRESH      = NOT_VALIDATED
SERVICE_ACCOUNT              = NOT_VALIDATED
```
