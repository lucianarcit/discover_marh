# Probe — 05. Validação do Converse API

**Região:** sa-east-1
**Método testado:** `bedrock-runtime:Converse`
**Permissão IAM correspondente:** `bedrock:InvokeModel` (a API Converse usa esta permissão, não `bedrock:Converse`)
**Prompt sintético:** "Responda apenas: OK"
**Max tokens:** 10
**Timeout por chamada:** 20s

## Nota sobre permissão IAM

O Bedrock Converse API **não tem uma permissão IAM própria** chamada `bedrock:Converse` ou `bedrock-runtime:Converse`. Internamente usa:
- `bedrock:InvokeModel` — para invocação síncrona (Converse)
- `bedrock:InvokeModelWithResponseStream` — para streaming (ConverseStream)

Documentação AWS confirma: a ação IAM necessária para `Converse` é `bedrock:InvokeModel`.

## Resultados (excluindo Claude 3 Sonnet da shortlist — ver 04_generation_models.md)

| modelId | Status | Latência |
|---|---|---|
| `mistral.mistral-large-2402-v1:0` | CONVERSE_ACTIVE_IN_REGION | 402ms |
| `mistral.magistral-small-2509` | CONVERSE_ACTIVE_IN_REGION | 283ms |
| `mistral.ministral-3-14b-instruct` | CONVERSE_ACTIVE_IN_REGION | 259ms |
| `mistral.ministral-3-8b-instruct` | CONVERSE_ACTIVE_IN_REGION | 201ms |
| `mistral.mistral-7b-instruct-v0:2` | CONVERSE_ACTIVE_IN_REGION | 191ms |
| `mistral.mixtral-8x7b-instruct-v0:1` | CONVERSE_ACTIVE_IN_REGION | 264ms |
| `google.gemma-3-27b-it` | CONVERSE_ACTIVE_IN_REGION | 226ms |
| `google.gemma-3-12b-it` | CONVERSE_ACTIVE_IN_REGION | 281ms |
| `google.gemma-3-4b-it` | CONVERSE_ACTIVE_IN_REGION | 305ms |
| `nvidia.nemotron-nano-12b-v2` | CONVERSE_ACTIVE_IN_REGION | 286ms |
| `qwen.qwen3-32b-v1:0` | CONVERSE_ACTIVE_IN_REGION | 200ms |

## Classificações observadas

| Classificação | Quantidade |
|---|---|
| CONVERSE_ACTIVE_IN_REGION | **11** (shortlist, excl. Claude 3 Sonnet) |
| ACCESS_NOT_GRANTED | 0 |
| CROSS_REGION_REQUIRED | 0 |
| NOT_SUPPORTED | 0 |
| TIMEOUT | 0 |

## Conclusão

Todos os candidatos da shortlist respondem ao Converse API diretamente em sa-east-1, sem inference profile cross-region. Preferência arquitetural `CONVERSE_ACTIVE_IN_REGION` atendida por múltiplos modelos.
