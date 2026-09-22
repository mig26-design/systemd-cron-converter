'use strict';
(function (root) {
  const EXEC = '6a761202';
  const MULTISEND = '8d80ff0a';
  const EXAMPLE = '6a76120200000000000000000000000011111111111111111111111111111111111111110000000000000000000000000000000000000000000000000de0b6b3a7640000000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000222222222222222222222222222222222222222200000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000004aabbccdd000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111100000000000000000000000000000000000000000000000000000000000000';

  const SELECTORS = {
    '0x6a761202': 'execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)',
    '0x8d80ff0a': 'multiSend(bytes)',
    '0xa0e67e2b': 'getOwners()',
    '0xe75235b8': 'getThreshold()',
    '0xaffed0e0': 'nonce()',
    '0xc9106389': 'getGuard()',
    '0xffa1ad74': 'VERSION()',
    '0xd4d9bdcd': 'approveHash(bytes32)',
    '0xcc2f8452': 'getModulesPaginated(address,uint256)',
    '0xa9059cbb': 'transfer(address,uint256)',
    '0x23b872dd': 'transferFrom(address,address,uint256)',
    '0x095ea7b3': 'approve(address,uint256)',
    '0x42842e0e': 'safeTransferFrom(address,address,uint256)',
    '0xb88d4fde': 'safeTransferFrom(address,address,uint256,bytes)',
    '0x70a08231': 'balanceOf(address)',
    '0x3644e515': 'DOMAIN_SEPARATOR()'
  };

  const EVENTS = {
    '0x442e715f626346e8c54381002da614f62bee8d27386535b2521ec8540898556e': 'ExecutionSuccess(bytes32,uint256)',
    '0x23428b18acfb3ea64b08dc0c1d296ea9c09702c09083ca5272e64d115b687d23': 'ExecutionFailure(bytes32,uint256)',
    '0x9465fa0c962cc76958e6373a993326400c1c94f8be2fe3a952adfa7f60b2ea26': 'AddedOwner(address)',
    '0xf8d49fc529812e9a7c5c50e69c20f0dccc0db8fa95c98bc58cc9a4f1c1299eaf': 'RemovedOwner(address)',
    '0x610f7ff2b304ae8903c3de74c60c6ab1f7d6226b3f52c5161905bb5ad4039c93': 'ChangedThreshold(uint256)',
    '0xecdf3a3effea5783a3c4c2140e677577666428d44ed9d474a0b3a4c9943f8440': 'EnabledModule(address)',
    '0xaab4fa2b463f581b2b32cb3b7e3b704b9ce37cc209b5fb4d77e593ace4054276': 'DisabledModule(address)',
    '0x1151116914515bc0891ff9047a6cb32cf902546f83066499bcf8ba33d2353fa2': 'ChangedGuard(address)',
    '0xf2a0eb156472d1440255b0d7c1e19cc07115d1051fe605b0dce69acfec884d9c': 'ApproveHash(bytes32,address)',
    '0x3d0ce9bfc3ed7d6862dbb28b2dea94561fe714a1b4d019aa8af39730d1ad7c3d': 'SafeReceived(address,uint256)',
    '0x6895c13664aa4f67288b25d7a21d7aaa34916e355fb9b6fae0a139a9085becb8': 'ExecutionFromModuleSuccess(address)',
    '0xacd2c8702804128fdb0db2bb49f6d127dd0181c13fd45dbfe16de0930e2bd375': 'ExecutionFromModuleFailure(address)'
  };

  function normalizeHex(input) {
    let s = String(input || '').trim().replace(/\s+/g, '');
    if (/^0x/i.test(s)) s = s.slice(2);
    if (!s || /[^0-9a-fA-F]/.test(s) || s.length % 2 !== 0) return null;
    return s.toLowerCase();
  }

  function isTxHash(hex) {
    return !!hex && hex.length === 64;
  }

  function wordAt(hex, index) {
    const start = 8 + index * 64;
    if (start + 64 > hex.length) return null;
    return hex.slice(start, start + 64);
  }

  function u256(word) { return BigInt('0x' + word); }

  function addressOf(word) { return '0x' + word.slice(24); }

  function dirtyAddress(word) { return word.slice(0, 24) !== '000000000000000000000000'; }

  function readBytes(hex, offsetWord) {
    const offset = u256(offsetWord);
    if (offset > 5000000n) throw new Error('A dynamic offset is larger than this decoder accepts.');
    const start = 8 + Number(offset) * 2;
    if (start + 64 > hex.length) throw new Error('A dynamic bytes offset points past the end of the input.');
    const len = u256(hex.slice(start, start + 64));
    if (len > 2000000n) throw new Error('A bytes length is larger than this decoder accepts.');
    const n = Number(len);
    const dataEnd = start + 64 + n * 2;
    if (dataEnd > hex.length) throw new Error('The bytes payload is shorter than its length word.');
    return { hex: hex.slice(start + 64, dataEnd), length: n };
  }

  function formatWei(dec) {
    const bi = BigInt(dec);
    const sign = bi < 0n ? '-' : '';
    const v = bi < 0n ? -bi : bi;
    const whole = v / 1000000000000000000n;
    const frac = (v % 1000000000000000000n).toString().padStart(18, '0').replace(/0+$/, '');
    return bi.toString() + ' wei (' + sign + whole.toString() + (frac ? '.' + frac : '') + ' ETH)';
  }

  function decodeExecTransaction(input) {
    const hex = normalizeHex(input);
    if (!hex) return { ok: false, error: 'Input is not even-length hex.' };
    if (isTxHash(hex)) return { ok: false, needsRpc: true, hash: '0x' + hex };
    if (hex.length < 8) return { ok: false, error: 'Calldata is shorter than a 4-byte selector.' };
    const selector = hex.slice(0, 8);
    const result = {
      ok: true,
      selector: '0x' + selector,
      name: SELECTORS['0x' + selector] || 'unknown',
      recognized: selector === EXEC,
      byteLength: hex.length / 2,
      warnings: []
    };
    if (selector !== EXEC) {
      result.warnings.push('Selector is not Safe execTransaction (0x6a761202).');
      return result;
    }
    if (hex.length < 8 + 10 * 64) {
      result.recognized = false;
      result.warnings.push('Calldata is shorter than the 10-word execTransaction head.');
      return result;
    }
    const words = [];
    for (let i = 0; i < 10; i++) words.push(wordAt(hex, i));
    let data; let sigs;
    try {
      data = readBytes(hex, words[2]);
      sigs = readBytes(hex, words[9]);
    } catch (err) {
      result.recognized = false;
      result.warnings.push(err.message);
      return result;
    }
    const operation = u256(words[3]);
    result.to = addressOf(words[0]);
    result.valueWei = u256(words[1]).toString();
    result.dataLength = data.length;
    result.dataHex = data.hex;
    result.dataSelector = data.length >= 4 ? '0x' + data.hex.slice(0, 8) : '';
    result.operation = operation.toString();
    result.operationName = operation === 0n ? 'CALL' : operation === 1n ? 'DELEGATECALL' : 'unknown';
    result.safeTxGas = u256(words[4]).toString();
    result.baseGas = u256(words[5]).toString();
    result.gasPrice = u256(words[6]).toString();
    result.gasToken = addressOf(words[7]);
    result.refundReceiver = addressOf(words[8]);
    result.signaturesLength = sigs.length;
    result.signaturesHex = sigs.hex;
    if (dirtyAddress(words[0])) result.warnings.push('The to word has non-zero high bytes.');
    if (operation === 1n) result.warnings.push('operation is DELEGATECALL. The Safe would run inner data in its own storage.');
    if (result.dataSelector === '0x' + MULTISEND) result.warnings.push('Inner data starts with MultiSend. Expand it with the batch unroll tool.');
    return result;
  }

  function unrollPacked(packedHex) {
    const hex = packedHex.toLowerCase().replace(/^0x/, '');
    const calls = [];
    let i = 0;
    while (i + 2 + 40 + 64 + 64 <= hex.length) {
      const operation = parseInt(hex.slice(i, i + 2), 16);
      i += 2;
      const to = '0x' + hex.slice(i, i + 40);
      i += 40;
      const value = BigInt('0x' + hex.slice(i, i + 64)).toString();
      i += 64;
      const dataLen = Number(BigInt('0x' + hex.slice(i, i + 64)));
      i += 64;
      if (!Number.isFinite(dataLen) || dataLen < 0 || i + dataLen * 2 > hex.length) {
        throw new Error('MultiSend payload ended early at call ' + (calls.length + 1) + '.');
      }
      const data = hex.slice(i, i + dataLen * 2);
      i += dataLen * 2;
      calls.push({
        operation: operation === 0 ? 'CALL' : operation === 1 ? 'DELEGATECALL' : String(operation),
        to: to,
        valueWei: value,
        dataLength: dataLen,
        selector: dataLen >= 4 ? '0x' + data.slice(0, 8) : ''
      });
      if (calls.length > 64) break;
    }
    return calls;
  }

  function unrollMultiSend(input) {
    const hex = normalizeHex(input);
    if (!hex) throw new Error('MultiSend input is not hex.');
    let packed = hex;
    if (hex.slice(0, 8) === MULTISEND) {
      const decoded = readBytes(hex, wordAt(hex, 0));
      packed = decoded.hex;
    } else if (hex.slice(0, 8) === EXEC) {
      const exec = decodeExecTransaction(hex);
      if (!exec.recognized) throw new Error('execTransaction could not be decoded.');
      if ((exec.dataSelector || '').toLowerCase() !== '0x' + MULTISEND) {
        throw new Error('Inner data is not multiSend.');
      }
      return unrollMultiSend(exec.dataHex);
    }
    return unrollPacked(packed);
  }

  function decodeStaticCall(input, kind) {
    const hex = normalizeHex(input);
    if (!hex || hex.length < 8) return { ok: false, error: 'Need calldata, not just a hash.' };
    const selector = '0x' + hex.slice(0, 8);
    const name = SELECTORS[selector] || 'unknown';
    const words = [];
    for (let i = 0; 8 + (i + 1) * 64 <= hex.length && i < 8; i++) words.push(wordAt(hex, i));
    if (kind === 'erc20' && (selector === '0xa9059cbb' || selector === '0x095ea7b3') && words.length >= 2) {
      return { ok: true, selector: selector, name: name, to: addressOf(words[0]), amount: u256(words[1]).toString() };
    }
    if (kind === 'erc20' && selector === '0x23b872dd' && words.length >= 3) {
      return { ok: true, selector: selector, name: name, from: addressOf(words[0]), to: addressOf(words[1]), amount: u256(words[2]).toString(), shared: true };
    }
    if (kind === 'erc721' && selector === '0x42842e0e' && words.length >= 3) {
      return { ok: true, selector: selector, name: name, from: addressOf(words[0]), to: addressOf(words[1]), tokenId: u256(words[2]).toString() };
    }
    if (kind === 'erc721' && selector === '0xb88d4fde' && words.length >= 3) {
      return { ok: true, selector: selector, name: name, from: addressOf(words[0]), to: addressOf(words[1]), tokenId: u256(words[2]).toString(), hasData: true };
    }
    if (kind === 'erc721' && selector === '0x23b872dd' && words.length >= 3) {
      return { ok: true, selector: selector, name: name, from: addressOf(words[0]), to: addressOf(words[1]), tokenId: u256(words[2]).toString(), shared: true };
    }
    if (selector === '0xd4d9bdcd' && words.length >= 1) {
      return { ok: true, selector: selector, name: name, hash: '0x' + words[0] };
    }
    return { ok: true, selector: selector, name: name, words: words.map(addressOf) };
  }

  function signatureStats(length) {
    const n = Number(length) || 0;
    const ecdsa = Math.floor(n / 65);
    const remainder = n % 65;
    return {
      length: n,
      ecdsaChunks: ecdsa,
      remainder: remainder,
      exact: remainder === 0 && n > 0
    };
  }

  function payloadClass(length) {
    const n = Number(length) || 0;
    if (n === 0) return 'empty';
    if (n < 1024) return 'small';
    if (n < 8192) return 'typical';
    if (n < 24576) return 'large';
    return 'very large';
  }

  function dumpWords(input) {
    const hex = normalizeHex(input);
    if (!hex) return [];
    const body = hex.slice(8);
    const words = [];
    for (let i = 0; i + 64 <= body.length && words.length < 24; i += 64) {
      const word = body.slice(i, i + 64);
      words.push({
        index: words.length,
        word: '0x' + word,
        address: dirtyAddress(word) ? '' : addressOf(word),
        uint: u256(word).toString()
      });
    }
    return words;
  }

  function decodeAddressArray(returnHex) {
    const hex = normalizeHex(returnHex);
    if (!hex || hex.length < 128) return [];
    const offset = Number(u256(hex.slice(0, 64)));
    const start = offset * 2;
    const len = Number(u256(hex.slice(start, start + 64)));
    const out = [];
    for (let i = 0; i < len && i < 64; i++) {
      const word = hex.slice(start + 64 + i * 64, start + 128 + i * 64);
      if (word.length < 64) break;
      out.push(addressOf(word));
    }
    return out;
  }

  function decodeAddressWord(returnHex) {
    const hex = normalizeHex(returnHex);
    if (!hex || hex.length < 64) return null;
    return addressOf(hex.slice(0, 64));
  }

  function decodeUintWord(returnHex) {
    const hex = normalizeHex(returnHex);
    if (!hex || hex.length < 64) return null;
    return u256(hex.slice(0, 64)).toString();
  }

  function assertRpc(url) {
    let parsed;
    try { parsed = new URL(String(url || '').trim()); }
    catch (err) { throw new Error('The RPC URL is not valid.'); }
    if (parsed.protocol !== 'https:' && parsed.hostname !== 'localhost' && parsed.hostname !== '127.0.0.1') {
      throw new Error('Use an https:// JSON-RPC URL.');
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
      throw new Error('The RPC request did not complete. It may be blocking this browser (CORS) or offline. Paste raw calldata to skip the RPC.');
    }
    let payload = null;
    try { payload = await res.json(); } catch (err) { payload = null; }
    if (!res.ok) throw new Error('The RPC returned HTTP ' + res.status + '.');
    if (!payload) throw new Error('The RPC response was not JSON.');
    if (payload.error) throw new Error('RPC error: ' + (payload.error.message || 'unknown'));
    return payload.result;
  }

  async function getTransaction(url, hash) {
    const result = await rpc(url, 'eth_getTransactionByHash', [hash]);
    if (!result) throw new Error('No transaction with that hash on this RPC. It may be the wrong chain.');
    return result;
  }

  async function getReceipt(url, hash) {
    const result = await rpc(url, 'eth_getTransactionReceipt', [hash]);
    if (!result) throw new Error('No receipt yet. The transaction may be pending or on another chain.');
    return result;
  }

  function parseSafeLogs(logs) {
    return (logs || []).map(function (log, index) {
      const topic0 = (log.topics && log.topics[0] || '').toLowerCase();
      return {
        index: index,
        address: log.address || '',
        name: EVENTS[topic0] || 'unknown',
        topic0: topic0,
        topics: log.topics || [],
        data: log.data || '0x'
      };
    });
  }

  function jobIdCandidates(dataHex) {
    const hex = (dataHex || '').replace(/^0x/, '');
    if (hex.length < 64) return [];
    const word = hex.slice(0, 64);
    return [{ hex: '0x' + word, uint: BigInt('0x' + word).toString() }];
  }

  function zeroAddress(addr) {
    return !addr || /^0x0{40}$/i.test(addr);
  }

  root.Evm = {
    SELECTORS: SELECTORS,
    EVENTS: EVENTS,
    EXAMPLE: '0x' + EXAMPLE,
    normalizeHex: normalizeHex,
    isTxHash: isTxHash,
    decodeExecTransaction: decodeExecTransaction,
    formatWei: formatWei,
    unrollMultiSend: unrollMultiSend,
    decodeStaticCall: decodeStaticCall,
    signatureStats: signatureStats,
    payloadClass: payloadClass,
    dumpWords: dumpWords,
    decodeAddressArray: decodeAddressArray,
    decodeAddressWord: decodeAddressWord,
    decodeUintWord: decodeUintWord,
    rpc: rpc,
    getTransaction: getTransaction,
    getReceipt: getReceipt,
    parseSafeLogs: parseSafeLogs,
    jobIdCandidates: jobIdCandidates,
    zeroAddress: zeroAddress
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
