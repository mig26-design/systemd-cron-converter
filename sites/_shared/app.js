'use strict';
(function () {
  const KEY = 'c2s-theme';
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const navBtn = document.getElementById('nav-toggle');
  const sidebar = document.getElementById('sidebar');

  function preferred() {
    const saved = localStorage.getItem(KEY);
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function apply(theme) {
    root.setAttribute('data-theme', theme);
    if (toggle) {
      toggle.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      toggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    }
  }
  apply(preferred());
  if (toggle) {
    toggle.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(KEY, next);
      apply(next);
    });
  }
  if (navBtn && sidebar) {
    navBtn.addEventListener('click', function () {
      const open = sidebar.classList.toggle('open');
      navBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  async function copyText(text) {
    if (!text) return false;
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      const area = document.createElement('textarea');
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      document.body.removeChild(area);
      return true;
    }
  }

  document.addEventListener('click', function (ev) {
    const btn = ev.target.closest('[data-copy]');
    if (!btn) return;
    const sel = btn.getAttribute('data-copy');
    const el = sel ? document.querySelector(sel) : null;
    const text = el ? (el.value != null ? el.value : el.textContent) : '';
    copyText(text).then(function (ok) {
      if (!ok) return;
      const prev = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = prev; }, 1400);
    });
  });

  globalThis.C2S = {
    copyText: copyText,
    bindLive: function (ids, fn) {
      ids.forEach(function (id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', fn);
        el.addEventListener('change', fn);
      });
      fn();
    }
  };
})();
