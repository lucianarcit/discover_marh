# Documentação Vigente — Agente Consultivo MARH

## Fonte autoritativa

    docs/cliente/00_Agente_Consultivo_MARH.html

## Finalidade

Esta pasta contém a documentação técnica vigente do Agente Consultivo MARH, baseada na especificação fornecida pelo cliente em julho de 2026.

## Ordem de leitura

| # | Documento | Status |
|---|---|---|
| 01 | `01_requisitos-cliente.md` | Consolidado da spec |
| 02 | `02_arquitetura-logica.md` | Proposta aprovada |
| 03 | `03_workflow-agente.md` | Proposta aprovada |
| 04 | `04_contratos.md` | Proposta — bloqueadores pendentes |
| 05 | `05_infraestrutura-aws-mvp.md` | Proposta — decisões pendentes |
| 06 | `06_plano-testes.md` | Proposta |
| 07 | `07_decisoes-pendentes.md` | Atualizado continuamente |
| 08 | `08_mapeamento-apis-e-rotas.md` | Referência técnica — APIs, rotas, campos, POC |

**08 — `08_mapeamento-apis-e-rotas.md`**

- **Finalidade:** inventário técnico das operações consultivas, rotas de webview, campos observados e gaps identificados a partir da consolidação do brief técnico.
- **Fontes usadas:** `docs/cliente/brief_kiro_apis_rotas_marh.md` (consolidação de Gestao_de_Colaboradores.html, Gestao_de_Pedidos.html, Rotas_hr_space.html).
- **Posição de leitura:** após `04_contratos.md` e antes de `06_plano-testes.md`. Serve como referência para validação de contratos e construção de testes.
- **Não é fonte funcional:** não altera os requisitos de `01_requisitos-cliente.md`.

## Decisões bloqueadoras

Ver `07_decisoes-pendentes.md` para a lista completa. Principais:

1. Contrato da ma-hr-orch (schema, URL, auth, erros)
2. Autenticação server-to-server (API MARH → Agente)
3. Autenticação Agente → ma-hr-orch
4. Campos de dados permitidos para exibição

## Referências

- Desenho: `docs/desenhos/arquitetura_bot_alelo_v4_cliente.drawio.xml`
- Discovery histórico: `docs/discover/`
- Knowledge Base de domínio (referência): `docs/kb/`
