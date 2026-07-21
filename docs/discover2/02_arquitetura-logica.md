# Arquitetura Lógica — Agente Consultivo MARH

Diagrama: `docs/desenhos/arquitetura_bot_alelo_v4_cliente.drawio.xml`

---

## Fluxo Principal

```
API MARH (cliente server-to-server)
    → API REST do Agente (endpoint protegido)
        → Validação de Entrada (schema, escopo, prompt injection)
        → Agente IA (LLM com Intent Router)
            ├── CONSULTIVA → tool: consultar ma-hr-orch
            ├── INFORMATIVA_MARH → tool: consultar Markdown
            └── FORA_DO_ESCOPO → resposta orientativa
        → Output Validator (schema, allowlist, tokens, tamanho, navegação)
        → Resposta estruturada
    → API MARH
        → App Meu Alelo
```

---

## Limites de Responsabilidade

| Camada | Responsável por | NÃO responsável por |
|---|---|---|
| **App Meu Alelo** | Enviar mensagem + empresa selecionada | Auth do agente; classificação |
| **API MARH** | Intermediar; enviar contexto confiável; autenticar-se no agente | Gerar resposta; classificar intenção |
| **API REST do Agente** | Autenticação server-to-server; throttling; payload limits | Auth do usuário final; permissão |
| **Validação de Entrada** | Schema; tamanho; prompt injection; escopo | Token do usuário; FNP |
| **Agente IA** | Classificar intenção; gerar resposta; chamar tools | Validar token; permissão; empresa; FNP |
| **Tool ma-hr-orch** | Repassar operation + params + empresa | Autorização (é da ma-hr-orch) |
| **ma-hr-orch (externa)** | Token; permissão; empresa; FNP; orquestração; sanitização; erros | Gerar resposta em linguagem natural |
| **Markdown** | Conteúdo oficial da feature | Dados transacionais |
| **Output Validator** | Schema final; allowlist campos; navegação; tamanho | Autorização de dados |

---

## Contexto Confiável vs. Mensagem Não Confiável

### A. Contexto confiável (enviado pela API MARH)

- `selected_company_id` — obrigatório
- `contract_id` — quando necessário
- `interlocutor_id` — quando necessário
- `session_id` — obrigatório
- `correlation_id` — obrigatório

**Estes valores NÃO podem ser substituídos pela mensagem do usuário.**

### B. Entrada não confiável

- `message` — texto livre do usuário

O agente pode extrair da mensagem: nome, CPF, nº pedido, status.
O agente NUNCA pode usar a mensagem para alterar o contexto confiável.

---

## Autenticação — Dois Níveis Separados

### Nível 1: Usuário (responsabilidade da API MARH + ma-hr-orch)

Token, interlocutor, permissão, empresa, FNP, prova de vida.
**O agente NÃO implementa este nível.**

### Nível 2: Serviço (API MARH → Agente)

A API REST do agente deve validar que o chamador é a API MARH autorizada.

**Decisão pendente** — mecanismo:
- IAM / SigV4
- JWT de serviço
- mTLS
- Lambda Authorizer corporativo
- API privada via VPC endpoint
- Outro mecanismo aprovado

---

## Componentes por Status

| Componente | Status | Justificativa |
|---|---|---|
| API Gateway | **Candidato** | Exposição REST, auth entre serviços, throttling, payload |
| Lambda (runtime do agente) | **Obrigatório** | Computação serverless |
| AgentCore Runtime | **Candidato** | Tool calling nativo. Alternativa: strands-agents em Lambda |
| AgentCore Memory | **Opcional** | Depende de quem mantém histórico, TTL, LGPD |
| AgentCore Observability | **Candidato** | Traces e custo. Alternativa: CloudWatch puro |
| Knowledge Base + S3 Vectors | **Opcional** | Para 1 Markdown pode ser overkill. Avaliar volume futuro |
| Markdown no runtime | **Candidato alternativo** | Simples para 1 arquivo, sem custo de KB |
| CloudWatch | **Obrigatório** | Logs, métricas, alarmes |
| Bedrock Guardrails | **Opcional** | Pode ser validação determinística no código |

### Componentes removidos do escopo do agente

| Componente | Motivo |
|---|---|
| Token Provider (OAuth) | Responsabilidade da ma-hr-orch |
| Secrets Manager (creds HRM) | Agente não acessa HRM |
| HRM API Adapter | Agente consulta ma-hr-orch, não HRM |
| Policy/Cedar (auth usuário) | Responsabilidade da ma-hr-orch |
| NAT Gateway (egress para HRM) | Agente não acessa HRM diretamente |
| Multi-agent / sub-agents | 3 intenções não justificam |
| Tool Response Validator (pós-HRM) | Não há acesso à HRM |

---

## Rede e Egress

**Decisão pendente:** Como o agente acessa a ma-hr-orch?

Opções:
- ma-hr-orch acessível via internet (NAT Gateway necessário)
- ma-hr-orch na mesma VPC (PrivateLink ou invocação direta)
- ma-hr-orch como Lambda invocada diretamente
- Outro mecanismo

Depende da topologia definida pelo time Alelo.
