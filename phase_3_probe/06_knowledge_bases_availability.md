# Probe — 06. Bedrock Knowledge Bases

**Região:** sa-east-1

## Resultados do probe

| Verificação | Status |
|---|---|
| `bedrock-agent:ListKnowledgeBases` | **KNOWLEDGE_BASE_SERVICE_REACHABLE=CONFIRMED** |
| `bedrock-agent-runtime:Retrieve` | **ENDPOINT_REACHABLE** — retornou `ValidationException` sem KB real (esperado) |
| Validação end-to-end (ingestão + Retrieve real) | **KNOWLEDGE_BASE_END_TO_END=NOT_YET_VALIDATED** |

## Interpretação

- A API `bedrock-agent` está disponível e responde em sa-east-1.
- O endpoint `Retrieve` está alcançável — retorna `ValidationException` ao ser chamado com KB inexistente, confirmando que o serviço está ativo na região e que a chamada chega ao plano de controle.
- **End-to-end não validado:** criar KB real, ingerir corpus, executar Retrieve e validar chunks + scores é o gate do Passo 8 (ver seção Gate Futuro abaixo). Não fazer agora.

## Modalidade de uso planejada (Fase 3)

- **Data source:** S3 (corpus `marh_feature_knowledge.md`)
- **Vector store:** S3 Vectors (ver ADR-001 — opção Knowledge Bases + S3 Vectors)
- **Operação de recuperação:** `bedrock-agent-runtime:Retrieve` — **NÃO** `RetrieveAndGenerate`
- **Geração:** separada, via `LanguageModelClient` (preserva interface)
- **Sincronização:** `StartIngestionJob` via S3 → Knowledge Base

## Gate futuro — antes do Passo 8

Antes de criar a infra definitiva, executar um probe end-to-end temporário:

1. Criar KB temporária em sa-east-1 com S3 Vectors
2. Fazer upload do corpus
3. Executar `StartIngestionJob`
4. Executar `Retrieve` real com queries do mapeamento `topic_to_query`
5. Validar chunks retornados e scores (verificar se threshold 0.70 é adequado)
6. Destruir todos os recursos criados no probe
7. Registrar resultado antes de avançar para Terraform definitivo

## Permissões futuras necessárias (não ampliar agora)

```
bedrock-agent:CreateKnowledgeBase
bedrock-agent:CreateDataSource
bedrock-agent:StartIngestionJob
bedrock-agent:GetKnowledgeBase
bedrock-agent-runtime:Retrieve
```

Permissão IAM para invocação do modelo de geração: `bedrock:InvokeModel` (não `bedrock:Converse`).

## Bloqueador

Nenhum para implementação de código. Gate end-to-end antes do Passo 8.
