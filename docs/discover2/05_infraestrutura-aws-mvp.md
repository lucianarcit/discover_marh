# Infraestrutura AWS — MVP Agente Consultivo MARH

**Região obrigatória:** sa-east-1 (São Paulo)
**Cross-region inference:** desativado

---

## Componentes Avaliados

| Componente | Classificação | Justificativa |
|---|---|---|
| **API Gateway** | Candidato | Exposição REST; auth server-to-server; throttling; payload limits; métricas. Não usar CORS como justificativa (cliente é API MARH, não browser) |
| **Lambda (Chat Handler)** | Obrigatório | Computação serverless; recebe request; invoca agente; retorna resposta |
| **AgentCore Runtime** | Candidato | Tool calling nativo; orquestração. Alternativa: strands-agents em Lambda pura |
| **Modelo Bedrock in-region** | Obrigatório | LLM para classificação e geração. Modelo específico: decisão pendente |
| **AgentCore Memory** | Opcional | Depende de: quem mantém histórico; se API MARH envia contexto suficiente; TTL; LGPD |
| **AgentCore Observability** | Candidato | Traces, custo/sessão. Alternativa: CloudWatch puro |
| **CloudWatch** | Obrigatório | Logs, métricas, alarmes — baseline |
| **Bedrock Knowledge Base + S3 Vectors** | Opcional | Para 1 Markdown pode ser desnecessário. Avaliar volume futuro |
| **Markdown no runtime** | Candidato alternativo | Carregado na Lambda; simples; zero custo KB; menos flexível |
| **S3 (armazenamento)** | Candidato | Se usar KB ou recuperação simples do Markdown |
| **Bedrock Guardrails** | Opcional | Alternativa: validação determinística no Handler |
| **Secrets Manager** | Decisão pendente | Depende do mecanismo de auth server-to-server |
| **NAT Gateway / egress** | Decisão pendente | Depende de onde está a ma-hr-orch |

### Componentes removidos

| Componente | Motivo |
|---|---|
| Token Provider (OAuth HRM) | Responsabilidade da ma-hr-orch |
| Secrets Manager (creds HRM) | Agente não acessa HRM |
| HRM API Adapter | Agente consulta ma-hr-orch |
| Policy/Cedar (auth usuário) | Responsabilidade da ma-hr-orch |
| Multi-agent / sub-agents | 3 intenções não justificam |
| OpenSearch Serverless | Substituído; KB pode usar S3 Vectors se necessário |
| ElastiCache Redis | Memory é do AgentCore ou desnecessário |

---

## Comparação: Knowledge Source

| Opção | Volume | Atualização | Custo | Complexidade | Recomendação |
|---|---|---|---|---|---|
| A. Markdown no runtime (Lambda) | 1 arquivo | Redeploy | Zero | Mínima | **MVP se conteúdo estável** |
| B. S3 + recuperação simples | 1-5 arquivos | Upload S3 | ~$0 | Baixa | Se precisar atualizar sem redeploy |
| C. Bedrock KB + S3 Vectors | N arquivos, busca semântica | Ingestão | ~$5-10/mês | Média | Se conteúdo crescer significativamente |

---

## Comparação: Runtime do Agente

| Opção | Tool calling | Observabilidade | Custo | Complexidade |
|---|---|---|---|---|
| A. AgentCore Runtime | Nativo | AgentCore Observability | Por invocação + tokens | Média |
| B. strands-agents em Lambda | Via SDK | CloudWatch manual | Lambda + Bedrock | Baixa |
| C. LangChain/LangGraph em Lambda | Via framework | CloudWatch manual | Lambda + Bedrock | Média-alta |

**Decisão pendente.** Ambos são viáveis para 3 intenções e 2 tools.

---

## Autenticação Server-to-Server

O endpoint do agente deve autenticar a API MARH como cliente autorizado.

**Decisão pendente** — mecanismo:

| Opção | Prós | Contras |
|---|---|---|
| IAM / SigV4 | Nativo AWS; sem segredo extra | Acoplamento AWS |
| JWT de serviço | Padrão; rotação independente | Precisa de emissor/verificador |
| mTLS | Forte; não depende de token | Complexidade de certificados |
| Lambda Authorizer corporativo | Reutiliza infra existente | Dependência de equipe |
| API privada (VPC endpoint) | Sem exposição pública | Requer VPC compartilhada |

---

## Rede

**Decisão pendente:** Como o agente acessa a ma-hr-orch?

| Cenário | Componente necessário |
|---|---|
| ma-hr-orch acessível via internet | NAT Gateway (~$32/mês + dados) |
| ma-hr-orch na mesma VPC | Security group + rota interna |
| ma-hr-orch via PrivateLink | VPC endpoint |
| ma-hr-orch como Lambda (invoke direto) | IAM permission |

---

## Residência Regional (sa-east-1)

Todos os componentes candidatos devem estar disponíveis em sa-east-1. Validações anteriores confirmaram:

- AgentCore Runtime: ✅
- AgentCore Memory: ✅ (Mar 2026)
- AgentCore Observability: ✅
- Bedrock Knowledge Bases: ✅
- S3 Vectors: ✅ (Mar 2026)
- Lambda, API Gateway, CloudWatch, S3, Secrets Manager: ✅

Modelo LLM específico: **decisão pendente** (confirmar versão in-region).
