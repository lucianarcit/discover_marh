# 01 — Requisitos Arquiteturais

> Derivados de `discover3/01_requisitos_cliente.md`, `discover3/12_criterios_aceite.md` e restrições do projeto.
> Revisão corretiva: 2026-07-23

---

## Requisitos Funcionais da Arquitetura

| ID | Requisito | Origem | Notas |
|---|---|---|---|
| RA-001 | Agente disponível via API REST — consumido pela API MARH | RF-006, RNF-001 | Entrada via InvokeFunction SDK ou Function URL AWS_IAM |
| RA-002 | Receber e validar contexto de empresa em cada request | RF-007, RF-008 | Validar presença e formato — não autorização |
| RA-003 | Classificar intenção (CONSULTIVA, INFORMATIVA, FORA_DO_ESCOPO) | RF-002 | Classificação determinística — sem LLM |
| RA-004 | Responder perguntas informativas via RAG (marh_feature_knowledge.md) | RF-004, RF-010 | RAG_ONLY: INT-010, INT-013, INT-019, INT-020 |
| RA-005 | Consultar dados em tempo real via ma-hr-orch | RF-003, RF-009 | API_ONLY: INT-001–005; somente GET |
| RA-006 | Retornar respostas estáticas para CLIENT_POLICY e REDIRECT | RF-005 | INT-008-009, INT-011-018, INT-021-027 |
| RA-007 | Tratar erros com mensagens ERR-001 a ERR-010 do Discovery | ERR-001 a ERR-010 | Sem textos alternativos |
| RA-008 | Sanitizar PII em 4 camadas antes de qualquer uso | SEG-003, TEC-017, TEC-019 | CPF como parâmetro técnico transitório |
| RA-009 | Impedir troca de empresa pelo chat | SEG-002, RN-012 | Empresa vem do contexto confiável |
| RA-010 | Delegar autorização à ma-hr-orch (sem RBAC próprio) | RN-004, SEG-001 | Sem papéis admin/rh/colaborador no agente |
| RA-011 | Usar allowlist de campos reais por endpoint | TEC-017, TEC-019 | Campos derivados do inventário real das APIs |
| RA-012 | Sem LLM nos fluxos API_ONLY, CLIENT_POLICY e REDIRECT | RNA-012 | Template determinístico |

## Requisitos Não Funcionais

| ID | Requisito | Tipo | Meta |
|---|---|---|---|
| RNA-001 | Região exclusiva sa-east-1 | Compliance | Obrigatório |
| RNA-002 | Sem cross-Region inference | Compliance | Obrigatório |
| RNA-003 | Latência total API_ONLY (sem LLM) | Performance | < 11s (ASSUMPTION_REQUIRES_LOAD_TEST) |
| RNA-004 | Latência total RAG_ONLY | Performance | ASSUMPTION_REQUIRES_LOAD_TEST |
| RNA-005 | Latência STATIC/CLIENT_POLICY | Performance | < 100ms |
| RNA-006 | Custo fixo mensal (sem Bedrock) | Custo | < $10/mês |
| RNA-007 | Zero PII no contexto do modelo | Segurança | Obrigatório |
| RNA-008 | Criptografia at-rest com KMS | Segurança | Obrigatório |
| RNA-009 | Criptografia in-transit TLS 1.2+ | Segurança | Obrigatório |
| RNA-010 | Logs sem PII | Segurança | Obrigatório |
| RNA-011 | Stateless (sem memória de longo prazo no POC) | Simplicidade | POC |
| RNA-012 | LLM somente em RAG_ONLY | Custo/Latência | Obrigatório na POC |
| RNA-013 | Modelo ACTIVE In-Region sa-east-1 | Compliance | Obrigatório — REQUIRES_ACCOUNT_VALIDATION |
| RNA-014 | Sem shared secret | Segurança | Obrigatório |

## Restrições Obrigatórias

1. **Região:** Todos os recursos em `sa-east-1`
2. **Modelo:** Somente modelos com inferência In-Region ACTIVE em sa-east-1 (sem inference profile cross-region)
3. **Dados:** Nenhum dado processado fora de sa-east-1
4. **Operações:** Somente GET consultivo — sem POST/PUT/DELETE
5. **Orquestração:** Chamadas corporativas apenas via ma-hr-orch
6. **Agente:** Single-agent — sem arquitetura multiagente
7. **Sessão:** Stateless na POC
8. **Cache:** Sem cache de dados corporativos na POC
9. **LLM:** Somente em RAG_ONLY — não chamar LLM para API_ONLY
10. **Autorização:** Delegada à ma-hr-orch — sem RBAC inventado no agente
11. **Sanitização:** 4 camadas (schema + allowlist + complementar + validação final)
12. **Autenticação entrada:** IAM (InvokeFunction ou Function URL AWS_IAM) — sem shared secret

## Mapeamento: Requisitos → Componentes

| Componente | Requisitos atendidos |
|---|---|
| Lambda (runtime) | RA-001, RA-002, RA-003, RA-005, RA-006, RA-007, RA-008, RA-009, RA-010, RA-011, RA-012 |
| Bedrock (LLM) | RA-004, RNA-012 |
| Embedding + S3 Vectors | RA-004 |
| S3 (documentos) | RA-004, RNA-008 |
| Secrets Manager | RNA-008, RNA-009, RNA-014 |
| KMS | RNA-008 |
| CloudWatch | RNA-010 |

---

*Fonte: `discover3/01_requisitos_cliente.md`, `discover3/12_criterios_aceite.md` · Revisão corretiva: 2026-07-23*
