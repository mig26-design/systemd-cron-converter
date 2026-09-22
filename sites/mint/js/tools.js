'use strict';
(function () {
  const S = globalThis.Solana;
  if (!S || !document.body) return;
  const $ = S.$;

  function mintField() {
    return ($('mint') && $('mint').value.trim()) || '';
  }

  function authRows(loaded, verdict) {
    const info = loaded.info;
    return [
      ['mint', loaded.mint],
      ['program', S.programName(loaded.owner)],
      ['decimals', String(info.decimals)],
      ['supply', String(info.supply)],
      ['mintAuthority', verdict.mintAuthority === null ? 'null (revoked)' : String(verdict.mintAuthority)],
      ['freezeAuthority', verdict.freezeAuthority === null ? 'null (revoked)' : String(verdict.freezeAuthority)]
    ];
  }

  const pages = {
    'solana-mint-check': function () {
      document.querySelectorAll('[data-mint]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          $('mint').value = btn.getAttribute('data-mint');
          $('go').click();
        });
      });
      S.onRun(async function () {
        const loaded = await S.mintAccount(S.rpcValue(), mintField());
        const verdict = S.classifyMint(loaded.info);
        if (!verdict) throw new Error('mintAuthority and freezeAuthority were missing from the parsed mint.');
        if (verdict.pass) {
          S.render('pass', 'PASS — mintAuthority and freezeAuthority are null (revoked)', authRows(loaded, verdict));
        } else {
          const why = [];
          if (!verdict.mintRevoked) why.push('mintAuthority is still set');
          if (!verdict.freezeRevoked) why.push('freezeAuthority is still set');
          S.render('fail', 'FAIL — ' + why.join('; '), authRows(loaded, verdict));
        }
      });
    },

    'freeze-authority-check': function () {
      S.onRun(async function () {
        const loaded = await S.mintAccount(S.rpcValue(), mintField());
        const frozen = loaded.info.freezeAuthority !== null;
        const state = S.extension(loaded.info, 'defaultAccountState');
        const rows = [
          ['mint', loaded.mint],
          ['freezeAuthority', frozen ? String(loaded.info.freezeAuthority) : 'null (revoked)'],
          ['defaultAccountState', state ? JSON.stringify(state.state) : 'none']
        ];
        if (!frozen && !state) S.render('pass', 'PASS — freeze authority is revoked', rows);
        else S.render('fail', 'FAIL — a freeze control is still available', rows, [
          { level: 'warn', text: 'A set freeze authority can freeze holder accounts. Token-2022 can also freeze new accounts via defaultAccountState.' }
        ]);
      });
    },

    'lp-burn-or-lock': function () {
      S.onRun(async function () {
        const mint = mintField();
        const supply = await S.tokenSupply(S.rpcValue(), mint);
        const largest = await S.largestAccounts(S.rpcValue(), mint);
        const top = largest.slice(0, 8);
        const accounts = await S.multipleAccounts(S.rpcValue(), top.map(function (row) { return row.address; }));
        const owners = accounts.map(function (acct) {
          const info = acct && acct.data && acct.data.parsed && acct.data.parsed.info;
          return (info && info.owner) || 'unknown';
        });
        const amounts = top.map(function (row) { return row.amount; });
        const burned = S.burnedShare(owners, amounts, supply.amount);
        const kind = burned.burned ? 'pass' : 'fail';
        const title = burned.burned
          ? 'BURNED — at least 95% of supply sits at a known burn address'
          : 'NOT BURNED — supply is not concentrated on a known burn address';
        S.render(kind, title, [
          ['lp mint', mint],
          ['supply', supply.uiAmountString || supply.amount],
          ['known burn share', burned.burnedPct + '%']
        ], [S.table(['token account owner', 'amount', 'label'], burned.rows.map(function (row) {
          return [row.owner, row.amount, row.label];
        })), { level: 'note', text: 'Lockers that are not in the short burn list are labeled unlisted. This does not prove a lock contract.' }]);
      });
    },

    'token-2022-fee-check': function () {
      S.onRun(async function () {
        const loaded = await S.mintAccount(S.rpcValue(), mintField());
        const bps = S.transferFeeBps(loaded.info);
        const rows = [
          ['program', S.programName(loaded.owner)],
          ['transfer fee bps', bps == null ? 'none' : String(bps)],
          ['extensions', S.extension(loaded.info, 'transferFeeConfig') ? 'transferFeeConfig' : (loaded.info.extensions || []).map(function (e) { return e.extension; }).join(', ') || 'none']
        ];
        if (loaded.owner !== S.TOKEN_2022) {
          S.render('pending', 'Not Token-2022 — classic SPL mints have no transfer-fee extension', rows);
        } else if (bps == null) {
          S.render('pass', 'PASS — no transfer fee configured', rows);
        } else if (bps >= 1000) {
          S.render('fail', 'FAIL — transfer fee is ' + bps + ' bps', rows);
        } else {
          S.render('warn', 'Fee configured — ' + bps + ' bps', rows);
        }
      });
    },

    'top10-holder-concentration': function () {
      S.onRun(async function () {
        const mint = mintField();
        const supply = await S.tokenSupply(S.rpcValue(), mint);
        const largest = await S.largestAccounts(S.rpcValue(), mint);
        const share = S.topShare(largest, supply.amount);
        const kind = share.totalPct >= 50 ? 'fail' : share.totalPct >= 20 ? 'warn' : 'pass';
        const title = kind === 'fail'
          ? 'CONCENTRATED — top accounts hold ' + share.totalPct + '% of supply'
          : 'Top accounts hold ' + share.totalPct + '% of supply';
        S.render(kind, title, [
          ['mint', mint],
          ['supply', supply.uiAmountString || supply.amount],
          ['top share', share.totalPct + '%']
        ], [S.table(['token account', 'raw amount', 'share'], share.rows.map(function (row) {
          return [row.address, row.amount, row.pct + '%'];
        }))]);
      });
    },

    'deployer-wallet-holdings': function () {
      S.onRun(async function () {
        const mint = mintField();
        const wallet = $('wallet').value.trim();
        if (!S.validPubkey(wallet)) throw new Error('Wallet must be a Solana address.');
        const supply = await S.tokenSupply(S.rpcValue(), mint);
        const result = await S.rpc(S.rpcValue(), 'getTokenAccountsByOwner', [wallet, { mint: mint }, { encoding: 'jsonParsed' }]);
        const list = (result && result.value) || [];
        let held = 0n;
        const rows = list.map(function (item) {
          const info = item.account.data.parsed.info;
          const amount = BigInt(info.tokenAmount.amount || '0');
          held += amount;
          return [item.pubkey, info.tokenAmount.uiAmountString || amount.toString()];
        });
        const pct = BigInt(supply.amount || '0') > 0n ? Number((held * 10000n) / BigInt(supply.amount)) / 100 : 0;
        const kind = pct >= 20 ? 'warn' : 'pass';
        S.render(kind, 'Wallet holds ' + pct + '% of supply', [
          ['wallet', wallet],
          ['mint', mint],
          ['accounts', String(list.length)],
          ['raw held', held.toString()],
          ['share', pct + '%']
        ], rows.length ? [S.table(['token account', 'ui amount'], rows)] : [{ level: 'note', text: 'This wallet has no token account for that mint.' }]);
      });
    },

    'honeypot-transfer-sim': function () {
      S.onRun(async function () {
        const mint = mintField();
        const loaded = await S.mintAccount(S.rpcValue(), mint);
        const signals = S.honeypotSignals(loaded.info);
        const amount = ($('amount') && $('amount').value.trim()) || '1000000';
        let quoteNote = { level: 'note', text: 'Jupiter quote was not attempted.' };
        try {
          const url = 'https://lite-api.jup.ag/swap/v1/quote?inputMint=' + encodeURIComponent(mint) +
            '&outputMint=' + encodeURIComponent(S.WSOL) + '&amount=' + encodeURIComponent(amount) + '&slippageBps=50';
          const res = await fetch(url);
          const body = await res.json();
          if (body && body.outAmount) {
            quoteNote = { level: 'note', text: 'Jupiter quote returned outAmount ' + body.outAmount + ' (not a guarantee you can sell).' };
          } else {
            quoteNote = { level: 'warn', text: 'Jupiter did not return a route (' + (body.error || body.errorCode || res.status) + '). No route is not the same as a honeypot.' };
          }
        } catch (err) {
          quoteNote = { level: 'warn', text: 'The Jupiter quote request failed (often CORS). Static mint flags are still shown.' };
        }
        const kind = signals.high ? 'fail' : signals.flags.length ? 'warn' : 'pass';
        const title = signals.high ? 'FAIL — high-risk transfer controls on the mint' : (signals.flags.length ? 'REVIEW — medium signals only' : 'PASS — no high-risk mint controls');
        S.render(kind, title, [
          ['mint', mint],
          ['program', S.programName(loaded.owner)],
          ['flags', signals.flags.map(function (f) { return f.level + ': ' + f.text; }).join(' | ') || 'none']
        ], [quoteNote, { level: 'note', text: 'This does not sign or simulate a wallet sell. Freeze, delegate, and fee extensions are the on-mint signals.' }]);
      });
    },

    'pump-fun-graduated-check': function () {
      S.onRun(async function () {
        const mint = mintField();
        if (!S.validPubkey(mint)) throw new Error('Paste the pump.fun token mint.');
        const found = await S.findExistingPda(
          S.rpcValue(),
          [new TextEncoder().encode('bonding-curve'), S.decodeBase58(mint)],
          S.PUMP,
          5
        );
        if (!found) throw new Error('No pump.fun bonding-curve account in the first PDA bumps. It may not be a pump.fun mint, or the RPC hid the account.');
        if (found.value.owner !== S.PUMP) {
          throw new Error('Derived account owner is ' + found.value.owner + ', not the pump.fun program.');
        }
        const raw = Array.isArray(found.value.data) ? found.value.data[0] : '';
        const curve = S.parsePumpCurve(S.decodeBase64(raw));
        if (!curve) throw new Error('Bonding-curve account is shorter than the expected layout. The program layout may have changed.');
        if (curve.complete) {
          S.render('pass', 'GRADUATED — bonding curve complete flag is set', [
            ['curve', found.address],
            ['bump searched', String(found.bump)],
            ['real SOL reserves', curve.realSolReserves],
            ['token total supply', curve.tokenTotalSupply]
          ], [{ level: 'note', text: 'complete=1 is the on-account graduation flag. This page does not confirm the Raydium migration transaction.' }]);
        } else {
          S.render('pending', 'NOT GRADUATED — bonding curve is still open', [
            ['curve', found.address],
            ['real token reserves', curve.realTokenReserves],
            ['real SOL reserves', curve.realSolReserves]
          ]);
        }
      });
    },

    'raydium-pool-ownership': function () {
      S.onRun(async function () {
        const pool = mintField();
        const value = await S.account(S.rpcValue(), pool, 'base64');
        if (!value) throw new Error('No account at that address.');
        const label = S.RAYDIUM[value.owner];
        const data = Array.isArray(value.data) ? value.data[0] : '';
        const bytes = data ? S.decodeBase64(data).length : 0;
        if (label) {
          S.render('pass', 'PASS — owner is ' + label, [
            ['pool', pool],
            ['owner', value.owner],
            ['data bytes', String(bytes)],
            ['lamports', String(value.lamports)]
          ], [{ level: 'note', text: 'Ownership of the program is not the same as LP burned or locked. Check the LP mint with the burn tool.' }]);
        } else {
          S.render('fail', 'FAIL — owner is not a known Raydium AMM/CPMM/CLMM program', [
            ['pool', pool],
            ['owner', value.owner],
            ['owner label', S.programName(value.owner)],
            ['data bytes', String(bytes)]
          ]);
        }
      });
    },

    'meteora-lp-status': function () {
      S.onRun(async function () {
        const pool = mintField();
        const value = await S.account(S.rpcValue(), pool, 'base64');
        if (!value) throw new Error('No account at that address.');
        const label = S.METEORA[value.owner];
        const data = Array.isArray(value.data) ? value.data[0] : '';
        const bytes = data ? S.decodeBase64(data).length : 0;
        S.render(label ? 'pass' : 'fail', label ? ('Recognized ' + label) : 'Not a known Meteora program', [
          ['account', pool],
          ['owner', value.owner],
          ['label', label || S.programName(value.owner)],
          ['data bytes', String(bytes)],
          ['executable', value.executable ? 'yes' : 'no']
        ], [{ level: 'note', text: 'This checks the account owner only. It does not compute DLMM bin liquidity or whether LP tokens are locked.' }]);
      });
    },

    'mint-revoke-history': function () {
      S.onRun(async function () {
        const mint = mintField();
        const loaded = await S.mintAccount(S.rpcValue(), mint);
        const sigs = await S.signatures(S.rpcValue(), mint, 12);
        const events = [];
        for (let i = 0; i < Math.min(sigs.length, 6); i++) {
          const tx = await S.transaction(S.rpcValue(), sigs[i].signature);
          const message = tx && tx.transaction && tx.transaction.message;
          const list = (message && message.instructions) || [];
          const inner = (tx && tx.meta && tx.meta.innerInstructions) || [];
          const all = list.slice();
          inner.forEach(function (group) { (group.instructions || []).forEach(function (ix) { all.push(ix); }); });
          all.forEach(function (ix) {
            const parsed = ix.parsed;
            if (!parsed || parsed.type !== 'setAuthority') return;
            events.push([
              sigs[i].signature.slice(0, 12) + '…',
              String(sigs[i].slot),
              parsed.info && parsed.info.authorityType || '',
              parsed.info && (parsed.info.newAuthority || 'null')
            ]);
          });
        }
        const verdict = S.classifyMint(loaded.info);
        S.render(events.length ? 'pending' : 'pass', events.length ? ('Found ' + events.length + ' setAuthority instruction(s) in the recent sample') : 'No setAuthority in the most recent sampled transactions', [
          ['mint', mint],
          ['current mintAuthority', verdict && verdict.mintAuthority === null ? 'null' : String(verdict && verdict.mintAuthority)],
          ['current freezeAuthority', verdict && verdict.freezeAuthority === null ? 'null' : String(verdict && verdict.freezeAuthority)],
          ['signatures scanned', String(Math.min(sigs.length, 6))]
        ], events.length ? [S.table(['signature', 'slot', 'authority type', 'new authority'], events)] : [{ level: 'note', text: 'Only a handful of recent transactions are fetched. Older revokes can be missed. A null authority now is the current state, even if the revoke tx was not in this page.' }]);
      });
    },

    'freeze-enable-risk': function () {
      S.onRun(async function () {
        const loaded = await S.mintAccount(S.rpcValue(), mintField());
        const risk = S.freezeRisk(loaded.info);
        S.render(risk.level, risk.label, [
          ['mint', loaded.mint],
          ['score', String(risk.score)],
          ['freezeAuthority', loaded.info.freezeAuthority || 'null']
        ], risk.reasons.map(function (text) { return { level: 'warn', text: text }; }));
      });
    },

    'bundled-snipe-flag': function () {
      S.onRun(async function () {
        const mint = mintField();
        const sigs = await S.signatures(S.rpcValue(), mint, 40);
        const best = S.clusterSlots(sigs);
        if (!best) throw new Error('The RPC returned no signatures for that address.');
        const bundled = best.count >= 4;
        const oldest = sigs[sigs.length - 1];
        S.render(bundled ? 'fail' : 'pass', bundled ? ('SPIKE — ' + best.count + ' signatures share slot ' + best.slot) : 'No 4+ signature slot in this sample', [
          ['mint', mint],
          ['signatures', String(sigs.length)],
          ['densest slot', String(best.slot)],
          ['count in that slot', String(best.count)],
          ['oldest slot in sample', oldest ? String(oldest.slot) : '']
        ], [{ level: 'note', text: 'getSignaturesForAddress returns the newest signatures first. A busy mint will not show its creation bundle in a 40-signature window. Same-slot counts are a heuristic, not proof of a Jito bundle.' }]);
      });
    },

    'update-authority-check': function () {
      S.onRun(async function () {
        const meta = await S.loadMetadata(S.rpcValue(), mintField());
        const revoked = meta.updateAuthority === '11111111111111111111111111111111';
        S.render(revoked ? 'pass' : 'fail', revoked ? 'PASS — update authority is the system program (revoked)' : 'FAIL — update authority is still a wallet or program', [
          ['metadata', meta.address],
          ['name', meta.name],
          ['symbol', meta.symbol],
          ['updateAuthority', meta.updateAuthority],
          ['seller fee bps', String(meta.sellerFeeBasisPoints)]
        ]);
      });
    },

    'metadata-mutable-check': function () {
      S.onRun(async function () {
        const meta = await S.loadMetadata(S.rpcValue(), mintField());
        if (meta.isMutable == null) throw new Error('Could not read the mutable flag. The account layout may not match this parser.');
        S.render(meta.isMutable ? 'fail' : 'pass', meta.isMutable ? 'FAIL — metadata is still mutable' : 'PASS — metadata is immutable', [
          ['metadata', meta.address],
          ['name', meta.name],
          ['symbol', meta.symbol],
          ['uri', meta.uri],
          ['isMutable', meta.isMutable ? 'true' : 'false'],
          ['updateAuthority', meta.updateAuthority]
        ]);
      });
    },

    'tax-bps-decoder': function () {
      S.onRun(async function () {
        const mint = mintField();
        let bps = Number($('bps').value);
        let source = 'manual';
        if (S.validPubkey(mint)) {
          const loaded = await S.mintAccount(S.rpcValue(), mint);
          const fromMint = S.transferFeeBps(loaded.info);
          if (fromMint != null) { bps = fromMint; source = 'mint transferFeeConfig'; }
        }
        const applied = S.applyBps($('amount').value, bps);
        S.render('pending', source === 'manual' ? 'Manual bps math' : 'Fee read from the mint', [
          ['source', source],
          ['bps', String(applied.bps)],
          ['gross base units', applied.raw],
          ['fee base units', applied.fee],
          ['net base units', applied.net],
          ['fee percent', (applied.bps / 100) + '%']
        ], [{ level: 'note', text: 'Basis points are out of 10,000. A 100 bps fee is 1%. Token-2022 also has a max fee; this page shows the bps cut only.' }]);
      });
    },

    'ca-vs-ticker-lookup': function () {
      S.onRun(async function () {
        const raw = mintField();
        if (!S.validPubkey(raw)) {
          S.render('fail', 'That is not a mint address', [
            ['input', raw || '(empty)'],
            ['why', 'Tickers are not unique and are not the contract address']
          ], [{ level: 'warn', text: 'Paste the base58 mint (the CA). A symbol like BONK is not enough to identify a token.' }]);
          return;
        }
        const meta = await S.loadMetadata(S.rpcValue(), raw);
        S.render('pass', 'Ticker and contract are different fields', [
          ['contract (mint)', raw],
          ['on-chain symbol', meta.symbol || '(empty)'],
          ['on-chain name', meta.name || '(empty)'],
          ['update authority', meta.updateAuthority]
        ], [{ level: 'note', text: 'Anyone can copy a symbol. Match the full mint address, not the ticker.' }]);
      });
    },

    'rugcheck-summary-card': function () {
      S.onRun(async function () {
        const mint = mintField();
        const loaded = await S.mintAccount(S.rpcValue(), mint);
        const verdict = S.classifyMint(loaded.info);
        let metaNote = 'metadata not found';
        let mutable = 'unknown';
        try {
          const meta = await S.loadMetadata(S.rpcValue(), mint);
          mutable = meta.isMutable ? 'mutable' : 'immutable';
          metaNote = (meta.symbol || '') + ' / ' + (meta.name || '');
        } catch (err) {
          metaNote = err.message;
        }
        const supply = await S.tokenSupply(S.rpcValue(), mint);
        const largest = await S.largestAccounts(S.rpcValue(), mint);
        const share = S.topShare(largest, supply.amount);
        const bps = S.transferFeeBps(loaded.info);
        const bad = !verdict.pass || share.totalPct >= 50 || mutable === 'mutable' || (bps != null && bps >= 1000);
        S.render(bad ? 'fail' : 'pass', bad ? 'REVIEW — at least one signal needs a human look' : 'QUIET — no high signal in this card', [
          ['mint', mint],
          ['authorities', verdict.pass ? 'both revoked' : 'not both revoked'],
          ['metadata', metaNote],
          ['mutable', mutable],
          ['top holder share', share.totalPct + '%'],
          ['transfer fee bps', bps == null ? 'none' : String(bps)]
        ], [{ level: 'note', text: 'This is a local summary of public RPC reads, not a RugCheck.xyz score and not a promise about liquidity.' }]);
      });
    },

    'jupiter-organic-score': function () {
      S.onRun(async function () {
        const pasted = $('paste') && $('paste').value.trim();
        let token = null;
        if (pasted) {
          const json = JSON.parse(pasted);
          token = Array.isArray(json) ? json[0] : json;
        } else {
          const mint = mintField();
          if (!S.validPubkey(mint)) throw new Error('Paste a mint, or paste Jupiter JSON into the box.');
          S.busy('Asking Jupiter…');
          let res;
          try {
            res = await fetch('https://lite-api.jup.ag/tokens/v2/search?query=' + encodeURIComponent(mint));
          } catch (err) {
            throw new Error('The browser could not read Jupiter (usually CORS). Paste the JSON from that URL instead.');
          }
          if (!res.ok) throw new Error('Jupiter returned HTTP ' + res.status + '.');
          const list = await res.json();
          token = (Array.isArray(list) ? list : []).find(function (item) { return item && (item.id === mint || item.address === mint); }) || (Array.isArray(list) ? list[0] : null);
          if (!token) throw new Error('Jupiter returned no token for that mint.');
        }
        const score = token.organicScore != null ? token.organicScore : token.organicScoreLabel;
        S.render(score == null ? 'pending' : 'pass', score == null ? 'No organicScore field in that JSON' : ('organicScore ' + score), [
          ['id', token.id || token.address || ''],
          ['symbol', token.symbol || ''],
          ['name', token.name || ''],
          ['organicScore', token.organicScore == null ? '—' : String(token.organicScore)],
          ['label', token.organicScoreLabel || '—']
        ], [{ level: 'note', text: 'Organic score is Jupiter’s field, copied here. This page does not recompute it.' }]);
      });
    },

    'sol-token-security-checklist': function () {
      const boxes = ['chk-mint', 'chk-freeze', 'chk-meta', 'chk-lp', 'chk-holders', 'chk-fee', 'chk-ca'];
      function paint() {
        const pending = boxes.filter(function (id) { return !$(id).checked; });
        const el = $('summary');
        if (!pending.length) {
          el.className = 'verdict pass';
          el.textContent = 'Checklist complete';
        } else {
          el.className = 'verdict pending';
          el.textContent = pending.length + ' item' + (pending.length === 1 ? '' : 's') + ' still open';
        }
      }
      S.onRun(async function () {
        const loaded = await S.mintAccount(S.rpcValue(), mintField());
        const verdict = S.classifyMint(loaded.info);
        const hints = [];
        hints.push(verdict.mintRevoked ? 'Mint authority is null.' : 'Mint authority is still set — leave the mint box open until you accept that.');
        hints.push(verdict.freezeRevoked ? 'Freeze authority is null.' : 'Freeze authority is still set.');
        const bps = S.transferFeeBps(loaded.info);
        hints.push(bps == null ? 'No Token-2022 transfer fee on the mint.' : ('Transfer fee ' + bps + ' bps.'));
        $('hints').textContent = hints.join(' ');
        paint();
      });
      if (globalThis.C2S) C2S.bindLive(boxes.concat(['mint']), paint);
    }
  };

  const tool = document.body.getAttribute('data-tool');
  if (pages[tool]) pages[tool]();
})();
