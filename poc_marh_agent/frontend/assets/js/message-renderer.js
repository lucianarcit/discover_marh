/**
 * message-renderer.js — Renderização visual de respostas do ChatAlelo
 *
 * Segurança: toda inserção de texto usa textContent/appendChild.
 * Nenhum dado do backend é passado para innerHTML, eval ou similar.
 */

(function () {
  "use strict";

  /* ── SVG icons (inline, sem dependência externa) ── */
  var ICONS = {
    person: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
    order: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/></svg>',
    list: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>',
    sparkles: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
    info: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    warning: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
    question: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    redirect: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>',
    error: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
  };

  /* ── Helpers ── */
  function el(tag, className) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    return node;
  }

  function txt(text) {
    return document.createTextNode(String(text || ""));
  }

  function setIcon(container, iconKey) {
    var svg = ICONS[iconKey] || ICONS.info;
    // Usamos innerHTML APENAS para SVG estático definido neste arquivo,
    // nunca para dados vindos do backend.
    container.innerHTML = svg;
  }

  /* ── Badge de status ── */
  function renderStatusBadge(label, tone) {
    if (!label) return null;
    var badge = el("span", "agent-response-status agent-response-status--" + (tone || "neutral"));
    badge.setAttribute("aria-label", "Status: " + label);
    badge.appendChild(txt(label));
    return badge;
  }

  /* ── Ícone do card ── */
  function renderCardIcon(iconKey) {
    var wrap = el("div", "agent-response-icon");
    wrap.setAttribute("aria-hidden", "true");
    setIcon(wrap, iconKey || "info");
    return wrap;
  }

  /* ── Cabeçalho do card ── */
  function renderHeader(presentation) {
    var header = el("div", "agent-response-header");

    var icon = renderCardIcon(presentation.icon);
    header.appendChild(icon);

    var textWrap = el("div", "agent-response-header-text");

    var title = el("h2", "agent-response-title");
    title.appendChild(txt(presentation.title));
    textWrap.appendChild(title);

    if (presentation.subtitle) {
      var sub = el("p", "agent-response-subtitle");
      sub.appendChild(txt(presentation.subtitle));
      textWrap.appendChild(sub);
    }

    header.appendChild(textWrap);

    if (presentation.status_label) {
      var badge = renderStatusBadge(presentation.status_label, presentation.tone);
      if (badge) header.appendChild(badge);
    }

    return header;
  }

  /* ── Campos (fields) ── */
  function renderFields(fields) {
    if (!fields || fields.length === 0) return null;

    var grid = el("div", "agent-response-fields");

    fields.forEach(function (field) {
      if (!field.value || field.value === "" || field.value === "null" || field.value === "undefined") return;

      var isFull = field.emphasis || field.label === "Produtos" || field.label === "Nome";
      var fieldEl = el("div", "agent-response-field" + (isFull ? " agent-response-field--full" : "") + (field.emphasis ? " agent-response-field--emphasis" : ""));

      var labelEl = el("div", "agent-response-field-label");
      labelEl.appendChild(txt(field.label));
      fieldEl.appendChild(labelEl);

      // Produtos com chips
      if (field.label === "Produtos") {
        var products = field.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
        if (products.length > 1) {
          var chips = el("div", "agent-response-chips");
          products.forEach(function (p) {
            var chip = el("span", "agent-response-chip");
            chip.appendChild(txt(p));
            chips.appendChild(chip);
          });
          fieldEl.appendChild(chips);
        } else {
          var valEl = el("div", "agent-response-field-value");
          valEl.appendChild(txt(field.value));
          fieldEl.appendChild(valEl);
        }
      } else {
        var valEl2 = el("div", "agent-response-field-value");
        valEl2.appendChild(txt(field.value));
        fieldEl.appendChild(valEl2);
      }

      grid.appendChild(fieldEl);
    });

    if (!grid.hasChildNodes()) return null;
    return grid;
  }

  /* ── Items (order_list, capabilities_list) ── */
  function renderItems(items, variant) {
    if (!items || items.length === 0) return null;

    if (variant === "capabilities_list") {
      return renderCapabilityItems(items);
    }
    return renderOrderItems(items);
  }

  function renderOrderItems(items) {
    var list = el("div", "agent-response-items");
    items.forEach(function (item) {
      var row = el("div", "agent-response-item");

      var left = el("div", "agent-response-item-left");

      var titleEl = el("div", "agent-response-item-title");
      titleEl.appendChild(txt(item.title || ""));
      left.appendChild(titleEl);

      if (item.subtitle) {
        var subEl = el("div", "agent-response-item-subtitle");
        subEl.appendChild(txt(item.subtitle));
        left.appendChild(subEl);
      }

      row.appendChild(left);

      var right = el("div", "agent-response-item-right");

      if (item.value) {
        var val = el("div", "agent-response-item-value");
        val.appendChild(txt(item.value));
        right.appendChild(val);
      }

      if (item.badge) {
        var badge = renderStatusBadge(item.badge, item.tone || "neutral");
        if (badge) right.appendChild(badge);
      }

      row.appendChild(right);
      list.appendChild(row);
    });
    return list;
  }

  function renderCapabilityItems(items) {
    var list = el("div", "agent-response-items");
    items.forEach(function (item) {
      var row = el("div", "agent-response-capability-item");

      var bullet = el("div", "agent-response-capability-bullet");
      bullet.setAttribute("aria-hidden", "true");
      row.appendChild(bullet);

      var textEl = el("div", "agent-response-capability-text");
      textEl.appendChild(txt(item.title || ""));
      row.appendChild(textEl);

      list.appendChild(row);
    });
    return list;
  }

  /* ── Notice card (warning/error/info/clarification) ── */
  function renderNoticeCard(presentation) {
    var tone = presentation.tone || "neutral";
    var notice = el("div", "agent-response-notice agent-response-notice--" + tone);
    notice.setAttribute("role", "status");

    var iconWrap = el("div", "agent-response-notice__icon");
    iconWrap.setAttribute("aria-hidden", "true");
    setIcon(iconWrap, presentation.icon || "info");
    notice.appendChild(iconWrap);

    var textWrap = el("div");
    var titleEl = el("strong");
    titleEl.appendChild(txt(presentation.title));
    textWrap.appendChild(titleEl);

    notice.appendChild(textWrap);
    return notice;
  }

  /* ── Nota consultiva (capacidades) ── */
  function renderConsultiveNote() {
    var note = el("div", "agent-response-consultive-note");
    note.appendChild(txt("Sou um agente consultivo — não realizo ações diretamente."));
    return note;
  }

  /* ── Texto de knowledge ── */
  function renderKnowledgeText(message) {
    var textEl = el("div", "agent-response-knowledge-text");
    // Renderiza texto sem markdown, com quebras de linha preservadas (white-space: pre-wrap no CSS)
    textEl.appendChild(txt(message || ""));
    return textEl;
  }

  /* ── Renderiza presentation completo ── */
  function renderPresentation(presentation, message) {
    if (!presentation || !presentation.variant) {
      return renderFallbackMessage(message);
    }

    var variant = presentation.variant;
    var tone = presentation.tone || "neutral";

    // Variants que usam notice simples (sem card estruturado)
    var noticeVariants = ["warning_notice", "error_notice", "clarification", "transactional_redirect", "informational_notice"];
    if (noticeVariants.indexOf(variant) !== -1) {
      var frag = document.createDocumentFragment();
      frag.appendChild(renderNoticeCard(presentation));
      // Adiciona o texto da mensagem abaixo do notice
      var textWrapper = el("div");
      textWrapper.style.marginTop = "8px";
      textWrapper.style.fontSize = "var(--font-size-sm)";
      textWrapper.style.color = "var(--color-ink)";
      textWrapper.style.lineHeight = "1.55";
      textWrapper.appendChild(txt(message || ""));
      frag.appendChild(textWrapper);
      return frag;
    }

    // Card estruturado (collaborator_summary, order_summary, order_list, capabilities_list, knowledge_answer)
    var toneModifier = (tone !== "neutral" && tone !== "informative") ? " agent-response-card--" + tone : "";
    var card = el("div", "agent-response-card" + toneModifier);

    var header = renderHeader(presentation);
    card.appendChild(header);

    var body = el("div", "agent-response-body");

    if (variant === "knowledge_answer") {
      body.appendChild(renderKnowledgeText(message));
    } else if (variant === "capabilities_list") {
      var items = renderItems(presentation.items, variant);
      if (items) body.appendChild(items);
      body.appendChild(renderConsultiveNote());
    } else if (variant === "order_list") {
      var orderItems = renderItems(presentation.items, variant);
      if (orderItems) body.appendChild(orderItems);
    } else {
      // collaborator_summary, order_summary
      var fields = renderFields(presentation.fields);
      if (fields) body.appendChild(fields);
    }

    card.appendChild(body);
    return card;
  }

  /* ── Fallback: texto simples (sem presentation) ── */
  function renderFallbackMessage(message) {
    var frag = document.createDocumentFragment();
    var lines = (message || "Sem resposta.").split("\n");
    lines.forEach(function (line, i) {
      if (i > 0) frag.appendChild(document.createElement("br"));
      // Suporte a **negrito**
      var parts = line.split(/(\*\*[^*]+\*\*)/g);
      parts.forEach(function (part) {
        if (part.startsWith("**") && part.endsWith("**")) {
          var strong = document.createElement("strong");
          strong.textContent = part.slice(2, -2);
          frag.appendChild(strong);
        } else {
          frag.appendChild(document.createTextNode(part));
        }
      });
    });
    return frag;
  }

  /* ── Entry point ── */
  function renderMessage(response) {
    if (response.presentation) {
      return renderPresentation(response.presentation, response.message || "");
    }
    return renderFallbackMessage(response.message || "Sem resposta.");
  }

  /* ── Exporta globalmente ── */
  window.MessageRenderer = {
    renderMessage: renderMessage,
    renderPresentation: renderPresentation,
    renderFallbackMessage: renderFallbackMessage,
    renderStatusBadge: renderStatusBadge,
  };
})();
