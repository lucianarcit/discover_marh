/**
 * config.js — Configuração da POC MARH Agent
 *
 * Para ativar o backend real: altere USE_MOCK_AGENT para false
 * e defina AGENT_API_URL com o endereço do servidor local.
 *
 * Nunca inclua credenciais, tokens ou segredos neste arquivo.
 * Classificação: POC LOCAL — sem dados reais
 */

const CONFIG = Object.freeze({
  /** Quando true, usa MockAgent sem chamadas HTTP */
  USE_MOCK_AGENT: false,

  /** URL do backend quando USE_MOCK_AGENT = false */
  AGENT_API_URL: "https://pzn843po3h.execute-api.sa-east-1.amazonaws.com/chat",

  /** Timeout de requisição em milissegundos */
  REQUEST_TIMEOUT_MS: 30000,

  /**
   * Identificadores sintéticos para a POC.
   * Em produção estes valores viriam da sessão autenticada —
   * nunca de campos preenchidos pelo usuário na conversa.
   */
  SYNTHETIC_COMPANY_ID:  "empresa-sintetica-001",
  SYNTHETIC_USER_ID:     "usuario-sintetico-001",
  SYNTHETIC_SESSION_ID:  "sessao-sintetica-001",

  /** Ambiente alvo para deeplinks e navegação */
  ENVIRONMENT: "HML",

  /**
   * Allowlist de hosts permitidos para webview.
   * Qualquer URL de navegação é validada contra esta lista.
   */
  ALLOWED_WEBVIEW_HOSTS: [
    "meualelo-webviews-hml.siteteste.inf.br",
    "meualelo-webviews.alelo.com.br",
  ],

  /** Base de URLs de webview por ambiente */
  WEBVIEW_BASE_URLS: {
    HML: "https://meualelo-webviews-hml.siteteste.inf.br/",
    PRD: "https://meualelo-webviews.alelo.com.br/",
  },

  /**
   * Rotas permitidas para navegação interna.
   * Apenas IDs nesta allowlist são aceitos no Navigation Builder.
   */
  ALLOWED_ROUTES: {
    "ROUTE-ORDER-DETAIL":       "#/order-detail/",
    "ROUTE-ORDER-LIST":         "#/order-list",
    "ROUTE-COLLABORATOR-DETAIL":"#/collaborator-detail/",
    "ROUTE-COLLABORATOR-LIST":  "#/collaborator-list",
    "ROUTE-EMISSION":           "#/emission",
    "ROUTE-REPORTS":            "#/reports",
  },

  /** Modo de exibição do indicador de ambiente */
  get ENV_LABEL() {
    if (this.USE_MOCK_AGENT) return "MOCK LOCAL";
    if (this.AGENT_API_URL.includes("localhost")) return "BACKEND MOCK";
    return "AWS HML";
  },

  get ENV_BADGE_CLASS() {
    if (this.USE_MOCK_AGENT) return "env-badge--mock";
    if (this.AGENT_API_URL.includes("localhost")) return "env-badge--local";
    return "env-badge--hml";
  },
});
