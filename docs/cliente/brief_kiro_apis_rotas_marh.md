# Brief compacto para o Kiro — APIs e rotas MARH

> Use este arquivo como entrada consolidada.  
> **Não abra nem releia os três HTMLs de origem nesta etapa**, salvo se eu apontar uma dúvida específica depois.

## 1. Hierarquia das fontes

1. `docs/cliente/00_Agente_Consultivo_MARH.html`
   - fonte funcional autoritativa;
   - define escopo, limitações, mensagens e critérios de aceite;
   - o agente é consultivo e não executa transações.

2. `Gestao_de_Colaboradores.html` e `Gestao_de_Pedidos.html`
   - fontes técnicas de endpoints, parâmetros, respostas e campos;
   - a existência de endpoint transacional **não autoriza** o agente a chamá-lo.

3. `Rotas_hr_space.html`
   - fonte técnica das rotas de webview;
   - rota transacional pode ser usada apenas para abrir a jornada oficial;
   - abrir uma tela não significa executar uma ação.

## 2. Regra absoluta de escopo

O agente pode:

- consultar colaboradores;
- consultar pedido por número;
- consultar último pedido;
- consultar pedidos por status, desde que exista suporte técnico correto;
- apoiar rastreamento quando houver dados confirmados;
- responder dúvidas da feature pelo Markdown;
- retornar navegação quando fizer sentido.

O agente não pode:

- criar, alterar ou cancelar pedido;
- cadastrar, editar ou excluir colaborador;
- solicitar ou reemitir cartão;
- realizar pagamento;
- alterar endereço ou status;
- chamar endpoints POST/PUT/PATCH/DELETE transacionais no MVP.

Para ações transacionais, o comportamento permitido é:

1. informar que o chat não executa a ação;
2. orientar a jornada oficial;
3. retornar `list_navigation` apenas quando existir rota autorizada;
4. nunca executar automaticamente.

## 3. APIs consultivas confirmadas para análise do MVP

### 3.1 Colaboradores

```http
GET cardholders-hr-management/v1/beneficiaries
```

Query parameters documentados:

- `nameOrCpf`: nome ou CPF;
- `page`: página.

Respostas documentadas:

- `200`: sucesso;
- `204`: nenhum conteúdo;
- erros de segurança/permissão devem ser tratados pela `ma-hr-orch`.

Uso no agente:

- consulta por nome ou CPF;
- múltiplos resultados exigem desambiguação;
- não exibir automaticamente todos os campos retornados;
- CPF, endereço, telefone, e-mail e outros dados pessoais devem ser avaliados para mascaramento/omissão.

### 3.2 Pedidos — lista/consulta

```http
GET cardholders-hr-management/v1/orders
```

Query parameters documentados:

- `page`;
- `size`;
- `orderNumber`.

Limitação documentada:

- não há filtro por período de 30, 60 ou 90 dias;
- não inventar query parameter de data;
- filtro por status não está confirmado como parâmetro do request.

Uso no agente:

- consultar pedido;
- obter lista para “último pedido”;
- apoiar pedidos por status somente após definir onde o filtro ocorrerá;
- não filtrar apenas uma página e apresentar como resultado completo.

Campos observados na documentação:

- número/ID do pedido;
- datas;
- valores;
- produto;
- quantidade de colaboradores/cartões;
- etapas;
- `collectNumber`;
- `trackingStatus`;
- `statusHistory`;
- `paymentType`;
- `productInfo`.

Não transformar a lista acima em contrato final sem normalização da `ma-hr-orch`.

### 3.3 Detalhe de pedido

```http
GET cardholders-hr-management/v1/orders/{orderNumber}
```

Uso no agente:

- detalhe do pedido pelo número;
- campos exibidos somente quando disponíveis e autorizados;
- resposta deve ser normalizada pela `ma-hr-orch`.

### 3.4 Colaboradores de um pedido

```http
GET cardholders-hr-management/v1/orders/{orderNumber}/beneficiaries
```

Query parameters:

- `page`;
- `size`.

Uso:

- consulta complementar;
- não ampliar o escopo funcional principal sem aprovação;
- pode apoiar detalhe de pedido e navegação para colaboradores do pedido.

## 4. Endpoints transacionais existentes

A documentação técnica contém operações transacionais, inclusive cancelamento de pedido.

Esses endpoints devem ser classificados como:

```text
TRANSACIONAL — PROIBIDO PARA O AGENTE NO MVP
```

Não criar tools para eles.

Usá-los somente para:

- identificar bloqueios;
- criar testes negativos;
- documentar a jornada correspondente;
- orientar navegação, quando existir rota autorizada.

## 5. Rotas hr-space relevantes

A aplicação usa `HashRouter`.

Padrão:

```text
{BASE_URL}/#{ROTA}
```

### Colaboradores

```text
#/employees
#/employees/new
#/employees/new/filiais
#/employees/new/postos
#/employees/new/residencia
#/employees/:id/edit
#/employees/:id/edit/filiais
#/employees/:id/edit/postos
#/employees/:id/edit/residencia
```

Classificação:

- `#/employees`: consultiva;
- rotas `/new...`: transacionais, somente navegação orientativa;
- rotas `/:id/edit...`: transacionais; não tratar como tela de detalhe somente leitura.

### Pedidos

```text
#/orders
#/order-request-group
#/order-detail/:orderNumber
#/order-detail/:orderNumber/beneficiaries
```

Classificação:

- `#/orders`: consultiva;
- `#/order-detail/:orderNumber`: consultiva;
- `#/order-detail/:orderNumber/beneficiaries`: consultiva complementar;
- `#/order-request-group`: confirmar finalidade antes de usar.

### Rastreamento

```text
#/card-tracking
#/card-tracking/:orderNumber
#/card-tracking/:orderNumber/:arNumber
```

Regras:

- usar somente parâmetros realmente disponíveis;
- não inventar `orderNumber` nem `arNumber`;
- rastreamento por CPF continua pendente;
- existência de `trackingStatus`, `collectNumber` ou histórico no pedido não confirma endpoint de rastreamento por CPF.

### Criação de pedido

```text
#/new-order/products
```

Uso permitido:

- somente orientação e abertura da jornada oficial;
- nunca criar pedido pelo chat.

### Segunda via de cartão

Nenhuma rota específica de segunda via foi confirmada neste resumo.

Comportamento:

- não inventar rota;
- informar limitação;
- orientar a jornada/canal oficial até confirmação.

## 6. Montagem do `list_navigation`

Algoritmo conceitual:

1. selecionar `BASE_URL` do ambiente;
2. montar a rota após `/#/`;
3. preencher somente IDs disponíveis;
4. não inventar ID, pedido ou AR;
5. gerar URL completa;
6. aplicar URL encoding à URL completa;
7. inserir no deeplink;
8. retornar como `list_navigation`.

Formato:

```markdown
[list_navigation](meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true)
```

Regras:

- retornar somente quando houver relação direta com a resposta;
- texto deve continuar compreensível sem o botão;
- ação transacional apenas abre a jornada;
- o botão nunca executa a ação automaticamente.

## 7. Mapeamento da POC do frontend

| Botão da POC | Comportamento correto |
|---|---|
| Descubra como posso te ajudar | Responder pelo Markdown de conhecimento, sem chamar API |
| Consultar pedido | Consultar lista/detalhe via `ma-hr-orch`; oferecer rota de pedido quando houver número |
| Adicionar novos colaboradores | Não executar cadastro; orientar e, se aprovado, abrir `#/employees/new` |
| Solicitar 2ª via do cartão | Não executar; não inventar rota; orientar jornada/canal oficial |

Não prometer na resposta inicial:

- leitura de áudio, PDF, imagem, Excel ou CSV;
- recargas, relatórios ou usuários;
- montagem/execução de pedido pelo chat;
- bloqueio, cancelamento ou segunda via como ação automática.

Essas capacidades só entram com aprovação funcional formal.

## 8. Decisões pendentes

Registrar em `07_decisoes-pendentes.md`:

1. Qual campo/regra define o “último pedido”?
2. A API retorna ordenação confiável?
3. Onde ocorre filtro por status?
4. Como tratar paginação ao filtrar status?
5. Rastreamento por CPF existe na `ma-hr-orch`?
6. Quando `arNumber` é obrigatório?
7. Existe rota oficial para segunda via?
8. A rota `#/employees/:id/edit` pode ser usada em um agente consultivo?
9. Qual camada constrói a URL/deeplink?
10. Quais campos podem ser exibidos e quais devem ser mascarados?
11. Qual identificador de colaborador é seguro para navegação?
12. O frontend espera texto puro com `[list_navigation]` ou resposta estruturada?

## 9. Documentos a atualizar

Não alterar novamente `01_requisitos-cliente.md`, salvo novo requisito funcional aprovado.

Atualizar:

- `02_arquitetura-logica.md`
  - fontes técnicas;
  - papel da `ma-hr-orch`;
  - navegação sem execução transacional.

- `03_workflow-agente.md`
  - intenção → consulta → normalização → resposta → navegação;
  - fluxos negativos para ações proibidas.

- `04_contratos.md`
  - operações consultivas normalizadas;
  - parâmetros;
  - respostas;
  - erros;
  - contrato de navegação.

- `06_plano-testes.md`
  - 200, 204, 403;
  - múltiplos colaboradores;
  - paginação;
  - último pedido sem ordenação confiável;
  - status sem filtro nativo;
  - IDs ausentes;
  - rotas transacionais sem execução;
  - segunda via sem rota confirmada.

- `07_decisoes-pendentes.md`
  - todas as decisões da seção 8.

Criar:

```text
docs/discover2/08_mapeamento-apis-e-rotas.md
```

Conteúdo esperado:

- matriz caso de uso × API × rota;
- APIs permitidas;
- APIs proibidas;
- campos relevantes;
- rotas consultivas;
- rotas transacionais;
- gaps e decisões.

## 10. Tarefa para o Kiro

Use somente este brief e os arquivos atuais de `docs/discover2`.

**Não abra os três HTMLs de API/rotas nesta etapa.**

Primeiro apresente um plano curto com:

1. arquivos a alterar;
2. seções a adicionar;
3. decisões que permanecerão pendentes;
4. riscos de ampliar escopo;
5. testes impactados.

Aguarde aprovação antes de editar.

Não implementar código.
Não criar tools.
Não chamar APIs.
Não alterar `docs/discover/`.
Não executar `git add`, `commit` ou `push`.
