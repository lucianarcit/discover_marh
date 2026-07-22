# Conhecimento MARH — Agente Consultivo

> Este arquivo é a fonte de conhecimento informativo do Agente Consultivo MARH.
> Seu conteúdo foi consolidado a partir dos documentos da base de conhecimento (`docs/kb`) e verifica conformidade com o escopo definido pelo cliente.
>
> **Uso previsto:** responder exclusivamente perguntas informativas sobre o funcionamento do MARH e do Espaço RH, sem realizar ações, sem consultar dados em tempo real e sem inventar informações.
>
> **Não contém:** endpoints, tokens, headers, dados pessoais reais, integrações internas ou operações transacionais.
>
> **Status:** aguardando aprovação do cliente antes de uso em produção.

---

## 1. O que é o MARH e o Espaço RH

O **MARH** (Meu Alelo RH) é o módulo do aplicativo Meu Alelo voltado para os interlocutores de RH das empresas. Por meio do Espaço RH, o interlocutor pode gerenciar colaboradores, realizar pedidos de benefícios e acompanhar entregas — tudo dentro do próprio aplicativo.

O **Espaço RH** é a área do app Meu Alelo onde essas funcionalidades estão reunidas. O Agente Consultivo MARH está disponível nessa área para auxiliar nas consultas do dia a dia.

> Fontes internas: `1CONFIG_BENE_1.md`, `2CADASTRO_INTERLO_PERFIS.md`

---

## 2. O que o Agente Consultivo MARH pode fazer

O agente realiza exclusivamente **consultas informativas**. Ele não executa ações, não altera dados e não realiza pedidos.

### Consultas disponíveis

1. **Consultar colaborador** — pelo nome ou CPF
2. **Consultar pedido** — pelo número do pedido
3. **Consultar o último pedido** da empresa selecionada
4. **Consultar pedidos por status** — pago, pendente, cancelado, em processamento etc.
5. **Rastrear cartão** de um colaborador — informando o número do pedido

### O que o agente não faz

O agente não realiza as seguintes ações. Para executá-las, acesse o Espaço RH:

- Criar, alterar ou cancelar pedidos
- Cadastrar, editar ou excluir colaboradores
- Alterar endereço de entrega
- Solicitar ou reemitir segunda via de cartão
- Realizar pagamentos
- Emitir relatórios ou boletos

> Fontes internas: `00_Agente_Consultivo_MARH.html` (seções 1, 7.3, 12)

---

## 3. Como usar o agente

### Empresa selecionada

O agente trabalha sempre com a empresa que você selecionou no app. Não é possível trocar a empresa digitando o nome, CNPJ ou número de contrato no chat. Se precisar consultar outra empresa, selecione-a no app antes de iniciar a conversa.

### Como fazer uma consulta

Basta digitar sua pergunta em linguagem natural. Exemplos:

- "Consultar colaborador João Silva."
- "Consultar pedido 342671."
- "Qual foi o último pedido?"
- "Quais pedidos estão pendentes?"
- "Rastrear cartão do pedido 342671."

> Fontes internas: `00_Agente_Consultivo_MARH.html` (seções 5, 8.1–8.5, 10)

---

## 4. Perfis de interlocutores

O sistema de pedidos Alelo reconhece quatro perfis de interlocutores. Cada perfil tem acesso a funções diferentes.

### Decisão
- Responsável autorizado pela empresa, definido no contrato com a Alelo.
- Tem acesso a todos os menus.
- Pode conceder acesso e gerenciar os demais interlocutores.
- **Não pode ser atribuído pelo sistema** — é definido exclusivamente no contrato.
- Para alterar o Interlocutor de Decisão, é necessário entrar em contato com a **Central de Atendimento**.

### Gerenciamento
- Autorizado pelo interlocutor de Decisão.
- Acesso a todos os menus, incluindo configuração de benefícios e pedidos.

### Operação
- Autorizado pelo interlocutor de Decisão.
- Acesso a todos os menus, **exceto** configuração de benefícios.

### Financeiro
- Acesso exclusivo ao menu financeiro (cobranças, boletos, notas fiscais, demonstrativo fiscal).
- Não realiza pedidos nem cadastro de colaboradores.

> Fontes internas: `2CADASTRO_INTERLO_PERFIS.md`, `2CADASTRO_INTERLO_EDITAR.md`

---

## 5. Configuração de benefícios

### Perfis que podem configurar

Somente interlocutores com perfil **Decisão** ou **Gerenciamento** podem habilitar ou desabilitar modalidades de benefícios.

### Modalidades disponíveis

| Modalidade | Onde é aceito |
|---|---|
| **Alimentação** | Supermercados, armazéns, mercearias, açougues, peixarias, hortimercados, padarias, comércios de laticínios e frios |
| **Refeição** | Restaurantes, lanchonetes, bares, padarias |
| **Multibenefícios** | Supermercados, restaurantes, postos de combustível, farmácias, livrarias e outras redes credenciadas |

### Regras importantes

- Se todas as modalidades estiverem desabilitadas, **não é possível realizar pedidos**.
- Habilitar uma modalidade na configuração **não faz o benefício aparecer automaticamente** no aplicativo do colaborador. É necessário também realizar um pedido com valor para que os créditos sejam disponibilizados.
- **Não é permitida transferência** de saldo entre as contas de Alimentação, Refeição e Benefícios.

> Fontes internas: `1CONFIG_BENE_1.md`, `1CONFIG_BENE_REDES.md`

---

## 6. Colaboradores

### Campos obrigatórios no cadastro

Para cadastrar um colaborador, os seguintes campos são obrigatórios:

- Nome completo
- CPF
- Data de nascimento
- Nome da mãe
- Tipo de entrega (filial ou residência)

E-mail e telefone não são obrigatórios, mas são importantes para o processo de onboarding no aplicativo.

### Regra sobre CPF

**O CPF de um colaborador não pode ser alterado após o cadastro.**

### Cadastro por planilha

É possível importar múltiplos colaboradores de uma vez usando uma planilha no formato `.xls` ou `.xlsx`. Se a planilha contiver um CPF já cadastrado, os dados do colaborador existente serão **atualizados** — não será criado um registro duplicado.

### Tags de produto

A tag de produto (ex.: Tudo, Alimentação, Refeição, Benefícios) é atribuída ao colaborador **apenas quando ele é incluído em um pedido**. O cadastro na tela de colaboradores, por si só, não cria uma tag.

> Fontes internas: `3CADASTRO_COLAB_TELA.md`, `3CADASTRO_COLAB_PLANILHA.md`, `3CADASTRO_COLAB_TAGS.md`

---

## 7. Pedidos

### Como criar um pedido

Um pedido pode ser criado de duas formas:
- **Via tela**: selecionando colaboradores manualmente
- **Via planilha**: importando uma planilha com os dados dos colaboradores e valores

O fluxo é dividido em **5 etapas**:
1. Forma do pedido
2. Colaboradores e benefícios
3. Forma de pagamento e crédito
4. Resumo
5. Pagamento

> Atenção: Para evitar espera na validação de CPFs junto à Receita Federal, é recomendado cadastrar colaboradores novos **antes** de iniciar o pedido.

### Forma de pagamento

A única forma de pagamento disponível é o **boleto bancário**.

### Disponibilização de créditos

Os créditos podem ser disponibilizados de duas formas:

| Tipo | Como funciona |
|---|---|
| **Automática** | Até 2 dias úteis após a compensação do boleto |
| **Agendada** | Na data futura escolhida, desde que o boleto seja pago antes |

### Cancelamento automático

Pedidos com boleto **não pago em até 30 dias após o vencimento** são cancelados automaticamente.

> Fontes internas: `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md`, `6ACOMPA_PEDIDO_STATUS.md`

---

## 8. Status dos pedidos

Os pedidos passam pelos seguintes status:

| Status | Significado |
|---|---|
| **Aguardando pagamento** | Pedido processado, boleto gerado, aguardando pagamento |
| **Pagamento confirmado** | Pagamento registrado, aguardando emissão da nota fiscal |
| **Nota Fiscal Emitida** | Nota fiscal emitida, créditos em processo de disponibilização |
| **Aguardando Disponibilização** | Pagamento confirmado, aguardando liberação dos créditos nos cartões |
| **Pedido creditado** | Créditos disponibilizados nos cartões dos colaboradores |
| **Cancelado** | Pedido cancelado pelo cliente ou por falta de pagamento do boleto após 30 dias |

> Fontes internas: `6ACOMPA_PEDIDO_STATUS.md`

---

## 9. Boleto e Nota Fiscal

### Boleto

O boleto é gerado automaticamente após a confirmação do pedido e fica disponível para pagamento imediatamente. Pode ser acessado na tela de acompanhamento de pedidos.

O prazo de compensação do boleto é de **até 2 dias úteis** após o pagamento.

### Nota Fiscal

A nota fiscal é emitida **somente após a disponibilização dos créditos** nos cartões. Não é emitida no momento do pedido.

> Fontes internas: `6ACOMPA_PEDIDO_BOLETO_NF.md`, `5PAG_DISPO_BOLETO.md`

---

## 10. Modelo de cobrança (tarifas)

A cobrança de tarifas segue o modelo abaixo:

| Pedido | O que é cobrado no boleto |
|---|---|
| **1º pedido** | Tarifa de emissão de cartão + valor dos créditos |
| **2º pedido em diante** | Tarifas e taxas do pedido anterior + valor dos créditos do pedido atual |

Ou seja, as tarifas de administração aparecem sempre no boleto **do próximo pedido**, não no pedido que as gerou. Exceção: no primeiro pedido, a tarifa de emissão de cartão já vem junto.

> Fontes internas: `5PAG_DISPO_MODELO_COBRANCA.md`

---

## 11. Alterar data de disponibilização de créditos

É possível alterar a data em que os créditos serão disponibilizados nos cartões. Condições:

- Disponível apenas para pedidos **já pagos** (com pagamento confirmado).
- Pedidos com status "Aguardando pagamento" **não permitem** alteração de data.
- **Não há cobrança de tarifa** para antecipar ou postergar a data.

> Fontes internas: `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md`

---

## 12. Rastreamento de cartões

O rastreamento de cartões acompanha o processo de produção e entrega desde a emissão até o recebimento.

### Status de rastreamento

| Status | Significado |
|---|---|
| **Em processamento** | Pedido de cartão em processamento normal |
| **Aguardando código de rastreio** | Cartões ainda não foram despachados para entrega |
| **Erro no processamento** | Ocorreu um problema; entrar em contato com a central de atendimento |

### Informações disponíveis no rastreio

Quando o rastreio está disponível, é possível ver:
- Número de rastreamento
- Endereço de entrega
- Previsão de entrega
- Linha do tempo de eventos (ex.: "Saiu para entrega", "Em produção")

### Atenção

- O rastreio de cartões só fica disponível **após os cartões serem encaminhados para a transportadora**.
- Enquanto a fabricação e entrega dos cartões não for iniciada, o detalhe de rastreio fica indisponível.

### Como o agente faz o rastreamento

O agente realiza o rastreamento por meio de consulta via sistema. Para isso, **é necessário informar o número do pedido**. O rastreamento direto pelo CPF do colaborador está em avaliação técnica — por enquanto, o agente solicitará o número do pedido caso apenas o CPF seja informado.

> Fontes internas: `8RASTREIO_CARTOES.md`, `manual-emissao-2via.md`

---

## 13. Emissão de 2ª via de cartão

A 2ª via de cartão pode ser solicitada diretamente no Sistema de Pedidos em casos de **perda ou roubo**. Para outros motivos, é necessário entrar em contato com a central de atendimento.

### Pontos importantes

- Ao confirmar a solicitação, os **cartões ativos são cancelados automaticamente**. Confirme com o colaborador antes de solicitar.
- Cartões virtuais continuam funcionando até que o novo cartão físico seja ativado.
- A reemissão **não pode ser cancelada** após a confirmação.
- As taxas de reemissão aparecem no **próximo pedido**.
- O rastreio do cartão reemitido só fica disponível após o encaminhamento para a transportadora. O prazo de entrega é de **7 a 10 dias úteis**.

> **Atenção:** O agente não solicita 2ª via. Para iniciar o processo, acesse a jornada de emissão de 2ª via no Espaço RH.

> Fontes internas: `manual-emissao-2via.md`

---

## 14. Relatórios disponíveis

O sistema disponibiliza quatro tipos de relatórios:

| Tipo | Conteúdo | Formato |
|---|---|---|
| **Sintético de Cobrança** | Visão geral de todas as cobranças dos pedidos selecionados, com status, valores, descontos e datas | PDF |
| **Analítico de Cobrança** | Detalhamento das taxas e tarifas de um pedido específico | PDF |
| **Disponibilização** | Créditos disponibilizados nos cartões, com status, datas e valores | PDF |
| **Espelho de Pedidos** | Acompanhamento dos pedidos com exportação da planilha importada | Excel |

> **Atenção:** O agente não gera relatórios. Para acessá-los, utilize o menu Relatórios no Sistema de Pedidos.

> Fontes internas: `7RELATORIOS.md`

---

## 15. Contratos

Os dados do contrato com a Alelo podem ser consultados no Sistema de Pedidos, em Administração > Contratos. As informações disponíveis incluem número do contrato, produto, filial contratante, status, tarifas de emissão, reemissão, entrega e disponibilização.

Para alterar o Interlocutor de Decisão responsável pelo contrato, é necessário entrar em contato com a **Central de Atendimento**. Essa alteração não pode ser feita pelo sistema.

> Fontes internas: `9VISUALIZAR_CONTRATOS.md`, `2CADASTRO_INTERLO_EDITAR.md`

---

## 16. Locais de entrega e filiais

### Filiais

As filiais são os locais de entrega dos cartões. Podem ser cadastradas via tela ou por importação de planilha. Cada filial pode ter até 3 responsáveis pelo recebimento dos cartões e até 3 responsáveis pela nota fiscal.

### Postos de trabalho

Postos de trabalho também podem ser cadastrados como locais de entrega. A importação via planilha aceita arquivos `.xls` ou `.xlsx` de até **15 MB**. Ao reimportar um CNPJ já cadastrado, os dados são atualizados — não é criado um registro duplicado.

### Faturamento descentralizado

No faturamento descentralizado, é possível realizar pedidos com CNPJs de faturamento distintos, desde que tenham a **mesma raiz de CNPJ**. Cada CNPJ gera boletos separados, e é necessário pagar **todos os boletos** de cada CNPJ para que os benefícios sejam disponibilizados integralmente.

> Fontes internas: `10CADASTRO_FILIAIS_TELA.md`, `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md`, `faturamento-descentralizado.md`

---

## 17. Quando o agente não sabe responder

Se uma pergunta não estiver contemplada neste documento, o agente informará que não possui essa informação disponível sobre o MARH e orientará para as consultas que pode realizar: colaboradores, pedidos e rastreamento de cartões.

---

*Consolidado a partir de: `1CONFIG_BENE_1.md`, `1CONFIG_BENE_REDES.md`, `2CADASTRO_INTERLO_PERFIS.md`, `2CADASTRO_INTERLO_EDITAR.md`, `3CADASTRO_COLAB_TELA.md`, `3CADASTRO_COLAB_PLANILHA.md`, `3CADASTRO_COLAB_TAGS.md`, `4PEDIDO_PLANILHA.md`, `4PEDIDO_TELA.md`, `5PAG_DISPO.md`, `5PAG_DISPO_BOLETO.md`, `5PAG_DISPO_MODELO_COBRANCA.md`, `6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md`, `6ACOMPA_PEDIDO_BOLETO_NF.md`, `6ACOMPA_PEDIDO_STATUS.md`, `7RELATORIOS.md`, `8RASTREIO_CARTOES.md`, `9VISUALIZAR_CONTRATOS.md`, `10CADASTRO_FILIAIS_TELA.md`, `10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md`, `faturamento-descentralizado.md`, `manual-emissao-2via.md`*

*Status: PENDING_CLIENT_APPROVAL · Gerado em 2026-07-22*
