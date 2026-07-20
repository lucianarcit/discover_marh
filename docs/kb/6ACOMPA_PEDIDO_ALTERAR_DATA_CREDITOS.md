# Alterar Data de Disponibilização de Créditos

## Descrição
Funcionalidade disponível no Acompanhamento de Pedidos que permite à Empresa/RH alterar a data em que os créditos serão disponibilizados nos cartões dos colaboradores, desde que o boleto do pedido já esteja pago. O processo é realizado em quatro etapas via modal (acessar a opção, informar nova data, selecionar no calendário e confirmar), sem cobrança de tarifa adicional pela mudança de data.

**Nível de confidencialidade:** Uso interno

## Visão Geral

Funcionalidade que permite alterar a data em que os créditos serão disponibilizados nos cartões dos colaboradores.

- **Disponível apenas para pedidos pagos.**
- **Não será cobrada tarifa** pelo serviço de antecipação do crédito.

## Como Alterar a Data de Crédito

**Caminho:** Menu **Acompanhamento de Pedidos** → Detalhe do pedido → **"Alterar Data de Crédito"**

### Passo a Passo (4 etapas):

**Etapa 1 — Acessar a opção**
- No detalhe do pedido, localizar o botão **"ALTERAR DATA DE CRÉDITO"**
- O pedido deve estar com status de pagamento confirmado

**Etapa 2 — Informar nova data**
- Uma janela modal será exibida com:
  - **Data de crédito atual:** data já configurada (ex.: 14/08)
  - **Nova data de crédito:** campo para definir a nova data (calendário)
- Clicar no ícone de calendário para selecionar a data

**Etapa 3 — Selecionar no calendário**
- Calendário exibido com navegação por mês
- Selecionar a nova data desejada (ex.: 20/08)

**Etapa 4 — Confirmar a alteração**
- Tela de confirmação exibe:
  - **Nova data de crédito:** data selecionada (ex.: 20/08)
- Botões:
  - **VOLTAR** — cancela a operação
  - **CONFIRMAR ALTERAÇÃO** — efetiva a mudança

## Exemplo de Uso

| Campo | Antes | Depois |
|-------|-------|--------|
| Data de crédito | 14/08 | 20/08 |
| Pedido | 25603632 | 25603632 |
| Tarifa adicional | — | Nenhuma |

## Observações Importantes

- A alteração **só é possível após o pagamento** do boleto ser confirmado.
- Não há cobrança de tarifa para antecipação ou postergação da data de crédito.
- A nova data deve ser futura em relação à data atual.
- Pedidos com status "Aguardando pagamento" **não** permitem alteração de data.
