/**
 * mock-agent.js — MockAgent local para POC MARH
 *
 * Substitui chamadas reais ao backend durante desenvolvimento.
 * Todos os dados são SINTÉTICOS — sem informação real de pedidos ou colaboradores.
 * Classificação: SYNTHETIC_TEST_DATA
 */

const MockAgent = (() => {
  /**
   * Delay simulado para dar sensação realista de resposta.
   * Entre 600ms e 1400ms.
   */
  function _delay() {
    const ms = 600 + Math.floor(Math.random() * 800);
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /** Gera um correlation_id pseudoaleatório sem usar Math.random no nível global */
  function _correlationId(prefix) {
    const ts = Date.now().toString(36);
    const rnd = Math.floor(Math.random() * 0xffff).toString(16).padStart(4, "0");
    return `${prefix}-${ts}-${rnd}`;
  }

  /** Escapa texto para exibição segura (textContent já faz isso, mas usamos aqui como documentação) */
  function _safe(text) {
    return String(text);
  }

  /* ────────────────────────────────────────────────────
     Padrões de reconhecimento de intenção
     ──────────────────────────────────────────────────── */
  const PATTERNS = [
    {
      id: "INT-003",
      regex: /consultar\s+pedido\s+(\d{4,10})/i,
      handler: _handleOrderDetail,
    },
    {
      id: "INT-002",
      regex: /último\s+pedido|ultimo\s+pedido|pedido\s+mais\s+recente/i,
      handler: _handleLastOrder,
    },
    {
      id: "INT-004",
      regex: /pedidos?\s+(com\s+)?status\s+pago|pedidos?\s+pagos/i,
      handler: _handleOrdersByStatus,
    },
    {
      id: "INT-005",
      regex: /consultar\s+colaborador|buscar\s+colaborador|listar\s+colaboradores/i,
      handler: _handleCollaborator,
    },
    {
      id: "INT-BLOCKED",
      regex: /cancel[ea]\s+(o\s+)?pedido|cancelar\s+pedido/i,
      handler: _handleBlockedAction,
    },
    {
      id: "INT-001",
      regex: /o\s+que\s+(posso|eu\s+posso)\s+fazer|quais?\s+(são\s+)?as?\s+fun[çc][oõ]es|me\s+ajude|como\s+funciona/i,
      handler: _handleCapabilities,
    },
    {
      id: "INT-EMPRESA",
      regex: /empresa[\s-]sintetica|company_id|alterar\s+(a\s+)?empresa|mudar\s+(a\s+)?empresa/i,
      handler: _handleBlockedCompanyChange,
    },
  ];

  /* ────────────────────────────────────────────────────
     Handlers de intenção
     ──────────────────────────────────────────────────── */

  function _handleOrderDetail(match) {
    const orderNumber = _safe(match[1]);
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-003",
      flow: "API_ONLY",
      message:
        `Encontrei o pedido ${orderNumber}.\n\n` +
        `**Status:** Pago\n` +
        `**Data do pedido:** 21/07/2026\n` +
        `**Produto:** Produto Exemplo (Sintético)\n` +
        `**Valor:** R$ 90,00\n\n` +
        `_Estes dados são sintéticos para fins de POC._`,
      navigation: {
        type: "list_navigation",
        route_id: "ROUTE-ORDER-DETAIL",
        label: "Ver detalhes do pedido",
        route_suffix: orderNumber,
        webview_url: `${CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT]}#/order-detail/${orderNumber}`,
        deeplink: `meualelo://app/webview?url=${encodeURIComponent(
          CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT] +
            "#/order-detail/" +
            orderNumber
        )}&isModal=false&showNavbar=false&authRequired=true`,
      },
    };
  }

  function _handleLastOrder() {
    const orderNumber = "342671";
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-002",
      flow: "API_ONLY",
      message:
        `Seu último pedido registrado é o **${orderNumber}**.\n\n` +
        `**Status:** Pago\n` +
        `**Data:** 21/07/2026\n` +
        `**Produto:** Produto Exemplo (Sintético)\n` +
        `**Valor:** R$ 90,00\n\n` +
        `_Estes dados são sintéticos para fins de POC._`,
      navigation: {
        type: "list_navigation",
        route_id: "ROUTE-ORDER-DETAIL",
        label: "Ver detalhes do último pedido",
        route_suffix: orderNumber,
        webview_url: `${CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT]}#/order-detail/${orderNumber}`,
        deeplink: `meualelo://app/webview?url=${encodeURIComponent(
          CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT] +
            "#/order-detail/" +
            orderNumber
        )}&isModal=false&showNavbar=false&authRequired=true`,
      },
    };
  }

  function _handleOrdersByStatus() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-004",
      flow: "API_ONLY",
      message:
        `Encontrei **3 pedidos** com status **Pago** nos últimos 30 dias:\n\n` +
        `• Pedido **342671** — R$ 90,00 — 21/07/2026\n` +
        `• Pedido **342580** — R$ 150,00 — 15/07/2026\n` +
        `• Pedido **342401** — R$ 60,00 — 08/07/2026\n\n` +
        `_Estes dados são sintéticos para fins de POC._`,
      navigation: {
        type: "list_navigation",
        route_id: "ROUTE-ORDER-LIST",
        label: "Ver lista de pedidos pagos",
        route_suffix: null,
        webview_url: `${CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT]}#/order-list`,
        deeplink: `meualelo://app/webview?url=${encodeURIComponent(
          CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT] + "#/order-list"
        )}&isModal=false&showNavbar=false&authRequired=true`,
      },
    };
  }

  function _handleCollaborator() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-005",
      flow: "API_ONLY",
      message:
        `Para consultar um colaborador, informe o **nome**, **CPF** ou **matrícula**.\n\n` +
        `Exemplo: _"Consultar colaborador João Silva"_\n\n` +
        `Posso buscar informações cadastrais e status de cartões associados.\n\n` +
        `_Esta é uma POC — nenhum dado real é consultado._`,
      navigation: {
        type: "list_navigation",
        route_id: "ROUTE-COLLABORATOR-LIST",
        label: "Ver lista de colaboradores",
        route_suffix: null,
        webview_url: `${CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT]}#/collaborator-list`,
        deeplink: `meualelo://app/webview?url=${encodeURIComponent(
          CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT] + "#/collaborator-list"
        )}&isModal=false&showNavbar=false&authRequired=true`,
      },
    };
  }

  function _handleBlockedAction() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-BLOCKED",
      flow: "BLOCKED",
      message:
        `Não consigo realizar o cancelamento de pedidos diretamente por aqui.\n\n` +
        `Para cancelar um pedido, acesse o Espaço RH e utilize a opção **"Meus Pedidos"**, ` +
        `ou entre em contato com o suporte Alelo.\n\n` +
        `Posso te ajudar com **consultas** de pedidos ou colaboradores.`,
      navigation: null,
    };
  }

  function _handleCapabilities() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-001",
      flow: "API_ONLY",
      message:
        `Sou o **ChatAlelo**, assistente de RH com IA. Posso te ajudar com:\n\n` +
        `• **Consultar pedido** — busque pelo número do pedido\n` +
        `• **Último pedido** — veja o pedido mais recente\n` +
        `• **Pedidos por status** — filtre por Pago, Pendente, etc.\n` +
        `• **Consultar colaborador** — busque por nome, CPF ou matrícula\n` +
        `• **Rastreamento de cartões** — status de entrega\n` +
        `• **Processo de pedido** — tire dúvidas sobre como fazer um pedido\n\n` +
        `O que você gostaria de saber?`,
      navigation: null,
    };
  }

  function _handleBlockedCompanyChange() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-BLOCKED",
      flow: "BLOCKED",
      message:
        `Não é possível alterar a empresa através da conversa. ` +
        `O contexto da empresa é definido pela sua sessão autenticada.`,
      navigation: null,
    };
  }

  function _handleUnknown() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-000",
      flow: "API_ONLY",
      message:
        `Não entendi exatamente o que você precisa. Posso te ajudar com:\n\n` +
        `• Consultar pedido (ex: _"Consultar pedido 342671"_)\n` +
        `• Ver último pedido\n` +
        `• Pedidos por status\n` +
        `• Consultar colaborador\n\n` +
        `Tente reformular sua pergunta ou escolha uma das sugestões acima.`,
      navigation: null,
    };
  }

  /* ────────────────────────────────────────────────────
     Ponto de entrada público
     ──────────────────────────────────────────────────── */

  /**
   * Processa uma mensagem e retorna uma resposta simulada.
   * @param {object} payload - Contrato de request
   * @returns {Promise<object>} - Contrato de response
   */
  async function sendMessage(payload) {
    const message = String(payload.message || "").trim();

    await _delay();

    for (const pattern of PATTERNS) {
      const match = message.match(pattern.regex);
      if (match) {
        return pattern.handler(match);
      }
    }

    return _handleUnknown();
  }

  return { sendMessage };
})();
