# ADR-001 — Mecanismo de Armazenamento Vetorial

**Status:** DECIDIDO PROVISORIAMENTE — 2026-07-23
**Região:** sa-east-1 exclusivamente
**Revisão obrigatória:** gate end-to-end antes do Passo 8

## Contexto

A Fase 3 requer armazenamento e recuperação vetorial de chunks do corpus `marh_feature_knowledge.md`. Knowledge Bases e S3 Vectors **não são opções mutuamente excludentes** — Knowledge Bases pode usar S3 Vectors como vector store backend.

## Opções avaliadas

### Opção A — Knowledge Bases + S3 Vectors

Knowledge Bases como serviço de orquestração (ingestão, chunking, sincronização), usando S3 Vectors como vector store backend regional.

| Critério | Avaliação |
|---|---|
| Disponibilidade KB em sa-east-1 | **CONFIRMADA** (`KNOWLEDGE_BASE_SERVICE_REACHABLE=CONFIRMED`) |
| Disponibilidade S3 Vectors em sa-east-1 | **CONFIRMADA** (`list_vector_buckets` acessível) |
| Retrieve sem RetrieveAndGenerate | SIM — `bedrock-agent-runtime:Retrieve` reachable |
| Custo fixo | S3 Vectors sem custo fixo de OCU (diferença da Opção B) |
| Custo por query | Retrieve + S3 Vectors por consulta |
| Terraform | `aws_bedrockagent_knowledge_base` + S3 vector bucket |
| Controle da recuperação | Score por chunk retornado pelo Retrieve; threshold no cliente |
| Complexidade operacional | Menor que Opção C — ingestão gerenciada pela KB |
| Dependências adicionais | S3 Vectors (confirmado disponível) |
| End-to-end validado | **NÃO** — gate do Passo 8 |

### Opção B — Knowledge Bases + OpenSearch Serverless

Knowledge Bases com OpenSearch Serverless como vector store backend (padrão AWS).

| Critério | Avaliação |
|---|---|
| Disponibilidade em sa-east-1 | Disponível, mas OpenSearch Serverless tem custo fixo de OCU |
| Custo fixo | ~$0.10/OCU-hora mínimo — custo alto para POC/HML com uso esporádico |
| Retrieve sem RetrieveAndGenerate | SIM |
| Vantagem sobre Opção A | Nenhuma para POC |
| Desvantagem | Custo fixo de OCU durante todo o período HML |

### Opção C — Retriever próprio + S3 Vectors

Implementação manual de busca por similaridade diretamente no S3 Vectors, sem Knowledge Bases.

| Critério | Avaliação |
|---|---|
| Disponibilidade S3 Vectors em sa-east-1 | **CONFIRMADA** |
| Custo fixo | Nenhum além do S3 |
| Controle da recuperação | Total — implementação própria |
| Complexidade | Alta — ingestão manual, busca manual, embedding por query |
| Vantagem sobre Opções A/B | Controle total do score e filtros |
| Desvantagem | Mais código, mais superfície de falha para POC |

## Decisão provisória

**Opção A — Knowledge Bases + S3 Vectors**

### Justificativa

1. Menor custo fixo vs. Opção B (sem OCU do OpenSearch Serverless).
2. Menor complexidade de implementação vs. Opção C.
3. S3 Vectors e Knowledge Bases ambos confirmados disponíveis em sa-east-1.
4. `Retrieve` separado de geração preserva as interfaces `Retriever` e `LanguageModelClient`.
5. `RetrieveAndGenerate` não será usado em nenhuma opção.

### Condição para confirmação definitiva

A decisão é **provisória** até o gate end-to-end do Passo 8:
- Criar KB temporária com S3 Vectors em sa-east-1
- Ingerir corpus `marh_feature_knowledge.md`
- Executar `Retrieve` real com queries do `topic_to_query`
- Validar chunks + scores
- Se S3 Vectors não funcionar como backend da KB, revisar para Opção B ou C
- Destruir recursos do probe após validação

## Restrição mantida

`RetrieveAndGenerate` **não será utilizado** em nenhuma das opções. O fluxo sempre usa:

```
Retriever.retrieve() → chunks + scores → filtragem por threshold → LanguageModelClient.generate()
```

## Consequências

- Terraform criará: `aws_bedrockagent_knowledge_base` + S3 vector bucket
- IAM da Lambda: `bedrock:InvokeModel`, `bedrock-agent-runtime:Retrieve`
- Opção B (OpenSearch Serverless) disponível como fallback se gate falhar
- Opção C (Retriever próprio) disponível como último recurso
