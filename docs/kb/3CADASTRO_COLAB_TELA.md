# Cadastro de Colaboradores via Tela

## Descrição
Funcionalidade que permite cadastrar colaboradores individualmente por meio de formulário em tela, preenchendo dados pessoais (nome, CPF, data de nascimento, nome da mãe, e-mail e telefone) e informações de entrega (filial ou residência com endereço completo). Após o cadastro, o colaborador pode ser editado ou excluído na listagem, sendo que o CPF não pode ser alterado após o cadastro.

**Nível de confidencialidade:** Uso interno

## Acesso

**Caminho:** Menu **Cadastro** → **"Adicionar Novo Colaborador"**

## Como Cadastrar

Preencha os dados do colaborador na tela de cadastro. Campos obrigatórios devem ser preenchidos para prosseguir.

### Etapa 1 — Dados e Tipo de Entrega

**Dados do Colaborador:**

| Campo | Obrigatoriedade |
|-------|----------------|
| Nome do Colaborador | Obrigatório |
| CPF | Obrigatório |
| Data de Nascimento | Obrigatório |
| Nome da Mãe | Obrigatório |
| E-mail | Importante para onboarding no aplicativo |
| Telefone | Importante para onboarding no aplicativo |

> Os campos de e-mail e telefone não são obrigatórios, mas são **importantes para o onboarding** na utilização do aplicativo.

**Entrega:**
- **Tipo de entrega** (obrigatório) — selecionar entre:
  - **Filial**
  - **Residência**

### Etapa 2 — Endereço de Entrega

**Se o tipo de entrega for Filial:**
- Selecionar o **CNPJ da filial cadastrada** (obrigatório)
- Clicar em **SALVAR**

**Se o tipo de entrega for Residência:**
- Preencher o endereço completo:
  - CEP (obrigatório)
  - Endereço (obrigatório)
  - Número (obrigatório)
  - Complemento
  - Bairro (obrigatório)
  - Estado (obrigatório)
  - Município (obrigatório)

### Botões de navegação:
- **CANCELAR** — cancela o cadastro
- **AVANÇAR** — avança para a etapa de endereço
- **VOLTAR** — retorna à etapa anterior
- **SALVAR** — conclui o cadastro

## Editar ou Excluir Colaborador

Na listagem de colaboradores, ao lado de cada colaborador há dois ícones:
- ✏️ **Editar** — abre o formulário de edição
- 🗑️ **Excluir** — remove o colaborador

> **Atenção:** Não será possível alterar o **CPF** do colaborador após o cadastro.
