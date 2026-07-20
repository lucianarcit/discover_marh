# Pedido via Planilha

## Descrição
Funcionalidade que permite realizar pedidos de crédito para colaboradores importando uma planilha com dados pessoais, informações de entrega e valores por modalidade de benefício (Alimentação, Refeição e Benefícios). A planilha também realiza o cadastro dos colaboradores novos durante o processo, que é dividido em cinco etapas: forma do pedido, colaboradores e benefícios, forma de pagamento, resumo e pagamento.

**Nível de confidencialidade:** Uso interno

## Visão Geral

Permite importar uma planilha para realizar pedido de crédito para os colaboradores.

## Atenção — Tempo de Processamento

> Ao cadastrar novos colaboradores, são necessárias validações de CPFs junto à Receita Federal. Por isso, o processamento pode não ser imediato. **Para evitar espera na hora de fazer o pedido, cadastre os colaboradores novos na tela "Cadastro de Colaboradores" primeiro.**

## Como Iniciar o Pedido via Planilha

1. Acesse **"Faça seu pedido"**
2. Selecione **"Pedido via importação de planilha"**
3. Na tela de importação, acesse o modelo de planilha e as instruções
4. Clique em **CONTINUAR**

## Etapas do Pedido

O processo de pedido é dividido em 5 etapas:

1. **Forma do pedido** — selecionar "Pedido via importação de planilha"
2. **Colaboradores e benefícios** — dados via planilha
3. **Forma de pagamento e crédito**
4. **Resumo**
5. **Pagamento**

## Detalhes da Planilha de Pedido

A planilha de pedidos também realiza o **cadastro de colaboradores**, incluindo:
- Dados do colaborador
- Local de entrega
- Endereço
- Valores dos créditos por benefício

### Estrutura da Planilha — Colunas:

**Bloco A — Dados do Colaborador:**

| Coluna | Descrição |
|--------|-----------|
| NOME_COLABORADOR | Nome completo |
| CPF | CPF do colaborador |
| DATA_DE_NASCIMENTO | Data no formato DD/MM/AAAA |
| NOME_MAE | Nome da mãe |
| TELEFONE | Telefone de contato |
| EMAIL | E-mail do colaborador |

**Bloco B — Entrega:**

| Coluna | Descrição |
|--------|-----------|
| TIPO_DO_LOCAL | `FI` (Filial) ou `ER` (Entrega Residência) |
| CNPJ_VINCULADO | CNPJ da filial vinculada |
| CEP | CEP do endereço |
| ENDEREÇO_DE_ENTREGA | Logradouro |
| NUMERO | Número |
| COMPLEMENTO | Complemento |
| MUNICIPIO | Cidade |
| BAIRRO | Bairro |
| ESTADO | UF |

**Bloco C — Valores de Crédito:**

| Coluna | Descrição |
|--------|-----------|
| ALIMENTACAO | Valor do crédito de Alimentação (R$) |
| REFEICAO | Valor do crédito de Refeição (R$) |
| BENEFICIOS | Valor do crédito de Benefícios (R$) |

### Exemplo de linha preenchida:
- Maria Silva — CPF: 66000105096 — Nascimento: 30/04/1990 — Mãe: Teste — Tel: 1199785432 — Email: maria@hotmail.com — Tipo: ER — CNPJ: 11111111111111 — CEP: 08976-076 — Rua das Acucenas, 20 — São Paulo / Saúde / SP
