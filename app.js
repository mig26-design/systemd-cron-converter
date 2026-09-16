'use strict';

(function () {
  const C = globalThis.CronSystemd;
  if (!C) {
    console.error('converter.js failed to load');
    return;
  }

  const cronInput = document.getElementById('cron-input');
  const calInput = document.getElementById('cal-input');
  const cronStatus = document.getElementById('cron-status');
  const calStatus = document.getElementById('cal-status');
  const explanation = document.getElementById('explanation');
  const messages = document.getElementById('messages');
  const presetRow = document.getElementById('preset-row');
  const themeToggle = document.getElementById('theme-toggle');
  const cronPanel = document.querySelector('.panel[data-side="cron"]');
  const calPanel = document.querySelector('.panel[data-side="calendar"]');

  let source = 'cron';
  let updating = false;

  function preferredTheme() {
    const saved = localStorage.getItem('croncal-theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    themeToggle.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  }

  applyTheme(preferredTheme());
  themeToggle.addEventListener('click', function () {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('croncal-theme', next);
    applyTheme(next);
  });

  function setStatus(el, kind, text) {
    el.className = 'panel-status' + (kind ? ' ' + kind : '');
    el.textContent = text || '';
  }

  function renderMessages(result) {
    messages.innerHTML = '';
    const items = [];
    (result.errors || []).forEach(function (t) { items.push({ kind: 'error', t: t }); });
    (result.warnings || []).forEach(function (t) { items.push({ kind: 'warn', t: t }); });
    (result.notes || []).forEach(function (t) { items.push({ kind: 'note', t: t }); });
    items.forEach(function (item) {
      const li = document.createElement('li');
      li.className = item.kind;
      li.textContent = item.t;
      messages.appendChild(li);
    });
  }

  function markSource(side) {
    cronPanel.classList.toggle('active', side === 'cron');
    calPanel.classList.toggle('active', side === 'calendar');
  }

  function convertFromCron() {
    const value = cronInput.value;
    const result = C.cronToOnCalendar(value);
    if (result.empty) {
      calInput.value = '';
      setStatus(cronStatus, '', '');
      setStatus(calStatus, '', '');
      explanation.textContent = 'Type a cron expression or an OnCalendar= value to see the translation.';
      messages.innerHTML = '';
      return;
    }
    if (!result.ok) {
      setStatus(cronStatus, 'error', result.errors[0]);
      setStatus(calStatus, '', '');
      explanation.textContent = 'Fix the cron expression to convert it.';
      renderMessages(result);
      return;
    }
    calInput.value = result.output;
    setStatus(cronStatus, 'ok', 'Valid 5-field cron');
    if (result.representable) {
      setStatus(calStatus, 'ok', result.shortcut ? 'Shortcut: ' + result.shortcut : 'OnCalendar equivalent');
    } else {
      setStatus(calStatus, 'warn', 'Not a single OnCalendar= — see notes');
    }
    explanation.textContent = result.explanation;
    renderMessages(result);
  }

  function convertFromCalendar() {
    const value = calInput.value;
    const result = C.onCalendarToCron(value);
    if (result.empty) {
      cronInput.value = '';
      setStatus(cronStatus, '', '');
      setStatus(calStatus, '', '');
      explanation.textContent = 'Type a cron expression or an OnCalendar= value to see the translation.';
      messages.innerHTML = '';
      return;
    }
    if (!result.ok) {
      setStatus(calStatus, 'error', result.errors[0]);
      setStatus(cronStatus, '', '');
      explanation.textContent = 'Fix the OnCalendar expression to convert it.';
      renderMessages(result);
      return;
    }
    cronInput.value = result.output;
    setStatus(calStatus, 'ok', result.shortcut ? 'Shortcut: ' + result.shortcut : 'Valid calendar event');
    if (result.representable) {
      setStatus(cronStatus, 'ok', '5-field cron equivalent');
    } else {
      setStatus(cronStatus, 'warn', 'Not representable as standard cron');
    }
    explanation.textContent = result.explanation;
    renderMessages(result);
  }

  function run() {
    updating = true;
    markSource(source);
    if (source === 'cron') convertFromCron();
    else convertFromCalendar();
    updating = false;
  }

  cronInput.addEventListener('input', function () {
    if (updating) return;
    source = 'cron';
    run();
  });
  calInput.addEventListener('input', function () {
    if (updating) return;
    source = 'calendar';
    run();
  });

  C.PRESETS.forEach(function (preset) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'preset';
    btn.textContent = preset.label;
    btn.title = preset.hint || (preset.cron && preset.calendar
      ? preset.cron + '  ↔  ' + preset.calendar
      : preset.cron || preset.calendar);
    btn.addEventListener('click', function () {
      Array.prototype.forEach.call(presetRow.querySelectorAll('.preset'), function (el) {
        el.setAttribute('aria-pressed', el === btn ? 'true' : 'false');
      });
      if (preset.cron && !preset.calendar) {
        source = 'cron';
        cronInput.value = preset.cron;
      } else if (preset.calendar && !preset.cron) {
        source = 'calendar';
        calInput.value = preset.calendar;
      } else {
        source = 'cron';
        cronInput.value = preset.cron;
      }
      run();
      (source === 'cron' ? cronInput : calInput).focus();
    });
    presetRow.appendChild(btn);
  });

  async function copyText(text, button) {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      const area = document.createElement('textarea');
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      document.body.removeChild(area);
    }
    const prev = button.textContent;
    button.textContent = 'Copied';
    setTimeout(function () { button.textContent = prev; }, 1400);
  }

  document.querySelectorAll('.copy-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const side = btn.getAttribute('data-copy');
      const text = side === 'cron' ? cronInput.value : calInput.value;
      copyText(text, btn);
    });
  });

  cronInput.value = '0 4 * * *';
  source = 'cron';
  run();
})();
