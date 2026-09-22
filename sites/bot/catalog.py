"""Discord bot mini-site copy. Flagship first, required slug order."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
from sitegen import esc, tool_shell  # noqa: E402

GROUP_ORDER = ["Invite", "Intents", "Errors", "Checklist"]

PERMS = [
    ("Create instant invite", 0), ("Kick members", 1), ("Ban members", 2), ("Administrator", 3),
    ("Manage channels", 4), ("Manage guild", 5), ("Add reactions", 6), ("View audit log", 7),
    ("Priority speaker", 8), ("Stream", 9), ("View channel", 10), ("Send messages", 11),
    ("Send TTS messages", 12), ("Manage messages", 13), ("Embed links", 14), ("Attach files", 15),
    ("Read message history", 16), ("Mention everyone", 17), ("Use external emojis", 18),
    ("Connect", 20), ("Speak", 21), ("Mute members", 22), ("Deafen members", 23),
    ("Move members", 24), ("Change nickname", 26), ("Manage nicknames", 27), ("Manage roles", 28),
    ("Manage webhooks", 29), ("Use application commands", 31), ("Manage threads", 34),
    ("Create public threads", 35), ("Send messages in threads", 38), ("Moderate members", 40),
    ("Send voice messages", 46),
]


def perm_boxes() -> str:
    labels = []
    for name, shift in PERMS:
        labels.append(f'<label><input type="checkbox" id="perm-{1 << shift}"> {esc(name)}</label>')
    return '<div class="check-row span-2">' + "".join(labels) + "</div>"


SCOPES = """<div class="span-2 check-row">
      <label><input type="checkbox" id="scope-bot" checked> bot</label>
      <label><input type="checkbox" id="scope-commands" checked> applications.commands</label>
      <label><input type="checkbox" id="scope-cmd-perms"> applications.commands.permissions.update</label>
    </div>"""

APP = """<label class="field span-2">Application ID
      <input id="app-id" inputmode="numeric" spellcheck="false" placeholder="123456789012345678" autocomplete="off"></label>"""


def page(fields, explain, button="Run"):
    return tool_shell(fields, explain, button=button)


def checks(items, explain):
    lis = []
    for cid, title, body in items:
        lis.append(f"<li><label><input type=\"checkbox\" id=\"{cid}\"> {esc(title)}</label><p>{body}</p></li>")
    return f"""
<section class="panel">
  <ul class="checklist">{''.join(lis)}</ul>
  <p class="verdict pending" id="summary" style="margin-top:0.9rem"></p>
</section>
<section class="explain">{explain}</section>
"""


TOOLS = [
    {"slug": "discord-bot-offline", "title": "Discord bot offline checklist", "nav": "Bot offline", "group": "Invite",
     "description": "Build an invite URL and walk the usual reasons a bot stays offline. No Discord API."},
    {"slug": "message-content-intent-check", "title": "Message Content Intent check", "nav": "Message content", "group": "Intents",
     "description": "Compare the portal toggle with whether your library requests the Message Content intent."},
    {"slug": "oauth2-invite-url-builder", "title": "OAuth2 invite URL builder", "nav": "Invite URL", "group": "Invite",
     "description": "Build a Discord bot invite URL from an application id, scopes, and a permission integer."},
    {"slug": "bot-vs-user-token-warn", "title": "Bot versus user token warning", "nav": "Token shape", "group": "Errors",
     "description": "Locally classify a token-shaped string, then clear it. Nothing is sent."},
    {"slug": "privileged-intents-checklist", "title": "Privileged intents checklist", "nav": "Privileged intents", "group": "Intents",
     "description": "Check the three privileged intents and that code and portal match."},
    {"slug": "applications-commands-scope-check", "title": "applications.commands scope", "nav": "Commands scope", "group": "Invite",
     "description": "Require the applications.commands scope on an invite before expecting slash commands."},
    {"slug": "gateway-intents-bitfield-decode", "title": "Gateway intents bitfield", "nav": "Intent bits", "group": "Intents",
     "description": "Decode a gateway intent integer into intent names, including privileged ones."},
    {"slug": "discord-api-error-decoder", "title": "Discord API error decoder", "nav": "Error codes", "group": "Errors",
     "description": "Look up common Discord JSON error codes such as 50001 and 50013."},
    {"slug": "slash-command-not-showing-fix", "title": "Slash command not showing", "nav": "Missing slash command", "group": "Errors",
     "description": "Checklist for slash commands that never appear in the picker."},
    {"slug": "bot-permissions-calculator", "title": "Bot permissions calculator", "nav": "Permissions", "group": "Invite",
     "description": "Sum Discord permission bits from checkboxes, including Administrator."},
    {"slug": "missing-access-403-guide", "title": "Missing access guide", "nav": "Missing access", "group": "Errors",
     "description": "Walk error 50001 Missing Access: membership, View Channel, and overwrites."},
    {"slug": "reset-token-vs-intents", "title": "Reset token or intents", "nav": "Token vs intents", "group": "Errors",
     "description": "Decide whether a failure means reset the token or fix a privileged intent mismatch."},
    {"slug": "presence-intent-when-needed", "title": "When presence intent is needed", "nav": "Presence intent", "group": "Intents",
     "description": "Presence intent is only for receiving other users’ presence. The bot can be online without it."},
    {"slug": "server-members-intent-use-cases", "title": "Server Members Intent uses", "nav": "Members intent", "group": "Intents",
     "description": "See whether your feature actually needs the privileged Server Members intent."},
    {"slug": "discord-webhook-vs-bot", "title": "Webhook versus bot", "nav": "Webhook vs bot", "group": "Invite",
     "description": "Pick a webhook or a bot from what you need to do. No API calls."},
    {"slug": "interaction-endpoint-url-check", "title": "Interaction endpoint URL", "nav": "Interactions URL", "group": "Errors",
     "description": "Check that an interactions endpoint URL is public https, and remember the PING/PONG handshake."},
    {"slug": "rate-limit-429-explainer", "title": "429 rate limit explainer", "nav": "429 explainer", "group": "Errors",
     "description": "Parse a Discord 429 body or Retry-After header and explain the wait."},
    {"slug": "sharding-when-required", "title": "When sharding is required", "nav": "Sharding", "group": "Intents",
     "description": "Discord requires sharding at 2,500 guilds. Estimate a shard count from a guild total."},
    {"slug": "discord-dev-portal-checklist", "title": "Developer Portal checklist", "nav": "Portal checklist", "group": "Checklist",
     "description": "Walk application, bot user, token, intents, and install settings in the Developer Portal."},
    {"slug": "discord-bot-security-checklist", "title": "Bot security checklist", "nav": "Security checklist", "group": "Checklist",
     "description": "A local checklist for token handling, Administrator, intents, and public install."},
]

PAGES = {
    "discord-bot-offline": """
<section class="panel">
  <div class="form-grid two">""" + APP + """
    <p class="status span-2" id="id-status" aria-live="polite"></p>
    """ + SCOPES + """
    <label class="field">Permissions integer
      <input id="perms" value="0" spellcheck="false" inputmode="numeric"></label>
  </div>
  <div class="output-head" style="margin-top:0.9rem"><h2>Invite URL</h2>
    <button type="button" class="copy-btn" data-copy="#invite">Copy</button></div>
  <textarea id="invite" class="output" readonly rows="3"></textarea>
  <ul class="checklist" style="margin-top:0.9rem">
    <li><label><input type="checkbox" id="chk-scopes"> Invite scopes</label><p>The URL includes <code>bot</code> and you used it to add this application to the server.</p></li>
    <li><label><input type="checkbox" id="chk-content"> Message Content Intent</label><p>Privileged. If the library requests it and the portal toggle is off, the gateway closes.</p></li>
    <li><label><input type="checkbox" id="chk-presence"> Presence Intent</label><p>Also privileged. Only needed if the process requests GUILD_PRESENCES.</p></li>
    <li><label><input type="checkbox" id="chk-gateway"> Gateway running</label><p>The process is up and the logs show a gateway connection, not a crash loop.</p></li>
    <li><label><input type="checkbox" id="chk-online"> Bot user online</label><p>The bot user is online, idle, or dnd in the member list.</p></li>
  </ul>
  <p class="verdict pending" id="summary" style="margin-top:0.9rem"></p>
  <p class="status" id="next"></p>
</section>
<section class="explain"><h2>No Discord API</h2><p>The invite is <code>https://discord.com/api/oauth2/authorize</code> with your application id and scopes. Presence intent is not required for every bot to show online.</p></section>
""",
    "message-content-intent-check": page("""<div class="span-2 check-row">
      <label><input type="checkbox" id="portal"> Enabled in the Developer Portal</label>
      <label><input type="checkbox" id="code"> Library requests MESSAGE_CONTENT</label>
    </div>""",
        "<h2>Mismatch</h2><p>Requesting the intent while the portal toggle is off disconnects the gateway. Leaving the portal on while the code does not request it is wasteful, not fatal.</p>",
        "Compare"),
    "oauth2-invite-url-builder": page(APP + SCOPES + perm_boxes() + """<label class="field">Permissions integer
      <input id="perms" value="0" spellcheck="false"></label>
    <label class="field span-2">Invite URL
      <textarea id="invite" class="output" readonly rows="3"></textarea></label>""",
        "<h2>URL</h2><p>Checking a permission box rewrites the integer. You can also type an integer directly. The bot scope adds <code>permissions</code> to the query.</p>",
        "Build"),
    "bot-vs-user-token-warn": page("""<label class="field span-2">Token (cleared locally, never sent)
      <input id="token" type="password" spellcheck="false" autocomplete="off" placeholder="paste then run — the field is wiped"></label>""",
        "<h2>Do not share tokens</h2><p>Bot and user tokens can both look like three base64 segments. This page reports segment counts only, then deletes the field. A real token that was pasted should be reset.</p>",
        "Check shape"),
    "privileged-intents-checklist": checks([
        ("chk-members", "Server Members Intent", "Enable it only if you need the member list, join events, or member chunks."),
        ("chk-presence", "Presence Intent", "Enable it only if you subscribe to other users’ presence."),
        ("chk-content", "Message Content Intent", "Enable it only if you read message text outside interactions and mentions."),
        ("chk-match", "Code matches the portal", "Every privileged intent the library sends is toggled on, and you are not requesting extras."),
    ], "<h2>Privileged</h2><p>All three are off by default. A request for one that is disabled closes the socket.</p>"),
    "applications-commands-scope-check": page(APP + SCOPES, "<h2>Scope</h2><p>Slash commands need <code>applications.commands</code>. The bot scope adds the bot user. Either can be used alone; both is the usual install.</p>", "Check scopes"),
    "gateway-intents-bitfield-decode": page("""<label class="field span-2">Intent integer
      <input id="bits" value="33281" spellcheck="false"></label>""",
        "<h2>Bits</h2><p>33281 is GUILDS + GUILD_MESSAGES + MESSAGE_CONTENT, a common example. Privileged names are called out. This does not connect to the gateway.</p>",
        "Decode"),
    "discord-api-error-decoder": page("""<label class="field">JSON code
      <input id="code" value="50001" spellcheck="false"></label>""",
        "<h2>Codes</h2><p>Covers frequent REST codes including 50001 Missing Access, 50013 Missing Permissions, 40001 Unauthorized, and 10062 Unknown interaction. Unknown numbers are left blank rather than guessed.</p>",
        "Look up"),
    "slash-command-not-showing-fix": checks([
        ("chk-scope", "Invite included applications.commands", "Old invites without that scope never registered commands for that user."),
        ("chk-global", "Global commands waited long enough", "Global registration can take up to an hour to show up."),
        ("chk-guild", "Guild commands targeted this server", "A guild command registered for a different id will not appear here."),
        ("chk-name", "Name is unique and lowercase", "Discord rejects duplicates and uppercase command names."),
        ("chk-ready", "The bot is in the server", "You cannot see its commands from a server it never joined."),
        ("chk-cache", "The client was restarted", "The desktop and mobile clients cache the command list."),
    ], "<h2>Still missing</h2><p>If every box is ticked and the command is still absent, compare the registration response body for a 50035 invalid form body.</p>"),
    "bot-permissions-calculator": page(perm_boxes() + """<label class="field">Integer
      <input id="total" readonly value="0"></label>""",
        "<h2>Bits</h2><p>Administrator is bit 3 (value 8) and is flagged because it bypasses channel overwrites. The integer is what the invite URL calls <code>permissions</code>.</p>",
        "Sum"),
    "missing-access-403-guide": checks([
        ("chk-in-guild", "Bot is in the server", "50001 is often just “the bot was never invited”."),
        ("chk-view", "View Channel is allowed", "A deny overwrite on the channel beats a role allow."),
        ("chk-channel", "The id is a channel the bot can see", "Unknown Channel (10003) is a different code. 50001 means the channel exists and the bot may not see it."),
        ("chk-role", "Role order is not the issue you think", "Missing Access is visibility. Manage Messages and similar failures are 50013."),
        ("chk-intent", "You are not blocked on intents instead", "Intent failures drop the gateway. 50001 is an HTTP response."),
    ], "<h2>50001</h2><p>HTTP 403 with code 50001. Fix membership and View Channel before rotating the token.</p>"),
    "reset-token-vs-intents": page("""<div class="span-2 check-row">
      <label><input type="checkbox" id="unauth"> 401 or code 40001</label>
      <label><input type="checkbox" id="close"> Gateway closes during identify</label>
      <label><input type="checkbox" id="logged"> This token has logged in before</label>
    </div>""",
        "<h2>Split</h2><p>Unauthorized means reset or replace the token. A close on identify after a good login usually means a privileged intent mismatch.</p>",
        "Decide"),
    "presence-intent-when-needed": page("""<div class="span-2 check-row"><label><input type="checkbox" id="need"> I need other users’ online status or activities</label></div>""",
        "<h2>Not for being online</h2><p>The bot’s own online status does not require the Presence intent. Requesting it without the portal toggle disconnects you.</p>",
        "Decide"),
    "server-members-intent-use-cases": page("""<div class="span-2 check-row">
      <label><input type="checkbox" id="members"> List or search members</label>
      <label><input type="checkbox" id="join"> Join and leave events</label>
      <label><input type="checkbox" id="roles"> Member role updates</label>
      <label><input type="checkbox" id="chunks"> Request all guild members</label>
    </div>""",
        "<h2>Privileged</h2><p>Any of those needs GUILD_MEMBERS. Seeing the bot user itself does not.</p>",
        "Decide"),
    "discord-webhook-vs-bot": page("""<label class="field">I need to
      <select id="choice"><option value="webhook">Post into one channel</option><option value="bot">Read, reply, or use slash commands</option></select></label>""",
        "<h2>Either tool</h2><p>Webhooks are URLs. Bots are applications. A webhook cannot replace a gateway bot, and a bot token should not be pasted where a webhook URL goes.</p>",
        "Compare"),
    "interaction-endpoint-url-check": page("""<label class="field span-2">Interactions endpoint URL
      <input id="url" spellcheck="false" placeholder="https://example.com/interactions" autocomplete="off"></label>""",
        "<h2>Handshake</h2><p>Discord sends a PING (type 1) and expects a PONG (type 1) with a valid ed25519 signature check. This page only checks the URL shape.</p>",
        "Check URL"),
    "rate-limit-429-explainer": page("""<label class="field span-2">429 body or headers
      <textarea id="raw" rows="8" spellcheck="false" placeholder='{"message":"You are being rate limited.","retry_after":1.5,"global":false}'></textarea></label>""",
        "<h2>Wait</h2><p>Honor <code>retry_after</code>. Global true means every route is slowed, not just the one you called.</p>",
        "Explain"),
    "sharding-when-required": page("""<label class="field">Guild count
      <input id="guilds" value="100" inputmode="numeric" spellcheck="false"></label>""",
        "<h2>2500</h2><p>Below 2,500 guilds, one shard is enough. At or above that, Discord requires sharding. The suggestion is ceil(guilds / 1000). Confirm with <code>GET /gateway/bot</code>.</p>",
        "Estimate"),
    "discord-dev-portal-checklist": checks([
        ("chk-app", "Application created", "You are in the right team and the right application."),
        ("chk-bot-user", "Bot user added", "The Bot tab exists and the username is the one you expect."),
        ("chk-token", "Token stored once", "The token is in a secret store. It is not in git."),
        ("chk-intents", "Intents match the code", "Privileged toggles equal the intents the process requests."),
        ("chk-redirect", "OAuth2 redirects, if any, are https", "Only needed if you use a user OAuth code flow."),
        ("chk-install", "Install link uses the scopes you meant", "bot and applications.commands are explicit, not assumed."),
    ], "<h2>Portal</h2><p>This list is local. It does not log into the Developer Portal.</p>"),
    "discord-bot-security-checklist": checks([
        ("chk-secret", "Token is not in client code", "Browsers and mobile apps must not embed the bot token."),
        ("chk-reset", "Leaked tokens were reset", "Resetting invalidates the old string immediately."),
        ("chk-admin", "Administrator is intentional", "Prefer specific permissions over bit 8."),
        ("chk-intents", "Privileged intents are minimal", "Message content, members, and presence are off unless a feature needs them."),
        ("chk-mention", "Public bot rules are understood", "A public bot can be invited by other people. Limit what the default permissions allow."),
        ("chk-public", "Interactions are verified", "If you set an interactions endpoint, you verify the ed25519 signature before doing work."),
    ], "<h2>Local only</h2><p>Nothing here calls Discord. Reset a token in the Developer Portal, not on this page.</p>"),
}
