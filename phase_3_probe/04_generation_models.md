# Probe — 04. Modelos de Geração

**Região:** sa-east-1
**Excluídos explicitamente:** Claude 3 Haiku, Claude 3.5 Haiku
**Filtro de lifecycle:** `modelLifecycle.status == ACTIVE` (campo real da API)

## Nota sobre Claude 3 Sonnet

`anthropic.claude-3-sonnet-20240229-v1:0` aparece como `lifecycle=ACTIVE` na API de sa-east-1 em 2026-07-23, mas é um modelo de março de 2024. A Anthropic anunciou substituição progressiva por modelos mais recentes e recomenda migração para Claude 3.5+ ou Claude 3.7+. **Removido da shortlist** por risco de ciclo de vida curto — a seleção deve priorizar modelos com histórico de suporte mais longo na região.

## Candidatos testados com Converse — 12 ATIVOS

Todos com `modelLifecycle.status = ACTIVE` e `inferenceTypesSupported = ON_DEMAND`.

| modelId | Provider | Converse | Latência | lifecycle |
|---|---|---|---|---|
| `mistral.mistral-large-2402-v1:0` | Mistral AI | ATIVO | 402ms | ACTIVE |
| `mistral.magistral-small-2509` | Mistral AI | ATIVO | 283ms | ACTIVE |
| `mistral.ministral-3-14b-instruct` | Mistral AI | ATIVO | 259ms | ACTIVE |
| `mistral.ministral-3-8b-instruct` | Mistral AI | ATIVO | 201ms | ACTIVE |
| `mistral.mistral-7b-instruct-v0:2` | Mistral AI | ATIVO | 191ms | ACTIVE |
| `mistral.mixtral-8x7b-instruct-v0:1` | Mistral AI | ATIVO | 264ms | ACTIVE |
| `google.gemma-3-27b-it` | Google | ATIVO | 226ms | ACTIVE |
| `google.gemma-3-12b-it` | Google | ATIVO | 281ms | ACTIVE |
| `google.gemma-3-4b-it` | Google | ATIVO | 305ms | ACTIVE |
| `nvidia.nemotron-nano-12b-v2` | NVIDIA | ATIVO | 286ms | ACTIVE |
| `qwen.qwen3-32b-v1:0` | Qwen | ATIVO | 200ms | ACTIVE |
| `anthropic.claude-3-sonnet-20240229-v1:0` | Anthropic | ATIVO | 1123ms | ACTIVE (excluído da shortlist — ver nota) |

**Nenhum ACCESS_NOT_GRANTED. Nenhum CROSS_REGION_REQUIRED. Nenhum TIMEOUT.**

## Shortlist para avaliação PT-BR (Passo 10)

Critérios: lifecycle ACTIVE, Converse ativo em sa-east-1, adequado para respostas conversacionais em PT-BR, sem dependência de ciclo de vida curto.

| Candidato | Provider | Latência | Motivo de inclusão |
|---|---|---|---|
| `mistral.mistral-large-2402-v1:0` | Mistral | 402ms | PT-BR documentado, modelo maduro |
| `mistral.magistral-small-2509` | Mistral | 283ms | PT-BR adequado, lançamento recente |
| `mistral.ministral-3-14b-instruct` | Mistral | 259ms | multilingual, rápido |
| `google.gemma-3-27b-it` | Google | 226ms | multilingual — qualidade PT-BR a avaliar no Passo 10 |
| `qwen.qwen3-32b-v1:0` | Qwen | 200ms | multilingual amplo — qualidade PT-BR a avaliar no Passo 10 |

**Nota sobre Gemma e Qwen:** a inclusão na shortlist é baseada em suporte multilingual documentado pelos provedores, **não** em inferência a partir do nome do modelo. A qualidade real em PT-BR será determinada pela execução do dataset de avaliação no Passo 10.

## Status

`GENERATION_MODEL=PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION`

Seleção definitiva ocorre no Passo 10 com o dataset de 20 casos.

**Bloqueador:** nenhum.
