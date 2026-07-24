# Notebooks — Fase 3 RAG

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `phase3_rag_validation_demo.ipynb` | Notebook de validação e demonstração do RAG |
| `helpers.py` | Funções auxiliares testáveis (carregamento, métricas, gráficos, HTML) |
| `build_notebook.py` | Gera o `.ipynb` programaticamente via nbformat |
| `generate_report.py` | Executa o notebook e exporta `reports/phase3_rag_validation_demo.html` |
| `tests/test_helpers.py` | 38 testes unitários das funções de `helpers.py` |

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

Sem chamadas AWS. Sem credenciais necessárias.

### LIVE_HML (disponível após Passo 9)

Requer ambiente RAG HML permanente com:
- `BEDROCK_KNOWLEDGE_BASE_ID`
- `BEDROCK_MODEL_ID`
- `BEDROCK_REGION=sa-east-1`
- `RETRIEVAL_SCORE_THRESHOLD=0.65`

## Como executar

### 1. Instalar dependências

```powershell
pip install -r phase_3_e2e_gate/requirements.txt
# ou
pip install nbformat nbconvert matplotlib jupyter pandas
```

### 2. Gerar o HTML (recomendado — sem precisar abrir o Jupyter)

```powershell
cd C:\proj\discover_alelo\notebooks
python generate_report.py
```

O HTML é gerado em `reports/phase3_rag_validation_demo.html`.

### 3. Abrir no Jupyter

```powershell
cd C:\proj\discover_alelo\notebooks
jupyter lab phase3_rag_validation_demo.ipynb
```

Após abrir: **Kernel → Restart Kernel and Run All Cells**

### 4. Executar testes dos helpers

```powershell
cd C:\proj\discover_alelo\notebooks
python -m pytest tests/test_helpers.py -v
```

## Segurança

O notebook e os helpers **nunca expõem**:
- Account ID AWS
- ARNs de recursos
- Nomes completos de buckets
- IDs de Knowledge Base ou ingestão
- Credenciais ou tokens

A função `mask_sensitive()` remove esses dados automaticamente de qualquer
string processada.

## Notas

- O notebook não modifica os artefatos originais do gate
- Quando um artefato está ausente, o notebook exibe uma mensagem clara de aviso
- O gráfico de métricas é salvo em `reports/threshold_metrics.png`
- `build_notebook.py` pode ser re-executado após edições no código — gera
  um `.ipynb` limpo sem outputs anteriores
