"""MockKnowledgeClient — substituto do RAG para a POC.

Todas as respostas são derivadas de:
  discover3/knowledge/marh_feature_knowledge.md

Regras:
- Conteúdo aprovado apenas — sem invenção.
- Sem LLM, sem embeddings, sem busca vetorial.
- Cada tópico tem source_section rastreável ao markdown.
- data_classification = APPROVED_KNOWLEDGE_MOCK em todos os registros.
- Políticas do agente NÃO ficam aqui — ficam em templates/policies.py.
"""

from __future__ import annotations

from marh_agent.clients.knowledge_client import KnowledgeClient

_NOT_FOUND = {
    "content": None,
    "source_section": None,
    "data_classification": "APPROVED_KNOWLEDGE_MOCK",
    "found": False,
}


class MockKnowledgeClient(KnowledgeClient):
    """Implementação mock do cliente de conhecimento."""

    # Mapeamento de tópico → conteúdo aprovado + seção de origem
    _KNOWLEDGE: dict[str, dict] = {
        # INT-019 — O que é o MARH?
        "MARH_OVERVIEW": {
            "content": (
                "O MARH (Meu Alelo RH) é a funcionalidade do app Meu Alelo "
                "que permite aos interlocutores de RH gerenciar colaboradores, "
                "pedidos e benefícios pelo celular, dentro do Espaço RH."
            ),
            "source_section": "marh_feature_knowledge.md — contexto geral",
        },
        # INT-020 — O que é o Espaço RH?
        "ESPACO_RH_OVERVIEW": {
            "content": (
                "O Espaço RH é a área dentro do app Meu Alelo dedicada aos "
                "interlocutores de RH, onde é possível gerenciar colaboradores, "
                "realizar pedidos, acompanhar rastreamentos e outras operações "
                "administrativas de benefícios Alelo."
            ),
            "source_section": "marh_feature_knowledge.md — contexto geral",
        },
        # INT-008 — O que posso fazer?
        "AGENT_CAPABILITIES": {
            "content": (
                "Posso ajudar você com:\n"
                "• Consultar colaboradores por nome ou CPF\n"
                "• Consultar pedidos pelo número\n"
                "• Verificar o último pedido\n"
                "• Listar pedidos por status\n"
                "• Informações sobre rastreamento de cartões\n"
                "• Dúvidas sobre o Espaço RH e o MARH\n\n"
                "No momento, consigo apenas consultar informações. "
                "Para realizar ações como criar ou cancelar pedidos, "
                "acesse a jornada correspondente no Espaço RH."
            ),
            "source_section": "agent_policy.md — capacidades do agente",
        },
        # INT-009 — Quais informações posso consultar?
        "CONSULTABLE_INFO": {
            "content": (
                "Posso consultar informações de colaboradores (por nome ou CPF), "
                "pedidos (por número, último pedido ou por status) e informações "
                "sobre rastreamento de cartões."
            ),
            "source_section": "agent_policy.md — escopo de consulta",
        },
        # INT-010 — Como fazer um pedido?
        "ORDER_PROCESS": {
            "content": (
                "Um pedido pode ser criado de duas formas:\n"
                "• Via tela: seleção manual de colaboradores e valores.\n"
                "• Via planilha: importação de arquivo .xls/.xlsx.\n\n"
                "Ambas seguem o mesmo fluxo de 5 etapas:\n"
                "1. Forma do pedido\n"
                "2. Colaboradores e benefícios\n"
                "3. Forma de pagamento e crédito\n"
                "4. Resumo\n"
                "5. Pagamento\n\n"
                "A única forma de pagamento disponível é o boleto bancário. "
                "Para criar um pedido, acesse a jornada de Novo Pedido no Espaço RH."
            ),
            "source_section": "marh_feature_knowledge.md — seção 4 (Pedidos)",
        },
        # INT-011 — Como consultar um pedido?
        "HOW_CONSULT_ORDER": {
            "content": (
                "Para consultar um pedido, me informe o número do pedido. "
                "Exemplo: 'Consultar pedido 342671'. "
                "Você também pode perguntar qual foi o último pedido ou "
                "listar pedidos por status (pago, pendente, cancelado etc.)."
            ),
            "source_section": "agent_policy.md — INT-003 comportamento esperado",
        },
        # INT-012 — Como consultar um colaborador?
        "HOW_CONSULT_COLLABORATOR": {
            "content": (
                "Para consultar um colaborador, me informe o nome ou CPF. "
                "Exemplos:\n"
                "• 'Consultar colaborador Ana Silva'\n"
                "• 'Consultar colaborador CPF 000.000.000-00'"
            ),
            "source_section": "agent_policy.md — INT-001/INT-002 comportamento esperado",
        },
        # INT-013 — Rastreamento de cartões (informativo)
        "CARD_TRACKING_INFO": {
            "content": (
                "O rastreamento de cartões está disponível pela tela de "
                "rastreamento no Espaço RH. Para consultar, informe o número "
                "do pedido. No momento, não consigo rastrear apenas pelo CPF "
                "do colaborador — o endpoint de rastreamento por CPF está "
                "sendo validado.\n\n"
                "O rastreio fica disponível após os cartões serem encaminhados "
                "para a transportadora."
            ),
            "source_section": "marh_feature_knowledge.md — seção 9 (Rastreamento)",
        },
        # INT-014 — Pode cancelar pedido?
        "CANNOT_CANCEL": {
            "content": (
                "Não, eu não consigo cancelar pedidos. Minha função é apenas "
                "consultiva. Para cancelar um pedido, acesse a jornada "
                "correspondente no Espaço RH."
            ),
            "source_section": "agent_policy.md — FORA-002",
        },
        # INT-015 — Pode alterar colaborador?
        "CANNOT_EDIT_COLLABORATOR": {
            "content": (
                "Não, eu não consigo alterar dados de colaboradores. Minha "
                "função é apenas consultiva. Para editar um colaborador, "
                "acesse a jornada correspondente no Espaço RH."
            ),
            "source_section": "agent_policy.md — FORA-004",
        },
        # INT-016 — Consulta qualquer empresa?
        "COMPANY_SCOPE": {
            "content": (
                "Não, eu consulto apenas os dados da empresa selecionada no "
                "app. Para consultar outra empresa, selecione-a no Espaço RH."
            ),
            "source_section": "agent_policy.md — seção 3 (empresa selecionada)",
        },
        # INT-017 — Precisa selecionar empresa?
        "COMPANY_REQUIRED": {
            "content": (
                "Sim, é necessário ter uma empresa selecionada no app para que "
                "eu possa realizar consultas. Todas as minhas respostas são "
                "baseadas na empresa selecionada."
            ),
            "source_section": "agent_policy.md — seção 3 (empresa selecionada)",
        },
        # INT-018 — Substitui o portal?
        "AGENT_VS_PORTAL": {
            "content": (
                "Não, eu não substituo o portal web. Sou um assistente "
                "consultivo que ajuda com consultas rápidas. Para realizar "
                "ações como criar pedidos ou editar colaboradores, continue "
                "usando o Espaço RH."
            ),
            "source_section": "agent_policy.md — RN-001",
        },
        # INT-021 — Quais perguntas posso fazer?
        "QUESTION_TYPES": {
            "content": (
                "Você pode me perguntar sobre:\n"
                "• Colaboradores (consulta por nome ou CPF)\n"
                "• Pedidos (por número, último pedido ou por status)\n"
                "• Rastreamento de cartões\n"
                "• Dúvidas sobre o MARH e o Espaço RH\n\n"
                "Também posso orientar sobre como realizar ações no Espaço RH."
            ),
            "source_section": "agent_policy.md — seção 2 (capacidades)",
        },
        # EV-028 — O que significa um status de pedido?
        "ORDER_STATUS_INFO": {
            "content": (
                "Os status de pedidos no sistema Alelo indicam a etapa atual "
                "do processo:\n"
                "• Aguardando pagamento: boleto gerado, aguardando pagamento\n"
                "• Pagamento confirmado: pagamento registrado, NF em processo\n"
                "• Nota Fiscal Emitida: NF emitida, créditos sendo disponibilizados\n"
                "• Pedido creditado: créditos disponíveis nos cartões\n"
                "• Cancelado: pedido cancelado pelo cliente ou por falta de pagamento\n\n"
                "Para verificar o status atual de um pedido específico, "
                "me informe o número do pedido."
            ),
            "source_section": "marh_feature_knowledge.md — seção 5 (Status dos pedidos)",
        },
    }

    def query(self, topic: str) -> dict:
        """Consulta conhecimento aprovado por tópico."""
        entry = self._KNOWLEDGE.get(topic)
        if not entry:
            return _NOT_FOUND
        return {
            "content": entry["content"],
            "source_section": entry["source_section"],
            "data_classification": "APPROVED_KNOWLEDGE_MOCK",
            "found": True,
        }

    def get_all_topics(self) -> list[str]:
        """Retorna todos os tópicos disponíveis."""
        return list(self._KNOWLEDGE.keys())
