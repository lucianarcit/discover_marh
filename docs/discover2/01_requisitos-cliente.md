# Requisitos — Agente Consultivo MARH

Consolidação da especificação do cliente (`docs/cliente/00_Agente_Consultivo_MARH.html`).

---

## 1. Objetivo (Spec §1)

Permitir que o interlocutor de RH consulte informações da empresa selecionada no Espaço RH por meio de um agente de IA conversacional.

O agente é **exclusivamente consultivo**. Não deve criar, alterar, cancelar, excluir, aprovar, reprovar ou executar qualquer ação transacional.

Consultas suportadas:
- Colaboradores
- Pedidos (por número)
- Último pedido
- Pedidos por status
- Rastreamento de cartão de colaborador
- Dúvidas sobre a feature MARH

---

> **Nota de rastreabilidade:** a Seção 2 — Referências da especificação
> autoritativa foi incorporada às seções "Atores e Sistemas" e
> "Responsabilidades", preservando integralmente seus requisitos.

## 2. Atores e Sistemas (Spec §2, §3)

| Ator / Sistema | Responsabilidade |
|---|---|
| App Meu Alelo | Envia mensagem + empresa selecionada para API MARH |
| API MARH | Intermediário; encaminha para o agente com contexto confiável |
| Agente IA MARH | Classifica intenção; consulta ma-hr-orch ou Markdown; gera resposta |
| ma-hr-orch | Valida token, permissão, empresa, FNP; orquestra integrações; retorna dados |
| Markdown de conhecimento | Fonte oficial para perguntas informativas sobre a feature |

---

## 3. Fluxo de Integração (Spec §3)

```
App Meu Alelo → API MARH → Agente IA MARH → ma-hr-orch (ou Markdown) → Agente → API MARH → App
```

O agente NÃO é acessado diretamente pelo App.

---

## 4. Responsabilidades da ma-hr-orch (Spec §4)

- Validar o token do usuário
- Validar se o usuário é interlocutor da empresa
- Validar permissão para acessar dados da empresa selecionada
- Validar FNP, prova de vida ou controles de segurança aplicáveis
- Garantir consulta no contexto da empresa selecionada
- Orquestrar chamadas para sistemas internos
- Retornar apenas informações que podem ser exibidas
- Padronizar erros

O agente **não deve implementar** validação de token, permissão, autorização ou controles dos sistemas internos.

---

## 5. Contexto Obrigatório da Empresa (Spec §5)

Parâmetros enviados pela API MARH ao agente:
- Identificador da empresa selecionada (obrigatório)
- Identificador do contrato (quando necessário)
- Identificador do usuário/interlocutor (quando necessário)
- Mensagem do usuário
- Dados mínimos para contexto correto

Regras:
- O agente não decide qual empresa consultar
- O agente usa sempre a empresa recebida
- O agente repassa o contexto para a ma-hr-orch
- O usuário não pode trocar empresa pelo chat (CNPJ, contrato ou nome)
- Empresa ausente → erro orientativo

---

## 6. Fonte de Conhecimento Markdown (Spec §6)

Arquivo Markdown oficial para perguntas informativas sobre a feature MARH.

Regras:
- Se intenção consultiva → consulta ma-hr-orch
- Se dúvida sobre a feature → consulta Markdown
- Informação não encontrada → resposta padronizada
- Não inventar capacidades fora do Markdown
- Markdown versionado com a feature
- Revisado a cada evolução do escopo

---

## 7. Classificação de Intenção (Spec §7)

| Intenção | Quando | Ação |
|---|---|---|
| **CONSULTIVA** | Consultar dados da empresa | Chama ma-hr-orch |
| **INFORMATIVA_MARH** | Pergunta sobre a feature/capacidades | Consulta Markdown |
| **FORA_DO_ESCOPO** | Ação transacional ou não suportada | Resposta orientativa |

---

## 8. Casos de Uso do MVP (Spec §8)

### 8.1 Consultar colaborador (nome ou CPF)
- Busca via ma-hr-orch na empresa selecionada
- Múltiplos resultados → pedir escolha
- Não encontrado → mensagem padronizada
- Pode retornar navegação

### 8.2 Consultar pedido por número
- Exibe: status, data, produto, valor, qtd colaboradores, cartões, etapas
- Não permite ações transacionais
- Pode retornar navegação

### 8.3 Consultar último pedido
- Retorna pedido mais recente disponível
- Pode retornar navegação

### 8.4 Consultar pedidos por status
- Filtro por status (pago, pendente, cancelado, em processamento)
- Status inválido → mensagem orientativa

### 8.5 Rastrear cartão do colaborador
- Preferencialmente por CPF (pendente confirmação técnica)
- Se indisponível por CPF → solicitar número do pedido
- Exibe: status, data atualização, endereço, código rastreio
- Não inventar prazo ou transportadora

---

## 9. Navegação (Spec §9)

Formato: `[list_navigation](meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true)`

Regras:
- Retornar apenas quando houver relação com a resposta
- Texto compreensível sem renderização do componente visual
- Frontend interpreta e decide componente visual
- URL encoded
- Não inventar identificadores
- Link não executa operação automaticamente
- Destino deve estar autorizado

**Decisão pendente:** qual camada constrói a URL final.

---

## 10. Regras de Segurança (Spec §11)

- Consultar apenas dados da empresa selecionada
- Usar ma-hr-orch como fonte consultiva
- NÃO validar token, permissão, FNP ou prova de vida
- NÃO permitir consulta de outra empresa
- NÃO expor tokens, integrações internas ou dados sensíveis
- Responder sobre a feature apenas com base no Markdown
- Navegação apenas para telas permitidas do Espaço RH
- Links não acionam operações transacionais

---

## 11. Fora de Escopo (Spec §12)

O agente NÃO deve:
- Criar, cancelar, alterar, excluir pedidos
- Editar, excluir colaboradores
- Alterar endereço de entrega
- Solicitar ou reemitir cartão
- Alterar status
- Realizar pagamento
- Consultar empresa sem permissão
- Responder sobre capacidades fora do Markdown
- Retornar links para telas fora do contexto autorizado

---

## 12. Tratamento de Erros (Spec §13)

| Cenário | Resposta |
|---|---|
| Colaborador não encontrado | "Não encontrei nenhum colaborador com os dados informados para a empresa selecionada." |
| Pedido não encontrado | "Não encontrei o pedido informado para a empresa selecionada." |
| Status não reconhecido | "Não reconheci o status informado. Tente consultar por status como pago, pendente, cancelado ou em processamento." |
| Empresa ausente | "Não consegui identificar a empresa selecionada para realizar a consulta. Selecione uma empresa no Espaço RH e tente novamente." |
| Sem permissão | "Você não tem permissão para consultar informações dessa empresa no Espaço RH." |
| Validação de segurança | "Não consegui acessar essas informações porque a validação de segurança não foi concluída. Verifique se sua sessão está ativa e tente novamente." |
| Consulta indisponível | "Não consegui consultar essa informação agora. Tente novamente em alguns instantes." |
| Info não no Markdown | "Ainda não tenho essa informação disponível sobre o MARH. Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões." |
| Navegação indisponível | "Encontrei a informação solicitada, mas não consegui gerar o atalho de navegação para essa tela." |

---

## 13. Critérios de Aceite (Spec §14)

1. Agente disponível via API REST
2. App consome via API MARH
3. API MARH envia empresa selecionada
4. Empresa usada como contexto obrigatório
5. Agente consulta via ma-hr-orch
6. ma-hr-orch valida token, permissão, empresa, segurança
7. Agente possui Markdown de conhecimento
8. Responde dúvidas com base no Markdown
9. Identifica intenção (consultiva, informativa, fora do escopo)
10. Consulta colaborador por nome ou CPF
11. Consulta pedido por número
12. Retorna último pedido
13. Lista pedidos por status
14. Trata status inválido
15. Informa quando não encontrar dados
16. Não executa ações transacionais
17. Avalia rastreio por CPF via ma-hr-orch
18. Pode retornar elemento de navegação
19. Frontend identifica e renderiza `[list_navigation]`
20. Navegação não executa ações automaticamente
