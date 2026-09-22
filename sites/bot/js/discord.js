'use strict';
(function (root) {
  const PERMISSIONS = [
    ['Create instant invite', 1n << 0n],
    ['Kick members', 1n << 1n],
    ['Ban members', 1n << 2n],
    ['Administrator', 1n << 3n],
    ['Manage channels', 1n << 4n],
    ['Manage guild', 1n << 5n],
    ['Add reactions', 1n << 6n],
    ['View audit log', 1n << 7n],
    ['Priority speaker', 1n << 8n],
    ['Stream', 1n << 9n],
    ['View channel', 1n << 10n],
    ['Send messages', 1n << 11n],
    ['Send TTS messages', 1n << 12n],
    ['Manage messages', 1n << 13n],
    ['Embed links', 1n << 14n],
    ['Attach files', 1n << 15n],
    ['Read message history', 1n << 16n],
    ['Mention everyone', 1n << 17n],
    ['Use external emojis', 1n << 18n],
    ['Connect', 1n << 20n],
    ['Speak', 1n << 21n],
    ['Mute members', 1n << 22n],
    ['Deafen members', 1n << 23n],
    ['Move members', 1n << 24n],
    ['Change nickname', 1n << 26n],
    ['Manage nicknames', 1n << 27n],
    ['Manage roles', 1n << 28n],
    ['Manage webhooks', 1n << 29n],
    ['Use application commands', 1n << 31n],
    ['Manage threads', 1n << 34n],
    ['Create public threads', 1n << 35n],
    ['Send messages in threads', 1n << 38n],
    ['Moderate members', 1n << 40n],
    ['Send voice messages', 1n << 46n]
  ];

  const INTENTS = [
    ['GUILDS', 1 << 0],
    ['GUILD_MEMBERS', 1 << 1],
    ['GUILD_MODERATION', 1 << 2],
    ['GUILD_EMOJIS_AND_STICKERS', 1 << 3],
    ['GUILD_INTEGRATIONS', 1 << 4],
    ['GUILD_WEBHOOKS', 1 << 5],
    ['GUILD_INVITES', 1 << 6],
    ['GUILD_VOICE_STATES', 1 << 7],
    ['GUILD_PRESENCES', 1 << 8],
    ['GUILD_MESSAGES', 1 << 9],
    ['GUILD_MESSAGE_REACTIONS', 1 << 10],
    ['GUILD_MESSAGE_TYPING', 1 << 11],
    ['DIRECT_MESSAGES', 1 << 12],
    ['DIRECT_MESSAGE_REACTIONS', 1 << 13],
    ['DIRECT_MESSAGE_TYPING', 1 << 14],
    ['MESSAGE_CONTENT', 1 << 15],
    ['GUILD_SCHEDULED_EVENTS', 1 << 16],
    ['AUTO_MODERATION_CONFIGURATION', 1 << 20],
    ['AUTO_MODERATION_EXECUTION', 1 << 21],
    ['GUILD_MESSAGE_POLLS', 1 << 24],
    ['DIRECT_MESSAGE_POLLS', 1 << 25]
  ];

  const ERRORS = {
    0: 'General error.',
    10003: 'Unknown channel.',
    10004: 'Unknown guild.',
    10008: 'Unknown message.',
    10011: 'Unknown role.',
    10013: 'Unknown user.',
    10015: 'Unknown webhook.',
    10062: 'Unknown interaction. The token expired or the id is wrong. Acknowledge interactions quickly.',
    40001: 'Unauthorized. The token is missing, revoked, or not a bot token.',
    40060: 'Interaction has already been acknowledged.',
    50001: 'Missing access. The bot is not in the channel, or it lacks View Channel.',
    50013: 'Missing permissions. The bot is in the channel but lacks the permission this route needs.',
    50035: 'Invalid form body. A field is the wrong type or missing.',
    60003: 'Two-factor is required for this action on the server.',
    30001: 'Maximum number of guilds reached for this account.',
    30007: 'Maximum number of webhooks reached.',
    40002: 'You need to verify your account.',
    20012: 'You are not authorized to perform this action on this application.'
  };

  function selectedScopes(flags) {
    const scopes = [];
    if (flags.bot) scopes.push('bot');
    if (flags.commands) scopes.push('applications.commands');
    if (flags.commandPerms) scopes.push('applications.commands.permissions.update');
    return scopes;
  }

  function buildInvite(appId, flags, permissions) {
    const id = String(appId || '').trim();
    if (!/^\d{15,22}$/.test(id)) return '';
    const scopes = selectedScopes(flags || {});
    if (!scopes.length) return '';
    const params = new URLSearchParams();
    params.set('client_id', id);
    params.set('scope', scopes.join(' '));
    if (scopes.indexOf('bot') !== -1) {
      const perms = String(permissions == null ? '0' : permissions).trim() || '0';
      params.set('permissions', /^\d+$/.test(perms) ? perms : '0');
    }
    return 'https://discord.com/api/oauth2/authorize?' + params.toString();
  }

  function decodeBits(value, table) {
    let n;
    try { n = BigInt(String(value).trim() || '0'); } catch (err) { return []; }
    return table.filter(function (row) { return (n & row[1]) === row[1]; }).map(function (row) { return row[0]; });
  }

  function sumBits(names, table) {
    const want = new Set(names);
    let total = 0n;
    table.forEach(function (row) { if (want.has(row[0])) total |= row[1]; });
    return total.toString();
  }

  function errorText(code) {
    const n = Number(code);
    if (!Number.isFinite(n)) return '';
    return ERRORS[n] || '';
  }

  function tokenShape(input) {
    const raw = String(input || '').trim();
    if (!raw) return { empty: true };
    let prefix = '';
    let body = raw;
    if (/^bot\s+/i.test(raw)) { prefix = 'Bot'; body = raw.replace(/^bot\s+/i, ''); }
    else if (/^bearer\s+/i.test(raw)) { prefix = 'Bearer'; body = raw.replace(/^bearer\s+/i, ''); }
    const parts = body.split('.');
    const looks = parts.length === 3 && parts.every(function (p) { return p.length >= 4; });
    return {
      empty: false,
      prefix: prefix,
      segments: parts.length,
      lengths: parts.map(function (p) { return p.length; }),
      looksLikeToken: looks,
      mfa: /^mfa\./i.test(body)
    };
  }

  function shardAdvice(guilds) {
    const n = Number(guilds);
    if (!Number.isFinite(n) || n < 0) return { error: 'Guild count must be a number.' };
    const required = n >= 2500;
    const suggested = Math.max(1, Math.ceil(n / 1000));
    return { guilds: n, required: required, suggested: required ? suggested : 1 };
  }

  function parse429(raw) {
    const text = String(raw || '');
    let retry = null;
    let global = false;
    let message = '';
    const jsonStart = text.indexOf('{');
    if (jsonStart >= 0) {
      try {
        const body = JSON.parse(text.slice(jsonStart));
        if (body.retry_after != null) retry = Number(body.retry_after);
        if (body.global) global = true;
        message = body.message || '';
      } catch (err) { message = ''; }
    }
    const header = text.match(/retry-after:\s*([0-9.]+)/i);
    if (retry == null && header) retry = Number(header[1]);
    return { retry: retry, global: global, message: message };
  }

  function endpointIssues(url) {
    const issues = [];
    let parsed = null;
    try { parsed = new URL(url); } catch (err) { return ['That is not a URL.']; }
    if (parsed.protocol !== 'https:') issues.push('Discord interaction endpoints must be https.');
    if (parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1') issues.push('localhost is not reachable by Discord. Use a public https host.');
    if (parsed.protocol === 'https:' && !issues.length) issues.push('URL shape is fine. Discord will POST a PING (type 1); you must answer with a PONG (type 1).');
    return issues;
  }

  root.DiscordTools = {
    PERMISSIONS: PERMISSIONS,
    INTENTS: INTENTS,
    ERRORS: ERRORS,
    selectedScopes: selectedScopes,
    buildInvite: buildInvite,
    decodeBits: decodeBits,
    sumBits: sumBits,
    errorText: errorText,
    tokenShape: tokenShape,
    shardAdvice: shardAdvice,
    parse429: parse429,
    endpointIssues: endpointIssues
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
