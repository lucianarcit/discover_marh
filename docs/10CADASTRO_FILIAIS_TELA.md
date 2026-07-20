# Cadastro de Filiais - Via Tela

## Descrição
Funcionalidade que permite cadastrar uma ou mais filiais diretamente no Sistema de Pedidos, por meio de um formulário em tela dividido em três etapas: dados cadastrais, definição dos responsáveis pelo recebimento dos cartões e responsáveis pela nota fiscal. Ao final, a filial cadastrada passa a aparecer na listagem de locais de entrega e pode ser editada ou excluída.

**Manual:** Cadastro de filial via tela
**Data:** Janeiro 2025

## Visão Geral

A funcionalidade de cadastro de filial via tela permite cadastrar uma ou mais filiais de forma prática e intuitiva diretamente no Sistema de Pedidos.

**Objetivo:** Melhorar a experiência do cliente, proporcionando conveniência, segurança e personalização de entrega, aumentando a satisfação e fidelidade do cliente.

## O que é possível fazer

1. **Cadastrar** quantas filiais forem necessárias
2. **Associar até 3 colaboradores** responsáveis pelas entregas nesta filial
3. **Associar até 3 colaboradores** responsáveis pelas notas fiscais desta filial

## Como acessar

- Acesse o **Sistema de Pedidos**
- Clique em: **Cadastro > Locais de Entrega**
- A tela exibirá a listagem dos locais de entrega cadastrados

## Passo a Passo do Cadastro

### Passo 1 — Listagem de Locais de Entrega
A tela inicial exibe:
- Lista de locais de entrega com colunas: **Nome**, **Tipo**, **CNPJ**, **Código do Local**, **Cidade**, **Estado**, **Ações**
- Botões disponíveis: **ADICIONAR NOVO LOCAL** | **IMPORTAR LOCAIS** | **FILTROS**
- Paginação com número de registros encontrados (ex: 100 registros)
- Ações por registro: editar (lápis) e excluir (lixeira)

### Passo 2 — Adicionar Novo Local
Ao clicar em **"Adicionar novo local"**, abre-se um modal com 3 etapas:
1. Dados cadastrais
2. Responsável pelos cartões
3. Responsável pela nota fiscal

> Não é permitido avançar sem que os dados obrigatórios estejam preenchidos. O botão "Avançar" só é habilitado quando todos os campos obrigatórios estão corretos.

### Passo 3 — Dados Cadastrais
Campos obrigatórios (*) da seção **Dados da empresa**:

| Campo | Observação |
|-------|-----------|
| Raiz do CNPJ | Preenchido automaticamente |
| Final do CNPJ* | Informar o sufixo |
| Nome da Filial* | Nome da filial |
| Inscrição Estadual | Opcional |
| Inscrição Municipal | Opcional |
| Telefone Comercial* | Com DDD |
| Ramal | Opcional |
| Telefone Secundário | Opcional |
| Ramal secundário | Opcional |
| CNPJ para faturamento* | Selecionável |

Campos de **Endereço**:

| Campo | Observação |
|-------|-----------|
| Tipo de local* | Filial, etc. |
| CEP* | |
| Endereço* | |
| Número* | |
| Complemento | Opcional |
| Bairro* | |
| Estado* | |
| Município* | |

> **Atenção:** Preencher os dados de acordo com o cadastro na Receita Federal.

### Passo 4 — Responsável pelos Cartões
- Título da seção: **Responsáveis pelo recebimento dos cartões**
- Informe até **3 pessoas** autorizadas a receber e distribuir cartões e senhas enviadas para este local de entrega
- Clicar em **"SELECIONE UM USUÁRIO EXISTENTE"** para abrir a lista de usuários

> **Proteção de dados sensíveis:** Por medida de segurança, a visualização de dados sensíveis desta seção está desativada. Para verificar essas informações, acesse o menu **Cadastro > Colaboradores**.

**Validação:** Ao finalizar o cadastro da filial com responsável selecionado, o sistema valida no menu "Usuários do sistema" se o perfil do interlocutor está com **perfil de recebimento**.

#### Lista de usuários — Responsável pela entrega
A lista exibe:
- **Nome**
- **CPF**
- **Tipo** (perfis: Gerenciamento, Faturamento, Recebimento, Decisão, Operação)

Após selecionar, são exibidos os dados do responsável:
- Nome completo
- E-mail
- Telefone comercial
- Ramal
- Botão: **REMOVER RESPONSÁVEL**

### Passo 5 — Responsável pela Nota Fiscal
- Título: **Responsáveis pelo recebimento da nota fiscal**
- Informe até **3 pessoas** autorizadas a receber a nota fiscal enviada para este local de entrega
- Mesma dinâmica do passo anterior: clicar em **"SELECIONE UM USUÁRIO EXISTENTE"**

**Etapas após seleção:**
- Ao selecionar um ou mais usuários, o botão **SELECIONAR** é habilitado
- Retorna ao modal com o botão **SALVAR** habilitado

### Passo 6 (Final) — Confirmação
- Ao salvar com sucesso, o sistema retorna para a tela de **listagem de filiais**
- A nova filial aparece na lista com todas as informações cadastradas

## Resumo do fluxo

```
Locais de Entrega
  └─ ADICIONAR NOVO LOCAL
       ├─ [1] Dados cadastrais → AVANÇAR
       ├─ [2] Responsável pelos cartões → AVANÇAR
       └─ [3] Responsável pela nota fiscal → SALVAR → Listagem atualizada
```

## Observações importantes

- É possível **editar** e **excluir** locais de entrega existentes
- Manter os dados sempre **atualizados**
- O cadastro via tela é uma alternativa à importação via planilha (**IMPORTAR LOCAIS**)
- Até **3 responsáveis** podem ser associados tanto para recebimento de cartões quanto para nota fiscal
- Usuários cadastrados apenas para ser responsável pela entrega são uma funcionalidade em desenvolvimento (opção desativada temporariamente)
