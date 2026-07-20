# Cadastro de Colaboradores via Planilha

## Descrição
Funcionalidade que permite importar múltiplos colaboradores de uma vez por meio de uma planilha `.xls`/`.xlsx` com campos obrigatórios como nome, CPF, data de nascimento, e-mail, telefone e informações de local de entrega (filial ou residência). Colaboradores já cadastrados têm seus dados atualizados automaticamente ao reimportar a planilha com o mesmo CPF.

**Nível de confidencialidade:** Uso interno

## Visão Geral

Permite importar uma planilha para cadastrar vários colaboradores de uma vez.

## Como Iniciar

1. No Menu **Cadastro**, clique em **"Importar colaboradores"**
2. Na tela de importação, você poderá tirar dúvidas e acessar o modelo de planilha
3. Após importar a planilha, clique em **"Avançar"**
4. Se estiver corretamente preenchida, a importação será realizada com sucesso

## Informação Importante

> Ao importar via planilha colaboradores (CPF) que já estão cadastrados no sistema, estes terão suas informações **atualizadas** com os dados contidos na planilha.

## Recursos Disponíveis na Tela de Importação

- **BAIXAR O ARQUIVO MODELO DA PLANILHA** — modelo que pode ser alterado e importado
- **BAIXAR AS INSTRUÇÕES DE PREENCHIMENTO** — documento com instruções detalhadas

## Detalhes da Planilha

Preencha os dados de **todos** os colaboradores, incluindo e-mail e telefone.

### Campos Obrigatórios para o Pedido:
- **Tipo do Local** — `FI` (Filial) ou `ER` (Entrega Residência)
- **Local de Entrega** — CNPJ da filial contratante (para Filial) ou deixar em branco (para Residência)

### Colunas da Planilha Modelo:

| Coluna | Descrição |
|--------|-----------|
| NOME_COLABORADOR | Nome completo do colaborador |
| CPF | CPF do colaborador (sem formatação) |
| DATA_DE_NASCIMENTO | Data no formato DD/MM/AAAA |
| NOME_MAE | Nome da mãe do colaborador |
| TELEFONE | Número de telefone |
| EMAIL | Endereço de e-mail |
| TIPO_DO_LOCAL | `FI` para Filial / `ER` para Entrega Residência |
| CNPJ_VINCULADO | CNPJ da filial (obrigatório quando TIPO_DO_LOCAL = FI) |
| CEP | CEP do endereço de entrega |
| ENDEREÇO_DE_ENTREGA | Logradouro |
| NUMERO | Número do endereço |
| COMPLEMENTO | Complemento do endereço |
| MUNICIPIO | Cidade |
| BAIRRO | Bairro |
| ESTADO | UF (sigla do estado) |

### Exemplo de preenchimento:
- Maria Silva — CPF: 41187635401 — Nascimento: 30/04/1990 — Telefone: 1199785432 — Email: maria@hotmail.com — Tipo: ER — CNPJ: 11111111000111 — CEP: 08976-076 — Rua das Acucenas, 20 — São Paulo / Saúde / SP
- João Fernando Magal — CPF: 333897802 — Nascimento: 23/05/1995 — Telefone: 1188739843 — Email: joa.magal@hotmail.com — Tipo: FI — CNPJ: 11111111000111
