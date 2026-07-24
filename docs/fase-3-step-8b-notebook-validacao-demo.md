# Fase 3 — Passo 8B: Notebook de Validação e Demonstração

**Data:** 2026-07-24
**STEP_8B_COMPONENT=RAG_VALIDATION_DEMO_NOTEBOOK**
**STATUS=IMPLEMENTED_PENDING_FINAL_VISUAL_REVIEW**
**EXECUTION_MODE=OFFLINE_EVIDENCE**
**AWS_ACCESS=NOT_REQUIRED**
**LIVE_HML=DEFERRED_UNTIL_STEP_9**

---

## 1. Objetivo

O notebook serve para:

- **Validar automaticamente** as evidências produzidas pelo gate end-to-end (Passo 8A)
- **Tornar os resultados compreensíveis** para público técnico e de negócio
- **Apresentar a arquitetura RAG** sem recriar a infraestrutura descartável
- **Demonstrar o pipeline** com os dados reais da execução 6 do gate
- **Preparar o modo LIVE_HML** para uso após o Passo 9 (não implementado ainda)

O notebook não acessa AWS, não cria recursos e não requer credenciais.

---

## 2. Arquivos criados

| Arquivo | Propósito |
|---|---|
| `notebooks/phase3_rag_validation_demo.ipynb` | Notebook principal executável |
| `notebooks/helpers.py` | Funções auxiliares puras e testáveis |
| `notebooks/build_notebook.py` | Gerador do `.ipynb` via nbformat |
| `notebooks/generate_report.py` | Executa o notebook e exporta HTML |
| `notebooks/requirements.txt` | Dependências isoladas do notebook |
| `notebooks/tests/test_helpers.py` | 38 testes unitários |

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `notebooks/README.md` | Reescrito com instruções de ambiente, kernel VS Code, troubleshooting |

## Artefatos gerados

| Arquivo | Tamanho |
|---|---|
| `reports/phase3_rag_validation_demo.html` | 405 KB — HTML autocontido |
| `reports/threshold_metrics.png` | 83 KB — gráfico de métricas |

---

## 3. Evidências consumidas

O notebook lê exclusivamente os artefatos sanitizados do gate. **Não altera os arquivos originais.**

| Artefato | Conteúdo |
|---|---|
| `gate_summary.json` | Resumo da execução completa do gate |
| `vector_index_validation.json` | Confirmação da metadataConfiguration do índice S3 Vectors |
| `ingestion_result.json` | Status da ingestão: COMPLETE, 1 doc, 0 falhas |
| `retrieve_scores.json` | Scores das 14 consultas positivas e 3 negativas |
| `threshold_analysis_query_level.json` | Métricas TP/FN/TN/FP por threshold (query-level) |
| `threshold_comparison_chunk_level.json` | Análise chunk-level (histórico) |
| `teardown_verification.json` | Confirmação de teardown: COMPLETE, residual=0 |

---

## 4. Conteúdo da demonstração

O notebook cobre 14 seções:

| Seção | Conteúdo |
|---|---|
| 0 | Diagnóstico do ambiente (Python, executável, kernel) |
| 1 | Configuração e carregamento de artefatos |
| Capa | Resumo executivo — GO_PHASE_3_INFRA_WITH_CONDITIONS |
| 2 | Objetivo da Fase 3 e isolamento de modos |
| 3 | Arquitetura: Router → Retrieve → threshold → geração |
| 4 | Validação do índice S3 Vectors (metadataConfiguration) |
| 5 | Resultado da ingestão (status, documentos, falhas) |
| 6 | Retrieve — 14 consultas positivas + 3 negativas com top_score |
| 7 | Análise query-level: tabela TP/FN/TN/FP por threshold |
| 8 | Gráficos: recall, specificity, F1, balanced_accuracy |
| 9 | Justificativa de 0.65 vs. rejeição de 0.70 |
| 10 | Smoke do pipeline (3 casos com cartões PASS/FAIL) |
| 11 | Auditoria do NEG-003 (FP isolado, inativo no pipeline real) |
| 12 | Teardown e residuais |
| 13 | Condições e limitações |
| 14 | Próximos passos — RAG HML |
| Apêndice | Componentes implementados, testes, corpus |

---

## 5. Segurança

O notebook aplica `mask_sensitive()` em qualquer string processada. **Nunca expõe:**

- Account ID AWS
- ARNs de recursos
- Nomes completos de buckets S3
- IDs de Knowledge Base, Data Source ou ingestão
- Credenciais ou tokens
- Caminhos sensíveis desnecessários

---

## 6. Modos de execução

### OFFLINE_EVIDENCE (padrão — implementado)

- Sem AWS
- Sem custo
- Usa os artefatos do gate (`phase_3_e2e_gate/artifacts/`)
- Adequado para apresentação ao cliente

### LIVE_HML (deferred — estrutura preparada, não implementado)

Será ativado após o Passo 9 fornecer:
- `BEDROCK_KNOWLEDGE_BASE_ID`
- `BEDROCK_MODEL_ID`
- Ambiente RAG HML permanente

---

## 7. Execução

### Pré-requisito: ambiente correto

```powershell
cd C:\proj\discover_alelo
py -3.11 -m venv .venv          # criar, se ainda não existir
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
# Esperado: C:\proj\discover_alelo\.venv\Scripts\python.exe
```

### Instalar dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\notebooks\requirements.txt
```

### Registrar kernel Jupyter

```powershell
python -m ipykernel install `
  --user `
  --name discover-alelo `
  --display-name "Python 3.11 — discover_alelo"
```

### Executar testes

```powershell
python -m pytest .\notebooks\tests\test_helpers.py -v
```

### Gerar relatório HTML

```powershell
python .\notebooks\generate_report.py
```

Resultado: `reports\phase3_rag_validation_demo.html`

### Abrir no Jupyter Lab

```powershell
jupyter lab .\notebooks\phase3_rag_validation_demo.ipynb
```

Após abrir: selecionar kernel **Python 3.11 — discover_alelo** e executar **Restart + Run All**.

---

## 8. Critérios de aceite

| Critério | Status |
|---|---|
| `requirements.txt` específico criado | ✅ |
| Dependências instaladas no `.venv` correto | ✅ |
| Kernel registrado como `discover-alelo` | ✅ |
| Restart Kernel + Run All executa sem erro | ✅ |
| f-strings compatíveis com Python 3.11 | ✅ (corrigidas em `build_notebook.py`) |
| 38 testes dos helpers passando | ✅ |
| HTML gerado (405 KB) | ✅ |
| Código oculto no HTML (`--no-input`) | ✅ |
| Gráficos renderizados | ✅ |
| Nenhuma informação sensível exposta | ✅ |
| Nenhuma chamada AWS em OFFLINE_EVIDENCE | ✅ |
| Artefatos ausentes geram aviso, não erro | ✅ |

---

## 9. Limitações

- Threshold 0.65 provisório — `THRESHOLD_STATUS=PROVISIONAL_PENDING_DATASET_EVALUATION`
- Modelo de geração provisório — `MODEL_STATUS=PROPOSED_PENDING_DATASET_EVALUATION`
- Corpus limitado ao conteúdo aprovado (`marh_feature_knowledge.md`)
- Modo LIVE_HML depende do ambiente permanente (Passo 9)
- Métricas devem ser revistas com dataset maior no Passo 10
- NEG-003: FP no Retrieve isolado, inativo no pipeline completo

---

## 10. Próximo passo

**Passo 9 — Terraform do ambiente permanente RAG HML**

- Lambda `marh-agent-rag-hml`
- Knowledge Base permanente com S3 Vectors em sa-east-1
- API Gateway, CloudFront, badge `AWS RAG HML`
- Secrets Manager: `BEDROCK_KNOWLEDGE_BASE_ID`, `BEDROCK_MODEL_ID`
- `RETRIEVAL_SCORE_THRESHOLD=0.65` (provisório)
