'use strict';
(function (root) {
  const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  const TOKEN = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';
  const TOKEN_2022 = 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb';
  const METADATA = 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s';
  const PUMP = '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P';
  const WSOL = 'So11111111111111111111111111111111111111112';
  const BURN = {
    '1nc1nerator11111111111111111111111111111111': 'incinerator',
    '11111111111111111111111111111111': 'system program'
  };
  const RAYDIUM = {
    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM v4',
    'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C': 'Raydium CPMM',
    'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK': 'Raydium CLMM'
  };
  const METEORA = {
    'LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo': 'Meteora DLMM',
    'Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB': 'Meteora Dynamic AMM',
    'cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG': 'Meteora DAMM v2'
  };
  const DEFAULT_RPC = 'https://solana-rpc.publicnode.com';

  function decodeBase58(str) {
    if (str == null || str === '' || /[^1-9A-HJ-NP-Za-km-z]/.test(str)) return null;
    const bytes = [0];
    for (let i = 0; i < str.length; i++) {
      let carry = BASE58.indexOf(str[i]);
      if (carry < 0) return null;
      for (let j = 0; j < bytes.length; j++) {
        carry += bytes[j] * 58;
        bytes[j] = carry & 0xff;
        carry >>= 8;
      }
      while (carry > 0) {
        bytes.push(carry & 0xff);
        carry >>= 8;
      }
    }
    for (let k = 0; str[k] === '1' && k < str.length - 1; k++) bytes.push(0);
    return new Uint8Array(bytes.reverse());
  }

  function encodeBase58(bytes) {
    let zeros = 0;
    while (zeros < bytes.length && bytes[zeros] === 0) zeros++;
    const digits = [0];
    for (let i = zeros; i < bytes.length; i++) {
      let carry = bytes[i];
      for (let j = 0; j < digits.length; j++) {
        carry += digits[j] << 8;
        digits[j] = carry % 58;
        carry = (carry / 58) | 0;
      }
      while (carry > 0) {
        digits.push(carry % 58);
        carry = (carry / 58) | 0;
      }
    }
    let out = '1'.repeat(zeros);
    for (let k = digits.length - 1; k >= 0; k--) out += BASE58[digits[k]];
    return out;
  }

  function validPubkey(text) {
    const bytes = decodeBase58(String(text || '').trim());
    return !!(bytes && bytes.length === 32);
  }

  function assertRpc(url) {
    let parsed;
    try { parsed = new URL(String(url || '').trim()); }
    catch (err) { throw new Error('The RPC URL is not valid. Use an https:// Solana JSON-RPC endpoint.'); }
    if (parsed.protocol !== 'https:' && parsed.hostname !== 'localhost' && parsed.hostname !== '127.0.0.1') {
      throw new Error('Use an https:// RPC URL so the browser can call it.');
    }
    return parsed.toString();
  }

  async function rpc(url, method, params) {
    const endpoint = assertRpc(url);
    let res;
    try {
      res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: method, params: params })
      });
    } catch (err) {
      throw new Error('The RPC request did not complete. The endpoint may be rate-limiting this browser, blocking cross-origin calls, or offline.');
    }
    let payload = null;
    try { payload = await res.json(); } catch (err) { payload = null; }
    if (!res.ok) {
      const msg = payload && payload.error && payload.error.message;
      if (res.status === 403) {
        throw new Error('The RPC refused this browser' + (msg ? ' (' + msg + ')' : '') + '. https://api.mainnet-beta.solana.com often returns HTTP 403 to web pages. Try https://solana-rpc.publicnode.com.');
      }
      throw new Error(msg ? ('RPC error (HTTP ' + res.status + '): ' + msg) : ('The RPC returned HTTP ' + res.status + '.'));
    }
    if (!payload) throw new Error('The RPC response was not JSON.');
    if (payload.error) throw new Error('RPC error: ' + (payload.error.message || 'unknown error'));
    return payload.result;
  }

  function programName(owner) {
    if (owner === TOKEN) return 'SPL Token';
    if (owner === TOKEN_2022) return 'Token-2022';
    if (RAYDIUM[owner]) return RAYDIUM[owner];
    if (METEORA[owner]) return METEORA[owner];
    if (owner === PUMP) return 'pump.fun';
    if (owner === METADATA) return 'Metaplex metadata';
    return owner || 'unknown';
  }

  function classifyMint(info) {
    if (!info || typeof info !== 'object') return null;
    if (!Object.prototype.hasOwnProperty.call(info, 'mintAuthority')) return null;
    if (!Object.prototype.hasOwnProperty.call(info, 'freezeAuthority')) return null;
    const mintRevoked = info.mintAuthority === null;
    const freezeRevoked = info.freezeAuthority === null;
    return {
      pass: mintRevoked && freezeRevoked,
      mintRevoked: mintRevoked,
      freezeRevoked: freezeRevoked,
      mintAuthority: info.mintAuthority,
      freezeAuthority: info.freezeAuthority
    };
  }

  function extensions(info) {
    return (info && info.extensions) || [];
  }

  function extension(info, name) {
    return extensions(info).find(function (ext) { return ext && ext.extension === name; }) || null;
  }

  function transferFeeBps(info) {
    const ext = extension(info, 'transferFeeConfig');
    if (!ext || !ext.state) return null;
    const fee = ext.state.newerTransferFee || ext.state.olderTransferFee || {};
    if (fee.transferFeeBasisPoints == null) return null;
    return Number(fee.transferFeeBasisPoints);
  }

  function applyBps(rawAmount, bps) {
    let raw;
    try { raw = BigInt(String(rawAmount).trim() || '0'); }
    catch (err) { throw new Error('Amount must be an integer in base units.'); }
    const n = Number(bps);
    if (!Number.isFinite(n) || n < 0) throw new Error('Basis points must be a non-negative number.');
    const fee = (raw * BigInt(Math.round(n))) / 10000n;
    return { raw: raw.toString(), fee: fee.toString(), net: (raw - fee).toString(), bps: n };
  }

  function formatUnits(raw, decimals) {
    const dec = Number(decimals);
    const v = BigInt(raw);
    const sign = v < 0n ? '-' : '';
    const abs = v < 0n ? -v : v;
    const base = 10n ** BigInt(Number.isFinite(dec) && dec > 0 ? dec : 0);
    const whole = abs / base;
    let frac = (abs % base).toString().padStart(Number.isFinite(dec) && dec > 0 ? dec : 0, '0').replace(/0+$/, '');
    return sign + whole.toString() + (frac ? '.' + frac : '');
  }

  async function account(url, address, encoding) {
    if (!validPubkey(address)) throw new Error('That does not look like a Solana address (base58, 32 bytes).');
    const result = await rpc(url, 'getAccountInfo', [address.trim(), { encoding: encoding || 'jsonParsed' }]);
    return result && result.value;
  }

  async function mintAccount(url, mint) {
    const value = await account(url, mint, 'jsonParsed');
    if (!value) throw new Error('No account exists at that address on this cluster.');
    const parsed = value.data && value.data.parsed;
    const info = parsed && parsed.info;
    if (!parsed || parsed.type !== 'mint' || !info) {
      const err = new Error('The account exists, but it is not a parsed token mint (owner ' + (value.owner || 'unknown') + ').');
      err.value = value;
      throw err;
    }
    return { value: value, info: info, owner: value.owner, mint: mint.trim() };
  }

  async function tokenSupply(url, mint) {
    const result = await rpc(url, 'getTokenSupply', [mint.trim()]);
    return result && result.value;
  }

  async function largestAccounts(url, mint) {
    const result = await rpc(url, 'getTokenLargestAccounts', [mint.trim()]);
    return (result && result.value) || [];
  }

  async function multipleAccounts(url, addresses) {
    if (!addresses.length) return [];
    const result = await rpc(url, 'getMultipleAccounts', [addresses, { encoding: 'jsonParsed' }]);
    return (result && result.value) || [];
  }

  async function signatures(url, address, limit) {
    return await rpc(url, 'getSignaturesForAddress', [address.trim(), { limit: limit || 20 }]) || [];
  }

  async function transaction(url, signature) {
    return await rpc(url, 'getTransaction', [signature, { encoding: 'jsonParsed', maxSupportedTransactionVersion: 0 }]);
  }

  async function sha256(bytes) {
    const hash = await crypto.subtle.digest('SHA-256', bytes);
    return new Uint8Array(hash);
  }

  async function deriveCandidate(seeds, programBytes, bump) {
    const parts = [];
    seeds.forEach(function (seed) { parts.push(seed); });
    parts.push(new Uint8Array([bump]));
    parts.push(programBytes);
    parts.push(new TextEncoder().encode('ProgramDerivedAddress'));
    let len = 0;
    parts.forEach(function (p) { len += p.length; });
    const buf = new Uint8Array(len);
    let off = 0;
    parts.forEach(function (p) { buf.set(p, off); off += p.length; });
    return encodeBase58(await sha256(buf));
  }

  async function findExistingPda(url, seeds, programId, maxBumps) {
    const programBytes = decodeBase58(programId);
    if (!programBytes || programBytes.length !== 32) throw new Error('Program id is not a pubkey.');
    const tries = maxBumps || 8;
    for (let bump = 255; bump > 255 - tries; bump--) {
      const address = await deriveCandidate(seeds, programBytes, bump);
      const value = await account(url, address, 'base64');
      if (value) return { address: address, bump: bump, value: value };
    }
    return null;
  }

  function readBorshString(bytes, offset) {
    if (offset + 4 > bytes.length) throw new Error('Metadata string is truncated.');
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const len = view.getUint32(offset, true);
    if (len > 500 || offset + 4 + len > bytes.length) throw new Error('Metadata string length looks wrong.');
    const text = new TextDecoder().decode(bytes.slice(offset + 4, offset + 4 + len)).replace(/\0+$/g, '');
    return { text: text, offset: offset + 4 + len };
  }

  function parseMetadata(bytes) {
    if (!bytes || bytes.length < 65) throw new Error('Metadata account is shorter than the header.');
    const updateAuthority = encodeBase58(bytes.slice(1, 33));
    const mint = encodeBase58(bytes.slice(33, 65));
    let cursor = readBorshString(bytes, 65);
    const name = cursor.text;
    cursor = readBorshString(bytes, cursor.offset);
    const symbol = cursor.text;
    cursor = readBorshString(bytes, cursor.offset);
    const uri = cursor.text;
    if (cursor.offset + 2 > bytes.length) throw new Error('Metadata fee field is truncated.');
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const sellerFee = view.getUint16(cursor.offset, true);
    let off = cursor.offset + 2;
    const hasCreators = bytes[off];
    off += 1;
    if (hasCreators === 1) {
      if (off + 4 > bytes.length) throw new Error('Creator list is truncated.');
      const count = view.getUint32(off, true);
      off += 4 + count * 34;
    }
    if (off + 1 >= bytes.length) {
      return { updateAuthority: updateAuthority, mint: mint, name: name, symbol: symbol, uri: uri, sellerFeeBasisPoints: sellerFee, isMutable: null, primarySale: null };
    }
    const primarySale = bytes[off] === 1;
    const isMutable = bytes[off + 1] === 1;
    return {
      key: bytes[0],
      updateAuthority: updateAuthority,
      mint: mint,
      name: name,
      symbol: symbol,
      uri: uri,
      sellerFeeBasisPoints: sellerFee,
      primarySale: primarySale,
      isMutable: isMutable
    };
  }

  function decodeBase64(b64) {
    const bin = atob(b64);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i) & 0xff;
    return out;
  }

  async function loadMetadata(url, mint) {
    const mintBytes = decodeBase58(mint.trim());
    const found = await findExistingPda(url, [new TextEncoder().encode('metadata'), decodeBase58(METADATA), mintBytes], METADATA, 6);
    if (!found) throw new Error('No Metaplex metadata account in the first PDA bumps. The mint may have no metadata.');
    const data = found.value.data;
    const b64 = Array.isArray(data) ? data[0] : '';
    const parsed = parseMetadata(decodeBase64(b64));
    parsed.address = found.address;
    parsed.bump = found.bump;
    return parsed;
  }

  function parsePumpCurve(bytes) {
    if (!bytes || bytes.length < 49) return null;
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    return {
      virtualTokenReserves: view.getBigUint64(8, true).toString(),
      virtualSolReserves: view.getBigUint64(16, true).toString(),
      realTokenReserves: view.getBigUint64(24, true).toString(),
      realSolReserves: view.getBigUint64(32, true).toString(),
      tokenTotalSupply: view.getBigUint64(40, true).toString(),
      complete: bytes[48] !== 0
    };
  }

  function clusterSlots(sigs) {
    const counts = new Map();
    (sigs || []).forEach(function (sig) {
      const slot = sig && sig.slot;
      if (slot == null) return;
      counts.set(slot, (counts.get(slot) || 0) + 1);
    });
    let best = null;
    counts.forEach(function (count, slot) {
      if (!best || count > best.count) best = { slot: slot, count: count };
    });
    return best;
  }

  function freezeRisk(info) {
    const reasons = [];
    let score = 0;
    if (info.freezeAuthority) {
      score += 50;
      reasons.push('freezeAuthority is set, so the authority can freeze token accounts');
    }
    const state = extension(info, 'defaultAccountState');
    if (state && state.state && String(state.state.state || state.state).toLowerCase().indexOf('frozen') >= 0) {
      score += 40;
      reasons.push('Token-2022 default account state is frozen');
    }
    if (extension(info, 'permanentDelegate')) {
      score += 20;
      reasons.push('A permanent delegate can transfer or burn tokens without the holder');
    }
    const bps = transferFeeBps(info);
    if (bps) {
      score += bps >= 1000 ? 25 : 10;
      reasons.push('Transfer fee is ' + bps + ' bps');
    }
    if (extension(info, 'nonTransferable')) {
      score += 40;
      reasons.push('nonTransferable extension is present');
    }
    let level = 'pass';
    let label = 'LOW — no freeze-style control detected';
    if (score >= 40) { level = 'fail'; label = 'HIGH — a freeze or transfer block is possible'; }
    else if (score > 0) { level = 'warn'; label = 'MEDIUM — a control exists, but it is not a hard freeze'; }
    return { score: score, level: level, label: label, reasons: reasons };
  }

  function honeypotSignals(info) {
    const flags = [];
    if (info.freezeAuthority) flags.push({ level: 'high', text: 'freezeAuthority is set' });
    if (info.mintAuthority) flags.push({ level: 'medium', text: 'mintAuthority is set (supply can increase)' });
    if (extension(info, 'nonTransferable')) flags.push({ level: 'high', text: 'nonTransferable extension' });
    if (extension(info, 'permanentDelegate')) flags.push({ level: 'high', text: 'permanentDelegate extension' });
    const bps = transferFeeBps(info);
    if (bps != null && bps >= 1000) flags.push({ level: 'high', text: 'transfer fee ' + bps + ' bps' });
    else if (bps) flags.push({ level: 'medium', text: 'transfer fee ' + bps + ' bps' });
    const high = flags.some(function (f) { return f.level === 'high'; });
    return { flags: flags, high: high, bps: bps };
  }

  function topShare(accounts, supplyRaw) {
    let supply = 0n;
    try { supply = BigInt(supplyRaw || '0'); } catch (err) { supply = 0n; }
    const rows = (accounts || []).slice(0, 10).map(function (acct) {
      let amount = 0n;
      try { amount = BigInt(acct.amount || '0'); } catch (err) { amount = 0n; }
      const pct = supply > 0n ? Number((amount * 10000n) / supply) / 100 : 0;
      return { address: acct.address, amount: amount.toString(), pct: pct };
    });
    let sum = 0n;
    rows.forEach(function (row) { sum += BigInt(row.amount); });
    const totalPct = supply > 0n ? Number((sum * 10000n) / supply) / 100 : 0;
    return { rows: rows, totalPct: totalPct, supply: supply.toString() };
  }

  function burnedShare(owners, amounts, supplyRaw) {
    let supply = 0n;
    try { supply = BigInt(supplyRaw || '0'); } catch (err) { supply = 0n; }
    let burned = 0n;
    const rows = owners.map(function (owner, i) {
      const amount = BigInt(amounts[i] || '0');
      const label = BURN[owner] || '';
      if (label) burned += amount;
      return { owner: owner, amount: amount.toString(), label: label || 'unlisted wallet or program' };
    });
    const pct = supply > 0n ? Number((burned * 10000n) / supply) / 100 : 0;
    return { rows: rows, burnedPct: pct, burned: pct >= 95 };
  }

  function $(id) { return document.getElementById(id); }

  function render(kind, title, rows, notes) {
    const result = $('result');
    if (!result) return;
    result.hidden = false;
    const verdict = $('verdict');
    verdict.className = 'verdict ' + (kind || 'pending');
    verdict.textContent = title;
    const kv = $('kv');
    kv.replaceChildren();
    (rows || []).forEach(function (row) {
      const dt = document.createElement('dt');
      dt.textContent = row[0];
      const dd = document.createElement('dd');
      dd.textContent = row[1] == null ? '' : String(row[1]);
      kv.appendChild(dt);
      kv.appendChild(dd);
    });
    const extra = $('extra');
    extra.replaceChildren();
    (notes || []).forEach(function (note) {
      if (note && note.nodeType) { extra.appendChild(note); return; }
      const p = document.createElement('p');
      p.className = 'banner ' + ((note && note.level) || 'note');
      p.textContent = note && note.text ? note.text : String(note || '');
      extra.appendChild(p);
    });
    const lines = (rows || []).map(function (row) { return row[0] + ': ' + row[1]; });
    (notes || []).forEach(function (note) {
      if (note && note.text) lines.push('note: ' + note.text);
    });
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
      $('status').textContent = message || 'Asking the RPC…';
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

  function rpcValue() {
    return ($('rpc') && $('rpc').value.trim()) || DEFAULT_RPC;
  }

  function onRun(fn) {
    if (!$('go')) return;
    $('go').addEventListener('click', function () {
      busy('Working…');
      Promise.resolve()
        .then(fn)
        .catch(function (err) { fail(err && err.message ? err.message : 'Something went wrong talking to the RPC.'); });
    });
  }

  root.Solana = {
    DEFAULT_RPC: DEFAULT_RPC,
    TOKEN: TOKEN,
    TOKEN_2022: TOKEN_2022,
    METADATA: METADATA,
    PUMP: PUMP,
    WSOL: WSOL,
    BURN: BURN,
    RAYDIUM: RAYDIUM,
    METEORA: METEORA,
    decodeBase58: decodeBase58,
    encodeBase58: encodeBase58,
    validPubkey: validPubkey,
    rpc: rpc,
    programName: programName,
    classifyMint: classifyMint,
    extension: extension,
    transferFeeBps: transferFeeBps,
    applyBps: applyBps,
    formatUnits: formatUnits,
    account: account,
    mintAccount: mintAccount,
    tokenSupply: tokenSupply,
    largestAccounts: largestAccounts,
    multipleAccounts: multipleAccounts,
    signatures: signatures,
    transaction: transaction,
    loadMetadata: loadMetadata,
    parseMetadata: parseMetadata,
    parsePumpCurve: parsePumpCurve,
    decodeBase64: decodeBase64,
    findExistingPda: findExistingPda,
    clusterSlots: clusterSlots,
    freezeRisk: freezeRisk,
    honeypotSignals: honeypotSignals,
    topShare: topShare,
    burnedShare: burnedShare,
    render: render,
    fail: fail,
    busy: busy,
    table: table,
    rpcValue: rpcValue,
    onRun: onRun,
    $: $
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
