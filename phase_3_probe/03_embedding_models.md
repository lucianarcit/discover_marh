# Probe — 03. Modelos de Embedding

**Região:** sa-east-1

## Candidatos listados (8)

| modelId | Provider | Lifecycle | Inference | Invocação ON_DEMAND |
|---|---|---|---|---|
| `cohere.embed-v4:0` | Cohere | ACTIVE | INFERENCE_PROFILE | FALHOU — requer profile |
| `amazon.titan-embed-image-v1:0` | Amazon | ACTIVE | PROVISIONED | FALHOU — não suporta ON_DEMAND |
| `amazon.titan-embed-image-v1` | Amazon | ACTIVE | ON_DEMAND | **SUCCESS — 1024 dim / 190ms** |
| `amazon.titan-embed-text-v2:0` | Amazon | ACTIVE | ON_DEMAND | **SUCCESS — 1024 dim / 233ms** |
| `cohere.embed-english-v3:0:512` | Cohere | ACTIVE | PROVISIONED | FALHOU — ResourceNotFound |
| `cohere.embed-english-v3` | Cohere | ACTIVE | ON_DEMAND | FALHOU — schema divergente (não aceita `inputText`) |
| `cohere.embed-multilingual-v3:0:512` | Cohere | ACTIVE | PROVISIONED | FALHOU — ResourceNotFound |
| `cohere.embed-multilingual-v3` | Cohere | ACTIVE | ON_DEMAND | FALHOU — schema divergente |

## Modelos com invocação bem-sucedida

### `amazon.titan-embed-text-v2:0` — **CANDIDATO PRIMÁRIO**

- Lifecycle: ACTIVE
- Dimensão: 1024
- Latência: 233ms
- Input: texto (inputText)
- Multilingual: sim (PT-BR confirmado pela AWS)
- Max tokens: 8.192
- Inference: ON_DEMAND
- Status: **INVOCAÇÃO CONFIRMADA EM sa-east-1**

### `amazon.titan-embed-image-v1` — candidato secundário

- Lifecycle: ACTIVE
- Dimensão: 1024
- Latência: 190ms
- Propósito: imagem + texto — overkill para corpus texto puro
- Status: invocação confirmada, mas **não é o modelo certo** para RAG de texto

## Decisão de embedding

**Selecionado:** `amazon.titan-embed-text-v2:0`

Justificativa: modelo de texto, ACTIVE, ON_DEMAND, 1024 dimensões, invocação confirmada em sa-east-1 sem cross-region.

**Bloqueador:** nenhum.
