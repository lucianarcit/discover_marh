# Probe — 02. Inventário de Foundation Models

**Região:** sa-east-1
**Total listado:** 55 modelos

Inventário completo em `artifacts/02_all_models_inventory.json`.

## Distribuição por modalidade de saída

| Modalidade de saída | Quantidade |
|---|---|
| TEXT (geração) | 47 |
| EMBEDDING | 8 |

## Inferência suportada

| Tipo | Modelos |
|---|---|
| ON_DEMAND | Maioria — disponível sem provisionamento |
| PROVISIONED | Alguns Cohere e Titan |
| INFERENCE_PROFILE | Cohere embed v4 (requer profile cross-account ou regional) |

## Observação sobre INFERENCE_PROFILE

`cohere.embed-v4:0` aparece na listagem mas exige `INFERENCE_PROFILE` para invocação — chamada direta ON_DEMAND retorna erro. Não é candidato sem configuração adicional.
