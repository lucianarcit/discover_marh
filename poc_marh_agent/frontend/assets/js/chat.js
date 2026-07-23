/**
 * chat.js — Lógica do ChatAlelo (chat-alelo.html)
 * POC MARH Agent
 *
 * Segurança:
 * - Mensagens renderizadas via textContent (nunca innerHTML com input do usuário)
 * - Navegação validada contra allowlist de hosts e routes
 * - Nenhum eval, nenhum script dinâmico
 * - Nenhum dado sensível em console.log
 */

(function () {
  "use strict";

  /* ── Referências ao DOM ── */
  const messagesArea    = document.getElementById("chat-messages");
  const inputField      = document.getElementById("chat-input");
  const sendBtn         = document.getElementById("btn-send");
  const attachBtn       = document.getElementById("btn-attach");
  const attachMenu      = document.getElementById("attach-menu");
  const attachCancel    = document.getElementById("attach-cancel");
  const attachOptions   = document.querySelectorAll("[data-attach-option]");
  const backdrop        = document.getElementById("overlay-backdrop");
  const liveRegion      = document.getElementById("chat-live-region");
  const welcomeSection  = document.getElementById("chat-welcome");
  const envBadge        = document.getElementById("env-badge");

  let isLoading = false;

  /* ── Inicialização ── */
  function init() {
    _setupEnvBadge();
    _setupInput();
    _setupSend();
    _setupAttach();
    _setupSuggestions();
    _setupKeyboard();
  }

  /* ── Indicador de ambiente ── */
  function _setupEnvBadge() {
    if (!envBadge) return;
    envBadge.className = "env-badge " + CONFIG.ENV_BADGE_CLASS;
    envBadge.querySelector(".env-badge__label").textContent = CONFIG.ENV_LABEL;
  }

  /* ── Input ── */
  function _setupInput() {
    if (!inputField || !sendBtn) return;

    inputField.addEventListener("input", () => {
      sendBtn.disabled = inputField.value.trim().length === 0 || isLoading;
      _autoResize();
    });
  }

  function _autoResize() {
    inputField.style.height = "auto";
    inputField.style.height = Math.min(inputField.scrollHeight, 120) + "px";
  }

  /* ── Envio ── */
  function _setupSend() {
    if (!sendBtn) return;
    sendBtn.addEventListener("click", _handleSend);
  }

  function _setupKeyboard() {
    if (!inputField) return;
    inputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) _handleSend();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeAttachMenu();
      }
    });
  }

  async function _handleSend() {
    const text = inputField.value.trim();
    if (!text || isLoading) return;

    _hideWelcome();
    _appendUserMessage(text);
    inputField.value = "";
    inputField.style.height = "auto";
    sendBtn.disabled = true;

    _showTyping();
    isLoading = true;

    let response;
    try {
      response = await AgentApiClient.sendMessage(text);
    } catch (err) {
      response = {
        flow: "ERROR",
        message: "Ocorreu um erro inesperado. Tente novamente.",
        navigation: null,
      };
    } finally {
      isLoading = false;
      _hideTyping();
    }

    _appendAgentMessage(response);
  }

  /* ── Sugestões ── */
  function _setupSuggestions() {
    const suggestions = document.querySelectorAll("[data-suggestion]");  /* abrange suggestion-row e qualquer variante futura */
    suggestions.forEach((card) => {
      card.addEventListener("click", () => {
        const msg = card.dataset.suggestion;
        if (!msg) return;
        inputField.value = msg;
        _autoResize();
        sendBtn.disabled = false;
        inputField.focus();
        _handleSend();
      });

      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          card.click();
        }
      });
    });
  }

  /* ── Oculta seção de boas-vindas na primeira mensagem ── */
  function _hideWelcome() {
    if (welcomeSection && !welcomeSection.hidden) {
      welcomeSection.hidden = true;
    }
  }

  /* ── Renderização de mensagens ── */
  function _appendUserMessage(text) {
    const wrap = document.createElement("div");
    wrap.className = "message message--user";
    wrap.setAttribute("role", "listitem");

    const avatar = document.createElement("span");
    avatar.className = "message__avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "EU";

    const content = document.createElement("div");
    content.className = "message__content";

    const bubble = document.createElement("div");
    bubble.className = "message__bubble";
    bubble.textContent = text;       // seguro: textContent, não innerHTML

    const time = document.createElement("span");
    time.className = "message__time";
    time.textContent = _currentTime();

    content.appendChild(bubble);
    content.appendChild(time);
    wrap.appendChild(content);
    wrap.appendChild(avatar);

    messagesArea.appendChild(wrap);
    _scrollBottom();

    _announce(text);
  }

  function _appendAgentMessage(response) {
    const wrap = document.createElement("div");
    wrap.className = "message message--agent";
    wrap.setAttribute("role", "listitem");

    const avatar = document.createElement("span");
    avatar.className = "message__avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "AI";

    const content = document.createElement("div");
    content.className = "message__content";

    const bubble = document.createElement("div");
    bubble.className = "message__bubble";

    // Renderiza o texto com suporte a markdown básico (negrito **texto**)
    // sem permitir HTML arbitrário
    const formatted = _formatMessageText(response.message || "Sem resposta.");
    bubble.appendChild(formatted);

    const time = document.createElement("span");
    time.className = "message__time";
    time.textContent = _currentTime();

    content.appendChild(bubble);
    content.appendChild(time);

    // Componente de navegação (list_navigation)
    if (response.navigation && response.navigation.type === "list_navigation") {
      const navCard = _buildNavCard(response.navigation);
      if (navCard) content.appendChild(navCard);
    }

    wrap.appendChild(avatar);
    wrap.appendChild(content);

    messagesArea.appendChild(wrap);
    _scrollBottom();

    _announce(response.message || "");
  }

  /**
   * Formata texto do agente com suporte básico a **negrito** e quebras de linha.
   * Nunca usa innerHTML com input de usuário ou backend — constrói nós DOM.
   */
  function _formatMessageText(text) {
    const container = document.createDocumentFragment();
    // Processa linha a linha
    const lines = text.split("\n");
    lines.forEach((line, i) => {
      if (i > 0) container.appendChild(document.createElement("br"));

      // Suporte básico a **negrito**
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      parts.forEach((part) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          const strong = document.createElement("strong");
          strong.textContent = part.slice(2, -2);
          container.appendChild(strong);
        } else if (part.startsWith("_") && part.endsWith("_")) {
          const em = document.createElement("em");
          em.textContent = part.slice(1, -1);
          container.appendChild(em);
        } else {
          container.appendChild(document.createTextNode(part));
        }
      });
    });
    return container;
  }

  /* ── Navigation Builder ── */
  function _buildNavCard(nav) {
    if (!nav.route_id) return null;

    const webviewUrl = AgentApiClient.buildWebviewUrl(
      nav.route_id,
      nav.route_suffix || null
    );

    if (!webviewUrl && !nav.webview_url) return null;

    const resolvedUrl = webviewUrl || nav.webview_url;

    // Valida host antes de criar o link
    if (!AgentApiClient.isAllowedWebviewUrl(resolvedUrl)) return null;

    const card = document.createElement("a");
    card.className = "nav-card";
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", nav.label || "Ver detalhes");

    // Deeplink real no data attribute (para uso futuro no app nativo)
    if (nav.deeplink) {
      card.dataset.deeplink = nav.deeplink;
    }

    // No desktop abre webview em nova aba
    card.href = resolvedUrl;
    card.target = "_blank";
    card.rel = "noopener noreferrer";

    const textDiv = document.createElement("div");
    textDiv.className = "nav-card__text";

    const label = document.createElement("div");
    label.className = "nav-card__label";
    label.textContent = nav.label || "Ver detalhes";

    const hint = document.createElement("div");
    hint.className = "nav-card__hint";
    hint.textContent = "Toque para abrir no app";

    textDiv.appendChild(label);
    textDiv.appendChild(hint);

    const arrow = document.createElement("div");
    arrow.className = "nav-card__arrow";
    arrow.setAttribute("aria-hidden", "true");
    arrow.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>`;

    card.appendChild(textDiv);
    card.appendChild(arrow);

    return card;
  }

  /* ── Indicador de digitação ── */
  let typingEl = null;

  function _showTyping() {
    if (typingEl) return;

    const wrap = document.createElement("div");
    wrap.className = "message message--agent typing-wrapper";
    wrap.id = "typing-indicator";
    wrap.setAttribute("aria-label", "ChatAlelo está digitando");
    wrap.setAttribute("aria-live", "polite");

    const avatar = document.createElement("span");
    avatar.className = "message__avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "AI";

    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";

    const dots = document.createElement("div");
    dots.className = "typing-indicator__dots";
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "typing-indicator__dot";
      dot.setAttribute("aria-hidden", "true");
      dots.appendChild(dot);
    }

    indicator.appendChild(dots);
    wrap.appendChild(avatar);
    wrap.appendChild(indicator);

    messagesArea.appendChild(wrap);
    typingEl = wrap;
    _scrollBottom();
  }

  function _hideTyping() {
    if (typingEl) {
      typingEl.remove();
      typingEl = null;
    }
  }

  /* ── Menu de anexos ── */
  function _setupAttach() {
    if (!attachBtn) return;

    attachBtn.addEventListener("click", openAttachMenu);

    if (attachCancel) {
      attachCancel.addEventListener("click", closeAttachMenu);
    }

    if (backdrop) {
      backdrop.addEventListener("click", closeAttachMenu);
    }

    attachOptions.forEach((opt) => {
      opt.addEventListener("click", () => {
        closeAttachMenu();
        setTimeout(() => {
          _showToast("Envio de anexos não faz parte desta POC.");
        }, 300);
      });
    });
  }

  function openAttachMenu() {
    if (!attachMenu || !backdrop) return;
    attachMenu.classList.add("open");
    backdrop.classList.add("open");
    attachMenu.setAttribute("aria-hidden", "false");
    attachCancel && attachCancel.focus();
  }

  function closeAttachMenu() {
    if (!attachMenu || !backdrop) return;
    attachMenu.classList.remove("open");
    backdrop.classList.remove("open");
    attachMenu.setAttribute("aria-hidden", "true");
  }

  /* ── Toast ── */
  function _showToast(msg) {
    let toast = document.getElementById("app-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "app-toast";
      toast.className = "toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add("toast--visible");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove("toast--visible"), 3500);
  }

  /* ── Aria live para leitores de tela ── */
  function _announce(text) {
    if (!liveRegion) return;
    liveRegion.textContent = "";
    requestAnimationFrame(() => {
      liveRegion.textContent = text.slice(0, 200);
    });
  }

  /* ── Helpers ── */
  function _scrollBottom() {
    if (!messagesArea) return;
    requestAnimationFrame(() => {
      messagesArea.scrollTop = messagesArea.scrollHeight;
    });
  }

  function _currentTime() {
    return new Date().toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  /* ── Bootstrap ── */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
