# MARH — Conhecimento da Feature

> **Fonte exclusiva:** `docs/kb/` — 22 arquivos analisados.
>
> Este arquivo contém **somente** fatos de domínio, regras de produto e procedimentos informativos cujas fontes são os arquivos da base de conhecimento. Não contém políticas do agente, regras de comportamento do agente, mensagens de erro definidas pelo cliente, nem capacidades ou limitações do agente consultivo.
>
> Para capacidades, comportamentos, políticas e regras do agente, consultar `discover3/agent_policy.md`.
>
> **Status:** PENDING_CLIENT_APPROVAL — conteúdo rastreado à KB, aguarda aprovação antes de uso em produção.

---

## 1. Perfis de interlocutores

O Sistema de Pedidos Alelo reconhece quatro perfis de acesso. Cada perfil tem permissões distintas.

### Decisão
- Responsável autorizado pela empresa, definido exclusivamente no contrato com a Alelo.
- Tem acesso a todos os menus do Sistema de Pedidos.
- Pode conceder, liberar e manter o acesso dos demais interlocutores.
- **Não pode ser atribuído pelo sistema** — somente via contrato.
- Para alterar o Interlocutor de Decisão, é necessário acionar a **Central de Atendimento**.

### Gerenciamento
- Autorizado pelo interlocutor de Decisão.
- Acesso a todos os menus, incluindo configuração de benefícios, pedidos, solicitações de cartões e cancelamentos.

### Operação
- Autorizado pelo interlocutor de Decisão.
- Acesso a todos os menus **exceto** configuração de benefícios.
- Pode efetuar pedidos, solicitar cartões e cancelamentos.

### Financeiro
- Acesso restrito ao menu financeiro: cobranças emitidas (NFs, boletos), RPS, demonstrativo fiscal e informe de rendimento.
- **Não realiza pedidos** nem cadastro de colaboradores ou locais de entrega.

> Fonte: `2CADASTRO_INTERLO_PERFIS.md`, `2CADASTRO_INTERLO_EDITAR.md`

---

## 2. Configuração de benefícios

### Quem pode configurar
Somente interlocutores com perfil **Decisão** ou **Gerenciamento** podem habilitar ou desabilitar modalidades de benefícios.

### Modalidades disponíveis

| Modalidade | Estabelecimentos aceitos |
|---|---|
| **Alimentação** | Supermercados, armazéns, mercearias, açougues, peixarias, hortimercados, padarias, comércios de laticínios e frios |
| **Refeição** | Restaurantes, lanchonetes, bares, padarias |
| **Multibenefícios** | Supermercados, restaurantes, postos de combustível, farmácias, livrarias e outras redes credenciadas. Aceito em mais de 10 mil farmácias com descontos de até 85% em medicamentos. |

### Regras

- Se todas as modalidades estiverem desabilitadas, **não é possível realizar pedidos**.
- Habilitar uma modalidade **não faz o benefício aparecer automaticamente** no aplicativo do colaborador. É necessário realizar um pedido com valor para que os créditos sejam disponibilizados.
- **Não é permitida transferência** de saldo entre as contas de Alimentação, Refeição e Benefícios.

> Fonte: `1CONFIG_BENE_1.md`, `1CONFIG_BENE_REDES.md`

---

## 3. Colaboradores

### Campos obrigatórios no cadastro individual (via tela)

| Campo | Obrigatoriedade |
|---|---|
| Nome completo | Obrigatório |
| CPF | Obrigatório |
| Data de nascimento | Obrigatório |
| Nome da mãe | Obrigatório |
| Tipo de entrega (filial ou residência) | Obrigatório |
| E-mail | Não obrigatório — importante para onboarding no aplicativo |
| Telefone | Não obrigatório — importante para onboarding no aplicativo |

### Regra do CPF

**O CPF de um colaborador não pode ser alterado após o cadastro.**

### Cadastro por planilha

- Formato aceito: `.xls` ou `.xlsx`.
- Se a planilha contiver um CPF já cadastrado, os dados do colaborador existente são **atualizados** — não é criado um registro duplicado.

### Tags de produto

A tag de produto (Tudo, Alimentação, Refeição, Benefícios) é atribuída ao colaborador **apenas quando ele é incluído em um pedido**. O cadastro na tela de colaboradores não cria a tag.

> Fonte: `3CADASTRO_COLAB_TELA.md`, `3CADASTRO_COLAB_PLANILHA.md`, `3CADASTRO_COLAB_TAGS.md`

---

## 4. Pedidos

### Formas de criação

Um pedido pode ser criado de duas formas, ambas com o mesmo fluxo de 5 etapas:
- **Via tela**: seleção manual de colaboradores e valores por benefício.
- **Via planilha**: importação de arquivo `.xls`/`.xlsx` com dados dos colaboradores e valores.

> Atenção: novos colaboradores incluídos via planilha de pedido passam por validação de CPF na Receita Federal, o que pode causar espera. Para evitar espera, cadastre colaboradores antes de iniciar o pedido.

### As 5 etapas do pedido

1. Forma do pedido
2. Colaboradores e benefícios
3. Forma de pagamento e crédito
4. Resumo
5. Pagamento

### Forma de pagamento

A única forma de pagamento disponível é o **boleto bancário**.

### Tipos de disponibilização de crédito

| Tipo | Como funciona |
|---|---|
| **Automática** | Até 2 dias úteis após a compensação do boleto |
| **Agendada** | Na data futura escolhida pelo RH, desde que o boleto seja pago antes da data agendada |

### Cancelamento automático por boleto vencido

Pedidos com boleto **não pago em até 30 dias após o vencimento** são cancelados automaticamente.

> Fonte: `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md`, `6ACOMPA_PEDIDO_STATUS.md`

---

## 5. Status dos pedidos

| Status | Significado |
|---|---|
| **Aguardando pagamento** | Pedido processado, boleto gerado, aguardando pagamento |
| **Pagamento confirmado** | Pagamento registrado, aguardando emissão da nota fiscal |
| **Nota Fiscal Emitida** | Nota fiscal emitida, créditos em processo de disponibilização |
| **Aguardando Disponibilização** | Pagamento confirmado, aguardando liberação dos créditos nos cartões |
| **Pedido creditado** | Créditos disponibilizados nos cartões dos colaboradores |
| **Cancelado** | Pedido cancelado pelo cliente ou por falta de pagamento do boleto após 30 dias do vencimento |

> Fonte: `6ACOMPA_PEDIDO_STATUS.md`

---

## 6. Boleto e Nota Fiscal

### Boleto

- Gerado automaticamente após a confirmação do pedido.
- Disponível para pagamento imediatamente após o pedido.
- Prazo de compensação: **até 2 dias úteis** após o pagamento.

### Nota Fiscal

- Emitida **somente após a disponibilização dos créditos** nos cartões.
- Não é emitida no momento do pedido.

> Fonte: `6ACOMPA_PEDIDO_BOLETO_NF.md`, `5PAG_DISPO_BOLETO.md`

---

## 7. Modelo de cobrança (tarifas)

| Pedido | Composição do boleto |
|---|---|
| **1º pedido** | Tarifa de emissão de cartão + valor dos créditos |
| **2º pedido em diante** | Tarifas e taxas do pedido anterior + valor dos créditos do pedido atual |

As tarifas de administração aparecem sempre no boleto **do próximo pedido**. Exceção: no primeiro pedido, a tarifa de emissão de cartão já está incluída.

> Fonte: `5PAG_DISPO_MODELO_COBRANCA.md`

---

## 8. Alterar data de disponibilização de créditos

- Disponível apenas para pedidos **já pagos** (com pagamento confirmado).
- Pedidos com status "Aguardando pagamento" **não permitem** alteração de data.
- **Não há cobrança de tarifa** para antecipar ou postergar a data.

> Fonte: `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md`

---

## 9. Rastreamento de cartões

### Status de rastreamento

| Status | Significado |
|---|---|
| **Em processamento** | Pedido de cartão em processamento normal |
| **Aguardando código de rastreio** | Cartões ainda não foram despachados para a transportadora |
| **Erro no processamento** | Ocorreu um problema — acionar a central de atendimento |

### Informações disponíveis no rastreio (quando disponível)

- Número de rastreamento
- Endereço de entrega
- Previsão de entrega
- Linha do tempo de eventos (ex.: "Saiu para entrega", "Em produção")
- Barra de progresso: Produção → A caminho → Entrega

### Atenção

- O rastreio só fica disponível **após os cartões serem encaminhados para a transportadora**.
- Enquanto a fabricação não for iniciada, o detalhe de rastreio fica indisponível.

> Fonte: `8RASTREIO_CARTOES.md`

---

## 10. Emissão de 2ª via de cartão

### Quando é possível solicitar

A 2ª via pode ser solicitada nos casos de **perda ou roubo**. Para outros motivos, é necessário entrar em contato com a central de atendimento.

### Informações sobre o processo

- Ao confirmar, os **cartões ativos são cancelados automaticamente**. O cancelamento é irreversível.
- **Cartões virtuais** continuam funcionando até a ativação do novo cartão físico.
- A reemissão **não pode ser cancelada** após confirmação.
- As taxas de reemissão aparecem no **próximo pedido**.
- O rastreio do novo cartão fica disponível somente após o encaminhamento para a transportadora.
- Prazo de entrega: **7 a 10 dias úteis** após a emissão.

> Fonte: `manual-emissao-2via.md`

---

## 11. Relatórios disponíveis

| Tipo | Conteúdo | Formato |
|---|---|---|
| **Sintético de Cobrança** | Visão geral de todas as cobranças com status, valores, descontos e datas | PDF |
| **Analítico de Cobrança** | Detalhamento das taxas e tarifas de um pedido específico | PDF |
| **Disponibilização** | Créditos disponibilizados nos cartões com status, datas e valores | PDF |
| **Espelho de Pedidos** | Acompanhamento dos pedidos com exportação da planilha importada | Excel |

> Fonte: `7RELATORIOS.md`

---

## 12. Contratos

Os dados do contrato com a Alelo incluem: número do contrato, produto, filial contratante, status, responsável pela decisão, dados cadastrais, forma de pagamento, tipo de entrega e tarifas (emissão, reemissão, entrega corporativa/residencial, disponibilização).

Para alterar o Interlocutor de Decisão, é necessário entrar em contato com a **Central de Atendimento**. Essa alteração não pode ser feita pelo sistema.

> Fonte: `9VISUALIZAR_CONTRATOS.md`, `2CADASTRO_INTERLO_EDITAR.md`

---

## 13. Locais de entrega

### Filiais

- Podem ser cadastradas via tela ou planilha.
- Cada filial pode ter até **3 responsáveis** pelo recebimento dos cartões e até **3 responsáveis** pela nota fiscal.
- Responsáveis não podem ser editados diretamente — é necessário remover e adicionar.

### Postos de trabalho

- Cadastrados via planilha no formato `.xls` ou `.xlsx`, com limite de **15 MB**.
- Ao reimportar um CNPJ já cadastrado, os dados são **atualizados** — não é criado um registro duplicado.
- Raiz do CNPJ e Final do CNPJ não podem ser editados após o cadastro.

### Faturamento descentralizado

- Permite realizar pedidos com CNPJs de faturamento distintos, desde que tenham a **mesma raiz de CNPJ**.
- Cada CNPJ gera boletos separados.
- É necessário pagar **todos os boletos** de cada CNPJ para que os benefícios sejam disponibilizados integralmente.
- Um número de solicitação único agrupa todos os pedidos gerados.

> Fonte: `10CADASTRO_FILIAIS_TELA.md`, `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md`, `faturamento-descentralizado.md`

---

*Consolidado a partir de: `1CONFIG_BENE_1.md`, `1CONFIG_BENE_REDES.md`, `2CADASTRO_INTERLO_PERFIS.md`, `2CADASTRO_INTERLO_EDITAR.md`, `3CADASTRO_COLAB_TELA.md`, `3CADASTRO_COLAB_PLANILHA.md`, `3CADASTRO_COLAB_TAGS.md`, `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md`, `5PAG_DISPO_MODELO_COBRANCA.md`, `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md`, `6ACOMPA_PEDIDO_BOLETO_NF.md`, `6ACOMPA_PEDIDO_STATUS.md`, `7RELATORIOS.md`, `8RASTREIO_CARTOES.md`, `9VISUALIZAR_CONTRATOS.md`, `10CADASTRO_FILIAIS_TELA.md`, `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md`, `faturamento-descentralizado.md`, `manual-emissao-2via.md`*

*Status: PENDING_CLIENT_APPROVAL · Gerado em 2026-07-22*
