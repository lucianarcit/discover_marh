# Boleto e Nota Fiscal

## Descrição
Documento que explica como acessar o boleto bancário e a nota fiscal no Sistema de Pedidos Alelo. O boleto fica disponível imediatamente após a confirmação do pedido e pode ser baixado na tela de Detalhe do Pedido ou no Acompanhamento de Pedidos. A nota fiscal é emitida somente após a disponibilização dos créditos nos cartões dos colaboradores, seguindo o fluxo: pedido criado → pagamento → compensação → créditos disponibilizados → nota fiscal emitida.

**Nível de confidencialidade:** Uso interno

## Visão Geral

### Boleto Bancário
- Disponibilizado assim que o pedido for confirmado.
- Pode ser consultado enquanto estiver aguardando pagamento.
- Acessível pela tela de **Detalhe do Pedido** ou na tela de **Acompanhamento de Pedidos**.

### Nota Fiscal
- Emitida **após a disponibilização dos créditos** nos cartões.
- Não é emitida no momento do pedido, mas sim após o crédito ser efetivado.

## Tela de Detalhe do Pedido

**Caminho:** Menu Acompanhamento de Pedidos → selecionar o pedido desejado

> "Acompanhe o pagamento, altere ou cancele o seu pedido aqui."

### Informações exibidas:

| Campo | Exemplo |
|-------|---------|
| Número do pedido | 101693 |
| Produto | Alelo Tudo |
| Benefícios | Refeição |
| Valor | R$ 1.000,00 |
| Quantidade de colaboradores | 1 |

### Ações disponíveis:
- **BAIXAR BOLETO** — faz o download do boleto bancário para pagamento
- **CANCELAR PEDIDO** — cancela o pedido (disponível antes do pagamento)

## Linha do Tempo — Situação do Pedido

A tela exibe uma linha do tempo com os marcos do pedido:

```
Pedido criado → Aguardando pagamento → Aguardando disponibilização → Aguardando emissão de nota fiscal
   (data)          [Baixar Boleto]            (data)                        (pendente)
```

### Exemplo real:
- **Pedido criado:** 21 de Junho de 2024
- **Aguardando pagamento:** link "Baixar Boleto"
- **Aguardando disponibilização:** 21 de Junho de 2024
- **Aguardando emissão de nota fiscal:** pendente

## Fluxo Completo

```
Pedido confirmado
      ↓
Boleto disponível (baixar e pagar)
      ↓
Pagamento compensado (até 2 dias úteis)
      ↓
Créditos disponibilizados nos cartões
      ↓
Nota Fiscal emitida
```
