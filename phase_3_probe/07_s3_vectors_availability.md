# Probe — 07. S3 Vectors

**Região:** sa-east-1

## Resultados

| Verificação | Status |
|---|---|
| Cliente boto3 `s3vectors` | **CREATABLE** — boto3 1.43.55 suporta |
| `list_vector_buckets` | **AVAILABLE_AND_ACCESSIBLE** — 0 buckets (esperado) |

## Interpretação

- S3 Vectors está disponível em sa-east-1 e acessível com as credenciais atuais.
- Nenhum vector bucket existe (correto — não criar neste probe).
- boto3 1.43.55 tem suporte ao cliente `s3vectors`.

## Relevância para ADR-001

S3 Vectors é uma alternativa viável, mas a escolha do probe é **Knowledge Bases** pelos motivos documentados no ADR-001:

- Knowledge Bases tem menor complexidade operacional
- Retrieve separado de geração preserva as interfaces `Retriever` / `LanguageModelClient`
- S3 Vectors requer implementação manual de busca por similaridade

S3 Vectors permanece como **opção de fallback** se Knowledge Bases apresentar restrição operacional não identificada no probe.

## Bloqueador

Nenhum.
