'use strict';
(function () {
  const X = globalThis.X402;
  const U = globalThis.SiteUI;
  const K = globalThis.Keccak;
  if (!X || !U || !document.body) return;

  function parsed() {
    return X.extractRequirements(X.parseDump(U.val('raw')));
  }

  function rowsFor(rec) {
    return [
      ['network', rec.network || '—'],
      ['payTo', rec.payTo || '—'],
      ['asset', rec.asset || '—'],
      ['amount', rec.amount || '—'],
      ['resource', rec.resource || '—'],
      ['scheme', rec.scheme || '—'],
      ['mimeType', rec.mimeType || '—'],
      ['maxTimeoutSeconds', rec.maxTimeoutSeconds || '—'],
      ['source', rec.source || '']
    ];
  }

  function showReqs(extracted, title, kind) {
    const reqs = extracted.requirements;
    const notes = reqs.map(function (rec, i) {
      return { level: 'note', text: 'Requirement ' + (i + 1) + ': ' + [rec.network, rec.payTo, rec.asset, rec.amount].filter(Boolean).join(' · ') };
    });
    if (reqs.length > 1 && U.$('extra')) {
      U.render(kind || (reqs.length ? 'pass' : 'fail'), title, rowsFor(reqs[0] || {}), [
        U.table(['#', 'network', 'payTo', 'asset', 'amount', 'resource'], reqs.map(function (rec, i) {
          return [String(i + 1), rec.network || '', rec.payTo || '', rec.asset || '', rec.amount || '', rec.resource || ''];
        }))
      ].concat(notes));
      return;
    }
    U.render(kind || (reqs.length ? 'pass' : 'fail'), title, rowsFor(reqs[0] || {}), notes);
  }

  const pages = {
    'x402-inspect': function () {
      if (U.$('sample')) U.$('sample').addEventListener('click', function () { U.$('raw').value = X.SAMPLE; U.$('go').click(); });
      if (U.$('fetch')) U.$('fetch').addEventListener('click', async function () {
        U.busy('Fetching… a cross-origin 402 is often invisible.');
        try {
          const url = new URL(U.val('url'));
          if (url.protocol !== 'http:' && url.protocol !== 'https:') throw new Error('Only http and https URLs can be fetched.');
          const res = await fetch(url.toString(), { method: 'GET', mode: 'cors', cache: 'no-store' });
          const headers = {};
          res.headers.forEach(function (value, key) { headers[key.toLowerCase()] = value; });
          const body = await res.text();
          const lines = Object.keys(headers).map(function (name) { return name + ': ' + headers[name]; });
          U.$('raw').value = ['HTTP/1.1 ' + res.status].concat(lines).concat(['', body]).join('\n');
          showReqs(X.extractRequirements({ status: res.status, headers: headers, body: body }), 'Fetched HTTP ' + res.status, res.status === 402 ? 'pass' : 'pending');
        } catch (err) {
          U.fail(err.message && err.message.indexOf('Only http') === 0 ? err.message : 'The browser could not read that URL. That is usually CORS. Paste the raw 402 from curl -D -.');
        }
      });
      U.onRun(function () {
        const extracted = parsed();
        const klass = X.classifyResponse(extracted);
        showReqs(extracted, klass.label + (extracted.requirements.length ? ' · ' + extracted.requirements.length + ' requirement(s)' : ''), klass.kind);
      });
    },

    'payment-required-header-decode': function () {
      if (U.$('sample')) U.$('sample').addEventListener('click', function () { U.$('raw').value = X.SAMPLE; U.$('go').click(); });
      U.onRun(function () {
        const dump = X.parseDump(U.val('raw'));
        const header = dump.headers['payment-required'] || dump.headers['x-payment-required'] || dump.headers['x-payment'] || '';
        if (!header) throw new Error('No payment-required, x-payment-required, or x-payment header in the paste.');
        const json = X.tryJson(header) || (function () {
          const extracted = X.extractRequirements({ status: dump.status, headers: { 'payment-required': header }, body: '' });
          return extracted.requirements[0] || null;
        })();
        const pretty = json && json.network ? JSON.stringify(json, null, 2) : header;
        U.render('pass', 'Decoded payment header', [
          ['status', dump.status == null ? '—' : String(dump.status)],
          ['header bytes', String(header.length)]
        ], [{ level: 'note', text: pretty.slice(0, 1200) }]);
      });
    },

    'payto-address-extract': function () {
      U.onRun(function () {
        const reqs = parsed().requirements.filter(function (r) { return r.payTo; });
        if (!reqs.length) throw new Error('No payTo field found.');
        U.render('pass', reqs.length + ' payTo value(s)', [], [U.table(['payTo', 'checksum or raw', 'network'], reqs.map(function (r) {
          const checksum = K && X.isHexAddress(r.payTo) ? K.eip55(r.payTo) : r.payTo;
          return [r.payTo, checksum, r.network || ''];
        }))]);
      });
    },

    'x402-network-id-check': function () {
      U.onRun(function () {
        const reqs = parsed().requirements;
        if (!reqs.length) throw new Error('No payment requirement to check.');
        const rec = reqs[0];
        const info = X.networkInfo(rec.network);
        U.render(info ? 'pass' : 'fail', info ? ('Known network ' + rec.network) : 'Network is not in the local list', [
          ['network', rec.network || '—'],
          ['chain id', info && info.chainId != null ? String(info.chainId) : '—'],
          ['known USDC', info ? info.usdc : '—']
        ]);
      });
    },

    'usdc-atomic-amount-decode': function () {
      U.onRun(function () {
        const reqs = parsed().requirements;
        const amount = U.val('amount') || (reqs[0] && reqs[0].amount);
        const decimals = Number(U.val('decimals') || '6');
        if (!amount) throw new Error('No amount in the paste and the amount field is empty.');
        const human = X.formatUnits(amount, decimals);
        U.render('pass', human + ' units', [
          ['atomic', amount],
          ['decimals', String(decimals)],
          ['human', human]
        ], [{ level: 'note', text: 'USDC uses 6 decimals. This does not check that the asset is USDC.' }]);
      });
    },

    'accept-payment-challenge-parse': function () {
      if (U.$('sample')) U.$('sample').addEventListener('click', function () { U.$('raw').value = X.SAMPLE; U.$('go').click(); });
      U.onRun(function () {
        const extracted = parsed();
        showReqs(extracted, extracted.requirements.length + ' accepts-style requirement(s)');
      });
    },

    'x402-resource-price-table': function () {
      U.onRun(function () {
        const reqs = parsed().requirements;
        if (!reqs.length) throw new Error('Nothing to tabulate.');
        U.render('pass', reqs.length + ' priced resource(s)', [], [U.table(
          ['resource', 'network', 'atomic amount', 'human @ 6 dp'],
          reqs.map(function (r) {
            let human = '';
            try { human = r.amount ? X.formatUnits(r.amount, 6) : ''; } catch (err) { human = ''; }
            return [r.resource || '(none)', r.network || '', r.amount || '', human];
          })
        )]);
      });
    },

    'base-usdc-payto-verify': function () {
      U.onRun(function () {
        const rec = parsed().requirements[0];
        if (!rec) throw new Error('No requirement found.');
        const info = X.networkInfo(rec.network);
        const payOk = X.isHexAddress(rec.payTo);
        const asset = (rec.asset || '').toLowerCase();
        const expected = info ? info.usdc.toLowerCase() : '';
        const assetOk = expected && asset === expected;
        const kind = payOk && assetOk ? 'pass' : 'fail';
        U.render(kind, kind === 'pass' ? 'payTo is an address and asset matches known USDC' : 'payTo or asset did not match', [
          ['network', rec.network || '—'],
          ['payTo', rec.payTo || '—'],
          ['payTo is 20-byte hex', payOk ? 'yes' : 'no'],
          ['asset', rec.asset || '—'],
          ['expected USDC', expected || 'network not in the Base/known list']
        ]);
      });
    },

    'x402-facilitator-hint': function () {
      U.onRun(function () {
        const body = X.tryJson(X.parseDump(U.val('raw')).body || '') || {};
        const rec = parsed().requirements[0] || {};
        const extra = rec.extra || body.extra || {};
        const blob = JSON.stringify(extra);
        const hint = /facilitator|cdp|coinbase/i.test(blob + JSON.stringify(body)) ? 'JSON mentions a facilitator-like field' : 'No facilitator field spotted';
        U.render('pending', hint, [
          ['extra', blob === '{}' ? '—' : blob.slice(0, 400)],
          ['scheme', rec.scheme || body.scheme || '—']
        ], [{ level: 'note', text: 'Facilitator URLs are copied from the JSON when present. This page does not call one.' }]);
      });
    },

    'max-timeout-seconds-check': function () {
      U.onRun(function () {
        const rec = parsed().requirements[0];
        const seconds = U.val('seconds') || (rec && rec.maxTimeoutSeconds);
        const verdict = X.timeoutVerdict(seconds);
        U.render(verdict.kind, verdict.label, [['maxTimeoutSeconds', String(seconds || '—')]]);
      });
    },

    'mime-type-payment-match': function () {
      U.onRun(function () {
        const rec = parsed().requirements[0];
        const expected = U.val('mime') || 'application/json';
        const actual = (rec && rec.mimeType) || '';
        if (!actual) throw new Error('No mimeType on the requirement.');
        const ok = actual.toLowerCase() === expected.toLowerCase();
        U.render(ok ? 'pass' : 'fail', ok ? 'MIME types match' : 'MIME types differ', [
          ['expected', expected],
          ['requirement', actual]
        ]);
      });
    },

    'x402-vs-402-plain': function () {
      if (U.$('sample')) U.$('sample').addEventListener('click', function () { U.$('raw').value = X.SAMPLE; U.$('go').click(); });
      U.onRun(function () {
        const extracted = parsed();
        const klass = X.classifyResponse(extracted);
        U.render(klass.kind, klass.label, [
          ['http status', extracted.status == null ? '—' : String(extracted.status)],
          ['requirements', String(extracted.requirements.length)]
        ]);
      });
    },

    'walletforge-endpoint-probe': function () {
      U.onRun(async function () {
        const url = new URL(U.val('url'));
        if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new Error('Use an http or https URL.');
        U.busy('Probing… CORS may hide a 402.');
        let res;
        try { res = await fetch(url.toString(), { method: 'GET', mode: 'cors', cache: 'no-store' }); }
        catch (err) { throw new Error('The browser could not read that URL (usually CORS). Paste the response into x402 inspect instead.'); }
        const headers = {};
        res.headers.forEach(function (v, k) { headers[k.toLowerCase()] = v; });
        const body = await res.text();
        const extracted = X.extractRequirements({ status: res.status, headers: headers, body: body });
        U.render(res.status === 402 ? 'pass' : 'pending', 'HTTP ' + res.status, [
          ['url', url.toString()],
          ['requirements seen', String(extracted.requirements.length)],
          ['payTo', (extracted.requirements[0] && extracted.requirements[0].payTo) || '—']
        ], [{ level: 'note', text: 'A probe does not pay. Payment headers may be hidden unless the server exposes them.' }]);
      });
    },

    'paid-200-vs-402-diff': function () {
      U.onRun(function () {
        const diff = X.diffDumps(U.val('unpaid'), U.val('paid'));
        U.render('pending', 'Unpaid HTTP ' + (diff.leftStatus == null ? '—' : diff.leftStatus) + ' vs paid HTTP ' + (diff.rightStatus == null ? '—' : diff.rightStatus), [
          ['unpaid requirements', String(diff.leftCount)],
          ['paid requirements', String(diff.rightCount)]
        ], [{ level: 'note', text: 'A paid response usually drops the 402 challenge. If both sides still list payTo, the second paste may still be a challenge.' }]);
      });
    },

    'x402-scheme-up-eip3009': function () {
      U.onRun(function () {
        const rec = parsed().requirements[0];
        if (!rec) throw new Error('No requirement found.');
        const extra = rec.extra || {};
        const schemeOk = (rec.scheme || '').toLowerCase() === 'exact';
        U.render(schemeOk ? 'pass' : 'pending', schemeOk ? 'scheme exact' : ('scheme ' + (rec.scheme || 'missing')), [
          ['scheme', rec.scheme || '—'],
          ['extra.name', extra.name || '—'],
          ['extra.version', extra.version || '—'],
          ['asset', rec.asset || '—']
        ], [{ level: 'note', text: 'EIP-3009 transferWithAuthorization is the usual exact-scheme rail for USDC. This page checks the scheme and extra name/version. It does not build an authorization.' }]);
      });
    },

    'paywall-header-pretty': function () {
      U.onRun(function () {
        const dump = X.parseDump(U.val('raw'));
        const names = Object.keys(dump.headers);
        if (!names.length) throw new Error('No Name: value headers found. Put a blank line between headers and body.');
        U.render('pass', names.length + ' header(s)', [
          ['status', dump.status == null ? '—' : String(dump.status)]
        ], [U.table(['header', 'value'], names.map(function (name) { return [name, dump.headers[name]]; }))]);
      });
    },

    'multi-resource-price-compare': function () {
      U.onRun(function () {
        const chunks = U.val('raw').split(/\n\s*\n/).map(function (c) { return c.trim(); }).filter(Boolean);
        const all = [];
        chunks.forEach(function (chunk, i) {
          X.extractRequirements(X.parseDump(chunk)).requirements.forEach(function (rec) {
            all.push([String(i + 1), rec.resource || '', rec.network || '', rec.amount || '']);
          });
        });
        if (!all.length) throw new Error('No prices found. Separate challenges with a blank line.');
        U.render('pass', all.length + ' price row(s)', [], [U.table(['paste #', 'resource', 'network', 'amount'], all)]);
      });
    },

    'x402-llms-txt-finder': function () {
      U.onRun(async function () {
        const pasted = U.val('raw');
        let text = pasted;
        if (!text && U.val('url')) {
          const origin = new URL(U.val('url')).origin;
          U.busy('Fetching llms.txt…');
          try {
            const res = await fetch(origin + '/llms.txt', { mode: 'cors' });
            text = await res.text();
            if (!res.ok) throw new Error('HTTP ' + res.status);
          } catch (err) {
            throw new Error('Could not read ' + origin + '/llms.txt (' + err.message + '). Paste the file instead.');
          }
        }
        if (!text) throw new Error('Paste llms.txt or a site URL.');
        const hits = text.split('\n').filter(function (line) { return /402|x402|payment|payto/i.test(line); });
        U.render(hits.length ? 'pass' : 'pending', hits.length + ' matching line(s)', [
          ['lines', String(text.split('\n').length)]
        ], [U.table(['line'], (hits.length ? hits : ['(no 402/x402/payment mention)']).map(function (line) { return [line.slice(0, 240)]; }))]);
      });
    },

    'settlement-network-mismatch': function () {
      U.onRun(function () {
        const expected = U.val('expected') || 'base';
        const reqs = parsed().requirements;
        if (!reqs.length) throw new Error('No requirement to compare.');
        const mismatches = reqs.filter(function (r) { return (r.network || '').toLowerCase() !== expected.toLowerCase(); });
        U.render(mismatches.length ? 'fail' : 'pass', mismatches.length ? 'Network mismatch' : 'Networks match ' + expected, [
          ['expected', expected],
          ['seen', reqs.map(function (r) { return r.network || '—'; }).join(', ')]
        ]);
      });
    },

    'x402-client-checklist': function () {
      const ids = ['chk-402', 'chk-fields', 'chk-asset', 'chk-timeout', 'chk-cors', 'chk-pay', 'chk-retry'];
      function paint() {
        const open = ids.filter(function (id) { return !U.$(id).checked; });
        const el = U.$('summary');
        if (!open.length) { el.className = 'verdict pass'; el.textContent = 'Checklist complete'; }
        else { el.className = 'verdict pending'; el.textContent = open.length + ' item' + (open.length === 1 ? '' : 's') + ' still open'; }
      }
      if (globalThis.C2S) C2S.bindLive(ids, paint);
    }
  };

  const tool = document.body.getAttribute('data-tool');
  if (pages[tool]) pages[tool]();
})();
