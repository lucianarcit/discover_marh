/**
 * api-client.js — Interface abstrata de comunicação com o agente MARH
 *
 * Modo mock  (CONFIG.USE_MOCK_AGENT = true):  usa MockAgent, sem HTTP
 * Modo real  (CONFIG.USE_MOCK_AGENT = false): POST para CONFIG.AGENT_API_URL
 *
 * Nunca inclua credenciais, tokens, access keys ou segredos neste arquivo.
 * Nunca leia company_id, user_id ou session_id da conversa do usuário.
 * Classificação: POC LOCAL — sem dados reais
 */

const AgentApiClient = (() => {
  /**
   * Monta o payload de request conforme o contrato do backend MARH.
   * Os campos corporativos são sempre sintéticos e fixos na POC.
   */
  function _buildPayload(userMessage) {
    return {
      company_id:  CONFIG.SYNTHETIC_COMPANY_ID,
      user_id:     CONFIG.SYNTHETIC_USER_ID,
      session_id:  CONFIG.SYNTHETIC_SESSION_ID,
      message:     String(userMessage).slice(0, 2000),
      environment: CONFIG.ENVIRONMENT,
    };
  }

  /**
   * Valida o formato mínimo da resposta recebida do backend.
   * Retorna true se a estrutura básica for válida.
   */
  function _validateResponse(data) {
    if (!data || typeof data !== "object") return false;
    if (typeof data.message !== "string") return false;
    return true;
  }

  /**
   * Constrói resposta de erro formatada no padrão de response.
   */
  function _errorResponse(message, code) {
    return {
      correlation_id: null,
      intent_id: null,
      flow: "ERROR",
      message,
      navigation: null,
      _error: true,
      _code: code,
    };
  }

  /**
   * Mapeia status HTTP para mensagem amigável.
   */
  function _httpErrorMessage(status) {
    const map = {
      400: "A requisição enviada é inválida. Tente novamente.",
      401: "Sessão não autorizada. Por favor, faça login novamente.",
      403: "Você não tem permissão para realizar esta ação.",
      404: "O serviço não foi encontrado. Verifique a configuração.",
      422: "Os dados enviados não puderam ser processados.",
      429: "Muitas requisições em pouco tempo. Aguarde alguns segundos e tente novamente.",
    };
    if (map[status]) return map[status];
    if (status >= 500) return "Erro interno do servidor. Tente novamente mais tarde.";
    return `Erro inesperado (${status}). Tente novamente.`;
  }

  /**
   * Modo real: envia POST para o backend com timeout e tratamento de erros.
   */
  async function _sendToBackend(payload) {
    const controller = new AbortController();
    const timer = setTimeout(
      () => controller.abort(),
      CONFIG.REQUEST_TIMEOUT_MS
    );

    let response;
    try {
      response = await fetch(CONFIG.AGENT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timer);
      if (err.name === "AbortError") {
        return _errorResponse(
          "A solicitação demorou muito para responder. Verifique sua conexão e tente novamente.",
          "TIMEOUT"
        );
      }
      return _errorResponse(
        "Não foi possível conectar ao servidor. Verifique se o backend está em execução.",
        "NETWORK_ERROR"
      );
    } finally {
      clearTimeout(timer);
    }

    if (!response.ok) {
      return _errorResponse(_httpErrorMessage(response.status), `HTTP_${response.status}`);
    }

    let data;
    try {
      data = await response.json();
    } catch {
      return _errorResponse(
        "A resposta do servidor não pôde ser interpretada.",
        "PARSE_ERROR"
      );
    }

    if (!_validateResponse(data)) {
      return _errorResponse(
        "A resposta do servidor está em formato inesperado.",
        "INVALID_FORMAT"
      );
    }

    return data;
  }

  /* ────────────────────────────────────────────────────
     Ponto de entrada público
     ──────────────────────────────────────────────────── */

  /**
   * Envia uma mensagem ao agente e retorna a resposta.
   *
   * @param {string} userMessage - Texto da mensagem do usuário
   * @returns {Promise<object>} - Response no contrato do agente MARH
   */
  async function sendMessage(userMessage) {
    const payload = _buildPayload(userMessage);

    if (CONFIG.USE_MOCK_AGENT) {
      return MockAgent.sendMessage(payload);
    }

    return _sendToBackend(payload);
  }

  /**
   * Valida se uma URL de webview pertence a um host permitido.
   * Usado pelo Navigation Builder antes de abrir qualquer link.
   *
   * @param {string} url
   * @returns {boolean}
   */
  function isAllowedWebviewUrl(url) {
    try {
      const parsed = new URL(url);
      return CONFIG.ALLOWED_WEBVIEW_HOSTS.some((host) => parsed.hostname === host);
    } catch {
      return false;
    }
  }

  /**
   * Valida e constrói uma URL de webview para um route_id e suffix conhecidos.
   * Protege contra path traversal e identificadores inválidos.
   *
   * @param {string} routeId - Chave do ALLOWED_ROUTES
   * @param {string|null} suffix - Sufixo numérico (ex: orderNumber)
   * @returns {string|null}
   */
  function buildWebviewUrl(routeId, suffix) {
    const routeBase = CONFIG.ALLOWED_ROUTES[routeId];
    if (!routeBase) return null;

    if (suffix !== null && suffix !== undefined) {
      if (!/^\d{1,20}$/.test(String(suffix))) return null;
    }

    const path = suffix ? routeBase + suffix : routeBase;
    const base = CONFIG.WEBVIEW_BASE_URLS[CONFIG.ENVIRONMENT];
    return base + path;
  }

  return { sendMessage, isAllowedWebviewUrl, buildWebviewUrl };
})();
