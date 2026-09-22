'use strict';
(function () {
  const E = globalThis.Evm;
  const U = globalThis.SiteUI;
  if (!E || !U || !document.body) return;
  const $ = U.$;

  if ($('chain') && $('rpc')) {
    $('chain').addEventListener('change', function () { $('rpc').value = $('chain').value; });
  }

  function rpc() { return U.val('rpc') || 'https://ethereum.publicnode.com'; }

  async function loadInput() {
    const raw = U.val('tx');
    const hex = E.normalizeHex(raw);
    if (!hex) throw new Error('Paste a transaction hash or even-length hex calldata.');
    if (!E.isTxHash(hex)) return { input: '0x' + hex, tx: null };
    U.busy('Loading the transaction…');
    const tx = await E.getTransaction(rpc(), '0x' + hex);
    return { input: tx.input || tx.data || '0x', tx: tx };
  }

  function execRows(decoded, tx) {
    const rows = [];
    if (tx) {
      rows.push(['tx hash', tx.hash || '']);
      rows.push(['from', tx.from || '']);
      rows.push(['safe (tx.to)', tx.to || '']);
      if (tx.value) rows.push(['outer value', E.formatWei(BigInt(tx.value).toString())]);
    }
    rows.push(['selector', decoded.selector]);
    rows.push(['function', decoded.name]);
    rows.push(['calldata bytes', String(decoded.byteLength)]);
    if (decoded.recognized && decoded.to) {
      rows.push(['to', decoded.to]);
      rows.push(['value', E.formatWei(decoded.valueWei)]);
      rows.push(['data length', decoded.dataLength + ' bytes']);
      rows.push(['data selector', decoded.dataSelector || '(under 4 bytes)']);
      rows.push(['operation', decoded.operation + ' (' + decoded.operationName + ')']);
      rows.push(['safeTxGas', decoded.safeTxGas]);
      rows.push(['baseGas', decoded.baseGas]);
      rows.push(['gasPrice', decoded.gasPrice]);
      rows.push(['gasToken', decoded.gasToken]);
      rows.push(['refundReceiver', decoded.refundReceiver]);
      rows.push(['signatures length', decoded.signaturesLength + ' bytes']);
    }
    return rows;
  }

  function notes(decoded) {
    return (decoded.warnings || []).map(function (text) { return { level: 'warn', text: text }; });
  }

  async function safeView(to, data) {
    const result = await E.rpc(rpc(), 'eth_call', [{ to: to, data: data }, 'latest']);
    return result;
  }

  const pages = {
    'safe-mech-decode': function () {
      if ($('example')) $('example').addEventListener('click', function () { $('tx').value = E.EXAMPLE; $('go').click(); });
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeExecTransaction(loaded.input);
        if (!decoded.ok) throw new Error(decoded.error || 'Could not decode.');
        const kind = decoded.recognized ? 'pass' : 'pending';
        U.render(kind, decoded.recognized ? 'Decoded execTransaction' : 'Selector noted, layout not execTransaction', execRows(decoded, loaded.tx), notes(decoded).concat([
          { level: 'note', text: 'A mech is often just the outer from. The delivered payload is the inner data. This does not check signatures or mech registries.' }
        ]));
      });
    },

    'safe-exec-transaction-decode': function () {
      if ($('example')) $('example').addEventListener('click', function () { $('tx').value = E.EXAMPLE; $('go').click(); });
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeExecTransaction(loaded.input);
        if (!decoded.ok) throw new Error(decoded.error || 'Could not decode.');
        if (!decoded.recognized) {
          U.render('fail', 'Not an execTransaction payload', execRows(decoded, loaded.tx), notes(decoded));
          return;
        }
        U.render(decoded.operationName === 'DELEGATECALL' ? 'fail' : 'pass', 'execTransaction ' + decoded.operationName, execRows(decoded, loaded.tx), notes(decoded));
      });
    },

    'gnosis-safe-multisig-summary': function () {
      U.onRun(async function () {
        const safe = U.val('safe');
        if (!/^0x[0-9a-fA-F]{40}$/.test(safe)) throw new Error('Paste the Safe address (0x and 40 hex digits).');
        const [ownersRaw, thresholdRaw, nonceRaw, versionRaw, guardRaw] = await Promise.all([
          safeView(safe, '0xa0e67e2b'),
          safeView(safe, '0xe75235b8'),
          safeView(safe, '0xaffed0e0'),
          safeView(safe, '0xffa1ad74'),
          safeView(safe, '0xc9106389')
        ]);
        const owners = E.decodeAddressArray(ownersRaw);
        const threshold = E.decodeUintWord(thresholdRaw);
        const nonce = E.decodeUintWord(nonceRaw);
        const guard = E.decodeAddressWord(guardRaw);
        let version = '';
        try {
          const hex = E.normalizeHex(versionRaw);
          if (hex && hex.length >= 128) {
            const len = Number(BigInt('0x' + hex.slice(64, 128)));
            version = new TextDecoder().decode(Uint8Array.from(hex.slice(128, 128 + len * 2).match(/../g).map(function (b) { return parseInt(b, 16); })));
          }
        } catch (err) { version = ''; }
        U.render('pass', threshold + ' of ' + owners.length + ' owners', [
          ['safe', safe],
          ['threshold', threshold],
          ['owners', String(owners.length)],
          ['nonce', nonce],
          ['version', version || '(unparsed)'],
          ['guard', E.zeroAddress(guard) ? 'none' : guard]
        ], [U.table(['#', 'owner'], owners.map(function (o, i) { return [String(i + 1), o]; }))]);
      });
    },

    'safe-nonce-gap-check': function () {
      U.onRun(async function () {
        const safe = U.val('safe');
        if (!/^0x[0-9a-fA-F]{40}$/.test(safe)) throw new Error('Paste the Safe address.');
        const nonce = Number(E.decodeUintWord(await safeView(safe, '0xaffed0e0')));
        const seen = U.val('seen');
        if (!seen) {
          U.render('pending', 'On-chain nonce is ' + nonce, [['safe', safe], ['nonce', String(nonce)]]);
          return;
        }
        const expected = Number(seen);
        if (!Number.isFinite(expected)) throw new Error('Expected nonce must be an integer.');
        const gap = nonce - expected;
        const kind = gap === 0 ? 'pass' : 'warn';
        U.render(kind, gap === 0 ? 'Nonce matches' : ('Gap of ' + gap), [
          ['safe', safe],
          ['on-chain nonce', String(nonce)],
          ['expected', String(expected)],
          ['gap', String(gap)]
        ], [{ level: 'note', text: 'A positive gap means the Safe executed transactions you have not accounted for. A negative gap means your number is ahead of the chain you queried.' }]);
      });
    },

    'safe-owner-threshold-card': function () {
      U.onRun(async function () {
        const safe = U.val('safe');
        if (!/^0x[0-9a-fA-F]{40}$/.test(safe)) throw new Error('Paste the Safe address.');
        const owners = E.decodeAddressArray(await safeView(safe, '0xa0e67e2b'));
        const threshold = Number(E.decodeUintWord(await safeView(safe, '0xe75235b8')));
        const kind = threshold <= 1 ? 'warn' : 'pass';
        U.render(kind, threshold + ' of ' + owners.length, [
          ['safe', safe],
          ['threshold', String(threshold)],
          ['owners', String(owners.length)]
        ], [U.table(['owner'], owners.map(function (o) { return [o]; })),
          threshold <= 1 ? { level: 'warn', text: 'Threshold 1 means any single owner can execute.' } : { level: 'note', text: 'This is the on-chain threshold, not a policy judgment.' }]);
      });
    },

    'safe-module-list': function () {
      U.onRun(async function () {
        const safe = U.val('safe');
        if (!/^0x[0-9a-fA-F]{40}$/.test(safe)) throw new Error('Paste the Safe address.');
        const start = (U.val('start') || '0x0000000000000000000000000000000000000001').toLowerCase().replace(/^0x/, '').padStart(64, '0');
        const size = (Number(U.val('size') || '20') || 20).toString(16).padStart(64, '0');
        const data = '0xcc2f8452' + start + size;
        const raw = await safeView(safe, data);
        const hex = E.normalizeHex(raw);
        const array = E.decodeAddressArray(raw);
        let next = '';
        if (hex && hex.length >= 128) {
          const second = hex.slice(64, 128);
          next = '0x' + second.slice(24);
        }
        U.render(array.length ? 'warn' : 'pass', array.length ? (array.length + ' module(s) in this page') : 'No modules in this page', [
          ['safe', safe],
          ['next cursor', next]
        ], [array.length ? U.table(['module'], array.map(function (m) { return [m]; })) : { level: 'note', text: 'An empty page does not prove modules were never enabled if you started the cursor past them.' }]);
      });
    },

    'safe-guard-status': function () {
      U.onRun(async function () {
        const safe = U.val('safe');
        if (!/^0x[0-9a-fA-F]{40}$/.test(safe)) throw new Error('Paste the Safe address.');
        const guard = E.decodeAddressWord(await safeView(safe, '0xc9106389'));
        const none = E.zeroAddress(guard);
        U.render(none ? 'pending' : 'pass', none ? 'No guard is set' : 'Guard is set', [
          ['safe', safe],
          ['guard', none ? '0x0000000000000000000000000000000000000000' : guard]
        ], [{ level: 'note', text: 'A guard can block execTransaction. None means there is no on-chain guard contract. This does not audit the guard’s code.' }]);
      });
    },

    'eth-tx-input-decoder': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const hex = E.normalizeHex(loaded.input);
        const selector = '0x' + hex.slice(0, 8);
        const words = E.dumpWords(loaded.input);
        U.render('pending', (E.SELECTORS[selector] || 'unknown') + ' · ' + words.length + ' words', [
          ['selector', selector],
          ['signature', E.SELECTORS[selector] || 'not in the local list'],
          ['bytes', String(hex.length / 2)]
        ], [U.table(['#', 'as address', 'as uint'], words.map(function (w) {
          return [String(w.index), w.address || '', w.uint];
        }))]);
      });
    },

    'calldata-4byte-lookup': function () {
      U.onRun(async function () {
        let selector = U.val('selector').toLowerCase();
        if (!selector && U.val('tx')) {
          const loaded = await loadInput();
          selector = '0x' + E.normalizeHex(loaded.input).slice(0, 8);
        }
        if (!/^0x[0-9a-f]{8}$/.test(selector)) throw new Error('Need a 4-byte selector, 0x plus 8 hex digits.');
        const local = E.SELECTORS[selector] || '';
        let remote = '';
        try {
          const res = await fetch('https://www.4byte.directory/api/v1/signatures/?hex_signature=' + selector);
          if (res.ok) {
            const body = await res.json();
            remote = ((body.results || []).map(function (row) { return row.text_signature; }).slice(0, 8)).join(' | ');
          }
        } catch (err) {
          remote = '';
        }
        U.render(local || remote ? 'pass' : 'pending', local || remote || 'No match', [
          ['selector', selector],
          ['local', local || '—'],
          ['4byte.directory', remote || 'not loaded (CORS or no hit)']
        ]);
      });
    },

    'erc20-transfer-decode': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeStaticCall(loaded.input, 'erc20');
        if (!decoded.ok) throw new Error(decoded.error);
        const decimals = Number(U.val('decimals') || '18');
        function human(raw) {
          if (raw == null) return '';
          const v = BigInt(raw);
          const base = 10n ** BigInt(Number.isFinite(decimals) ? decimals : 18);
          const frac = (v % base).toString().padStart(decimals, '0').replace(/0+$/, '');
          return (v / base).toString() + (frac ? '.' + frac : '');
        }
        if (!decoded.amount) {
          U.render('fail', 'Not a transfer, transferFrom, or approve', [['selector', decoded.selector], ['name', decoded.name]]);
          return;
        }
        U.render('pass', decoded.name, [
          ['selector', decoded.selector],
          ['from', decoded.from || '(msg.sender)'],
          ['to', decoded.to || ''],
          ['raw amount', decoded.amount],
          ['scaled', human(decoded.amount)],
          ['decimals used', String(decimals)]
        ], decoded.shared ? [{ level: 'warn', text: 'transferFrom(address,address,uint256) is also the ERC-721 selector. The third word may be a token id.' }] : []);
      });
    },

    'erc721-transfer-decode': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeStaticCall(loaded.input, 'erc721');
        if (!decoded.ok) throw new Error(decoded.error);
        if (!decoded.tokenId) {
          U.render('fail', 'Not an ERC-721 transfer selector', [['selector', decoded.selector], ['name', decoded.name]]);
          return;
        }
        U.render(decoded.shared ? 'warn' : 'pass', decoded.name, [
          ['from', decoded.from],
          ['to', decoded.to],
          ['tokenId or amount', decoded.tokenId],
          ['extra bytes argument', decoded.hasData ? 'yes' : 'no']
        ], decoded.shared ? [{ level: 'warn', text: 'This selector is shared with ERC-20 transferFrom. Confirm the target is an NFT.' }] : []);
      });
    },

    'internal-tx-trace-summary': function () {
      U.onRun(async function () {
        const hash = U.val('tx');
        if (!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('Paste a 32-byte transaction hash.');
        const receipt = await E.getReceipt(rpc(), hash);
        let traceNote = { level: 'note', text: 'debug_traceTransaction was not requested.' };
        const rows = [
          ['status', receipt.status === '0x1' ? 'success' : String(receipt.status)],
          ['block', receipt.blockNumber ? BigInt(receipt.blockNumber).toString() : ''],
          ['gas used', receipt.gasUsed ? BigInt(receipt.gasUsed).toString() : ''],
          ['logs', String((receipt.logs || []).length)],
          ['to', receipt.to || '']
        ];
        if ($('trace') && $('trace').checked) {
          try {
            const trace = await E.rpc(rpc(), 'debug_traceTransaction', [hash, { tracer: 'callTracer' }]);
            const calls = [];
            function walk(node, depth) {
              if (!node || calls.length > 30) return;
              calls.push([String(depth), node.type || '', node.to || '', node.error || '', node.input ? String(node.input).slice(0, 10) : '']);
              (node.calls || []).forEach(function (child) { walk(child, depth + 1); });
            }
            walk(trace, 0);
            traceNote = { level: 'note', text: 'callTracer returned ' + calls.length + ' frames (capped).' };
            U.render(receipt.status === '0x1' ? 'pass' : 'fail', 'Receipt plus call trace', rows, [U.table(['depth', 'type', 'to', 'error', 'selector'], calls), traceNote]);
            return;
          } catch (err) {
            traceNote = { level: 'warn', text: 'Trace failed: ' + err.message + ' Public RPCs often disable debug methods.' };
          }
        }
        U.render(receipt.status === '0x1' ? 'pass' : 'fail', 'Receipt summary', rows, [traceNote]);
      });
    },

    'safe-event-log-parser': function () {
      U.onRun(async function () {
        const hash = U.val('tx');
        if (!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('Paste a transaction hash.');
        const receipt = await E.getReceipt(rpc(), hash);
        const parsed = E.parseSafeLogs(receipt.logs);
        const known = parsed.filter(function (row) { return row.name !== 'unknown'; });
        U.render(known.length ? 'pass' : 'pending', known.length + ' known Safe event(s)', [
          ['logs', String(parsed.length)],
          ['status', receipt.status || '']
        ], [U.table(['log', 'name', 'address'], parsed.map(function (row) {
          return [String(row.index), row.name, row.address];
        }))]);
      });
    },

    'mech-job-id-from-tx': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeExecTransaction(loaded.input);
        if (!decoded.ok || !decoded.recognized) throw new Error('Need an execTransaction payload to look for an inner id.');
        const candidates = E.jobIdCandidates(decoded.dataHex);
        U.render('pending', candidates.length ? 'First inner word as a candidate id' : 'Inner data is shorter than 32 bytes', [
          ['to', decoded.to],
          ['data selector', decoded.dataSelector || ''],
          ['data length', String(decoded.dataLength)],
          ['candidate hex', candidates[0] ? candidates[0].hex : ''],
          ['candidate uint', candidates[0] ? candidates[0].uint : '']
        ], [{ level: 'note', text: 'Olas mech request ids are not one ABI across versions. This is the first 32-byte word of inner data, not a registry lookup.' }]);
      });
    },

    'deliver-payload-size': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeExecTransaction(loaded.input);
        const length = decoded.recognized ? decoded.dataLength : (E.normalizeHex(loaded.input).length / 2);
        const klass = E.payloadClass(decoded.recognized ? decoded.dataLength : length);
        const kind = klass === 'very large' ? 'warn' : 'pass';
        U.render(kind, klass + ' payload', [
          ['bytes', String(length)],
          ['class', klass],
          ['recognized execTransaction', decoded.recognized ? 'yes' : 'no']
        ], [{ level: 'note', text: 'small < 1 KB, typical < 8 KB, large < 24 KB, very large at or above 24 KB. Size is not a security verdict.' }]);
      });
    },

    'gnosis-chain-tx-status': function () {
      U.onRun(async function () {
        const hash = U.val('tx');
        if (!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('Paste a transaction hash.');
        const tx = await E.getTransaction(rpc(), hash);
        let receipt = null;
        try { receipt = await E.getReceipt(rpc(), hash); } catch (err) { receipt = null; }
        const status = !receipt ? 'pending or missing receipt' : (receipt.status === '0x1' ? 'success' : 'failed');
        U.render(status === 'success' ? 'pass' : 'pending', status, [
          ['hash', hash],
          ['from', tx.from || ''],
          ['to', tx.to || ''],
          ['block', tx.blockNumber ? BigInt(tx.blockNumber).toString() : 'pending'],
          ['gas used', receipt && receipt.gasUsed ? BigInt(receipt.gasUsed).toString() : ''],
          ['rpc', rpc()]
        ], [{ level: 'note', text: 'Point the RPC at Gnosis Chain (the default) or any other chain. A hash from another network will look missing.' }]);
      });
    },

    'safe-signature-count': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const decoded = E.decodeExecTransaction(loaded.input);
        if (!decoded.recognized) throw new Error('Signature bytes are only sliced from a decoded execTransaction.');
        const stats = E.signatureStats(decoded.signaturesLength);
        U.render(stats.exact ? 'pass' : 'warn', stats.ecdsaChunks + ' × 65-byte chunk(s)', [
          ['signature bytes', String(stats.length)],
          ['65-byte chunks', String(stats.ecdsaChunks)],
          ['remainder', String(stats.remainder)]
        ], [{ level: 'note', text: 'Contract signatures and approved hashes are not always 65-byte chunks. A remainder means the blob is not a clean list of ECDSA signatures. This does not recover signers.' }]);
      });
    },

    'approve-hash-vs-exec': function () {
      U.onRun(async function () {
        const loaded = await loadInput();
        const hex = E.normalizeHex(loaded.input);
        const selector = '0x' + hex.slice(0, 8);
        if (selector === '0x6a761202') {
          const decoded = E.decodeExecTransaction(loaded.input);
          U.render('pass', 'This is execTransaction, not approveHash', execRows(decoded, loaded.tx), [
            { level: 'note', text: 'execTransaction runs the inner call. approveHash only records an owner approval.' }
          ]);
          return;
        }
        if (selector === '0xd4d9bdcd') {
          const decoded = E.decodeStaticCall(loaded.input, 'approve');
          U.render('warn', 'This is approveHash', [
            ['hash', decoded.hash || ''],
            ['bytes', String(hex.length / 2)]
          ], [{ level: 'warn', text: 'approveHash does not execute the Safe transaction. A later execTransaction still has to be sent.' }]);
          return;
        }
        U.render('fail', 'Neither approveHash nor execTransaction', [
          ['selector', selector],
          ['known as', E.SELECTORS[selector] || 'unknown']
        ]);
      });
    },

    'batch-tx-unroll': function () {
      if ($('example')) $('example').addEventListener('click', function () {
        $('tx').value = '0x8d80ff0a' +
          '0000000000000000000000000000000000000000000000000000000000000020' +
          '0000000000000000000000000000000000000000000000000000000000000059' +
          '00' + '1111111111111111111111111111111111111111' +
          '0000000000000000000000000000000000000000000000000000000000000001' +
          '0000000000000000000000000000000000000000000000000000000000000004' +
          'aabbccdd';
        $('go').click();
      });
      U.onRun(async function () {
        const loaded = await loadInput();
        const calls = E.unrollMultiSend(loaded.input);
        U.render(calls.length ? 'pass' : 'fail', calls.length + ' inner call(s)', [
          ['calls', String(calls.length)]
        ], [U.table(['op', 'to', 'value wei', 'data bytes', 'selector'], calls.map(function (c) {
          return [c.operation, c.to, c.valueWei, String(c.dataLength), c.selector];
        })), { level: 'note', text: 'Packed MultiSend layout: uint8 operation, address, uint256 value, uint256 data length, data. Nested batches are not expanded further.' }]);
      });
    },

    'safe-tx-security-checklist': function () {
      const ids = ['chk-to', 'chk-value', 'chk-op', 'chk-data', 'chk-sig', 'chk-nonce', 'chk-guard'];
      function paint() {
        const open = ids.filter(function (id) { return !$(id).checked; });
        const el = $('summary');
        if (!open.length) { el.className = 'verdict pass'; el.textContent = 'Checklist complete'; }
        else { el.className = 'verdict pending'; el.textContent = open.length + ' item' + (open.length === 1 ? '' : 's') + ' still open'; }
      }
      if (globalThis.C2S) C2S.bindLive(ids, paint);
    }
  };

  const tool = document.body.getAttribute('data-tool');
  if (pages[tool]) pages[tool]();
})();
