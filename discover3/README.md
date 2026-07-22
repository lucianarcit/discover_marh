# discover3 — Requisitos do Cliente: Agente Consultivo MARH

## Objetivo

Esta pasta contém a análise de requisitos extraída integralmente das fontes documentais do cliente e do projeto. Nenhum requisito foi inventado; nenhuma recomendação técnica foi elevada a requisito.

## Fontes analisadas

### Documentos do cliente (docs/cliente/)
- `00_Agente_Consultivo_MARH.html` — Especificação técnica do Agente Consultivo MARH (14 seções)
- `Gestao_de_Colaboradores.html` — Documentação técnica de Gestão de Colaboradores (4 seções)
- `Gestao_de_Pedidos.html` — Documentação técnica de Gestão de Pedidos (11 seções)

### Base de conhecimento (docs/kb/)
22 arquivos cobrindo: configuração de benefícios, redes de aceitação, cadastro de interlocutores e perfis, cadastro de colaboradores (planilha e tela), pedidos (planilha e tela), pagamento e disponibilização, acompanhamento de pedidos, relatórios, rastreio de cartões, visualização de contratos, cadastro de filiais e postos de trabalho, faturamento descentralizado, emissão de 2ª via.

### Relatórios de API (docs/reports/)
- `api_inventory.md` / `api_inventory_pedidos.md` — Inventário de endpoints
- `api_test_report.md` / `api_test_report_pedidos.md` — Resultados de testes reais
- `model_consumption_assessment.md` / `model_consumption_assessment_pedidos.md` — Avaliação de consumo pelo modelo

### Artefatos de API (artifacts/api_inventory/)
- `gestao_colaboradores_apis.json` / `gestao_pedidos_apis.json` — Schemas com exemplos de request/response
- `model_data_catalog.json` / `model_data_catalog_pedidos.json` — Catálogo de campos úteis e restritos

## Arquivos gerados

| Arquivo | Descrição |
|---|---|
| `01_requisitos_cliente.md` | Catálogo completo de requisitos por categoria com ID, origem e status |
| `02_matriz_rastreabilidade.md` | Rastreabilidade de cada requisito às fontes documentais |
| `artifacts/requirements_catalog.json` | Catálogo de requisitos em JSON válido |
| `artifacts/source_registry.json` | Registro de todas as fontes analisadas |

## Contagem de requisitos

| Categoria | Prefixo | Qtd |
|---|---|---|
| Requisitos Funcionais | RF | 20 |
| Regras de Negócio | RN | 18 |
| Requisitos Não Funcionais | RNF | 5 |
| Segurança | SEG | 9 |
| Tratamento de Erros | ERR | 9 |
| Critérios de Aceite | ACE | 20 |
| Fora do Escopo | FORA | 13 |
| Ambiguidades e Pendências | AMB | 5 |
| **Total** | | **99** |

## Status utilizados

- **CONFIRMED** — declarado explicitamente na especificação do cliente
- **AMBIGUOUS** — presente, mas com definição incompleta ou dependente de decisão técnica
- **CONFLICTING** — contradição identificada entre duas fontes
- **NOT_VALIDATED** — mencionado mas sem evidência de validação técnica
- **RECOMMENDATION** — oriundo de recomendação técnica dos reports, não do cliente

## Gerado em

2026-07-22 · Baseado nas fontes listadas acima
