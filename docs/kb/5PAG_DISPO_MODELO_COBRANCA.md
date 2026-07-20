# Modelo de Cobrança

## Descrição
Documento que explica a estrutura de cobrança dos pedidos Alelo: no primeiro pedido, o boleto inclui a tarifa de emissão dos cartões novos mais o valor dos créditos; a partir do segundo pedido, as tarifas e taxas do pedido anterior são cobradas junto com os créditos do pedido atual. Ou seja, as tarifas de administração sempre chegam no boleto seguinte ao pedido que as gerou, exceto a tarifa de emissão de cartão no primeiro pedido.

**Nível de confidencialidade:** Uso interno

## Regra Geral

As tarifas e taxas referentes ao pedido **sempre serão cobradas no próximo pedido**, exceto no primeiro pedido, que já inclui a tarifa de emissão de cartões novos.

> Na emissão do boleto, fique atento às regras de cobrança!

## Estrutura de Cobrança por Pedido

### Primeiro Pedido

```
Cobrança do primeiro pedido =
  Tarifa de Emissão de cartão
  +
  Valor dos créditos a serem disponibilizados
```

- Inclui a **tarifa de emissão de cartões novos** (cobrada somente na primeira vez)
- Mais o **valor total dos créditos** dos benefícios selecionados

### Segundo Pedido em Diante

```
Cobrança do segundo pedido =
  Tarifas e taxas inerentes ao pedido anterior
  +
  Valor dos créditos a serem disponibilizados
```

- Inclui as **tarifas e taxas do pedido anterior** (cobradas com atraso de um ciclo)
- Mais o **valor total dos créditos** do pedido atual

## Resumo do Modelo

| Pedido | Composição do Boleto |
|--------|---------------------|
| 1º pedido | Tarifa de emissão de cartão + Valor dos créditos atuais |
| 2º pedido em diante | Tarifas do pedido anterior + Valor dos créditos atuais |

## Importante

- As tarifas de administração e outras taxas do pedido atual **não são cobradas no mesmo boleto** — aparecem no boleto seguinte.
- Exceção: o **primeiro pedido** já cobra a tarifa de emissão de cartão no próprio boleto.
