# 01 — Requisitos Arquiteturais

> Derivados de `discover3/01_requisitos_cliente.md`, `discover3/12_criterios_aceite.md` e restrições do projeto.

---

## Requisitos Funcionais da Arquitetura

| ID | Requisito | Origem |
|---|---|---|
| RA-001 | API REST consumida pela API MARH | RF-006, RNF-001 |
| RA-002 | Receber e validar contexto de empresa em cada request | RF-007, RF-008 |
| RA-003 | Classificar intenção (CONSULTIVA, INFORMATIVA, FORA_DO_ESCOPO) | RF-002 |
| RA-004 | Responder perguntas informativas via RAG (markdown) | RF-004, RF-010 |
| RA-005 | Consultar dados em tempo real via ma-hr-orch | RF-003, RF-009 |
| RA-006 | Retornar respostas estáticas para ações fora do escopo | RF-005 |
| RA-007 | Tratar 10 códigos de erro com mensagens padronizadas | ERR-001 a ERR-010 |
| RA-008 | Sanitizar PII antes de enviar ao modelo | SEG-003, TEC-017, TEC-019 |
| RA-009 | Suportar múltiplas empresas simultaneamente (multi-tenant) | RF-007, SEG-006 |
| RA-010 | Impedir troca de empresa pelo chat | SEG-002, RN-012 |

## Requisitos Não Funcionais

| ID | Requisito | Tipo | Meta |
|---|---|---|---|
| RNA-001 | Região exclusiva sa-east-1 | Compliance | Obrigatório |
| RNA-002 | Sem cross-Region inference | Compliance | Obrigatório |
| RNA-003 | Latência total < 8s (P95) para API_ONLY | Performance | ASSUMPTION_REQUIRES_VALIDATION |
| RNA-004 | Latência total < 5s (P95) para RAG_ONLY | Performance | ASSUMPTION_REQUIRES_VALIDATION |
| RNA-005 | Suporte a 100+ usuários simultâneos | Escalabilidade | POC |
| RNA-006 | Custo fixo < $50/mês | Custo | POC |
| RNA-007 | Zero PII no contexto do modelo | Segurança | Obrigatório |
| RNA-008 | Criptografia at-rest com KMS | Segurança | Obrigatório |
| RNA-009 | Criptografia in-transit TLS 1.2+ | Segurança | Obrigatório |
| RNA-010 | Logs sem PII | Segurança | Obrigatório |
| RNA-011 | Stateless (sem memória de longo prazo na POC) | Simplicidade | POC |
| RNA-012 | Menor número possível de chamadas ao modelo | Custo/Latência | Obrigatório |
| RNA-013 | Disponibilidade durante horário comercial | Disponibilidade | POC |
| RNA-014 | Recovery < 5 minutos | Resiliência | POC |

## Restrições Obrigatórias

1. **Região:** Todos os recursos em `sa-east-1`
2. **Modelo:** Somente modelos com inferência In-Region em sa-east-1
3. **Dados:** Nenhum dado processado fora de sa-east-1
4. **Operações:** Somente GET consultivo — sem POST/PUT/DELETE
5. **Orquestração:** Chamadas corporativas apenas via ma-hr-orch
6. **Agente:** Single-agent — sem arquitetura multiagente
7. **Sessão:** Stateless na POC (contexto na requisição)
8. **Cache:** Sem cache de dados corporativos na POC
9. **Frontend:** Sem frontend próprio — API consumida pela API MARH

## Mapeamento: Requisitos → Componentes

| Componente | Requisitos atendidos |
|---|---|
| Lambda (runtime) | RA-001, RA-002, RA-003, RA-005, RA-006, RA-007, RA-008, RA-009, RA-010 |
| Bedrock (LLM) | RA-004, RA-005, RNA-012 |
| Knowledge Bases (RAG) | RA-004 |
| S3 (documentos) | RA-004, RNA-008 |
| S3 Vectors | RA-004 |
| Secrets Manager | RNA-008, RNA-009 |
| KMS | RNA-008 |
| CloudWatch | RNA-010 |

---

*Fonte: `discover3/01_requisitos_cliente.md`, `discover3/12_criterios_aceite.md` · 2026-07-23*
