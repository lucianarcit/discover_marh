# Acompanhamento de Status de Pedidos

## Descrição
Funcionalidade que exibe a listagem de todos os pedidos do cliente com seus respectivos status (Aguardando pagamento, Pagamento confirmado, Nota Fiscal Emitida, Aguardando Disponibilização, Pedido creditado ou Cancelado) e permite acompanhar a progressão de cada pedido, baixar boleto, copiar código de barras e acessar o detalhe completo. Pedidos com boleto não pago em até 30 dias após o vencimento são cancelados automaticamente.

**Nível de confidencialidade:** Uso interno

## Acesso

**Caminho:** Menu **Acompanhamento de Pedidos** (área logada)

> "Listagem de todos os pedidos relacionados ao seu perfil."

## Status dos Pedidos

| Status | Descrição |
|--------|-----------|
| **Aguardando pagamento** | Pedido processado e com boleto criado |
| **Pagamento confirmado** | Pedido pago, aguardando nota fiscal |
| **Nota Fiscal Emitida** | Pedido pago e com nota fiscal emitida |
| **Aguardando Disponibilização** | Pedido pago, com nota fiscal, aguardando disponibilização dos créditos |
| **Pedido creditado** | Pedido pago e créditos disponibilizados nos cartões |
| **Cancelado** | Pedido cancelado pelo cliente ou por ausência de pagamento do boleto após **30 dias do vencimento** |

## Tela de Acompanhamento de Pedidos

### Informações da listagem:
- **Produto** (ex.: Alelo Tudo)
- **Número do Pedido** (ex.: 101693)
- **Valor** (ex.: R$ 1.000,00)
- **Previsão de crédito** (ex.: em 21 de Junho)
- **Status atual** com barra de progresso
- **Link para ação** (ex.: Baixar Boleto)

### Ações por pedido (ícones):
- 📋 Copiar linha do código de barras
- ℹ️ Ver detalhes do pedido
- ▶️ Navegar para o pedido

### Aviso sobre acompanhamento de cartões:
> O acompanhamento da entrega de seus cartões pode ser feito via **aplicativo do portador**. Em breve a funcionalidade estará disponível também no Sistema de Pedidos Alelo.

## Tela de Detalhe do Pedido

Ao clicar em um pedido, é exibida a tela de **Detalhe do Pedido** com:

### Informações do pedido:
- Número do pedido
- Produto (ex.: Alelo Tudo)
- Benefícios incluídos (ex.: Refeição)
- Valor total
- Quantidade de colaboradores

### Ações disponíveis no detalhe:
- **BAIXAR BOLETO** — download do boleto para pagamento
- **CANCELAR PEDIDO** — cancelamento do pedido

### Linha do tempo da situação:

```
Pedido criado → Aguardando pagamento → Aguardando disponibilização → Aguardando emissão de NF
   (data)          [Baixar Boleto]            (data)
```

## Regra de Cancelamento Automático

Pedidos com boleto **não pago em até 30 dias após o vencimento** são automaticamente cancelados.
