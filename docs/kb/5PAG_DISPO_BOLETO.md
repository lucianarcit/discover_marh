# Concluir e Gerar Boleto

## Descrição
Documento que descreve as etapas finais do fluxo de pedido: revisão do resumo com todas as informações (produto, contrato, benefícios, colaboradores, data de disponibilização e valor total) e geração do boleto bancário após confirmação. Após o pagamento do boleto, a compensação ocorre em até 2 dias úteis, os créditos são disponibilizados e a emissão e entrega dos cartões é iniciada.

**Nível de confidencialidade:** Uso interno

## Etapa 4 — Resumo do Pedido

Em **Resumo do Pedido** é possível confirmar todas as informações antes de finalizar.

### Informações exibidas no resumo:

- **Produto:** ex. Alelo Tudo
- **Contrato:** número do contrato
- **Benefícios:** tipos selecionados (ex.: Refeição)
- **Quantidade de colaboradores:** total de colaboradores no pedido
- **Entrega:** prazo (ex.: Até 7 dias úteis pós emissão dos cartões)
- **Data da disponibilização:** ex. Automática (até 2 dias úteis)
- **Pagamento:** ex. Antecipado
- **Meio de pagamento:** ex. Boleto
- **Total:** valor total + taxas

### Botões:
- **VOLTAR** — retorna para ajustes
- **FAZER PEDIDO** — confirma e processa o pedido

## Etapa 5 — Pagamento (Geração do Boleto)

Após clicar em **"FAZER PEDIDO"**, o sistema processa o pedido e exibe a tela de pagamento.

### Mensagens exibidas:

> **Seu boleto bancário já está disponível para pagamento!**
> O pedido foi processado e está disponível para pagamento aqui e na tela de acompanhamento de pedidos.

> **Atenção, lembre-se de pagar seu pedido!**
> O pedido só será finalizado e os cartões pedidos após o pagamento. Ao realizar o pagamento, o prazo para a confirmação é de até dois dias úteis. Por isso, não esqueça de pagar e se atente ao prazo do boleto assim que for gerado.

### Informações do pedido confirmado:

- **Produto:** ex. Alelo Tudo
- **Número do Pedido:** ex. 101693
- **Contrato:** ex. 90478624
- **Total:** R$ 1.000,00 + Taxas: R$ 0,00

### Botões disponíveis:
- **🖨 GERAR BOLETO** — gera o boleto para pagamento
- **Clique aqui para ir para a página de acompanhamento de pedidos**
- **VOLTAR PARA INÍCIO** — retorna à tela inicial
- **FAZER NOVO PEDIDO** — inicia um novo pedido

## Fluxo Resumido

```
Resumo do Pedido → FAZER PEDIDO → Boleto Gerado → Pagar Boleto → Compensação (até 2 dias úteis) → Créditos Disponibilizados → Emissão e Entrega dos Cartões
```
