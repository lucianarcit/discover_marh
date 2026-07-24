# Probe — 10. Bloqueadores Arquiteturais

**Região:** sa-east-1
**Data:** 2026-07-23

## Resultado

**Nenhum bloqueio arquitetural identificado.**

## Verificações realizadas

| Bloqueador potencial | ID | Resultado |
|---|---|---|
| Embedding não disponível em sa-east-1 | BLOCKER-EMBED-SA-EAST-1 | **NÃO ATIVADO** — `amazon.titan-embed-text-v2:0` ACTIVE, invocado com sucesso |
| Modelo de geração não disponível em sa-east-1 | BLOCKER-GEN-MODEL-SA-EAST-1 | **NÃO ATIVADO** — 12 modelos com Converse ativo |
| Armazenamento vetorial exige outra região | BLOCKER-VECTOR-STORE-SA-EAST-1 | **NÃO ATIVADO** — Knowledge Bases e S3 Vectors ambos disponíveis em sa-east-1 |
| Cross-region necessário | — | **NÃO DETECTADO** — nenhum componente exigiu outra região |

## Itens pendentes (não são bloqueadores)

| Item | Status |
|---|---|
| Seleção definitiva do modelo de geração | `PROPOSED_PENDING_ACTIVE_IN_REGION_VALIDATION` — múltiplos candidatos disponíveis |
| Calibração do threshold 0.70 | `PROPOSED_PENDING_EVALUATION` — ocorre no Passo 10 |
| Estimativa de custo definitiva | `PENDING_MODEL_AND_VECTOR_STORE_SELECTION` |
| Custo fixo do OpenSearch Serverless | Confirmar pricing sa-east-1 antes do deploy |
| Permissões de criação da Knowledge Base | Ampliar IAM no Passo 8 (Terraform) |
