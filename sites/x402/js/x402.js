'use strict';
(function (root) {
  const FIELD_MAP = {
    network: 'network',
    chain: 'network',
    payto: 'payTo',
    pay_to: 'payTo',
    recipient: 'payTo',
    asset: 'asset',
    token: 'asset',
    amount: 'amount',
    maxamountrequired: 'amount',
    max_amount_required: 'amount',
    maxamount: 'amount'
  };

  const NETWORKS = {
    base: { chainId: 8453, usdc: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913' },
    'base-sepolia': { chainId: 84532, usdc: '0x036cbd53842c5426634e7929541ec2318f3dcf7e' },
    ethereum: { chainId: 1, usdc: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' },
    mainnet: { chainId: 1, usdc: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' },
    avalanche: { chainId: 43114, usdc: '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e' },
    polygon: { chainId: 137, usdc: '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359' },
    solana: { chainId: null, usdc: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v' }
  };

  const SAMPLE = [
    'HTTP/1.1 402 Payment Required',
    'content-type: application/json',
    'payment-required: eyJ4NDAyVmVyc2lvbiI6MSwibmV0d29yayI6ImJhc2UiLCJwYXlUbyI6IjB4MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMSIsImFzc2V0IjoiMHg4MzM1ODlmQ0Q2ZURiNkUwOGY0YzdDMzJENGY3MWI1NGJkQTAyOTEzIiwiYW1vdW50IjoiMTAwMCIsIm1heFRpbWVvdXRTZWNvbmRzIjo2MCwic2NoZW1lIjoiZXhhY3QifQ==',
    '',
    '{"x402Version":1,"accepts":[{"scheme":"exact","network":"base-sepolia","maxAmountRequired":"2500","resource":"https://example.com/report","payTo":"0x2222222222222222222222222222222222222222","asset":"0x036CbD53842c5426634e7929541eC2318f3dCF7e","mimeType":"application/json","maxTimeoutSeconds":30}]}'
  ].join('\n');

  function tryJson(text) {
    if (typeof text !== 'string') return null;
    const trimmed = text.trim();
    if (!trimmed || (trimmed[0] !== '{' && trimmed[0] !== '[')) return null;
    try { return JSON.parse(trimmed); } catch (err) { return null; }
  }

  function tryB64Json(value) {
    const cleaned = String(value || '').replace(/\s+/g, '');
    if (cleaned.length < 8 || /[^A-Za-z0-9+/=_-]/.test(cleaned)) return null;
    let b64 = cleaned.replace(/-/g, '+').replace(/_/g, '/');
    while (b64.length % 4) b64 += '=';
    try {
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i) & 0xff;
      return tryJson(new TextDecoder().decode(bytes));
    } catch (err) { return null; }
  }

  function parseDump(raw) {
    const text = String(raw || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const trimmed = text.trim();
    if (!trimmed) return { status: null, headers: {}, body: '' };
    if (trimmed[0] === '{' || trimmed[0] === '[') return { status: null, headers: {}, body: trimmed };
    let headerPart = text;
    let body = '';
    const split = text.search(/\n[ \t]*\n/);
    if (split >= 0) {
      headerPart = text.slice(0, split);
      body = text.slice(split).replace(/^\n+/, '');
    }
    const headers = {};
    let status = null;
    headerPart.split('\n').forEach(function (line) {
      const statusMatch = line.match(/^HTTP\/\d(?:\.\d)?\s+(\d{3})/i);
      if (statusMatch) { status = Number(statusMatch[1]); return; }
      const headerMatch = line.match(/^([^:\s][^:]*):\s*(.*)$/);
      if (!headerMatch) return;
      const name = headerMatch[1].trim().toLowerCase();
      const value = headerMatch[2].trim();
      headers[name] = Object.prototype.hasOwnProperty.call(headers, name) ? headers[name] + ', ' + value : value;
    });
    return { status: status, headers: headers, body: body.trim() };
  }

  function collect(node, found, source) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(function (item) { collect(item, found, source); });
      return;
    }
    const rec = { source: source, extra: node.extra && typeof node.extra === 'object' ? node.extra : null };
    let any = false;
    Object.keys(node).forEach(function (key) {
      const mapped = FIELD_MAP[String(key).toLowerCase()];
      if (!mapped) return;
      const val = node[key];
      if (val == null || typeof val === 'object') return;
      rec[mapped] = String(val);
      any = true;
    });
    ['scheme', 'resource', 'mimeType', 'maxTimeoutSeconds', 'description'].forEach(function (key) {
      if (node[key] != null && typeof node[key] !== 'object') rec[key] = String(node[key]);
    });
    if (any) found.push(rec);
    Object.keys(node).forEach(function (key) {
      if (node[key] && typeof node[key] === 'object') collect(node[key], found, source);
    });
  }

  function dedupe(found) {
    const map = new Map();
    found.forEach(function (rec) {
      const key = [rec.network || '', rec.payTo || '', rec.asset || '', rec.amount || '', rec.resource || ''].join('|').toLowerCase();
      if (!key.replace(/\|/g, '')) return;
      const prev = map.get(key);
      if (!prev) { map.set(key, rec); return; }
      if (prev.source.indexOf(rec.source) === -1) prev.source += ', ' + rec.source;
    });
    return Array.from(map.values());
  }

  function extractRequirements(parsed) {
    const found = [];
    const headers = parsed.headers || {};
    const loose = { source: 'headers' };
    const looseNames = [];
    Object.keys(headers).forEach(function (name) {
      const value = headers[name];
      const asJson = tryJson(value) || tryB64Json(value);
      if (asJson) { collect(asJson, found, 'header ' + name); return; }
      const mapped = FIELD_MAP[name] || FIELD_MAP[name.replace(/^x-/, '')];
      if (mapped && value && loose[mapped] == null) {
        loose[mapped] = value;
        looseNames.push(name);
      }
    });
    if (looseNames.length) {
      loose.source = 'headers ' + looseNames.join(', ');
      found.push(loose);
    }
    const bodyJson = tryJson(parsed.body || '');
    if (bodyJson) collect(bodyJson, found, 'body');
    return { status: parsed.status, requirements: dedupe(found), headers: headers, body: parsed.body || '' };
  }

  function formatUnits(amount, decimals) {
    const dec = Number(decimals);
    const v = BigInt(String(amount).trim());
    const base = 10n ** BigInt(Number.isFinite(dec) && dec >= 0 ? dec : 6);
    const whole = v / base;
    const frac = (v % base).toString().padStart(dec || 6, '0').replace(/0+$/, '');
    return whole.toString() + (frac ? '.' + frac : '');
  }

  function networkInfo(name) {
    if (!name) return null;
    return NETWORKS[String(name).toLowerCase()] || null;
  }

  function isHexAddress(value) {
    return /^0x[0-9a-fA-F]{40}$/.test(String(value || ''));
  }

  function timeoutVerdict(seconds) {
    const n = Number(seconds);
    if (!Number.isFinite(n)) return { kind: 'fail', label: 'maxTimeoutSeconds is missing or not a number' };
    if (n < 5) return { kind: 'warn', label: 'Timeout is under 5 seconds' };
    if (n > 3600) return { kind: 'warn', label: 'Timeout is over an hour' };
    return { kind: 'pass', label: 'Timeout is in a normal window' };
  }

  function classifyResponse(extracted) {
    const reqs = extracted.requirements || [];
    const hasX402 = reqs.some(function (r) { return r.payTo || r.asset || r.network; });
    if (extracted.status === 402 && hasX402) return { kind: 'pass', label: 'x402-style 402' };
    if (extracted.status === 402) return { kind: 'warn', label: 'Plain HTTP 402 without payment fields' };
    if (hasX402) return { kind: 'pending', label: 'Payment fields without an HTTP 402 status line' };
    return { kind: 'fail', label: 'No 402 and no payment fields' };
  }

  function diffDumps(a, b) {
    const left = extractRequirements(parseDump(a));
    const right = extractRequirements(parseDump(b));
    return {
      leftStatus: left.status,
      rightStatus: right.status,
      leftCount: left.requirements.length,
      rightCount: right.requirements.length,
      left: left.requirements,
      right: right.requirements
    };
  }

  root.X402 = {
    SAMPLE: SAMPLE,
    NETWORKS: NETWORKS,
    parseDump: parseDump,
    extractRequirements: extractRequirements,
    formatUnits: formatUnits,
    networkInfo: networkInfo,
    isHexAddress: isHexAddress,
    timeoutVerdict: timeoutVerdict,
    classifyResponse: classifyResponse,
    diffDumps: diffDumps,
    tryJson: tryJson
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
