# Pedido via Tela

## Descrição
Funcionalidade que permite realizar pedidos de crédito para colaboradores diretamente na tela do sistema, selecionando colaboradores manualmente e definindo o valor de cada modalidade de benefício (Refeição, Alimentação e Benefícios). O processo é dividido em cinco etapas — forma do pedido, colaboradores e benefícios, forma de pagamento, resumo e pagamento — e os colaboradores cadastrados neste fluxo são automaticamente salvos na base de cadastro.

**Nível de confidencialidade:** Uso interno

## Visão Geral

Permite adicionar colaboradores manualmente e escolher o valor de cada caixa de saldo diretamente na tela do sistema.

- É possível adicionar novos colaboradores e editar dados de colaboradores existentes durante o fluxo de pedido.
- Todos os colaboradores cadastrados neste fluxo também serão salvos na base de cadastro de colaboradores.

> **Atenção:** Cadastre novos colaboradores na tela "Cadastro de Colaboradores" antes de fazer o pedido para evitar espera na validação de CPFs.

## Etapas do Pedido via Tela

O processo é dividido em **5 etapas**:

1. **Forma do pedido** — selecionar "Pedido em tela"
2. **Colaboradores e benefícios** — selecionar colaboradores e definir valores
3. **Forma do pagamento e crédito**
4. **Resumo**
5. **Pagamento**

## Etapa 1 — Forma do Pedido

Selecione a opção **"Pedido em tela"**.

## Etapa 2 — Colaboradores e Benefícios

### Tela de Seleção de Colaboradores:

> Atenção: essa tela serve apenas para cadastro! O cadastro aqui NÃO configura pedido — para isso, acesse a tela "Faça seu pedido".

**Ações disponíveis:**
- **ADICIONAR NOVO COLABORADOR**
- **IMPORTAR COLABORADORES**
- **EXCLUIR SELECIONADOS**
- **FILTROS**

**Colunas da listagem:**
- Nome / CPF
- Data de Nascimento
- Tipo (Filial ou Residência)
- Local de Entrega
- Produto (tag do produto)
- Ações (editar ✏️ / excluir 🗑️)

### Seleção de Benefícios e Valores:

Após selecionar os colaboradores, defina os valores por tipo de benefício:

| Benefício | Exemplo de valor |
|-----------|-----------------|
| Refeição | R$ 1.000,00 |
| Alimentação | R$ 0,00 |
| Benefícios | R$ 0,00 |

> Para habilitar mais benefícios, acesse **Configuração de Benefícios** e ative os desejados. Em seguida, retorne para fazer o pedido.

> **Regra:** Não é permitida a realização de quaisquer transferências nas contas Alimentação, Refeição e Benefícios.

**Botões:**
- **VOLTAR** — retorna à etapa anterior
- **CONTINUAR** — avança para a forma de pagamento
