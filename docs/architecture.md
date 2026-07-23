# Arquitetura — MARH Agent

## Visão Geral

O MARH Agent é um assistente consultivo de IA para interlocutores de RH dentro do app Meu Alelo. Ele responde perguntas sobre colaboradores, pedidos e benefícios sem substituir o portal web.

## Diagrama

```
┌─────────────────────────────────────────────────────────────────┐
│                        App Meu Alelo                            │
│                    (Espaço RH → Chat)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               CloudFront (HTTPS frontend)                       │
│         d1vtu9x0di76z9.cloudfront.net                           │
│                   ↕ S3 bucket                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ fetch POST /chat
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API Gateway HTTP API                           │
│              (throttling, CORS, OIDC authorizer*)                │
│              POST /chat    GET /health                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Lambda: marh-agent                            │
│                                                                 │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────────────────┐ │
│  │ Classificador│  │Orchestrator│  │      Router             │ │
│  │ (regex/LLM*) │→ │            │→ │  intent → handler       │ │
│  └──────────────┘  └────────────┘  └────────┬────────────────┘ │
│                                              │                  │
│              ┌───────────────────────────────┼──────────┐       │
│              ▼                               ▼          ▼       │
│  ┌────────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  ma-hr-orch Client │  │ Knowledge    │  │ Navigation      │ │
│  │  (HTTP/mock)       │  │ Client (RAG*)│  │ Builder         │ │
│  └─────────┬──────────┘  └──────┬───────┘  └─────────────────┘ │
│            │                     │                              │
└────────────┼─────────────────────┼──────────────────────────────┘
             │                     │
             ▼                     ▼
┌────────────────────┐  ┌──────────────────────┐
│   ma-hr-orch API   │  │  Bedrock Knowledge   │
│   (Alelo interna)  │  │  Bases (S3 + RAG)*   │
└────────────────────┘  └──────────────────────┘

* Componentes marcados com * serão integrados nas Fases 2–5.
```

## Fluxo de Dados (Request → Response)

1. Usuário envia mensagem no chat do Espaço RH
2. App Meu Alelo faz `POST /chat` com JWT no header
3. API Gateway valida CORS, aplica throttling, invoca Lambda
4. Lambda handler parseia o body, cria `ChatRequest`
5. **Orchestrator** processa:
   - Valida contexto confiável (company_id, user_id, session_id)
   - Classifica a intenção (27 intents possíveis)
   - Roteia para o handler correto
   - Aplica allowlists e sanitização
   - Constrói navigation (deeplinks)
6. Retorna `ChatResponse` com message + presentation + navigation

## Decisões de Design

| Decisão | Razão |
|---------|-------|
| **Uma única Lambda** | Simplicidade operacional; classificação + roteamento interno |
| **Regex primeiro, LLM depois** | Auditoria determinística na POC; custo zero; LLM na Fase 4 |
| **Framework-agnóstico** | O Orchestrator não depende de FastAPI nem Lambda SDK |
| **Cold-start cache** | Clientes instanciados fora do handler, reutilizados entre invocações |
| **Allowlists, não blocklists** | Só campos explicitamente autorizados passam na resposta |
| **Route catalog fechado** | Previne SSRF; novas rotas exigem aprovação explícita |
| **Sem innerHTML** | Frontend usa apenas DOM APIs; nenhum dado do backend vira HTML |

## Componentes por Fase

| Componente | Fase 1 | Fase 2 | Fase 3 | Fase 4 | Fase 5 |
|------------|--------|--------|--------|--------|--------|
| Lambda + API Gateway | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mock clients | ✅ | — | — | — | — |
| HTTP ma-hr-orch | — | ✅ | ✅ | ✅ | ✅ |
| Bedrock Knowledge Base | — | — | ✅ | ✅ | ✅ |
| Bedrock Classifier (LLM) | — | — | — | ✅ | ✅ |
| JWT Authorizer | — | — | — | — | ✅ |

## Segurança (resumo)

- Contexto confiável validado (company/user/session obrigatórios)
- Allowlists de campos por domínio
- Sanitização de CPF/CNPJ em texto
- Route catalog fechado (7 rotas)
- CORS restrito à origem do app
- Secrets Manager para credenciais (nunca em env vars)
- X-Ray tracing para observabilidade

## Observabilidade

| Ferramenta | Uso |
|------------|-----|
| CloudWatch Logs | Logs estruturados JSON (sem dados sensíveis) |
| X-Ray | Tracing distribuído (Lambda → API calls) |
| CloudWatch Alarms | Error rate > 5%, latência p99 > 10s |
