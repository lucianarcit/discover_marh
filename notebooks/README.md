# Notebooks — Fase 3 RAG

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `phase3_rag_validation_demo.ipynb` | Notebook de validação e demonstração do RAG |
| `helpers.py` | Funções auxiliares testáveis (carregamento, métricas, gráficos, HTML) |
| `build_notebook.py` | Gera o `.ipynb` programaticamente via nbformat |
| `generate_report.py` | Executa o notebook e exporta `reports/phase3_rag_validation_demo.html` |
| `requirements.txt` | Dependências do notebook (sem boto3 — modo OFFLINE_EVIDENCE) |
| `tests/test_helpers.py` | 38 testes unitários das funções de `helpers.py` |

---

## Configuração do ambiente

### 1. Criar o virtualenv (se ainda não existir)

```powershell
cd C:\proj\discover_alelo
py -3.11 -m venv .venv
```

### 2. Ativar o virtualenv

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Confirmar o Python correto

```powershell
python -c "import sys; print(sys.executable)"
```

Resultado esperado:

```
C:\proj\discover_alelo\.venv\Scripts\python.exe
```

Se o resultado mostrar outro caminho (ex: `proj-renner-modernizacao-broker-fase01-main\venv`),
o ambiente errado está ativo — desative e ative o correto.

### 4. Instalar dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\notebooks\requirements.txt
```

### 5. Registrar o kernel Jupyter

```powershell
python -m ipykernel install `
  --user `
  --name discover-alelo `
  --display-name "Python 3.11 — discover_alelo"
```

---

## Selecionar o kernel no VS Code

1. Abrir o notebook `notebooks/phase3_rag_validation_demo.ipynb`
2. Clicar no kernel no canto superior direito
3. Escolher **Select Another Kernel**
4. Selecionar: **Python 3.11 — discover_alelo**
5. Confirmar que o executável mostrado é:
   `C:\proj\discover_alelo\.venv\Scripts\python.exe`

**Célula de diagnóstico** (primeira célula do notebook):

```python
import sys
from pathlib import Path
print("Python   :", sys.version.split()[0])
print("Executável:", sys.executable)
print("Diretório :", Path.cwd())
```

Se o executável não for do projeto `discover_alelo`, o kernel está errado.

---

## Modos de execução

### OFFLINE_EVIDENCE (padrão)

Lê exclusivamente os artefatos sanitizados do gate end-to-end:

```
phase_3_e2e_gate/artifacts/
  ├── gate_summary.json
  ├── vector_index_validation.json
  ├── ingestion_result.json
  ├── retrieve_scores.json
  ├── threshold_analysis_query_level.json
  ├── threshold_comparison_chunk_level.json
  └── teardown_verification.json
```

**Sem chamadas AWS. Sem credenciais necessárias. Sem custo.**

### LIVE_HML (disponível após Passo 9)

Requer ambiente RAG HML permanente. Não implementado nesta etapa.

Variáveis necessárias quando disponível:
- `BEDROCK_KNOWLEDGE_BASE_ID`
- `BEDROCK_MODEL_ID`
- `BEDROCK_REGION=sa-east-1`
- `RETRIEVAL_SCORE_THRESHOLD=0.65`

---

## Comandos

### Gerar o HTML (recomendado — sem precisar abrir o Jupyter)

```powershell
cd C:\proj\discover_alelo
python .\notebooks\generate_report.py
```

Resultado: `reports\phase3_rag_validation_demo.html`

### Abrir no Jupyter Lab

```powershell
cd C:\proj\discover_alelo
jupyter lab .\notebooks\phase3_rag_validation_demo.ipynb
```

Após abrir: **Kernel → Restart Kernel and Run All Cells**

### Executar testes dos helpers

```powershell
cd C:\proj\discover_alelo
python -m pytest .\notebooks\tests\test_helpers.py -v
```

---

## Troubleshooting

### "Running cells requires the ipykernel package"

**Causa:** o kernel selecionado não é o do projeto `discover_alelo`.

**Solução:**
1. Verificar se o kernel ativo pertence a `C:\proj\discover_alelo\.venv`
2. **Não** instalar pacotes no ambiente de outro projeto (ex: Renner)
3. Selecionar o kernel correto: **Python 3.11 — discover_alelo**
4. Reiniciar o kernel
5. Executar novamente desde a primeira célula

### "ModuleNotFoundError: No module named 'matplotlib'"

**Causa:** dependências não instaladas no virtualenv correto.

**Solução:**

```powershell
cd C:\proj\discover_alelo
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\notebooks\requirements.txt
```

### Artefatos ausentes

O notebook exibe uma mensagem clara quando um artefato está ausente.
Para regenerar os artefatos, execute o gate (requer credenciais AWS ativas):

```powershell
python phase_3_e2e_gate\gate_runner.py
```

---

## Segurança

O notebook e os helpers **nunca expõem**:
- Account ID AWS
- ARNs de recursos
- Nomes completos de buckets
- IDs de Knowledge Base ou ingestão
- Credenciais ou tokens

A função `mask_sensitive()` remove esses dados de qualquer string processada.

---

## Notas

- O notebook não modifica os artefatos originais do gate
- `build_notebook.py` pode ser re-executado para gerar um `.ipynb` limpo
- O gráfico de métricas é salvo em `reports/threshold_metrics.png`
- O código é compatível com Python 3.11+ (sem sintaxe exclusiva do 3.12)
