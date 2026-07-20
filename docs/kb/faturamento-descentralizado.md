# Faturamento Descentralizado

## Descrição
Funcionalidade que permite à Empresa/RH cadastrar filiais com CNPJs de faturamento distintos (desde que da mesma raiz de CNPJ) e realizar pedidos de benefícios que geram boletos separados por CNPJ de faturamento. Um número de solicitação único agrupa todos os pedidos gerados, e o acompanhamento é feito por esse agrupador. É necessário pagar todos os boletos de cada CNPJ para que os benefícios sejam disponibilizados integralmente.

## 1. O que é?

O Faturamento Descentralizado é uma funcionalidade que permite cadastrar e fazer pedido para CNPJs de faturamento distintos.

---

## 2. Cadastro de Local de Entrega

- Cadastre o local de entrega da filial desejada clicando no **ícone do lápis**.
- O cadastro deve ser feito pelo **interlocutor do RH**, na **filial contratante**, que não precisa necessariamente ser a matriz.

> **Lembre-se:** só é possível cadastrar filiais que tenham a **mesma raiz de CNPJ**.

### Como acessar

- A funcionalidade fica na seção **Locais de entrega**.
- A tela exibe todos os endereços registrados com opções de filtro por: Nome, Tipo (Filial, Posto, CNPJ Contratante, Todos) e CNPJ.
- Botões disponíveis:
  - **ADICIONAR NOVO LOCAL**
  - **IMPORTAR POSTO DE TRABALHO**
  - **FILTRAR / REMOVER FILTROS**

### Observações importantes

1. **Filial cadastrada:** A filial selecionada deve estar **previamente cadastrada** no local de entrega.
2. **Opção de CNPJ:** Você também pode optar por **"Usar o mesmo CNPJ informado para este local"**. Essa opção permite que a filial que está sendo cadastrada ou editada utilize seu próprio CNPJ para o faturamento.

> **Atenção:** A exclusão total do endereço **não está disponível** para o CNPJ Contratante. Edite o CNPJ Contratante somente se seu objetivo for mudar o endereço dele, pois isso também alterará o endereço de faturamento. Para adicionar um novo endereço de entrega, utilize o botão "Adicionar Novo Local".

### Campos do formulário de Cadastro de Local de Entrega

O cadastro possui 3 etapas:

1. **Dados cadastrais**
2. **Responsável pelos cartões**
3. **Responsável pela nota fiscal**

**Campos da etapa "Dados cadastrais":**

| Campo | Obrigatório |
|---|---|
| Raiz do CNPJ (preenchido automaticamente) | — |
| Final do CNPJ | Sim |
| Nome da Filial | Sim |
| Inscrição Estadual | Não |
| Inscrição Municipal | Não |
| Telefone Comercial | Sim |
| Ramal | Não |
| Telefone Secundário | Não |
| Ramal (secundário) | Não |
| CNPJ para Faturamento | Sim |
| Tipo de local | Sim |
| CEP | Sim |
| Endereço | Sim |
| Bairro | Sim |

> Preencha os dados de acordo com o cadastro na Receita Federal.

**Campo "CNPJ para Faturamento"** apresenta um dropdown com as opções:
- Usar o mesmo CNPJ informado para este local
- CNPJs já cadastrados da mesma raiz (ex.: 17.677.878/0001-39, 17.677.878/0001-32, 17.677.878/0001-33...)
- Opção "Carregar mais CNPJs"

---

## 3. Faça seu Pedido

- Na jornada de pedido, as alterações relacionadas ao faturamento descentralizado ocorrem a partir da etapa de **Pagamento**.
- Ao realizar um pedido, será exibida uma **modal** informando sobre a mudança.

### Mensagem exibida na modal

> **"Uma nova visualização para os seus pedidos"**
>
> Na próxima tela, você pode encontrar até 2 pedidos para cada CNPJ de faturamento. Isso acontece porque um deles será emitido pela **Alelo Instituição de Pagamento S.A.** e o outro pela **NAIP Instituição de Pagamento S.A.** Cada um deles refere-se aos produtos que cada instituição oferece.
>
> **Não se preocupe! O valor total continua sendo o mesmo.**
>
> Atente-se para realizar o **pagamento de TODOS os pedidos de cada CNPJ de faturamento**, assim, seu pedido de benefícios será disponibilizado por completo.

### Número da Solicitação

- O **número da solicitação** é único e se refere a cada processo de solicitação.
- Ele **agrupa TODOS OS PEDIDOS**, independentemente de haver faturamento descentralizado ou não.
- A partir de uma única solicitação de pedido, **podem ser gerados vários pedidos** ao final do processo.

**Exemplo de exibição na tela:**
```
CNPJ de faturamento: 123.456.878/0001-63 | 24/01/2025 - 16:22 | Solicitação 123
```

Dentro dessa solicitação podem existir múltiplos pedidos, por exemplo:
- **Alelo Tudo | Ali e Ref** — Contrato: 12678419 — Pedido: 25604671 — Alimentação e Refeição R$ 3.000,00 + Tarifas R$ 100,00 — Total: R$ 3.100,00
- **Alelo Tudo | Benefícios** — Contrato: 12678419 — Pedido: 25604672 — Benefícios R$ 3.000,00 + Tarifas R$ 100,00 — Total: R$ 3.100,00

---

## 4. Acompanhamento de Pedidos

- A partir do faturamento descentralizado, o **número de solicitação** é exibido para facilitar o acompanhamento, pois ele é o **agrupador do pedido**.
- A tela de **Acompanhamento de Pedidos** lista todos os pedidos relacionados ao perfil do usuário.

> **Informação:** Esta tela é somente para acompanhar os status do pedido. Caso queira rastrear os cartões, basta clicar no ícone de caminhão do pedido desejado.

### Informações exibidas no painel do pedido

| Informação | Exemplo |
|---|---|
| Saldos | Alimentação e Refeição |
| Pedido de crédito | R$ 260.000,00 |
| Tarifas e Taxas | R$ 10.000,00 |
| Total | R$ 270.000,00 |
| Pedido feito em | 3 de Março de 2025 |
| Meio de pagamento | Boleto bancário |
| Forma de pagamento | Antecipado |
| Previsão de crédito | 05 de Março |

---

## 5. Detalhe do Pedido

Ao abrir o ícone de detalhes no pedido, as **novas informações** exibidas com o faturamento descentralizado são:

- **CNPJ de faturamento**
- **Número da solicitação**

### Campos do detalhamento do pedido

**Resumo do valor total:**
| Campo | Exemplo |
|---|---|
| Pedido de crédito | R$ 100,00 |
| Tarifas e Taxas | R$ 100,00 |
| Total | R$ 200,00 |

**Informações gerais:**
| Campo | Exemplo |
|---|---|
| Valor total do pedido | R$ 330.000,00 |
| Pedido criado em | 27/01/2023 |
| Previsão de crédito em | Disponibilização em até 2 dias úteis após confirmação da data de pagamento |
| Meio de pagamento | Boleto |
| Forma de pagamento | Antecipado |
| Cartões que serão emitidos | 100 |
| Número da solicitação | 222 |
| Prestador de serviço | 93.000.000/0001-12 - Alelo S/A |
| Tipo do pedido | Crédito |

**Detalhes de entrega e faturamento:**
| Campo | Exemplo |
|---|---|
| Tipo de entrega | Descentralizada |
| Valor para emissão de cartões | De acordo com o seu contrato |
| Taxas e Tarifas | De acordo com o seu contrato |
| Envio dos cartões | Após a emissão, 5 dias úteis para capitais e 7 dia úteis para demais cidades |
| CNPJ de faturamento | 10123.459878/0001-63 |
| Endereço de faturamento | Nome Endereço no cadastro (Filial contratante) \| Rua Heitor Penteado, 1797 - Sala 1797 - Vila Madalena, São Paulo - SP - CEP: 05025-000 |

- Botão disponível: **VER TODOS OS ENDEREÇOS DE ENTREGA**

---

## Resumo do Fluxo — Faturamento Descentralizado

```
1. Cadastrar local de entrega (filial com mesmo raiz de CNPJ)
        ↓
2. Definir CNPJ de faturamento no local de entrega
        ↓
3. Realizar pedido normalmente
        ↓
4. Na etapa de Pagamento, o sistema exibe os pedidos separados por CNPJ
        ↓
5. Um número de solicitação único agrupa todos os pedidos
        ↓
6. Pagar TODOS os boletos de cada CNPJ de faturamento
        ↓
7. Acompanhar pedidos pelo número de solicitação
```

---

*Alelo © Copyright. Todos os direitos reservados.*
