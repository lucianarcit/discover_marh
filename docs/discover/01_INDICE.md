# Documentação — Portal Alelo

Visão geral da pasta `docs/kb` e seus 22 arquivos de documentação, organizados por área funcional do portal.

---

## Estrutura da Pasta

A pasta `docs/kb` contém **22 arquivos Markdown** que cobrem as principais funcionalidades do portal Alelo. Os arquivos seguem uma numeração por área temática (1 a 10) mais dois arquivos suplementares sem número.

---

## Área 1 — Configuração de Benefícios

### [1CONFIG_BENE_1.md](../kb/1CONFIG_BENE_1.md)
Configuração inicial de benefícios, que deve ser feita antes do primeiro pedido. Apenas usuários com perfil **Decisão** ou **Gerenciamento** podem realizar essa configuração. Os três tipos de benefício disponíveis são **Refeição**, **Alimentação** e **Benefícios** — ao menos um deve estar habilitado para que pedidos possam ser feitos.

### [1CONFIG_BENE_REDES.md](../kb/1CONFIG_BENE_REDES.md)
Descreve as redes de aceitação de cada tipo de benefício:
- **Alimentação**: supermercados, açougues, padarias, etc.
- **Refeição**: restaurantes, lanchonetes, bares.
- **Multibenefícios**: aceito em supermercados, restaurantes, postos de gasolina, farmácias, livrarias e mais.

Essas informações são acessadas pelo tooltip (ícone de informação) na tela de configuração de benefícios.

---

## Área 2 — Cadastro de Interlocutores

### [2CADASTRO_INTERLO_PERFIS.md](../kb/2CADASTRO_INTERLO_PERFIS.md)
Define os quatro perfis de acesso dos usuários do portal:

| Perfil | Descrição |
|---|---|
| **Decisão** | Acesso completo; definido em contrato com a Alelo; gerencia os demais usuários. |
| **Gerenciamento** | Autorizado pelo perfil Decisão; pode configurar benefícios, fazer pedidos e gerenciar cartões/senhas. |
| **Operação** | Pode fazer pedidos, mas não configura benefícios. |
| **Financeiro** | Acesso somente leitura ao menu financeiro (faturas, boletos, RPS, demonstrativos fiscais). |

Inclui uma matriz completa de permissões por perfil.

### [2CADASTRO_INTERLO_EDITAR.md](../kb/2CADASTRO_INTERLO_EDITAR.md)
Passo a passo para criar e gerenciar interlocutores via *Menu Administração > Usuários do Sistema*. O cadastro é feito em duas etapas: dados pessoais (nome, CPF, data de nascimento, perfil) e dados profissionais (departamento, e-mail, telefone). Ações disponíveis: adicionar, editar, bloquear e excluir. Apenas o perfil **Decisão** pode gerenciar outros interlocutores.

---

## Área 3 — Cadastro de Colaboradores

### [3CADASTRO_COLAB_TELA.md](../kb/3CADASTRO_COLAB_TELA.md)
Cadastro manual (individual) de colaboradores diretamente na tela. Formulário em duas etapas: dados pessoais (nome, CPF, data de nascimento, nome da mãe, e-mail, telefone) e tipo de entrega (Filial ou Residência, com endereço completo). O CPF não pode ser alterado após o cadastro. Colaboradores podem ser editados ou excluídos.

### [3CADASTRO_COLAB_PLANILHA.md](../kb/3CADASTRO_COLAB_PLANILHA.md)
Cadastro em massa via planilha (`.xls`/`.xlsx`). Lista todas as colunas obrigatórias: `NOME_COLABORADOR`, `CPF`, `DATA_DE_NASCIMENTO`, `NOME_MAE`, `TELEFONE`, `EMAIL`, `TIPO_DO_LOCAL` (FI=Filial / ER=Residência), `CNPJ_VINCULADO` e campos de endereço. Reimportar um CPF já existente atualiza o registro.

### [3CADASTRO_COLAB_TAGS.md](../kb/3CADASTRO_COLAB_TAGS.md)
Explica as tags de produto (**Tudo**, **Alimentação**, **Refeição**, **Benefícios**) que são atribuídas aos colaboradores automaticamente — mas somente quando incluídos em um pedido, e não no momento do cadastro. A tela de colaboradores é usada apenas para pré-cadastro; os pedidos são feitos na tela "Faça seu Pedido".

---

## Área 4 — Pedidos

### [4PEDIDO_TELA.md](../kb/4PEDIDO_TELA.md)
Fluxo de pedido diretamente na tela (5 etapas): escolha do método > seleção de colaboradores e definição de valores de crédito por tipo de benefício > forma de pagamento > resumo > pagamento. Colaboradores podem ser adicionados ou editados no meio do fluxo. Todos os colaboradores incluídos são salvos no banco de dados de colaboradores.

### [4PEDIDO_PLANILHA.md](../kb/4PEDIDO_PLANILHA.md)
Fluxo de pedido via planilha. Mesmas 5 etapas do pedido por tela, mas os dados são importados de um arquivo `.xls`/`.xlsx` com colunas para dados do colaborador, tipo de entrega e valores por benefício (`ALIMENTACAO`, `REFEICAO`, `BENEFICIOS`). Novos colaboradores são cadastrados na importação, mas a validação do CPF na Receita Federal pode gerar atrasos.

---

## Área 5 — Pagamento e Disponibilização

### [5PAG_DISPO.md](../kb/5PAG_DISPO.md)
Descreve as opções de pagamento e disponibilização de créditos. O único meio de pagamento disponível é o **boleto bancário**. Dois modos de disponibilização:
- **Automática**: até 2 dias úteis após a compensação do boleto.
- **Agendada**: liberação em uma data futura escolhida (boleto deve ser pago antes da data).

A emissão e entrega de cartões físicos só começa após o pagamento do boleto.

### [5PAG_DISPO_BOLETO.md](../kb/5PAG_DISPO_BOLETO.md)
Cobre as etapas 4 (revisão do resumo) e 5 (geração do boleto) do fluxo de pedido. O resumo exibe produto, contrato, benefícios, número de colaboradores, prazo de entrega, data de crédito, forma de pagamento e total. Após clicar em "Fazer Pedido", o boleto é gerado imediatamente. A compensação leva até 2 dias úteis.

### [5PAG_DISPO_MODELO_COBRANCA.md](../kb/5PAG_DISPO_MODELO_COBRANCA.md)
Explica o modelo de cobrança com taxas diferidas:
- **Primeiro pedido**: boleto = taxa de emissão de cartão + valor do crédito.
- **Segundo pedido em diante**: boleto = taxas do pedido anterior + valor do crédito do pedido atual.

As taxas administrativas são sempre cobradas no ciclo de faturamento seguinte.

---

## Área 6 — Acompanhamento de Pedidos

### [6ACOMPA_PEDIDO_STATUS.md](../kb/6ACOMPA_PEDIDO_STATUS.md)
Lista todos os status possíveis de um pedido:

| Status | Descrição |
|---|---|
| Aguardando pagamento | Boleto gerado, aguardando compensação. |
| Pagamento confirmado | Boleto compensado. |
| Nota Fiscal Emitida | NF disponível. |
| Aguardando Disponibilização | Créditos ainda não liberados. |
| Pedido creditado | Créditos carregados nos cartões. |
| Cancelado | Cancelamento automático após 30 dias sem pagamento. |

Descreve a listagem (produto, número do pedido, valor, previsão de crédito, barra de progresso) e as ações disponíveis (copiar código de barras, ver detalhes).

### [6ACOMPA_PEDIDO_BOLETO_NF.md](../kb/6ACOMPA_PEDIDO_BOLETO_NF.md)
Como acessar o boleto e a nota fiscal. O boleto fica disponível imediatamente após a confirmação do pedido. A nota fiscal só é emitida após os créditos serem carregados nos cartões dos colaboradores. Apresenta o fluxo linear: pedido confirmado > boleto disponível > pagamento compensado > créditos liberados > NF emitida.

### [6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md](../kb/6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md)
Guia em 4 etapas para alterar a data de disponibilização de créditos de um pedido já pago: acessar o botão "Alterar Data de Crédito" no detalhe do pedido > visualizar a data atual > selecionar nova data no calendário > confirmar. Disponível apenas após confirmação do pagamento do boleto. Não há cobrança adicional pela alteração.

---

## Área 7 — Relatórios

### [7RELATORIOS.md](../kb/7RELATORIOS.md)
Descreve o módulo de relatórios (*Menu Relatórios*). Quatro tipos disponíveis:

| Relatório | Formato | Descrição |
|---|---|---|
| Sintético de Cobrança | PDF | Visão geral do faturamento. |
| Analítico de Cobrança | PDF | Detalhamento de taxas de um pedido específico. |
| Disponibilização | PDF | Créditos carregados nos cartões (status, data, valores). |
| Espelho de Pedidos | Excel | Planilha espelho dos pedidos. |

Os relatórios passam pelos status: *Aguardando processamento*, *Disponibilizado* ou *Erro no processamento*.

---

## Área 8 — Rastreio de Cartões

### [8RASTREIO_CARTOES.md](../kb/8RASTREIO_CARTOES.md)
Tela de rastreio de cartões (*Menu Cartões > Rastreio de Cartões*). Exibe todos os pedidos de cartão com produto, número do pedido, data, tipo de entrega (Centralizada/Descentralizada), quantidade de cartões emitidos, códigos de rastreio e status. "Ver Detalhes" abre a linha do tempo de entrega individual (em produção, no centro de distribuição, saiu para entrega), endereço, responsável pelo recebimento, barra de progresso e previsão de entrega. Pesquisável por CPF.

---

## Área 9 — Visualizar Contratos

### [9VISUALIZAR_CONTRATOS.md](../kb/9VISUALIZAR_CONTRATOS.md)
Como consultar os dados do contrato (*Menu Administração > Contratos*). Exibe número do contrato, produto, filial de faturamento (CNPJ), status, vendedor, dados do interlocutor Decisão, dados cadastrais da empresa, forma de pagamento, tipo de entrega e todas as taxas aplicáveis:

| Taxa | Valor |
|---|---|
| Emissão de cartão | R$ 10,00 |
| Reemissão de cartão | R$ 15,00 |
| Entrega corporativa | R$ 5,00 |
| Entrega residencial | R$ 2,00 |
| Disponibilização de crédito (por tipo) | R$ 2,00 |

Para alterar o interlocutor Decisão, é necessário entrar em contato com o suporte.

---

## Área 10 — Cadastro de Locais de Entrega

### [10CADASTRO_FILIAIS_TELA.md](../kb/10CADASTRO_FILIAIS_TELA.md)
Cadastro de filiais como locais de entrega diretamente na tela (*Menu Cadastro > Locais de Entrega*). Modal em 3 etapas: (1) dados cadastrais (sufixo do CNPJ, nome da filial, telefone, CNPJ de faturamento, endereço); (2) até 3 responsáveis pelo recebimento de cartões; (3) até 3 responsáveis pelo recebimento de nota fiscal. Locais existentes podem ser editados ou excluídos.

### [10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md](../kb/10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md)
Cadastro de **Postos de Trabalho** (tipo "PT") como locais de entrega via planilha. Baixar o modelo `.xls`, preencher tipo, código e endereço, depois importar (até 15 MB). Reimportar um CNPJ existente atualiza os dados. Também cobre edição (formulário em 3 etapas, igual ao de filial) e exclusão (com diálogo de confirmação irreversível). Inclui tabela com todos os botões e ações disponíveis na tela de locais de entrega.

---

## Arquivos Suplementares

### [faturamento-descentralizado.md](../kb/faturamento-descentralizado.md)
Guia completo da funcionalidade de **faturamento descentralizado**, que permite que filiais com diferentes CNPJs (mesmo raiz) tenham faturamentos separados. Pontos principais:
- Cada filial é associada a um CNPJ de faturamento.
- Um único pedido gera boletos separados por CNPJ de faturamento.
- Um "Número de Solicitação" agrupa todos os sub-pedidos resultantes.
- Todos os boletos devem ser pagos para a liberação integral dos créditos.

Inclui diagrama completo do fluxo em 7 etapas.

### [manual-emissao-2via.md](../kb/manual-emissao-2via.md)
Manual completo para emissão de **segunda via de cartões** (perda ou roubo). Acesso via *Menu Pedidos > Emissão de 2ª Via*. Processo em 4 etapas: selecionar produto/contrato > selecionar colaboradores e informar motivo (Perda/Roubo) > revisar resumo > aceitar termos e confirmar. Detalhes importantes:
- Cartões ativos são cancelados automaticamente na confirmação.
- Cartões virtuais permanecem ativos até a ativação do novo cartão físico.
- Prazo de entrega: 7 a 10 dias úteis.
- As taxas de reemissão aparecem no próximo pedido.
- O processo é irreversível após a confirmação.
- O rastreio só aparece após os cartões serem entregues à transportadora.

---

## Resumo Geral

| Arquivo | Área | Tipo |
|---|---|---|
| [1CONFIG_BENE_1.md](../kb/1CONFIG_BENE_1.md) | Configuração de benefícios | Guia de configuração |
| [1CONFIG_BENE_REDES.md](../kb/1CONFIG_BENE_REDES.md) | Redes de aceitação | Referência |
| [2CADASTRO_INTERLO_PERFIS.md](../kb/2CADASTRO_INTERLO_PERFIS.md) | Perfis de usuário | Referência / matriz de permissões |
| [2CADASTRO_INTERLO_EDITAR.md](../kb/2CADASTRO_INTERLO_EDITAR.md) | Gerenciamento de interlocutores | Passo a passo |
| [3CADASTRO_COLAB_TELA.md](../kb/3CADASTRO_COLAB_TELA.md) | Cadastro de colaboradores (tela) | Passo a passo |
| [3CADASTRO_COLAB_PLANILHA.md](../kb/3CADASTRO_COLAB_PLANILHA.md) | Cadastro de colaboradores (planilha) | Passo a passo |
| [3CADASTRO_COLAB_TAGS.md](../kb/3CADASTRO_COLAB_TAGS.md) | Tags de produto em colaboradores | Explicação conceitual |
| [4PEDIDO_TELA.md](../kb/4PEDIDO_TELA.md) | Pedido via tela | Passo a passo |
| [4PEDIDO_PLANILHA.md](../kb/4PEDIDO_PLANILHA.md) | Pedido via planilha | Passo a passo |
| [5PAG_DISPO.md](../kb/5PAG_DISPO.md) | Pagamento e disponibilização | Passo a passo |
| [5PAG_DISPO_BOLETO.md](../kb/5PAG_DISPO_BOLETO.md) | Geração do boleto e resumo do pedido | Passo a passo |
| [5PAG_DISPO_MODELO_COBRANCA.md](../kb/5PAG_DISPO_MODELO_COBRANCA.md) | Modelo de cobrança com taxas diferidas | Explicação conceitual |
| [6ACOMPA_PEDIDO_STATUS.md](../kb/6ACOMPA_PEDIDO_STATUS.md) | Status de pedidos | Referência |
| [6ACOMPA_PEDIDO_BOLETO_NF.md](../kb/6ACOMPA_PEDIDO_BOLETO_NF.md) | Acesso ao boleto e nota fiscal | Passo a passo |
| [6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md](../kb/6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md) | Alterar data de disponibilização | Passo a passo |
| [7RELATORIOS.md](../kb/7RELATORIOS.md) | Módulo de relatórios | Referência / passo a passo |
| [8RASTREIO_CARTOES.md](../kb/8RASTREIO_CARTOES.md) | Rastreio de entrega de cartões | Passo a passo |
| [9VISUALIZAR_CONTRATOS.md](../kb/9VISUALIZAR_CONTRATOS.md) | Consulta de dados do contrato | Passo a passo / referência |
| [10CADASTRO_FILIAIS_TELA.md](../kb/10CADASTRO_FILIAIS_TELA.md) | Cadastro de filiais (tela) | Passo a passo |
| [10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md](../kb/10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md) | Cadastro de postos de trabalho (planilha) | Passo a passo |
| [faturamento-descentralizado.md](../kb/faturamento-descentralizado.md) | Faturamento descentralizado | Guia de funcionalidade |
| [manual-emissao-2via.md](../kb/manual-emissao-2via.md) | Emissão de segunda via de cartão | Guia de funcionalidade |
