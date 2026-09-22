'use strict';
(function (root) {
  const MASK = (1n << 64n) - 1n;
  const RC = [
    0x0000000000000001n, 0x0000000000008082n, 0x800000000000808an, 0x8000000080008000n,
    0x000000000000808bn, 0x0000000080000001n, 0x8000000080008081n, 0x8000000000008009n,
    0x000000000000008an, 0x0000000000000088n, 0x0000000080008009n, 0x000000008000000an,
    0x000000008000808bn, 0x800000000000008bn, 0x8000000000008089n, 0x8000000000008003n,
    0x8000000000008002n, 0x8000000000000080n, 0x000000000000800an, 0x800000008000000an,
    0x8000000080008081n, 0x8000000000008080n, 0x0000000080000001n, 0x8000000080008008n
  ];
  const ROT = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14]
  ];

  function rot(x, n) {
    const s = BigInt(n);
    return ((x << s) | (x >> (64n - s))) & MASK;
  }

  function keccak256Bytes(data) {
    const st = new Array(25).fill(0n);
    const rate = 136;
    const msg = new Uint8Array(data.length + rate);
    msg.set(data);
    msg[data.length] = 0x01;
    let end = data.length + 1;
    if (end % rate !== rate - 1) {
      end += (rate - 1 - (end % rate) + rate) % rate;
    }
    msg[end] = 0x80;
    const total = end + 1;
    for (let off = 0; off < total; off += rate) {
      for (let i = 0; i < rate / 8; i++) {
        let v = 0n;
        for (let b = 0; b < 8; b++) v |= BigInt(msg[off + i * 8 + b]) << BigInt(8 * b);
        st[i] ^= v;
      }
      for (let rnd = 0; rnd < 24; rnd++) {
        const C = [0n, 0n, 0n, 0n, 0n];
        for (let x = 0; x < 5; x++) C[x] = st[x] ^ st[x + 5] ^ st[x + 10] ^ st[x + 15] ^ st[x + 20];
        const D = [0n, 0n, 0n, 0n, 0n];
        for (let x = 0; x < 5; x++) D[x] = C[(x + 4) % 5] ^ rot(C[(x + 1) % 5], 1);
        for (let x = 0; x < 5; x++) {
          for (let y = 0; y < 5; y++) st[x + 5 * y] ^= D[x];
        }
        const B = new Array(25).fill(0n);
        for (let x = 0; x < 5; x++) {
          for (let y = 0; y < 5; y++) B[y + 5 * ((2 * x + 3 * y) % 5)] = rot(st[x + 5 * y], ROT[x][y]);
        }
        for (let x = 0; x < 5; x++) {
          for (let y = 0; y < 5; y++) {
            st[x + 5 * y] = B[x + 5 * y] ^ ((~B[((x + 1) % 5) + 5 * y]) & B[((x + 2) % 5) + 5 * y] & MASK);
          }
        }
        st[0] = (st[0] ^ RC[rnd]) & MASK;
      }
    }
    const out = new Uint8Array(32);
    let n = 0;
    for (let i = 0; i < rate / 8 && n < 32; i++) {
      let v = st[i];
      for (let b = 0; b < 8 && n < 32; b++) {
        out[n++] = Number(v & 0xffn);
        v >>= 8n;
      }
    }
    return out;
  }

  function toBytes(input) {
    if (input instanceof Uint8Array) return input;
    if (typeof input === 'string') {
      const s = input.startsWith('0x') || input.startsWith('0X') ? input.slice(2) : input;
      if (s.length % 2 === 0 && /^[0-9a-fA-F]*$/.test(s) && s.length > 0 && input.startsWith('0x')) {
        const bytes = new Uint8Array(s.length / 2);
        for (let i = 0; i < bytes.length; i++) bytes[i] = parseInt(s.slice(i * 2, i * 2 + 2), 16);
        return bytes;
      }
      return new TextEncoder().encode(input);
    }
    throw new Error('keccak input must be a string or bytes');
  }

  function toHex(bytes) {
    let hex = '';
    for (let i = 0; i < bytes.length; i++) hex += bytes[i].toString(16).padStart(2, '0');
    return hex;
  }

  function keccak256(input) {
    return '0x' + toHex(keccak256Bytes(toBytes(input)));
  }

  function selector(signature) {
    return keccak256(signature).slice(0, 10);
  }

  function topic(signature) {
    return keccak256(signature);
  }

  function eip55(address) {
    const raw = String(address || '').toLowerCase().replace(/^0x/, '');
    if (!/^[0-9a-f]{40}$/.test(raw)) return address;
    const hash = keccak256(raw).slice(2);
    let out = '0x';
    for (let i = 0; i < 40; i++) {
      out += parseInt(hash[i], 16) >= 8 ? raw[i].toUpperCase() : raw[i];
    }
    return out;
  }

  root.Keccak = {
    keccak256: keccak256,
    keccak256Bytes: keccak256Bytes,
    selector: selector,
    topic: topic,
    eip55: eip55,
    toHex: toHex
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
