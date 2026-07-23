# Arquitetura AWS — POC do Agente Consultivo MARH

> **Versão:** 1.0  
> **Data:** 2026-07-23  
> **Região exclusiva:** `sa-east-1` (South America — São Paulo)  
> **Status:** Desenho arquitetural — nenhum recurso criado

---

## Objetivo

Desenho da arquitetura AWS para a POC do Agente Consultivo MARH, um agente de IA conversacional exclusivamente consultivo que responde perguntas sobre colaboradores, pedidos, rastreamento de cartões e dúvidas sobre a feature MARH no app Meu Alelo.

## Decisão Arquitetural

**Alternativa recomendada: B — Lambda com orquestração própria**

Justificativa resumida:
- Menor custo fixo (zero quando inativo)
- Menor complexidade operacional
- Latência controlável com provisioned concurrency
- Sem dependência de serviços em preview ou recém-lançados
- Totalmente disponível em `sa-east-1`
- Simples de implementar no prazo da POC

## Estrutura dos documentos

| Documento | Conteúdo |
|---|---|
| `00_resumo_decisao.md` | Decisão final com justificativa |
| `01_requisitos_arquiteturais.md` | Requisitos derivados do discovery |
| `02_disponibilidade_sa_east_1.md` | Matriz de disponibilidade regional |
| `03_alternativas_arquitetura.md` | Comparação das alternativas |
| `04_arquitetura_recomendada.md` | Arquitetura detalhada da POC |
| `05_fluxos_por_intencao.md` | Fluxos por tipo de intenção |
| `06_seguranca.md` | Segurança em camadas |
| `07_rede_conectividade.md` | Rede e conectividade |
| `08_performance_escalabilidade.md` | Performance, escalabilidade, latência |
| `09_resiliencia_erros.md` | Resiliência e tratamento de erros |
| `10_observabilidade.md` | Observabilidade e monitoramento |
| `11_estimativa_custos.md` | Estimativa de custos |
| `12_plano_poc.md` | Plano e escopo da POC |
| `13_riscos_pendencias.md` | Riscos e pendências |
| `14_adrs.md` | Architecture Decision Records |

### Diagramas (`diagrams/`)

Todos em formato Mermaid válido.

### Artefatos (`artifacts/`)

JSONs estruturados com dados de suporte.

## Restrições

- Todos os recursos em `sa-east-1`
- Sem cross-Region inference
- Sem serviços globais processando dados fora da região
- Apenas operações consultivas GET
- PII nunca enviado ao modelo
- Empresa selecionada vem exclusivamente do contexto da API MARH

---

*Fontes: `discover3/` — Discovery concluído em 2026-07-22*
