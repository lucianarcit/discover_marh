# Relatórios

## Descrição
Funcionalidade que permite à Empresa/RH solicitar, acompanhar e baixar relatórios sobre seus pedidos, disponível em quatro tipos: Sintético de Cobrança (visão geral das cobranças em PDF), Analítico de Cobrança (detalhamento de taxas em PDF), Disponibilização (créditos creditados nos cartões em PDF) e Espelho de Pedidos (planilha dos pedidos em Excel). Os relatórios passam pelos status de Aguardando processamento, Disponibilizado ou Erro no processamento.

**Nível de confidencialidade:** Uso interno

## Como Visualizar os Relatórios

**Caminho:** Menu **Relatórios** na área logada

> "Solicite, acompanhe e baixe os relatórios da sua empresa."

## Ações Disponíveis

- **SOLICITAR NOVO RELATÓRIO** — inicia a geração de um novo relatório
- **FILTROS** — filtra a lista de relatórios existentes

## Tipos de Relatórios Disponíveis

### 1. Relatório Sintético de Cobrança
- **Descrição:** Informações gerais de todas as cobranças dos pedidos selecionados.
- **Inclui:** status, valores, descontos e datas de pagamento.
- **Formato de download:** PDF

### 2. Relatório Analítico de Cobrança
- **Descrição:** Informações detalhadas da cobrança de um pedido específico.
- **Inclui:** detalhe de todas as taxas e tarifas incluídas na cobrança.
- **Formato de download:** PDF

### 3. Relatório de Disponibilização
- **Descrição:** Informações sobre os créditos disponibilizados nos cartões.
- **Inclui:** status, data e valores creditados nos cartões dos colaboradores.
- **Formato de download:** PDF

### 4. Relatório de Espelho de Pedidos
- **Descrição:** Acompanhamento dos pedidos com exportação da planilha.
- **Inclui:** planilha de pedidos importada e status do pedido.
- **Formato de download:** EXCEL

## Tela de Listagem de Relatórios

### Colunas da listagem:

| Coluna | Descrição |
|--------|-----------|
| Relatório | Nome do tipo e número do pedido |
| Status | Status do processamento |
| Solicitado em | Data da solicitação |
| Liberado em | Data em que o relatório ficou disponível |
| Ações | Botão de download (PDF ou EXCEL) e excluir 🗑️ |

### Status possíveis dos relatórios:

| Status | Significado |
|--------|-------------|
| **Aguardando processamento** | Relatório solicitado, ainda em geração |
| **Disponibilizado** | Relatório pronto para download |
| **Erro no processamento** | Falha na geração — pode ser necessário solicitar novamente |

## Exemplos de Relatórios na Listagem

| Relatório | Status | Solicitado em | Liberado em | Ação |
|-----------|--------|---------------|-------------|------|
| De Disponibilização \| Pedidos Nº: 101693 | Aguardando processamento | 21/06/2024 | — | PDF |
| Cobrança - Sintético \| Pedidos Nº: 95703 | Disponibilizado | 07/06/2024 | 07/06/2024 | PDF |
| Cobrança - Analítico \| Pedidos Nº: 95703 | Disponibilizado | 07/06/2024 | 07/06/2024 | PDF |
| De Espelho De Pedido \| Pedidos Nº: 95703 | Erro no processamento | 07/06/2024 | 07/06/2024 | EXCEL |
