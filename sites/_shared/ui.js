'use strict';
(function (root) {
  function $(id) { return document.getElementById(id); }

  function render(kind, title, rows, notes) {
    const result = $('result');
    if (!result) return;
    result.hidden = false;
    const verdict = $('verdict');
    if (verdict) {
      verdict.className = 'verdict ' + (kind || 'pending');
      verdict.textContent = title;
    }
    const kv = $('kv');
    if (kv) {
      kv.replaceChildren();
      (rows || []).forEach(function (row) {
        const dt = document.createElement('dt');
        dt.textContent = row[0];
        const dd = document.createElement('dd');
        dd.textContent = row[1] == null ? '' : String(row[1]);
        kv.appendChild(dt);
        kv.appendChild(dd);
      });
    }
    const extra = $('extra');
    if (extra) {
      extra.replaceChildren();
      (notes || []).forEach(function (note) {
        if (note && note.nodeType) { extra.appendChild(note); return; }
        const p = document.createElement('p');
        p.className = 'banner ' + ((note && note.level) || 'note');
        p.textContent = note && note.text ? note.text : String(note || '');
        extra.appendChild(p);
      });
    }
    const lines = (rows || []).map(function (row) { return row[0] + ': ' + row[1]; });
    (notes || []).forEach(function (note) { if (note && note.text) lines.push('note: ' + note.text); });
    if ($('out')) $('out').value = lines.join('\n');
    if ($('status')) {
      $('status').className = 'status ' + (kind === 'fail' ? 'error' : kind === 'pass' ? 'ok' : 'warn');
      $('status').textContent = 'Done.';
    }
  }

  function fail(message) {
    if ($('result')) $('result').hidden = true;
    if ($('status')) {
      $('status').className = 'status error';
      $('status').textContent = message;
    }
  }

  function busy(message) {
    if ($('status')) {
      $('status').className = 'status';
      $('status').textContent = message || 'Working…';
    }
  }

  function table(headers, rows) {
    const el = document.createElement('table');
    el.className = 'data';
    const thead = document.createElement('thead');
    const hr = document.createElement('tr');
    headers.forEach(function (h) {
      const th = document.createElement('th');
      th.textContent = h;
      hr.appendChild(th);
    });
    thead.appendChild(hr);
    el.appendChild(thead);
    const tb = document.createElement('tbody');
    rows.forEach(function (row) {
      const tr = document.createElement('tr');
      row.forEach(function (cell) {
        const td = document.createElement('td');
        td.textContent = cell == null ? '' : String(cell);
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    el.appendChild(tb);
    return el;
  }

  function onRun(fn) {
    const button = $('go');
    if (!button) return;
    button.addEventListener('click', function () {
      busy('Working…');
      Promise.resolve().then(fn).catch(function (err) {
        fail(err && err.message ? err.message : 'The request failed.');
      });
    });
  }

  function val(id) {
    const el = $(id);
    return el ? el.value.trim() : '';
  }

  root.SiteUI = { $: $, render: render, fail: fail, busy: busy, table: table, onRun: onRun, val: val };
})(typeof globalThis !== 'undefined' ? globalThis : this);
