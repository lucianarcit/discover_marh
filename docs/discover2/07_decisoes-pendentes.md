# Decisões Pendentes — Agente Consultivo MARH

---

| ID | Decisão | Impacto | Responsável | Status | Data limite |
|---|---|---|---|---|---|
| D01 | Contrato da ma-hr-orch (URL, schema, auth, erros, timeout) | **Blocker total** — sem isso não há implementação | Time Alelo (ma-hr-orch) | Pendente | — |
| D02 | Autenticação server-to-server: API MARH → Agente | Blocker de deploy | Time Alelo + Arquitetura | Pendente | — |
| D03 | Autenticação Agente → ma-hr-orch | Blocker de integração | Time Alelo | Pendente | — |
| D04 | Campos de colaborador/pedido que podem ser exibidos | Blocker de Output Validator | Produto + Compliance | Pendente | — |
| D05 | Quem constrói o deeplink (agente, MARH, frontend, ma-hr-orch?) | Blocker de contrato de saída | Frontend + Produto | Pendente | — |
| D06 | Rastreio por CPF disponível na ma-hr-orch? | Define UX do rastreio | Time Alelo técnico | Pendente | — |
| D07 | Onde está a ma-hr-orch (VPC? internet? PrivateLink?) | Define rede e egress | Infra Alelo | Pendente | — |
| D08 | Runtime: AgentCore Runtime ou strands-agents em Lambda? | Custo e complexidade | Time técnico | Pendente | — |
| D09 | Knowledge source: Markdown no runtime vs. S3 vs. KB gerenciada? | Infra e processo de atualização | Time técnico | Pendente | — |
| D10 | Histórico de sessão: quem mantém? API MARH ou agente? | Define necessidade de AgentCore Memory | Produto + LGPD | Pendente | — |
| D11 | Retenção de dados: TTL? LGPD? | Compliance | Jurídico + Produto | Pendente | — |
| D12 | Modelo LLM específico in-region (sa-east-1) | Custo e qualidade | Time técnico | Pendente | — |
| D13 | Mascaramento de PII por campo (CPF, email, telefone) | UX + compliance | Produto + Compliance | Pendente | — |
| D14 | Markdown oficial: conteúdo aprovado pelo cliente | Blocker de respostas informativas | Produto + Cliente | Pendente | — |
| D15 | Versionamento e publicação do Markdown | Processo operacional | Time técnico | Pendente | — |

---

## Matriz de Campos por Caso de Uso (decisão pendente D04/D13)

| Caso de uso | Campo | Pode chegar ao agente? | Pode ser exibido? | Transformação |
|---|---|---|---|---|
| Colaborador | nome | Decisão pendente | Decisão pendente | — |
| Colaborador | local_entrega | Decisão pendente | Decisão pendente | — |
| Colaborador | produto | Decisão pendente | Decisão pendente | — |
| Colaborador | CPF | Decisão pendente | Decisão pendente | Mascarar? Omitir? |
| Colaborador | email | Decisão pendente | Decisão pendente | Omitir? |
| Colaborador | telefone | Decisão pendente | Decisão pendente | Omitir? |
| Pedido | nº pedido | Decisão pendente | Decisão pendente | — |
| Pedido | status | Decisão pendente | Decisão pendente | — |
| Pedido | data | Decisão pendente | Decisão pendente | — |
| Pedido | produto | Decisão pendente | Decisão pendente | — |
| Pedido | valor | Decisão pendente | Decisão pendente | — |
| Pedido | qtd colaboradores | Decisão pendente | Decisão pendente | — |
| Pedido | qtd cartões | Decisão pendente | Decisão pendente | — |
| Pedido | etapas | Decisão pendente | Decisão pendente | — |
| Rastreio | status entrega | Decisão pendente | Decisão pendente | — |
| Rastreio | data atualização | Decisão pendente | Decisão pendente | — |
| Rastreio | endereço | Decisão pendente | Decisão pendente | — |
| Rastreio | código rastreio | Decisão pendente | Decisão pendente | — |
| Todos | tokens internos | **Não** | **Não** | Bloquear |
| Todos | headers técnicos | **Não** | **Não** | Bloquear |
| Todos | IDs internos de sistema | **Não** | **Não** | Bloquear |

> A ma-hr-orch deve retornar somente dados autorizados. O Output Validator aplica allowlist como camada adicional.

---

## Matriz: Informação para Markdown Oficial (decisão pendente D14)

| Informação | Fonte | Autorizada no MVP? | Entra no Markdown? |
|---|---|---|---|
| Capacidades do agente (consultas suportadas) | Spec §1, §8 | ✅ | ✅ |
| Limitações (não cria, não cancela) | Spec §12 | ✅ | ✅ |
| O que é o MARH / Espaço RH | Spec §6 | ✅ | ✅ |
| Necessidade de empresa selecionada | Spec §5 | ✅ | ✅ |
| Tipos de consulta possíveis | Spec §10 | ✅ | ✅ |
| Orientação para jornadas oficiais | Spec §6 | ✅ | ✅ (orientar sem executar) |
| Mensagens padronizadas de erro/orientação | Spec §13 | ✅ | ✅ |
| Configuração de benefícios (docs antigos) | Discovery | ❌ | ❌ |
| Fluxo de pedido passo a passo (portal) | Discovery | ❌ | ❌ |
| Relatórios, faturamento, contratos | Discovery | ❌ | ❌ |
| 2ª via de cartão, cadastro de locais | Discovery | ❌ | ❌ |
