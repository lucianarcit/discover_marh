# Manual - Cadastro de Posto de Trabalho via Planilha

## Descrição
Funcionalidade que permite cadastrar, editar e excluir Postos de Trabalho no Sistema de Pedidos por meio da importação de uma planilha no formato `.xls` ou `.xlsx`. O processo inclui o download de um arquivo modelo, preenchimento com os dados do posto (tipo, código e endereço) e importação em lote, com atualização automática dos registros já existentes. Após a importação, os postos passam a constar na listagem de Locais de Entrega.

**Produto:** Alelo  
**Data:** Janeiro 2025

---

## Visão Geral

A funcionalidade permite cadastrar Postos de Trabalho via planilha, de forma prática e intuitiva.

### O que você pode fazer:
1. Baixar uma planilha modelo para o cadastro dos Postos de Trabalho
2. Fazer importação em lote, de quantos Postos de Trabalho forem necessários
3. Adicionar novos, editar e excluir qualquer Posto de Trabalho, a qualquer momento

---

## Cadastro de Posto de Trabalho via Planilha

### Passo 1 — Acessar Locais de Entrega

- Acesse o **Sistema de Pedidos**
- Clique em **Cadastro > Locais de Entrega**
- Na página, você verá a listagem dos locais de entrega cadastrados
- Para adicionar via planilha, clique no botão **"Importar Locais"**

> A tela exibe as colunas: **Nome**, **Tipo**, **CNPJ**, **Código do Local**, **Cidade**, **Estado** e **Ações** (editar/excluir)

### Passo 2 — Importar Planilha

Ao clicar no botão **"Importar Locais"**, uma janela modal abre com duas opções:

- **Baixar o Arquivo Modelo da Planilha** — planilha modelo com os campos a serem preenchidos
- **Baixar as Instruções de Preenchimento** — documento com instruções detalhadas

> **Formato aceito:** arquivos `.xls` ou `.xlsx` de até **15MB**

> **Informação importante:** Ao importar via planilha locais (CNPJs) que já estão cadastrados no sistema, estes terão suas informações atualizadas com os dados contidos na planilha.

### Passo 3 — Preencher e Importar a Planilha

Preencha a planilha com os seguintes dados:

| Campo | Descrição |
|---|---|
| Tipo de local de entrega | Código **"PT"** (Posto de Trabalho) |
| Código do posto de trabalho | Código correspondente ao posto |
| Endereço | Endereço completo correspondente ao posto |

**Fluxo de importação:**
1. Preencha a planilha conforme o modelo
2. Na janela "Importar Locais", arraste ou selecione o arquivo `.xls`/`.xlsx`
3. O sistema valida a planilha de acordo com os campos
4. Clique em **"Salvar"**
5. A importação é realizada com sucesso
6. O registro do Posto de Trabalho aparece na listagem de Locais de Entrega

---

## Edição do Posto de Trabalho

### Passo 4 — Acessar Edição

- Na tela principal de **Locais de Entrega**, clique no ícone de **editar (lápis)** na linha do registro desejado
- Uma janela de **"Edição de local de entrega - Filial"** será aberta

### Campos editáveis (organizados em 3 etapas):

**Etapa 1 — Dados Cadastrais:**
- Nome da Filial
- Inscrição Estadual
- Inscrição Municipal
- Telefone Comercial / Ramal
- Telefone Secundário
- CNPJ para Faturamento
- Endereço (CEP, etc.)

> **Atenção:** Alguns dados **não podem ser editados** para garantir a segurança das informações (ex: Raiz do CNPJ, Final do CNPJ)

**Etapa 2 — Responsável pelos Cartões:**
- Os dados dos responsáveis **não podem ser editados diretamente**
- Para alterar: clique em **"X Remover Responsável"** e adicione outro responsável

**Etapa 3 — Responsável pela Nota Fiscal:**
- Informe até **3 pessoas** autorizadas a receber a nota fiscal
- Os dados dos responsáveis **não podem ser editados diretamente**
- Para alterar: clique em **"X Remover Responsável"** e adicione outro responsável

> **Proteção de dados sensíveis:** Como medida de segurança, a visualização de dados sensíveis desta seção está desativada. Para verificar essas informações, acesse o menu **Cadastro > Colaboradores**.

### Passo 6 — Salvar Alterações

- Após realizar as alterações, clique em **"Salvar"**
- Uma mensagem de confirmação aparecerá no **canto superior direito** da tela:
  > **Sucesso :)** — Local de entrega atualizado com sucesso.

---

## Exclusão do Posto de Trabalho

### Passo 7 — Excluir Registro

- Na tela principal de **Locais de Entrega**, clique no ícone de **lixeira** na linha do registro desejado
- Uma janela de confirmação será aberta com a mensagem:
  > *"Tem certeza que deseja excluir o local de entrega [Nome] de CNPJ [número]? Ao concluir essa ação, não haverá mais cadastro do local no sistema. Você pode cadastrá-lo novamente no futuro."*
- Clique em **"Fechar e Excluir"** para confirmar

> **Atenção:** Esta ação é **irreversível**. O local de entrega será excluído imediatamente.

- Uma mensagem de confirmação aparecerá no canto superior direito:
  > **Sucesso :)** — Local de entrega excluído com sucesso.

---

## Botões e Ações Disponíveis na Tela de Locais de Entrega

| Botão / Ação | Descrição |
|---|---|
| Adicionar Nova Filial | Abre formulário para cadastro manual de filial |
| Importar Posto de Trabalho | Abre modal para importação via planilha |
| Ícone lápis (editar) | Abre janela de edição do local selecionado |
| Ícone lixeira (excluir) | Inicia fluxo de exclusão do local selecionado |
| Filtros | Filtra a listagem por critérios |

---

## Informações Adicionais

- A listagem exibe paginação com opção de **10 resultados por página** (configurável)
- A listagem mostra colunas: **Nome**, **Tipo**, **CNPJ**, **Código do Local**, **Cidade**, **Estado** e **Ações**
- O tipo **"PT"** identifica registros de Posto de Trabalho (diferente de "Filial")
- Após qualquer operação (importação, edição, exclusão), o sistema exibe mensagem de confirmação no canto superior direito da tela
