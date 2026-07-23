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
        `Encontrei o pedido ${orderNumber}.\n` +
        `Status: Pagamento confirmado\n` +
        `Data do pedido: 21/07/2026\n` +
        `Produto: Produto Exemplo (Sintético)\n` +
        `Valor: R$ 90,00`,
      presentation: {
        variant: "order_summary",
        title: "Pedido " + orderNumber,
        icon: "order",
        tone: "positive",
        status_label: "Pagamento confirmado",
        fields: [
          { label: "Produto", value: "Produto Exemplo (Sintético)", emphasis: true },
          { label: "Data", value: "21/07/2026" },
          { label: "Valor", value: "R$ 90,00", emphasis: true },
        ],
        items: [],
      },
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
        `Seu pedido mais recente é o ${orderNumber}.\n` +
        `Status: Pagamento confirmado\n` +
        `Data do pedido: 21/07/2026\n` +
        `Produto: Produto Exemplo (Sintético)\n` +
        `Valor: R$ 90,00`,
      presentation: {
        variant: "order_summary",
        title: "Último pedido — " + orderNumber,
        icon: "order",
        tone: "positive",
        status_label: "Pagamento confirmado",
        fields: [
          { label: "Produto", value: "Produto Exemplo (Sintético)", emphasis: true },
          { label: "Data", value: "21/07/2026" },
          { label: "Valor", value: "R$ 90,00", emphasis: true },
        ],
        items: [],
      },
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
        `Encontrei 3 pedido(s) com o status Pagamento confirmado.\n` +
        `• Pedido 342671 — 21/07/2026 — R$ 90,00\n` +
        `• Pedido 342580 — 15/07/2026 — R$ 150,00\n` +
        `• Pedido 342401 — 08/07/2026 — R$ 60,00`,
      presentation: {
        variant: "order_list",
        title: "Pedidos com status: Pagamento confirmado",
        subtitle: "3 pedidos encontrados",
        icon: "list",
        tone: "positive",
        status_label: "Pagamento confirmado",
        fields: [],
        items: [
          { title: "Pedido 342671", subtitle: "21/07/2026", value: "R$ 90,00", badge: "Pagamento confirmado", tone: "positive" },
          { title: "Pedido 342580", subtitle: "15/07/2026", value: "R$ 150,00", badge: "Pagamento confirmado", tone: "positive" },
          { title: "Pedido 342401", subtitle: "08/07/2026", value: "R$ 60,00", badge: "Pagamento confirmado", tone: "positive" },
        ],
      },
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
        `Encontrei o colaborador solicitado.\n` +
        `Nome: Pessoa Colaboradora A\n` +
        `Local: Filial Centro\n` +
        `Tipo: Posto de trabalho\n` +
        `Produtos: Produto Alimentação`,
      presentation: {
        variant: "collaborator_summary",
        title: "Colaborador encontrado",
        icon: "person",
        tone: "neutral",
        fields: [
          { label: "Nome", value: "Pessoa Colaboradora A", emphasis: true },
          { label: "Local", value: "Filial Centro" },
          { label: "Tipo", value: "Posto de trabalho" },
          { label: "Produtos", value: "Produto Alimentação" },
        ],
        items: [],
      },
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
        `No momento eu consigo apenas consultar informações. ` +
        `Para realizar essa ação, acesse a jornada correspondente no Espaço RH.`,
      presentation: {
        variant: "transactional_redirect",
        title: "Ação não disponível aqui",
        icon: "redirect",
        tone: "informative",
        fields: [],
        items: [],
      },
      navigation: null,
    };
  }

  function _handleCapabilities() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-001",
      flow: "API_ONLY",
      message:
        `Posso ajudar você com:\n` +
        `• Consultar colaboradores por nome ou CPF\n` +
        `• Consultar pedidos pelo número\n` +
        `• Verificar o último pedido\n` +
        `• Listar pedidos por status\n` +
        `• Informações sobre rastreamento de cartões\n` +
        `• Dúvidas sobre o Espaço RH e o MARH\n\n` +
        `No momento, consigo apenas consultar informações.`,
      presentation: {
        variant: "capabilities_list",
        title: "Como posso ajudar?",
        subtitle: "Sou um assistente consultivo — não realizo ações.",
        icon: "sparkles",
        tone: "informative",
        fields: [],
        items: [
          { title: "Consultar colaboradores por nome ou CPF" },
          { title: "Consultar pedidos pelo número" },
          { title: "Verificar o último pedido" },
          { title: "Listar pedidos por status" },
          { title: "Informações sobre rastreamento de cartões" },
          { title: "Dúvidas sobre o Espaço RH e o MARH" },
        ],
      },
      navigation: null,
    };
  }

  function _handleBlockedCompanyChange() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-BLOCKED",
      flow: "BLOCKED",
      message:
        `A consulta considera apenas a empresa selecionada no app. ` +
        `Para consultar outra empresa, selecione-a no Espaço RH.`,
      presentation: {
        variant: "informational_notice",
        title: "Consulta por empresa",
        icon: "info",
        tone: "informative",
        fields: [],
        items: [],
      },
      navigation: null,
    };
  }

  function _handleUnknown() {
    return {
      correlation_id: _correlationId("mock"),
      intent_id: "INT-000",
      flow: "API_ONLY",
      message:
        `Ainda não tenho essa informação disponível sobre o MARH. ` +
        `Posso ajudar com consultas de colaboradores, pedidos e rastreamento de cartões.`,
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
