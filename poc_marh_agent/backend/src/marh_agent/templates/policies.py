"""Templates para respostas estáticas e políticas."""

from __future__ import annotations


# Resposta para ações transacionais (Grupo C)
REDIRECT_TO_OFFICIAL_JOURNEY: str = (
    "No momento eu consigo apenas consultar informações. "
    "Para realizar essa ação, acesse a jornada correspondente no Espaço RH."
)

# Resposta para troca de empresa
COMPANY_SWITCH_BLOCKED: str = (
    "A consulta considera apenas a empresa selecionada no app. "
    "Para consultar outra empresa, selecione-a no Espaço RH."
)

# Resposta informativa básica para "O que posso fazer?" (INT-008)
WHAT_CAN_I_DO: str = (
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
)

# Resposta para INT-007 (rastreamento sem backend validado)
TRACKING_NOT_VALIDATED: str = (
    "A funcionalidade de rastreamento de cartão por número de pedido "
    "está sendo validada. Você pode acompanhar o rastreamento "
    "diretamente pela tela de rastreamento no Espaço RH."
)

# Respostas informativas por intent_id
INFORMATIVE_RESPONSES: dict[str, str] = {
    "INT-008": WHAT_CAN_I_DO,
    "INT-009": (
        "Posso consultar informações de colaboradores (por nome ou CPF), "
        "pedidos (por número, último pedido ou por status) e informações "
        "sobre rastreamento de cartões."
    ),
    "INT-010": (
        "Para fazer um pedido, acesse a jornada de Novo Pedido no Espaço RH. "
        "Eu posso ajudar a consultar pedidos existentes, mas não consigo "
        "criar novos pedidos."
    ),
    "INT-011": (
        "Para consultar um pedido, me informe o número do pedido. "
        "Por exemplo: 'Consultar pedido 342671'."
    ),
    "INT-012": (
        "Para consultar um colaborador, me informe o nome ou CPF. "
        "Por exemplo: 'Consultar colaborador Ana' ou "
        "'Consultar CPF 000.000.000-00'."
    ),
    "INT-013": (
        "O rastreamento de cartões está disponível pela tela de "
        "rastreamento no Espaço RH. Para consultar, informe o número "
        "do pedido. No momento, não consigo rastrear apenas pelo CPF "
        "do colaborador."
    ),
    "INT-014": (
        "Não, eu não consigo cancelar pedidos. Minha função é apenas "
        "consultiva. Para cancelar um pedido, acesse a jornada "
        "correspondente no Espaço RH."
    ),
    "INT-015": (
        "Não, eu não consigo alterar dados de colaboradores. Minha "
        "função é apenas consultiva. Para editar um colaborador, "
        "acesse a jornada correspondente no Espaço RH."
    ),
    "INT-016": (
        "Não, eu consulto apenas os dados da empresa selecionada no "
        "app. Para consultar outra empresa, selecione-a no Espaço RH."
    ),
    "INT-017": (
        "Sim, é necessário ter uma empresa selecionada no app para que "
        "eu possa realizar consultas. Todas as minhas respostas são "
        "baseadas na empresa selecionada."
    ),
    "INT-018": (
        "Não, eu não substituo o portal web. Sou um assistente "
        "consultivo que ajuda com consultas rápidas. Para realizar "
        "ações como criar pedidos ou editar colaboradores, continue "
        "usando o Espaço RH."
    ),
    "INT-019": (
        "O MARH (Meu Alelo RH) é a funcionalidade do app Meu Alelo "
        "que permite aos interlocutores de RH gerenciar colaboradores, "
        "pedidos e benefícios pelo celular, dentro do Espaço RH."
    ),
    "INT-020": (
        "O Espaço RH é a área dentro do app Meu Alelo dedicada aos "
        "interlocutores de RH, onde é possível gerenciar colaboradores, "
        "realizar pedidos, acompanhar rastreamentos e outras operações "
        "administrativas."
    ),
    "INT-021": (
        "Você pode me perguntar sobre:\n"
        "• Colaboradores (consulta por nome ou CPF)\n"
        "• Pedidos (por número, último pedido ou por status)\n"
        "• Rastreamento de cartões\n"
        "• Dúvidas sobre o MARH e o Espaço RH\n\n"
        "Também posso orientar sobre como realizar ações no Espaço RH."
    ),
}
