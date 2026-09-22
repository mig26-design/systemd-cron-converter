'use strict';
(function () {
  const D = globalThis.DiscordTools;
  const U = globalThis.SiteUI;
  if (!D || !U || !document.body) return;

  function flags() {
    return {
      bot: !!(U.$('scope-bot') && U.$('scope-bot').checked),
      commands: !!(U.$('scope-commands') && U.$('scope-commands').checked),
      commandPerms: !!(U.$('scope-cmd-perms') && U.$('scope-cmd-perms').checked)
    };
  }

  function checklist(ids) {
    function paint() {
      const open = ids.filter(function (id) { return U.$(id) && !U.$(id).checked; });
      const el = U.$('summary');
      if (!el) return;
      if (!open.length) { el.className = 'verdict pass'; el.textContent = 'Checklist complete'; }
      else { el.className = 'verdict pending'; el.textContent = open.length + ' item' + (open.length === 1 ? '' : 's') + ' still open'; }
    }
    if (globalThis.C2S) C2S.bindLive(ids, paint);
    else paint();
  }

  const pages = {
    'discord-bot-offline': function () {
      function paint() {
        const id = U.val('app-id');
        const idOk = /^\d{15,22}$/.test(id);
        const f = flags();
        const url = D.buildInvite(id, f, U.val('perms') || '0');
        if (U.$('invite')) U.$('invite').value = url;
        if (U.$('id-status')) {
          U.$('id-status').className = 'status ' + (!id ? '' : idOk ? 'ok' : 'error');
          U.$('id-status').textContent = !id ? 'Paste the Application ID from the Developer Portal.' : (idOk ? 'Application ID looks like a snowflake.' : 'Application IDs are numeric, usually 17–20 digits.');
        }
        const items = [
          ['chk-scopes', 'Invite scopes'],
          ['chk-content', 'Message Content Intent'],
          ['chk-presence', 'Presence Intent'],
          ['chk-gateway', 'Gateway running'],
          ['chk-online', 'Bot user online']
        ];
        const pending = items.filter(function (item) { return !U.$(item[0]).checked; });
        const summary = U.$('summary');
        if (!idOk) { summary.className = 'verdict fail'; summary.textContent = 'Add a valid Application ID before using the invite URL'; }
        else if (!f.bot) { summary.className = 'verdict fail'; summary.textContent = 'bot scope is off — this URL will not add a bot user'; }
        else if (!pending.length) { summary.className = 'verdict pass'; summary.textContent = 'Checklist complete'; }
        else { summary.className = 'verdict pending'; summary.textContent = pending.length + ' item' + (pending.length === 1 ? '' : 's') + ' still open'; }
        if (U.$('next')) {
          U.$('next').textContent = pending.length
            ? 'Still to confirm: ' + pending.map(function (item) { return item[1]; }).join(', ') + '.'
            : 'If the member list still shows the bot offline, compare the intents your code requests with the portal toggles, and confirm the process is using this application’s token.';
        }
      }
      if (globalThis.C2S) C2S.bindLive(['app-id', 'scope-bot', 'scope-commands', 'scope-cmd-perms', 'perms', 'chk-scopes', 'chk-content', 'chk-presence', 'chk-gateway', 'chk-online'], paint);
    },

    'message-content-intent-check': function () {
      U.onRun(function () {
        const portal = U.$('portal').checked;
        const code = U.$('code').checked;
        let kind = 'pass';
        let title = 'Portal and code agree';
        if (code && !portal) { kind = 'fail'; title = 'FAIL — code requests Message Content but the portal toggle is off'; }
        else if (!code && portal) { kind = 'warn'; title = 'Portal is on, code does not request it'; }
        else if (!code && !portal) { kind = 'pass'; title = 'Message Content is off in both places'; }
        U.render(kind, title, [
          ['portal toggle', portal ? 'on' : 'off'],
          ['library requests it', code ? 'yes' : 'no'],
          ['intent bit', '1 << 15 = 32768']
        ], [{ level: 'note', text: 'A mismatch where the library requests the intent and the portal denies it closes the gateway. The bot then looks offline.' }]);
      });
    },

    'oauth2-invite-url-builder': function () {
      function paint() {
        const url = D.buildInvite(U.val('app-id'), flags(), U.val('perms') || '0');
        if (U.$('invite')) U.$('invite').value = url;
        const names = D.PERMISSIONS.filter(function (row) { return U.$('perm-' + row[1].toString()) && U.$('perm-' + row[1].toString()).checked; }).map(function (row) { return row[0]; });
        const active = document.activeElement;
        if (names.length && U.$('perms') && active && active.id && active.id.indexOf('perm-') === 0) {
          U.$('perms').value = D.sumBits(names, D.PERMISSIONS);
        }
      }
      const ids = ['app-id', 'scope-bot', 'scope-commands', 'scope-cmd-perms', 'perms'].concat(D.PERMISSIONS.map(function (row) { return 'perm-' + row[1].toString(); }));
      if (U.$('go')) U.$('go').addEventListener('click', paint);
      if (globalThis.C2S) C2S.bindLive(ids, paint);
    },

    'bot-vs-user-token-warn': function () {
      U.onRun(function () {
        const shape = D.tokenShape(U.val('token'));
        if (U.$('token')) U.$('token').value = '';
        if (shape.empty) throw new Error('Paste a token-shaped string. It is cleared from the box and is not sent anywhere.');
        const kind = shape.looksLikeToken ? 'fail' : 'pending';
        U.render(kind, shape.looksLikeToken ? 'This looks like a Discord token — reset it if it was real' : 'This does not look like a three-part token', [
          ['prefix', shape.prefix || '(none)'],
          ['segments', String(shape.segments)],
          ['segment lengths', shape.lengths.join(', ')],
          ['mfa-shaped', shape.mfa ? 'yes' : 'no']
        ], [{ level: 'warn', text: 'The value was removed from the field. Bot requests use Authorization: Bot. A Bearer user token is not a supported bot login. If this was a live token, reset it in the Developer Portal.' }]);
      });
    },

    'privileged-intents-checklist': function () {
      checklist(['chk-members', 'chk-presence', 'chk-content', 'chk-match']);
    },

    'applications-commands-scope-check': function () {
      function paint() {
        const url = D.buildInvite(U.val('app-id'), flags(), '0');
        const scopes = D.selectedScopes(flags());
        const hasCommands = scopes.indexOf('applications.commands') !== -1;
        const hasBot = scopes.indexOf('bot') !== -1;
        if (U.$('invite')) U.$('invite').value = url;
        let kind = 'pass';
        let title = 'Scopes can register slash commands';
        if (!hasCommands) { kind = 'fail'; title = 'applications.commands is missing'; }
        else if (!hasBot) { kind = 'warn'; title = 'Commands scope is on, bot scope is off'; }
        U.render(kind, title, [
          ['scopes', scopes.join(' ') || '(none)'],
          ['invite', url || '(need an application id)']
        ]);
      }
      if (U.$('go')) U.$('go').addEventListener('click', paint);
      if (globalThis.C2S) C2S.bindLive(['app-id', 'scope-bot', 'scope-commands', 'scope-cmd-perms'], paint);
    },

    'gateway-intents-bitfield-decode': function () {
      U.onRun(function () {
        const names = D.decodeBits(U.val('bits'), D.INTENTS.map(function (row) { return [row[0], BigInt(row[1])]; }));
        const privileged = names.filter(function (n) { return n === 'GUILD_MEMBERS' || n === 'GUILD_PRESENCES' || n === 'MESSAGE_CONTENT'; });
        U.render(privileged.length ? 'warn' : 'pass', names.length + ' intent(s)', [
          ['value', U.val('bits') || '0'],
          ['privileged', privileged.join(', ') || 'none']
        ], [U.table(['intent'], names.map(function (n) { return [n]; }))]);
      });
    },

    'discord-api-error-decoder': function () {
      U.onRun(function () {
        const code = U.val('code');
        const text = D.errorText(code);
        if (!text) {
          U.render('pending', 'No local note for code ' + code, [['code', code]], [{ level: 'note', text: 'Discord adds codes over time. Compare with the current API error list if this one is blank.' }]);
          return;
        }
        const kind = code === '50001' || code === '50013' || code === '40001' ? 'fail' : 'pending';
        U.render(kind, text, [['code', code]]);
      });
    },

    'slash-command-not-showing-fix': function () {
      checklist(['chk-scope', 'chk-global', 'chk-guild', 'chk-name', 'chk-ready', 'chk-cache']);
    },

    'bot-permissions-calculator': function () {
      function paint() {
        const names = D.PERMISSIONS.filter(function (row) {
          const el = U.$('perm-' + row[1].toString());
          return el && el.checked;
        }).map(function (row) { return row[0]; });
        const total = D.sumBits(names, D.PERMISSIONS);
        if (U.$('total')) U.$('total').value = total;
        const admin = names.indexOf('Administrator') !== -1;
        U.render(admin ? 'warn' : 'pass', admin ? 'Administrator is included' : 'Permission integer ' + total, [
          ['integer', total],
          ['count', String(names.length)]
        ], [U.table(['permission'], names.map(function (n) { return [n]; }))]);
      }
      const ids = D.PERMISSIONS.map(function (row) { return 'perm-' + row[1].toString(); });
      if (U.$('go')) U.$('go').addEventListener('click', paint);
      if (globalThis.C2S) C2S.bindLive(ids, paint);
    },

    'missing-access-403-guide': function () {
      checklist(['chk-in-guild', 'chk-view', 'chk-channel', 'chk-role', 'chk-intent']);
    },

    'reset-token-vs-intents': function () {
      U.onRun(function () {
        const unauth = U.$('unauth').checked;
        const close = U.$('close').checked;
        const logged = U.$('logged').checked;
        let title = 'Need more symptoms';
        let kind = 'pending';
        if (unauth) { title = 'Reset the token'; kind = 'fail'; }
        else if (close && !logged) { title = 'Intent mismatch is more likely than a bad token'; kind = 'warn'; }
        else if (logged && !close && !unauth) { title = 'The token is being accepted'; kind = 'pass'; }
        U.render(kind, title, [
          ['401 or invalid token', unauth ? 'yes' : 'no'],
          ['gateway closed on identify', close ? 'yes' : 'no'],
          ['logged in before', logged ? 'yes' : 'no']
        ], [{ level: 'note', text: '401 / 40001 means the token is wrong or was reset. A close during identify, after a previously good login, usually means a privileged intent is requested but disabled in the portal.' }]);
      });
    },

    'presence-intent-when-needed': function () {
      U.onRun(function () {
        const need = U.$('need').checked;
        U.render(need ? 'warn' : 'pass', need ? 'Turn Presence Intent on, and request GUILD_PRESENCES' : 'Leave Presence Intent off', [
          ['needed', need ? 'yes' : 'no'],
          ['bit', '1 << 8 = 256']
        ], [{ level: 'note', text: 'You need it only to receive presence updates (online, idle, dnd, offline, activities). A bot can be online itself without this intent.' }]);
      });
    },

    'server-members-intent-use-cases': function () {
      U.onRun(function () {
        const cases = ['members', 'join', 'roles', 'chunks'].filter(function (id) { return U.$(id) && U.$(id).checked; });
        U.render(cases.length ? 'warn' : 'pass', cases.length ? 'Server Members Intent is warranted' : 'You may not need Server Members Intent', [
          ['selected', cases.join(', ') || 'none'],
          ['bit', '1 << 1 = 2']
        ], [{ level: 'note', text: 'Member lists, join/leave events, and requesting all members need GUILD_MEMBERS. It is privileged. Do not enable it just to see the bot itself.' }]);
      });
    },

    'discord-webhook-vs-bot': function () {
      U.onRun(function () {
        const choice = U.val('choice');
        const map = {
          webhook: ['A webhook posts into one channel with a URL.', 'No gateway, no intents, no presence.', 'Anyone with the URL can post. Rotate it if it leaks.'],
          bot: ['A bot uses an application token and a gateway or interactions.', 'It can read context, use slash commands, and sit in many channels.', 'It needs intents and permissions. The token is not a webhook URL.']
        };
        const lines = map[choice] || map.bot;
        U.render('pending', choice === 'webhook' ? 'Use a webhook' : 'Use a bot', lines.map(function (line, i) { return ['note ' + (i + 1), line]; }));
      });
    },

    'interaction-endpoint-url-check': function () {
      U.onRun(function () {
        const issues = D.endpointIssues(U.val('url'));
        const bad = issues.some(function (line) { return line.indexOf('must') >= 0 || line.indexOf('not a URL') >= 0 || line.indexOf('localhost') >= 0; });
        U.render(bad ? 'fail' : 'pass', bad ? 'URL needs a change' : 'URL shape looks usable', issues.map(function (line, i) { return ['check', line]; }));
      });
    },

    'rate-limit-429-explainer': function () {
      U.onRun(function () {
        const parsed = D.parse429(U.val('raw'));
        if (parsed.retry == null && !parsed.message) throw new Error('Paste a 429 body or a Retry-After header.');
        U.render(parsed.global ? 'fail' : 'warn', parsed.global ? 'Global rate limit' : 'Bucket rate limit', [
          ['retry_after', parsed.retry == null ? '—' : String(parsed.retry)],
          ['global', parsed.global ? 'yes' : 'no'],
          ['message', parsed.message || '—']
        ], [{ level: 'note', text: 'Wait at least retry_after seconds. A global limit slows every route. Hammering the route keeps the bucket empty.' }]);
      });
    },

    'sharding-when-required': function () {
      U.onRun(function () {
        const advice = D.shardAdvice(U.val('guilds'));
        if (advice.error) throw new Error(advice.error);
        U.render(advice.required ? 'warn' : 'pass', advice.required ? 'Sharding is required' : 'One shard is enough', [
          ['guilds', String(advice.guilds)],
          ['threshold', '2500'],
          ['suggested shards', String(advice.suggested)]
        ], [{ level: 'note', text: 'Discord requires sharding at 2,500 guilds. The suggested count here is ceil(guilds / 1000). GET /gateway/bot is the authoritative shard number.' }]);
      });
    },

    'discord-dev-portal-checklist': function () {
      checklist(['chk-app', 'chk-bot-user', 'chk-token', 'chk-intents', 'chk-redirect', 'chk-install']);
    },

    'discord-bot-security-checklist': function () {
      checklist(['chk-secret', 'chk-reset', 'chk-admin', 'chk-intents', 'chk-mention', 'chk-public']);
    }
  };

  const tool = document.body.getAttribute('data-tool');
  if (pages[tool]) pages[tool]();
})();
