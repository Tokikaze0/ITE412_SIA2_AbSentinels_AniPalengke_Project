// AniPalengke main utilities: storage, session, nav, toasts, modal
(function () {
  const APP_PREFIX = 'ap_';

  function readJson(key, defaultValue) {
    try {
      const raw = localStorage.getItem(APP_PREFIX + key);
      return raw ? JSON.parse(raw) : defaultValue;
    } catch (e) {
      console.warn('Failed to parse storage for', key, e);
      return defaultValue;
    }
  }
  function writeJson(key, value) {
    localStorage.setItem(APP_PREFIX + key, JSON.stringify(value));
  }
  function generateId(prefix) {
    const rnd = Math.random().toString(36).slice(2, 8);
    const ts = Date.now().toString(36);
    return `${prefix}_${ts}${rnd}`;
  }

  // Session
  function getCurrentUser() {
    return readJson('session', null);
  }
  function setCurrentUser(user) {
    writeJson('session', user);
  }
  function logout() {
    localStorage.removeItem(APP_PREFIX + 'session');
    location.href = 'index.html';
  }
  function requireAuth() {
    const user = getCurrentUser();
    if (!user) {
      location.href = 'login.html';
    }
    return user;
  }
  function requireRole(roles) {
    const user = requireAuth();
    if (Array.isArray(roles) ? !roles.includes(user.role) : user.role !== roles) {
      location.href = 'index.html';
    }
    return user;
  }

  // Toasts
  function ensureToastRoot() {
    let root = document.getElementById('toast-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'toast-root';
      document.body.appendChild(root);
    }
    return root;
  }
  function showToast({ title = 'Notice', message = '', type = 'success', timeout = 3000 } = {}) {
    const root = ensureToastRoot();
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<div class="title">${title}</div><div>${message}</div>`;
    root.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(6px)';
      setTimeout(() => el.remove(), 200);
    }, timeout);
  }

  // Modal
  function ensureModal() {
    let overlay = document.querySelector('.modal-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal" role="dialog" aria-modal="true">
          <div class="modal-header">
            <div id="modal-title">Modal</div>
            <button class="btn btn-ghost" id="modal-close" aria-label="Close">✕</button>
          </div>
          <div class="modal-body"></div>
          <div class="modal-footer">
            <button class="btn btn-secondary" id="modal-cancel">Close</button>
          </div>
        </div>`;
      document.body.appendChild(overlay);
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
      });
      overlay.querySelector('#modal-close').addEventListener('click', closeModal);
      overlay.querySelector('#modal-cancel').addEventListener('click', closeModal);
    }
    return overlay;
  }
  function openModal({ title = 'Modal', content = '', footer = null } = {}) {
    const overlay = ensureModal();
    overlay.querySelector('#modal-title').textContent = title;
    overlay.querySelector('.modal-body').innerHTML = '';
    if (typeof content === 'string') {
      overlay.querySelector('.modal-body').innerHTML = content;
    } else if (content instanceof Node) {
      overlay.querySelector('.modal-body').appendChild(content);
    }
    const footerEl = overlay.querySelector('.modal-footer');
    footerEl.innerHTML = '';
    if (footer) {
      if (typeof footer === 'string') footerEl.innerHTML = footer; else footerEl.appendChild(footer);
    } else {
      footerEl.innerHTML = '<button class="btn btn-secondary" id="modal-cancel">Close</button>';
      footerEl.querySelector('#modal-cancel').addEventListener('click', closeModal);
    }
    overlay.classList.add('open');
  }
  function closeModal() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) overlay.classList.remove('open');
  }

  // Formatting
  function formatCurrency(value) {
    return new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP', maximumFractionDigits: 0 }).format(Number(value || 0));
  }
  function formatDate(ts) {
    const d = new Date(ts);
    return d.toLocaleString();
  }

  // Header/Nav
  function renderHeader(activePath = '') {
    const user = getCurrentUser();
    const header = document.querySelector('.site-header') || (() => {
      const h = document.createElement('header');
      h.className = 'site-header';
      document.body.prepend(h);
      return h;
    })();

    function link(href, label) {
      const active = activePath && href.endsWith(activePath) ? 'active' : '';
      return `<a href="${href}" class="${active}">${label}</a>`;
    }

    const role = user?.role;
    let links = '';
    if (role === 'farmer') {
      links = [
        link('farmer-dashboard.html', 'Dashboard'),
        link('product-list.html', 'Products'),
        link('orders.html', 'Orders'),
        link('delivery.html', 'Delivery'),
        link('community.html', 'Community'),
        link('notifications.html', 'Notifications')
      ].join('');
    } else if (role === 'buyer') {
      links = [
        link('buyer-dashboard.html', 'Dashboard'),
        link('product-list.html', 'Products'),
        link('cart.html', 'Cart'),
        link('orders.html', 'Orders'),
        link('delivery.html', 'Delivery'),
        link('community.html', 'Community'),
        link('notifications.html', 'Notifications')
      ].join('');
    } else if (role === 'admin') {
      links = [
        link('admin-dashboard.html', 'Dashboard'),
        link('product-list.html', 'Products'),
        link('orders.html', 'Orders'),
        link('delivery.html', 'Delivery'),
        link('community.html', 'Community'),
        link('notifications.html', 'Notifications')
      ].join('');
    } else {
      links = [
        link('index.html', 'Home'),
        link('product-list.html', 'Products'),
        link('community.html', 'Community')
      ].join('');
    }

    const authControls = user ? `
      <span class="badge">${user.name} · ${user.role}</span>
      <button class="btn btn-secondary" id="signout-btn">Sign out</button>
    ` : `
      <a class="btn btn-secondary" href="login.html">Login</a>
      <a class="btn btn-primary" href="register.html">Register</a>
    `;

    header.innerHTML = `
      <div class="container navbar">
        <a class="brand" href="index.html">
          <img src="assets/logo.png" alt="AniPalengke logo"/>
          <span>AniPalengke</span>
        </a>
        <nav class="nav-links">${links}</nav>
        <div class="nav-links">${authControls}</div>
      </div>
    `;

    const signoutBtn = document.getElementById('signout-btn');
    if (signoutBtn) signoutBtn.addEventListener('click', () => {
      logout();
    });
  }

  // Expose globally
  window.AniP = {
    readJson,
    writeJson,
    generateId,
    getCurrentUser,
    setCurrentUser,
    logout,
    requireAuth,
    requireRole,
    showToast,
    openModal,
    closeModal,
    formatCurrency,
    formatDate,
    renderHeader
  };

  // Auto-initialize header on DOMContentLoaded if not yet rendered
  document.addEventListener('DOMContentLoaded', () => {
    const path = location.pathname.split('/').pop();
    renderHeader(path);
  });
})();
