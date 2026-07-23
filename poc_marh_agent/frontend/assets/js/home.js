/**
 * home.js — Lógica da Home (index.html)
 * Espaço RH · POC MARH Agent
 */

(function () {
  "use strict";

  /* ── Dados sintéticos de últimos pedidos ── */
  const SYNTHETIC_ORDERS = [
    {
      id: "342671",
      product: "Produto Exemplo A (Sintético)",
      date: "21/07/2026",
      amount: "R$ 90,00",
      status: "paid",
      statusLabel: "Pago",
    },
    {
      id: "342580",
      product: "Produto Exemplo B (Sintético)",
      date: "15/07/2026",
      amount: "R$ 150,00",
      status: "pending",
      statusLabel: "Pendente",
    },
    {
      id: "342401",
      product: "Produto Exemplo C (Sintético)",
      date: "08/07/2026",
      amount: "R$ 60,00",
      status: "process",
      statusLabel: "Processando",
    },
  ];

  /* ── Inicia indicador de ambiente ── */
  function initEnvBadge() {
    const badge = document.getElementById("env-badge");
    if (!badge) return;
    badge.className = "env-badge " + CONFIG.ENV_BADGE_CLASS;
    badge.querySelector(".env-badge__label").textContent = CONFIG.ENV_LABEL;
  }

  /* ── Renderiza lista de últimos pedidos ── */
  function renderOrders() {
    const list = document.getElementById("orders-list");
    if (!list) return;

    list.innerHTML = "";

    SYNTHETIC_ORDERS.forEach((order) => {
      const item = document.createElement("button");
      item.className = "order-item";
      item.setAttribute("type", "button");
      item.setAttribute(
        "aria-label",
        `Pedido ${order.id} — ${order.statusLabel} — ${order.amount}`
      );

      item.innerHTML =
        `<span class="order-item__icon" aria-hidden="true">` +
        _iconReceipt() +
        `</span>` +
        `<span class="order-item__info">` +
        `<span class="order-item__id">Pedido #${_escText(order.id)}</span>` +
        `<span class="order-item__date">${_escText(order.date)}</span>` +
        `</span>` +
        `<span class="order-item__right">` +
        `<span class="order-item__amount">${_escText(order.amount)}</span>` +
        `<span class="status-badge status-badge--${_escText(order.status)}">${_escText(order.statusLabel)}</span>` +
        `</span>`;

      item.addEventListener("click", () => openOrderDemo(order));
      list.appendChild(item);
    });
  }

  /* ── Modal de demonstração de pedido ── */
  function openOrderDemo(order) {
    const overlay = document.getElementById("demo-modal-overlay");
    const title   = document.getElementById("demo-modal-title");
    const body    = document.getElementById("demo-modal-body");
    if (!overlay) return;

    title.textContent = `Pedido #${order.id}`;

    body.innerHTML =
      `<p class="demo-modal__text">` +
      `<strong>Status:</strong> ${_escText(order.statusLabel)}<br>` +
      `<strong>Data:</strong> ${_escText(order.date)}<br>` +
      `<strong>Produto:</strong> ${_escText(order.product)}<br>` +
      `<strong>Valor:</strong> ${_escText(order.amount)}` +
      `</p>` +
      `<p style="font-size:0.72rem;color:var(--color-muted);margin-bottom:var(--space-4)">` +
      `Dados sintéticos · POC MARH Agent` +
      `</p>`;

    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    document.getElementById("demo-modal-close").focus();
  }

  function closeOrderDemo() {
    const overlay = document.getElementById("demo-modal-overlay");
    if (!overlay) return;
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
  }

  /* ── Atalhos de navegação (demo visual) ── */
  function initShortcuts() {
    const shortcuts = document.querySelectorAll("[data-shortcut]");
    shortcuts.forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.shortcut;
        if (target === "chat") {
          window.location.href = "chat-alelo.html";
        } else {
          showDemoToast(`"${btn.querySelector(".shortcut-btn__label").textContent}" — demonstração visual`);
        }
      });
    });
  }

  /* ── "Ver mais" pedidos ── */
  function initSeeMore() {
    const btn = document.getElementById("btn-see-more");
    if (!btn) return;
    btn.addEventListener("click", () => {
      showDemoToast("Visualização completa de pedidos — disponível no app");
    });
  }

  /* ── Toast ── */
  function showDemoToast(msg) {
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
    toast._timer = setTimeout(() => toast.classList.remove("toast--visible"), 3000);
  }

  /* ── Escape fecha modal ── */
  function initKeyboard() {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeOrderDemo();
    });
  }

  /* ── Utilitário de escape ── */
  function _escText(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ── Ícones SVG inline (sem dependência externa) ── */
  function _iconReceipt() {
    return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
    </svg>`;
  }

  /* ── Bootstrap ── */
  function init() {
    initEnvBadge();
    renderOrders();
    initShortcuts();
    initSeeMore();
    initKeyboard();

    /* Fechar modal pelo overlay ou botão */
    const overlay = document.getElementById("demo-modal-overlay");
    const closeBtn = document.getElementById("demo-modal-close");

    if (overlay) {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeOrderDemo();
      });
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", closeOrderDemo);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
