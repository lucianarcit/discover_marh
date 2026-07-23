"""Catálogo de erros do Discovery — mensagens exatas."""

from __future__ import annotations

ERROR_CATALOG: dict[str, str] = {
    "ERR-001": (
        "Não consegui identificar a empresa selecionada para realizar a consulta. "
        "Selecione uma empresa no Espaço RH e tente novamente."
    ),
    "ERR-002": (
        "Não encontrei nenhum colaborador com os dados informados "
        "para a empresa selecionada."
    ),
    "ERR-003": (
        "Não encontrei o pedido informado para a empresa selecionada."
    ),
    "ERR-004": (
        "Não reconheci o status informado. Tente consultar por status "
        "como pago, pendente, cancelado ou em processamento."
    ),
    "ERR-005": (
        "Você não tem permissão para consultar informações dessa "
        "empresa no Espaço RH."
    ),
    "ERR-006": (
        "Não consegui acessar essas informações porque a validação de "
        "segurança não foi concluída. Verifique se sua sessão está "
        "ativa e tente novamente."
    ),
    "ERR-007": (
        "Não consegui consultar essa informação agora. "
        "Tente novamente em alguns instantes."
    ),
    "ERR-008": (
        "Ainda não tenho essa informação disponível sobre o MARH. "
        "Posso ajudar com consultas de colaboradores, pedidos e "
        "rastreamento de cartões."
    ),
    "ERR-009": (
        "Encontrei a informação solicitada, mas não consegui gerar "
        "o atalho de navegação para essa tela."
    ),
    "ERR-010": (
        "Ainda não consigo rastrear o cartão diretamente apenas pelo "
        "CPF do colaborador. Informe o número do pedido para eu "
        "consultar as informações disponíveis de rastreamento."
    ),
}
