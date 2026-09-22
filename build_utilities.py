#!/usr/bin/env python3
"""Generate the cron2systemd.dev utilities static site into ./output.

Zero pip dependencies. Stdlib only.

Run:
    python3 build_utilities.py

Then serve the artifact root:
    python3 -m http.server 8080 --directory output
"""

from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://cron2systemd.dev"
ADSENSE_CLIENT = "ca-pub-7911637649628733"
TIP_JAR = "https://buymeacoffee.com/1126"
SITE_NAME = "cron2systemd"
OUTPUT = Path(__file__).resolve().parent / "output"
ROOT = Path(__file__).resolve().parent

# Flagship converter lives at repo root today; copied into the artifact so a
# Pages output-directory switch to `output/` does not drop the original tool.
FLAGSHIP = {
    "slug": "oncalendar-cron-converter",
    "title": "OnCalendar ↔ crontab converter",
    "description": (
        "Bidirectional systemd timer OnCalendar= to 5-field crontab translator "
        "with plain-English explanations and quirk notes."
    ),
}

TOOLS = [
    {
        "slug": "cron-to-systemd-timer",
        "title": "Cron to systemd timer",
        "nav": "Cron → timer units",
        "description": (
            "Convert a crontab schedule into a systemd .service plus .timer "
            "with OnCalendar=, Persistent=, and a oneshot ExecStart."
        ),
        "keywords": "cron to systemd timer, OnCalendar, crontab to unit file",
        "group": "Scheduling",
    },
    {
        "slug": "crontab-generator",
        "title": "Crontab generator",
        "nav": "Crontab generator",
        "description": (
            "Build a 5-field cron expression from dropdowns and get an English "
            "explanation of when it fires."
        ),
        "keywords": "crontab generator, cron expression builder",
        "group": "Scheduling",
    },
    {
        "slug": "systemd-service-builder",
        "title": "systemd service builder",
        "nav": "Service unit builder",
        "description": (
            "Generate a systemd unit file from ExecStart, Restart, User, "
            "Environment, and hardening toggles."
        ),
        "keywords": "systemd service generator, unit file builder",
        "group": "systemd",
    },
    {
        "slug": "chmod-permissions-calculator",
        "title": "chmod permissions calculator",
        "nav": "chmod calculator",
        "description": (
            "Convert Unix file modes both ways: 755 ↔ rwxr-xr-x, with setuid, "
            "setgid, and sticky bits."
        ),
        "keywords": "chmod calculator, 755, rwxr-xr-x, unix permissions",
        "group": "Files",
    },
    {
        "slug": "cidr-subnet-calculator",
        "title": "CIDR subnet calculator",
        "nav": "CIDR calculator",
        "description": (
            "Expand an IPv4 CIDR into netmask, network, broadcast, usable host "
            "range, and host count."
        ),
        "keywords": "CIDR calculator, subnet, netmask, IP range",
        "group": "Network",
    },
    {
        "slug": "epoch-unix-timestamp-converter",
        "title": "Unix epoch converter",
        "nav": "Epoch converter",
        "description": (
            "Convert between Unix timestamps (seconds or milliseconds) and "
            "human-readable UTC / local datetimes."
        ),
        "keywords": "unix timestamp, epoch converter, milliseconds",
        "group": "Time",
    },
    {
        "slug": "htpasswd-generator",
        "title": "htpasswd generator",
        "nav": "htpasswd generator",
        "description": (
            "Create Apache htpasswd lines entirely in the browser using "
            "{SHA} Base64(SHA-1) via Web Crypto."
        ),
        "keywords": "htpasswd generator, apache basic auth, SHA1",
        "group": "Auth",
    },
    {
        "slug": "docker-run-to-compose",
        "title": "docker run → Compose",
        "nav": "docker run → Compose",
        "description": (
            "Parse a docker run command and emit a Compose service YAML snippet "
            "with ports, env, volumes, and restart policy."
        ),
        "keywords": "docker run to compose, docker-compose yaml",
        "group": "Containers",
    },
    {
        "slug": "nginx-reverse-proxy-builder",
        "title": "nginx reverse proxy builder",
        "nav": "nginx reverse proxy",
        "description": (
            "Generate an nginx server block for reverse proxying, with TLS, "
            "WebSocket upgrade headers, and body-size limits."
        ),
        "keywords": "nginx reverse proxy, server block generator, websocket",
        "group": "Network",
    },
    {
        "slug": "caddyfile-generator",
        "title": "Caddyfile generator",
        "nav": "Caddyfile generator",
        "description": (
            "Build a Caddyfile reverse-proxy site block with automatic HTTPS "
            "and optional gzip encoding."
        ),
        "keywords": "Caddyfile generator, caddy reverse proxy",
        "group": "Network",
    },
    {
        "slug": "ssh-keygen-command-builder",
        "title": "ssh-keygen command builder",
        "nav": "ssh-keygen builder",
        "description": (
            "Compose a safe ssh-keygen invocation for ed25519 (or RSA/ECDSA) "
            "with comment, path, and KDF rounds."
        ),
        "keywords": "ssh-keygen, ed25519, generate ssh key command",
        "group": "Auth",
    },
    {
        "slug": "base64-yaml-secret-encoder",
        "title": "Kubernetes Secret encoder",
        "nav": "K8s Secret encoder",
        "description": (
            "Base64-encode multi-line values into a Kubernetes Secret YAML "
            "manifest using TextEncoder (UTF-8)."
        ),
        "keywords": "kubernetes secret, base64 yaml, k8s opaque secret",
        "group": "Containers",
    },
    {
        "slug": "curl-to-python-fetch",
        "title": "cURL to Python",
        "nav": "cURL → Python",
        "description": (
            "Translate a curl command into Python requests and httpx client "
            "code, including headers, auth, and JSON bodies."
        ),
        "keywords": "curl to python, requests, httpx",
        "group": "HTTP",
    },
    {
        "slug": "json-to-yaml-converter",
        "title": "JSON to YAML converter",
        "nav": "JSON → YAML",
        "description": (
            "Convert JSON objects and arrays to YAML with a small in-browser "
            "emitter — no libraries."
        ),
        "keywords": "json to yaml, yaml emitter",
        "group": "Data",
    },
    {
        "slug": "keepalive-timeout-calculator",
        "title": "Keepalive timeout calculator",
        "nav": "Keepalive calculator",
        "description": (
            "Estimate proxy idle timeouts, upstream keepalive pools, and "
            "concurrency from RPS, latency, and backend count."
        ),
        "keywords": "keepalive timeout, nginx upstream, connection pool",
        "group": "Network",
    },
    {
        "slug": "dns-record-bind-formatter",
        "title": "BIND DNS record formatter",
        "nav": "BIND zone formatter",
        "description": (
            "Turn A, CNAME, TXT, and MX fields into BIND zone-file lines with "
            "TTL and origin."
        ),
        "keywords": "BIND zone file, DNS records, A CNAME TXT MX",
        "group": "Network",
    },
    {
        "slug": "systemd-journald-filter-builder",
        "title": "journalctl filter builder",
        "nav": "journalctl builder",
        "description": (
            "Assemble a journalctl command from unit, priority, time window, "
            "boot, and output format."
        ),
        "keywords": "journalctl, systemd journal, log filter",
        "group": "systemd",
    },
    {
        "slug": "iptables-rule-builder",
        "title": "iptables rule builder",
        "nav": "iptables builder",
        "description": (
            "Build allow/drop ingress and egress iptables (or ip6tables) rules "
            "with protocol, port, and connection state."
        ),
        "keywords": "iptables generator, firewall rule, ip6tables",
        "group": "Network",
    },
    {
        "slug": "uuid-v4-generator",
        "title": "UUID v4 generator",
        "nav": "UUID v4 generator",
        "description": (
            "Generate cryptographically random RFC 4122 UUID version 4 values, "
            "one at a time or in bulk."
        ),
        "keywords": "uuid v4 generator, random uuid, crypto.randomUUID",
        "group": "Data",
    },
    {
        "slug": "regex-cheatsheet-tester",
        "title": "Regex cheatsheet tester",
        "nav": "Regex tester",
        "description": (
            "Test JavaScript / grep / sed-style regular expressions against "
            "sample text with a POSIX vs PCRE cheatsheet."
        ),
        "keywords": "regex tester, grep sed bash regex cheatsheet",
        "group": "Data",
    },
    {
        "slug": "solana-mint-check",
        "title": "Solana mint authority check",
        "nav": "Solana mint check",
        "description": (
            "Paste a Solana token mint and see whether mintAuthority and "
            "freezeAuthority are revoked. Uses a public JSON-RPC getAccountInfo "
            "call from the browser."
        ),
        "keywords": "solana mint authority, freeze authority revoked, spl token",
        "group": "Checks",
    },
    {
        "slug": "safe-mech-decode",
        "title": "Safe execTransaction decoder",
        "nav": "Safe tx decode",
        "description": (
            "Decode a Gnosis Safe execTransaction from a transaction hash or "
            "raw calldata. Shows to, value, and inner data length, with notes "
            "on mech delivery."
        ),
        "keywords": "gnosis safe execTransaction decode, mech delivery, calldata",
        "group": "Checks",
    },
    {
        "slug": "x402-inspect",
        "title": "x402 payment inspector",
        "nav": "x402 inspect",
        "description": (
            "Inspect an HTTP 402 / x402 payment-required response for network, "
            "payTo, asset, and amount. Paste headers or try a CORS fetch."
        ),
        "keywords": "x402, HTTP 402 payment required, payTo, payment-required",
        "group": "Checks",
    },
    {
        "slug": "discord-bot-offline",
        "title": "Discord bot offline checklist",
        "nav": "Discord bot checklist",
        "description": (
            "Build a Discord bot invite URL from an application ID and scopes, "
            "and walk a checklist for intents, the gateway, and an offline bot user."
        ),
        "keywords": "discord bot offline, invite url, message content intent",
        "group": "Checks",
    },
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def canonical_for(slug: str | None) -> str:
    if not slug:
        return BASE_URL + "/"
    return f"{BASE_URL}/{slug}"


SITE_CSS = r"""
:root {
  color-scheme: dark;
  --bg: #09090b;
  --bg-accent: #131316;
  --surface: #18181b;
  --surface-2: #1f1f23;
  --ink: #fafafa;
  --muted: #a1a1aa;
  --line: #3f3f46;
  --line-soft: #27272a;
  --accent: #38bdf8;
  --accent-2: #2dd4bf;
  --accent-soft: rgba(56, 189, 248, 0.12);
  --warn-bg: #422006;
  --warn-ink: #fbbf24;
  --error-bg: #3f1219;
  --error-ink: #fb7185;
  --ok-bg: #052e16;
  --ok-ink: #4ade80;
  --placeholder: #71717a;
  --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  --radius: 14px;
  --sans: Inter, ui-sans-serif, system-ui, sans-serif;
  --mono: ui-monospace, "JetBrains Mono", "SF Mono", Menlo, monospace;
  --sidebar: 18.5rem;
}

html[data-theme="light"] {
  color-scheme: light;
  --bg: #f4f4f5;
  --bg-accent: #e4e4e7;
  --surface: #ffffff;
  --surface-2: #fafafa;
  --ink: #18181b;
  --muted: #52525b;
  --line: #d4d4d8;
  --line-soft: #e4e4e7;
  --accent: #0284c7;
  --accent-2: #0d9488;
  --accent-soft: rgba(2, 132, 199, 0.1);
  --warn-bg: #fef3c7;
  --warn-ink: #92400e;
  --error-bg: #fee2e2;
  --error-ink: #9f1239;
  --ok-bg: #dcfce7;
  --ok-ink: #166534;
  --placeholder: #a1a1aa;
  --shadow: 0 12px 36px rgba(24, 24, 27, 0.08);
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  font-family: var(--sans);
  background:
    radial-gradient(900px 420px at 0% -10%, rgba(56, 189, 248, 0.08), transparent 55%),
    radial-gradient(700px 380px at 100% 0%, rgba(45, 212, 191, 0.06), transparent 50%),
    var(--bg);
  color: var(--ink);
  line-height: 1.55;
  min-height: 100vh;
}

a { color: var(--accent); text-decoration-thickness: 1px; }
a:hover { color: var(--accent-2); }

.skip-link {
  position: absolute;
  left: 1rem;
  top: -4rem;
  background: var(--accent);
  color: var(--bg);
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  z-index: 20;
}
.skip-link:focus { top: 1rem; }

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 8;
  backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--bg) 86%, transparent);
  border-bottom: 1px solid var(--line-soft);
}

.header-inner {
  width: min(1280px, calc(100% - 2rem));
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 0.55rem;
  font-family: var(--mono);
  font-weight: 600;
  color: var(--ink);
  text-decoration: none;
  letter-spacing: 0.01em;
}
.brand:hover { color: var(--accent); }
.brand small {
  font-weight: 400;
  color: var(--muted);
  font-size: 0.78rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-toggle,
.theme-toggle,
.copy-btn,
.btn,
.preset {
  font: inherit;
  cursor: pointer;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  border-radius: 999px;
}

.nav-toggle,
.theme-toggle {
  padding: 0.35rem 0.85rem;
  font-size: 0.85rem;
}
.nav-toggle { display: none; }

.theme-toggle:hover,
.copy-btn:hover,
.btn:hover,
.preset:hover,
.nav-toggle:hover {
  border-color: var(--accent);
}

.layout {
  width: min(1280px, calc(100% - 2rem));
  margin: 0 auto;
  display: grid;
  grid-template-columns: var(--sidebar) minmax(0, 1fr);
  gap: 1.4rem;
  padding: 1.2rem 0 2.5rem;
  align-items: start;
}

.sidebar {
  position: sticky;
  top: 4.2rem;
  max-height: calc(100vh - 5rem);
  overflow: auto;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 0.9rem 0.85rem 1rem;
  box-shadow: var(--shadow);
}

.sidebar h2 {
  margin: 0.85rem 0 0.35rem;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 600;
}
.sidebar h2:first-child { margin-top: 0.15rem; }

.sidebar a {
  display: block;
  color: var(--ink);
  text-decoration: none;
  font-size: 0.88rem;
  padding: 0.28rem 0.5rem;
  border-radius: 8px;
}
.sidebar a:hover { background: var(--accent-soft); color: var(--accent); }
.sidebar a[aria-current="page"] {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}

.main-panel { min-width: 0; }

.hero, .tool-card, .panel, .tip-jar, .ad-slot, .explain, .cheatsheet {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.hero {
  padding: 1.4rem 1.4rem 1.3rem;
  margin-bottom: 1rem;
}
.hero h1, .tool-head h1 {
  margin: 0 0 0.5rem;
  font-size: clamp(1.55rem, 3vw, 2.2rem);
  letter-spacing: -0.03em;
  line-height: 1.15;
}
.lede {
  margin: 0;
  color: var(--muted);
  max-width: 46rem;
}

.crumb {
  margin: 0 0 0.45rem;
  font-size: 0.82rem;
  color: var(--muted);
}
.crumb a { color: var(--muted); }

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.8rem;
}

.tool-card {
  padding: 1rem 1.05rem 1.1rem;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-height: 8.2rem;
}
.tool-card:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
}
.tool-card h2 {
  margin: 0;
  font-size: 1.02rem;
  letter-spacing: -0.02em;
}
.tool-card p {
  margin: 0;
  color: var(--muted);
  font-size: 0.88rem;
}
.tool-card .kicker {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--accent-2);
}

.flagship {
  border-color: var(--accent);
  background:
    linear-gradient(180deg, var(--accent-soft), transparent 55%),
    var(--surface);
  margin-bottom: 1rem;
  min-height: auto;
}

.tool-head { margin-bottom: 0.9rem; }

.panel {
  padding: 1rem 1.1rem 1.15rem;
  margin-bottom: 0.9rem;
}
.panel h2 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem 0.9rem;
}
.form-grid.two { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.span-2 { grid-column: 1 / -1; }

label.field, .field {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
  font-size: 0.82rem;
  color: var(--muted);
  min-width: 0;
}

input[type="text"],
input[type="number"],
input[type="password"],
input[type="datetime-local"],
input[type="email"],
select,
textarea {
  font-family: var(--mono);
  font-size: 0.92rem;
  color: var(--ink);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.55rem 0.7rem;
  width: 100%;
}
textarea { min-height: 8rem; resize: vertical; line-height: 1.45; }
input::placeholder, textarea::placeholder { color: var(--placeholder); }

input:focus-visible,
select:focus-visible,
textarea:focus-visible,
.theme-toggle:focus-visible,
.copy-btn:focus-visible,
.btn:focus-visible,
.preset:focus-visible,
.nav-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.check-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem 1rem;
  align-items: center;
  font-size: 0.9rem;
  color: var(--ink);
}
.check-row label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--ink);
}

.perm-grid {
  display: grid;
  grid-template-columns: 6rem repeat(3, 1fr);
  gap: 0.35rem 0.5rem;
  align-items: center;
  font-family: var(--mono);
  font-size: 0.85rem;
}
.perm-grid span.head { color: var(--muted); font-size: 0.75rem; }

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.75rem;
}

.btn, .copy-btn, .preset {
  padding: 0.4rem 0.85rem;
  font-size: 0.85rem;
}
.btn.primary {
  background: var(--accent);
  color: #082f49;
  border-color: transparent;
  font-weight: 650;
}
html[data-theme="light"] .btn.primary { color: #fff; }

.preset-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.8rem;
}

.output {
  font-family: var(--mono);
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.85rem;
  min-height: 4.5rem;
  font-size: 0.86rem;
  line-height: 1.45;
}

.output-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.45rem;
}
.output-head h2, .output-head h3 {
  margin: 0;
  font-size: 0.95rem;
}

.status {
  min-height: 1.3rem;
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0.4rem 0 0;
}
.status.error { color: var(--error-ink); }
.status.warn { color: var(--warn-ink); }
.status.ok { color: var(--ok-ink); }

.banner {
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  font-size: 0.88rem;
  margin: 0.5rem 0;
}
.banner.note { background: var(--accent-soft); }
.banner.warn { background: var(--warn-bg); color: var(--warn-ink); }
.banner.error { background: var(--error-bg); color: var(--error-ink); }

.kv {
  display: grid;
  grid-template-columns: 11rem minmax(0, 1fr);
  gap: 0.35rem 0.8rem;
  font-size: 0.92rem;
}
.kv dt { color: var(--muted); font-family: var(--mono); font-size: 0.8rem; }
.kv dd { margin: 0; font-family: var(--mono); overflow-wrap: anywhere; }

.explain, .cheatsheet {
  padding: 1rem 1.1rem;
  margin: 0.9rem 0;
}
.explain h2, .cheatsheet h2 { margin: 0 0 0.5rem; font-size: 1rem; }
.cheatsheet table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
.cheatsheet th, .cheatsheet td {
  text-align: left;
  padding: 0.35rem 0.4rem;
  border-bottom: 1px solid var(--line-soft);
  vertical-align: top;
}
.cheatsheet code, code {
  font-family: var(--mono);
  font-size: 0.86em;
  background: var(--bg-accent);
  padding: 0.05em 0.32em;
  border-radius: 5px;
}

.match-hit {
  background: rgba(56, 189, 248, 0.28);
  outline: 1px solid var(--accent);
  border-radius: 3px;
}

.ad-slot {
  margin: 1rem 0;
  border-style: dashed;
  min-height: 72px;
  display: grid;
  place-items: center;
  color: var(--placeholder);
  font-size: 0.82rem;
  box-shadow: none;
}

.tip-jar {
  margin: 1rem 0 0;
  padding: 1rem 1.15rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem 1.1rem;
}
.tip-copy p { margin: 0; color: var(--muted); font-size: 0.92rem; }
.tip-kicker {
  font-weight: 650;
  color: var(--ink) !important;
  font-size: 0.8rem !important;
  margin-bottom: 0.2rem !important;
}
.tip-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.1rem;
  border-radius: 999px;
  background: var(--accent);
  color: #082f49;
  text-decoration: none;
  font-weight: 650;
}
html[data-theme="light"] .tip-btn { color: #fff; }
.tip-btn:hover { filter: brightness(1.08); color: #082f49; }

.site-footer {
  width: min(1280px, calc(100% - 2rem));
  margin: 0 auto;
  padding: 0 0 2.4rem;
  color: var(--muted);
  font-size: 0.88rem;
}
.site-footer p { margin: 0; }

.verdict {
  font-family: var(--mono);
  font-weight: 700;
  letter-spacing: 0.06em;
  font-size: 1.15rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  text-align: center;
  margin: 0 0 0.85rem;
}
.verdict.pass { background: var(--ok-bg); color: var(--ok-ink); }
.verdict.fail { background: var(--error-bg); color: var(--error-ink); }
.verdict.pending {
  background: var(--surface-2);
  color: var(--muted);
  letter-spacing: 0;
  font-weight: 600;
  font-size: 0.95rem;
}

.checklist {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.55rem;
}
.checklist li {
  background: var(--bg);
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
}
.checklist label {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
  color: var(--ink);
  font-size: 0.95rem;
}
.checklist input { margin-top: 0.22rem; }
.checklist p {
  margin: 0.28rem 0 0 1.55rem;
  color: var(--muted);
  font-size: 0.82rem;
}

.req-list { display: grid; gap: 0.7rem; }
.req-card {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  background: var(--bg);
}
.req-card h3 {
  margin: 0 0 0.45rem;
  font-size: 0.9rem;
}

.rows { display: grid; gap: 0.55rem; }
.row-inline {
  display: grid;
  grid-template-columns: 5.5rem 1fr 1.4fr 4.5rem auto;
  gap: 0.4rem;
  align-items: center;
}
@media (max-width: 720px) {
  .row-inline { grid-template-columns: 1fr 1fr; }
  .row-inline .grow { grid-column: 1 / -1; }
}

@media (max-width: 920px) {
  .nav-toggle { display: inline-flex; }
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: static;
    max-height: none;
    display: none;
  }
  .sidebar.open { display: block; }
  .kv { grid-template-columns: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; scroll-behavior: auto !important; }
}
"""

SHARED_JS = r"""
'use strict';
(function () {
  const KEY = 'c2s-theme';
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const navBtn = document.getElementById('nav-toggle');
  const sidebar = document.getElementById('sidebar');

  function preferred() {
    const saved = localStorage.getItem(KEY);
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function apply(theme) {
    root.setAttribute('data-theme', theme);
    if (toggle) {
      toggle.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      toggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    }
  }
  apply(preferred());
  if (toggle) {
    toggle.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(KEY, next);
      apply(next);
    });
  }
  if (navBtn && sidebar) {
    navBtn.addEventListener('click', function () {
      const open = sidebar.classList.toggle('open');
      navBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  async function copyText(text) {
    if (!text) return false;
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      const area = document.createElement('textarea');
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      document.body.removeChild(area);
      return true;
    }
  }

  document.addEventListener('click', function (ev) {
    const btn = ev.target.closest('[data-copy]');
    if (!btn) return;
    const sel = btn.getAttribute('data-copy');
    const el = sel ? document.querySelector(sel) : null;
    const text = el ? (el.value != null ? el.value : el.textContent) : '';
    copyText(text).then(function (ok) {
      if (!ok) return;
      const prev = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = prev; }, 1400);
    });
  });

  globalThis.C2S = {
    copyText: copyText,
    bindLive: function (ids, fn) {
      ids.forEach(function (id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', fn);
        el.addEventListener('change', fn);
      });
      fn();
    },
    shellQuote: function (s) {
      if (s === '') return "''";
      if (/^[A-Za-z0-9_./:=@%+-]+$/.test(s)) return s;
      return "'" + String(s).replace(/'/g, "'\\''") + "'";
    },
    tokenize: function (input) {
      const tokens = [];
      let i = 0;
      const str = String(input).replace(/\\\s*\n/g, ' ');
      while (i < str.length) {
        while (i < str.length && /\s/.test(str[i])) i++;
        if (i >= str.length) break;
        const ch = str[i];
        if (ch === '"' || ch === "'") {
          const q = str[i++];
          let t = '';
          while (i < str.length && str[i] !== q) {
            if (str[i] === '\\' && i + 1 < str.length) {
              t += str[i + 1];
              i += 2;
              continue;
            }
            t += str[i++];
          }
          if (i < str.length) i++;
          tokens.push(t);
        } else {
          let t = '';
          while (i < str.length && !/\s/.test(str[i])) {
            if (str[i] === '\\' && i + 1 < str.length) {
              t += str[i + 1];
              i += 2;
              continue;
            }
            t += str[i++];
          }
          tokens.push(t);
        }
      }
      return tokens;
    },
    utf8ToB64: function (text) {
      const bytes = new TextEncoder().encode(text);
      let bin = '';
      const chunk = 0x8000;
      for (let i = 0; i < bytes.length; i += chunk) {
        bin += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
      }
      return btoa(bin);
    },
    yamlString: function (value) {
      if (value == null) return 'null';
      if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'null';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      const s = String(value);
      if (s === '') return "''";
      if (/^[-]?(\d+(\.\d+)?)$/.test(s) || /^(true|false|null|yes|no|on|off)$/i.test(s)) {
        return JSON.stringify(s);
      }
      if (/[:#{}[\],&*?|<>=!%@`']/.test(s) || /\s/.test(s) || s !== s.trim()) {
        return JSON.stringify(s);
      }
      return s;
    }
  };
})();
"""


def sidebar_html(current: str | None) -> str:
    groups: dict[str, list[dict]] = {}
    for tool in TOOLS:
        groups.setdefault(tool["group"], []).append(tool)
    order = ["Scheduling", "systemd", "Network", "Containers", "Auth", "HTTP", "Time", "Files", "Data", "Checks"]
    parts = [
        '<h2>Flagship</h2>',
        f'<a href="{href_for(FLAGSHIP["slug"], current)}"'
        + (' aria-current="page"' if current == FLAGSHIP["slug"] else '')
        + ">"
        + esc(FLAGSHIP["title"])
        + "</a>",
        f'<a href="{href_for(None, current)}"'
        + (' aria-current="page"' if current is None else "")
        + ">All tools</a>",
    ]
    for name in order:
        tools = groups.get(name)
        if not tools:
            continue
        parts.append(f"<h2>{esc(name)}</h2>")
        for tool in tools:
            cur = ' aria-current="page"' if current == tool["slug"] else ""
            parts.append(
                f'<a href="{href_for(tool["slug"], current)}"{cur}>{esc(tool["nav"])}</a>'
            )
    return "\n".join(parts)


def href_for(slug: str | None, current: str | None) -> str:
    """Relative href from hub (depth 0) or a tool page (depth 1)."""
    depth = 0 if current is None else 1
    prefix = "../" if depth else ""
    if slug is None:
        return prefix if depth else "./"
    return f"{prefix}{slug}/"


def json_ld(name: str, url: str, description: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": name,
        "url": url,
        "description": description,
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Any",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
    }
    return json.dumps(payload, indent=2)


def page(
    *,
    slug: str | None,
    title: str,
    description: str,
    body: str,
    extra_js: list[str] | None = None,
    extra_head: str = "",
) -> str:
    canonical = canonical_for(slug)
    depth = 0 if slug is None else 1
    asset = "../assets" if depth else "assets"
    scripts = [f'<script src="{asset}/app.js"></script>']
    for src in extra_js or []:
        scripts.append(f'<script src="{src}"></script>')
    og_title = title if SITE_NAME.lower() in title.lower() else f"{title} — {SITE_NAME}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(og_title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#09090b">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:title" content="{esc(og_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(og_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
     crossorigin="anonymous"></script>
  <link rel="icon" href="{asset}/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{asset}/site.css">
  {extra_head}
  <script type="application/ld+json">
{json_ld(title, canonical, description)}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{href_for(None, slug)}">cron2systemd <small>dev utilities</small></a>
      <div class="header-actions">
        <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="sidebar">Menu</button>
        <button type="button" class="theme-toggle" id="theme-toggle">Theme</button>
      </div>
    </div>
  </header>
  <div class="layout">
    <nav class="sidebar" id="sidebar" aria-label="All tools">
      {sidebar_html(slug)}
    </nav>
    <div class="main-panel">
      <main id="main">
        {body}
        <!-- Carbon / EthicalAds slot: insert provider markup here when a placement ID exists.
             Suggested sizes: 728×90 desktop, 320×50 mobile. Do not invent a slot ID. -->
        <div class="ad-slot" aria-hidden="true">Advertisement placeholder</div>
        <!-- AdSense in-article / display unit: keep publisher script in <head> for verification.
             Replace this container with an <ins class="adsbygoogle"> unit after a slot is created. -->
        <aside class="tip-jar" aria-label="Support this tool">
          <div class="tip-copy">
            <p class="tip-kicker">Support this tool</p>
            <p>If a lookup in the man pages was skipped today, you can buy me a coffee.</p>
          </div>
          <a class="tip-btn" href="{TIP_JAR}" target="_blank" rel="noopener noreferrer">
            <span aria-hidden="true">☕</span> Buy me a coffee
          </a>
        </aside>
      </main>
    </div>
  </div>
  <footer class="site-footer">
    <p>
      Static, browser-only tools on <a href="{esc(BASE_URL + '/')}">{esc(SITE_NAME)}</a>.
      No accounts. RPC and URL checks run in your browser only when you ask.
      · <a href="{TIP_JAR}" target="_blank" rel="noopener noreferrer">Buy me a coffee</a>
    </p>
  </footer>
  {''.join(scripts)}
</body>
</html>
"""


def hub_body() -> str:
    cards = [
        f"""<a class="tool-card flagship" href="{FLAGSHIP['slug']}/">
        <span class="kicker">Flagship converter</span>
        <h2>{esc(FLAGSHIP['title'])}</h2>
        <p>{esc(FLAGSHIP['description'])}</p>
      </a>"""
    ]
    for tool in TOOLS:
        cards.append(
            f"""<a class="tool-card" href="{tool['slug']}/">
        <span class="kicker">{esc(tool['group'])}</span>
        <h2>{esc(tool['title'])}</h2>
        <p>{esc(tool['description'])}</p>
      </a>"""
        )
    return f"""
      <section class="hero">
        <p class="crumb">cron2systemd.dev</p>
        <h1>DevOps utilities that run in your browser</h1>
        <p class="lede">
          Client-side converters and builders for cron, systemd, nginx, Docker,
          DNS, and the other snippets you always end up grepping man pages for,
          plus Solana mint, Safe calldata, x402, and Discord invite checks.
          The original <a href="{FLAGSHIP['slug']}/">OnCalendar ↔ crontab</a> translator
          is included so this hub can be the static-host output root without dropping
          the flagship tool.
        </p>
      </section>
      <section class="tool-grid" aria-label="All tools">
        {''.join(cards)}
      </section>
    """


def tool_wrap(tool: dict, inner: str) -> str:
    return f"""
      <header class="tool-head">
        <p class="crumb"><a href="../">All tools</a> / {esc(tool['group'])}</p>
        <h1>{esc(tool['title'])}</h1>
        <p class="lede">{esc(tool['description'])}</p>
      </header>
      {inner}
    """


def _by_slug() -> dict[str, dict]:
    return {t["slug"]: t for t in TOOLS}


# ---------------------------------------------------------------------------
# Per-tool HTML fragments (inner main content)
# ---------------------------------------------------------------------------

HTML = {}

HTML["cron-to-systemd-timer"] = r"""
<section class="panel">
  <div class="preset-row">
    <button type="button" class="preset" data-cron="0 2 * * 1">Mon 02:00</button>
    <button type="button" class="preset" data-cron="*/15 * * * *">Every 15 min</button>
    <button type="button" class="preset" data-cron="0 4 * * *">Daily 04:00</button>
    <button type="button" class="preset" data-cron="@hourly">@hourly</button>
    <button type="button" class="preset" data-cron="30 4 1,15 * 5">1st/15th + Fri</button>
  </div>
  <div class="form-grid two">
    <label class="field span-2">Crontab (5 fields or @hourly / @daily / @weekly / @monthly / @yearly / @reboot)
      <textarea id="cron" spellcheck="false" rows="3">0 2 * * 1</textarea>
    </label>
    <label class="field">Unit name<input id="unit" value="site-backup" spellcheck="false"></label>
    <label class="field">User<input id="user" value="root" spellcheck="false"></label>
    <label class="field span-2">Description<input id="desc" value="Nightly site backup"></label>
    <label class="field span-2">ExecStart<input id="exec" value="/usr/local/bin/backup.sh" spellcheck="false"></label>
    <label class="field">AccuracySec<input id="accuracy" value="1min" spellcheck="false"></label>
    <label class="field">WorkingDirectory<input id="workdir" value="" placeholder="optional" spellcheck="false"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="persistent" checked> Persistent=true</label>
      <label><input type="checkbox" id="oneshot" checked> Type=oneshot</label>
    </div>
  </div>
  <p class="status" id="status"></p>
  <p class="lede" id="explain" style="margin-top:0.6rem"></p>
</section>
<section class="panel">
  <div class="output-head"><h2 id="timer-name">site-backup.timer</h2>
    <button type="button" class="copy-btn" data-copy="#timer-out">Copy</button></div>
  <textarea id="timer-out" class="output" readonly rows="14"></textarea>
</section>
<section class="panel">
  <div class="output-head"><h2 id="service-name">site-backup.service</h2>
    <button type="button" class="copy-btn" data-copy="#service-out">Copy</button></div>
  <textarea id="service-out" class="output" readonly rows="14"></textarea>
</section>
"""

HTML["crontab-generator"] = r"""
<section class="panel">
  <div class="preset-row">
    <button type="button" class="preset" data-preset="hourly">Hourly</button>
    <button type="button" class="preset" data-preset="daily">Daily midnight</button>
    <button type="button" class="preset" data-preset="weekday">Weekdays 09:00</button>
    <button type="button" class="preset" data-preset="weekly">Sunday midnight</button>
    <button type="button" class="preset" data-preset="monthly">1st of month</button>
    <button type="button" class="preset" data-preset="every15">Every 15 minutes</button>
  </div>
  <div class="form-grid">
    <label class="field">Minute
      <select id="min-mode">
        <option value="every">Every minute (*)</option>
        <option value="step">Every N minutes</option>
        <option value="specific" selected>Specific</option>
        <option value="range">Range</option>
      </select>
      <input id="min-val" value="0" placeholder="0 or 0,15,30">
    </label>
    <label class="field">Hour
      <select id="hour-mode">
        <option value="every">Every hour (*)</option>
        <option value="step">Every N hours</option>
        <option value="specific" selected>Specific</option>
        <option value="range">Range</option>
      </select>
      <input id="hour-val" value="2" placeholder="2 or 9,17">
    </label>
    <label class="field">Day of month
      <select id="dom-mode">
        <option value="every" selected>Every day (*)</option>
        <option value="step">Every N days</option>
        <option value="specific">Specific</option>
        <option value="range">Range</option>
      </select>
      <input id="dom-val" value="*" placeholder="1 or 1,15">
    </label>
    <label class="field">Month
      <select id="mon-mode">
        <option value="every" selected>Every month (*)</option>
        <option value="specific">Specific (1-12 or JAN)</option>
        <option value="range">Range</option>
      </select>
      <input id="mon-val" value="*" placeholder="* or 1-6">
    </label>
    <label class="field">Day of week
      <select id="dow-mode">
        <option value="every" selected>Every weekday (*)</option>
        <option value="specific">Specific (0-7 or MON)</option>
        <option value="range">Range (e.g. 1-5)</option>
      </select>
      <input id="dow-val" value="*" placeholder="1-5 for weekdays">
    </label>
    <label class="field">Command (optional)
      <input id="command" placeholder="/usr/local/bin/job.sh" spellcheck="false">
    </label>
  </div>
  <p class="banner note">0 = Sunday in cron (and 7). Monday is 1. systemd “weekly” is Monday — cron @weekly is Sunday.</p>
</section>
<section class="panel">
  <div class="output-head"><h2>Cron expression</h2>
    <button type="button" class="copy-btn" data-copy="#cron-out">Copy</button></div>
  <textarea id="cron-out" class="output" readonly rows="3"></textarea>
  <p class="status ok" id="explain"></p>
  <p class="status" id="oncal"></p>
</section>
"""

HTML["systemd-service-builder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Unit name<input id="name" value="myapp" spellcheck="false"></label>
    <label class="field">Type
      <select id="type">
        <option>simple</option><option>exec</option><option>oneshot</option>
        <option>forking</option><option>notify</option><option>idle</option>
      </select>
    </label>
    <label class="field span-2">Description<input id="desc" value="My application"></label>
    <label class="field span-2">ExecStart<input id="exec" value="/usr/local/bin/myapp --config /etc/myapp.toml" spellcheck="false"></label>
    <label class="field">ExecStop<input id="stop" placeholder="optional" spellcheck="false"></label>
    <label class="field">WorkingDirectory<input id="workdir" value="/var/lib/myapp" spellcheck="false"></label>
    <label class="field">User<input id="user" value="myapp"></label>
    <label class="field">Group<input id="group" value="myapp"></label>
    <label class="field">Restart
      <select id="restart">
        <option>no</option><option selected>on-failure</option>
        <option>always</option><option>on-abnormal</option>
        <option>on-success</option><option>on-abort</option>
      </select>
    </label>
    <label class="field">RestartSec<input id="restartsec" value="5s"></label>
    <label class="field">After<input id="after" value="network-online.target"></label>
    <label class="field">Wants<input id="wants" value="network-online.target"></label>
    <label class="field">WantedBy<input id="wantedby" value="multi-user.target"></label>
    <label class="field">TimeoutStartSec<input id="timeout" value="90"></label>
    <label class="field span-2">Environment (KEY=value per line)
      <textarea id="env" rows="4" placeholder="NODE_ENV=production&#10;PORT=3000">NODE_ENV=production
PORT=3000</textarea>
    </label>
    <label class="field">EnvironmentFile<input id="envfile" placeholder="/etc/myapp.env"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="privtmp" checked> PrivateTmp</label>
      <label><input type="checkbox" id="nonew" checked> NoNewPrivileges</label>
      <label><input type="checkbox" id="protect"> ProtectSystem=strict</label>
      <label><input type="checkbox" id="remain"> RemainAfterExit (oneshot)</label>
    </div>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>Unit file</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="22"></textarea>
</section>
"""

HTML["chmod-permissions-calculator"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Octal (e.g. 755 or 4755)<input id="octal" value="755" spellcheck="false"></label>
    <label class="field">Symbolic (e.g. rwxr-xr-x)<input id="symbolic" value="rwxr-xr-x" spellcheck="false"></label>
  </div>
  <div class="perm-grid" style="margin-top:1rem">
    <span></span><span class="head">Read</span><span class="head">Write</span><span class="head">Exec</span>
    <span>Owner</span>
    <input type="checkbox" id="ur" checked><input type="checkbox" id="uw" checked><input type="checkbox" id="ux" checked>
    <span>Group</span>
    <input type="checkbox" id="gr" checked><input type="checkbox" id="gw"><input type="checkbox" id="gx" checked>
    <span>Other</span>
    <input type="checkbox" id="or" checked><input type="checkbox" id="ow"><input type="checkbox" id="ox" checked>
  </div>
  <div class="check-row" style="margin-top:0.8rem">
    <label><input type="checkbox" id="suid"> setuid (4xxx)</label>
    <label><input type="checkbox" id="sgid"> setgid (2xxx)</label>
    <label><input type="checkbox" id="sticky"> sticky (1xxx)</label>
  </div>
</section>
<section class="panel">
  <dl class="kv" id="kv"></dl>
  <div class="output-head" style="margin-top:0.8rem"><h2>chmod command</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="3"></textarea>
  <p class="status" id="status"></p>
</section>
"""

HTML["cidr-subnet-calculator"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field span-2">IP / CIDR or IP + netmask
      <input id="input" value="192.168.1.10/24" spellcheck="false">
    </label>
  </div>
  <div class="preset-row" style="margin-top:0.7rem">
    <button type="button" class="preset" data-v="10.0.0.1/8">10/8</button>
    <button type="button" class="preset" data-v="172.16.0.0/12">172.16/12</button>
    <button type="button" class="preset" data-v="192.168.0.0/16">192.168/16</button>
    <button type="button" class="preset" data-v="10.0.0.0/24">10.0.0.0/24</button>
    <button type="button" class="preset" data-v="127.0.0.1/32">loopback /32</button>
  </div>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <dl class="kv" id="kv"></dl>
</section>
"""

HTML["epoch-unix-timestamp-converter"] = r"""
<section class="panel">
  <div class="btn-row">
    <button type="button" class="btn primary" id="now">Use now</button>
  </div>
  <div class="form-grid two" style="margin-top:0.8rem">
    <label class="field">Unix seconds<input id="sec" type="text" inputmode="numeric"></label>
    <label class="field">Unix milliseconds<input id="ms" type="text" inputmode="numeric"></label>
    <label class="field">ISO 8601 / RFC 3339<input id="iso" spellcheck="false"></label>
    <label class="field">Local datetime<input id="local" type="datetime-local" step="1"></label>
  </div>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <dl class="kv" id="kv"></dl>
</section>
"""

HTML["htpasswd-generator"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Username<input id="user" value="alice" spellcheck="false"></label>
    <label class="field">Password<input id="pass" type="password" value="change-me"></label>
    <label class="field">Confirm<input id="pass2" type="password" value="change-me"></label>
    <label class="field">Scheme
      <select id="scheme">
        <option value="sha" selected>{SHA} Base64(SHA-1)</option>
        <option value="sha256">SHA-256 hex (non-Apache, documented)</option>
      </select>
    </label>
  </div>
  <p class="banner note">Apache <code>{SHA}</code> is SHA-1 of the password, then Base64 — unsalted and legacy.
    bcrypt (<code>$2y$</code>) is stronger but needs a dedicated implementation; this page stays zero-dependency
    and uses Web Crypto only. Do not use {SHA} for new internet-facing logins if you can use bcrypt/argon2 on the server.</p>
  <div class="btn-row">
    <button type="button" class="btn primary" id="go">Generate</button>
  </div>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <div class="output-head"><h2>htpasswd line</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="3"></textarea>
</section>
"""

HTML["docker-run-to-compose"] = r"""
<section class="panel">
  <label class="field">docker run command
    <textarea id="cmd" rows="6" spellcheck="false">docker run -d --name web -p 8080:80 -e NGINX_HOST=example.com -v /var/www:/usr/share/nginx/html:ro --restart unless-stopped nginx:alpine</textarea>
  </label>
  <label class="field" style="margin-top:0.7rem">Compose service key (optional override)
    <input id="svc" placeholder="derived from --name or image" spellcheck="false">
  </label>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <div class="output-head"><h2>compose.yaml</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="22"></textarea>
</section>
"""

HTML["nginx-reverse-proxy-builder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">server_name<input id="server" value="app.example.com" spellcheck="false"></label>
    <label class="field">Listen port<input id="listen" value="80"></label>
    <label class="field span-2">proxy_pass (upstream)<input id="upstream" value="http://127.0.0.1:3000" spellcheck="false"></label>
    <label class="field">client_max_body_size<input id="body" value="20m"></label>
    <label class="field">Access log<input id="log" value="/var/log/nginx/app.access.log"></label>
    <label class="field">TLS cert<input id="cert" placeholder="/etc/letsencrypt/live/app.example.com/fullchain.pem"></label>
    <label class="field">TLS key<input id="key" placeholder="/etc/letsencrypt/live/app.example.com/privkey.pem"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="ssl"> Enable SSL (listen 443 ssl)</label>
      <label><input type="checkbox" id="redirect"> HTTP → HTTPS redirect</label>
      <label><input type="checkbox" id="ws" checked> WebSocket upgrade headers</label>
      <label><input type="checkbox" id="ipv6" checked> listen [::]</label>
    </div>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>nginx server block</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="24"></textarea>
</section>
"""

HTML["caddyfile-generator"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Site address<input id="site" value="app.example.com" spellcheck="false"></label>
    <label class="field">Upstream<input id="up" value="localhost:3000" spellcheck="false"></label>
    <label class="field">TLS
      <select id="tls">
        <option value="auto" selected>Automatic HTTPS (Let's Encrypt)</option>
        <option value="internal">tls internal</option>
        <option value="off">http:// (no TLS)</option>
        <option value="files">Certificate files</option>
      </select>
    </label>
    <label class="field">ACME email<input id="email" placeholder="ops@example.com"></label>
    <label class="field">Cert file<input id="cert" placeholder="/etc/certs/cert.pem"></label>
    <label class="field">Key file<input id="key" placeholder="/etc/certs/key.pem"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="encode" checked> encode gzip zstd</label>
      <label><input type="checkbox" id="headers" checked> security headers</label>
      <label><input type="checkbox" id="log"> file log</label>
    </div>
  </div>
  <p class="banner note">Caddy upgrades WebSockets automatically on <code>reverse_proxy</code> — no extra header stanza required.</p>
</section>
<section class="panel">
  <div class="output-head"><h2>Caddyfile</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="20"></textarea>
</section>
"""

HTML["ssh-keygen-command-builder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Type
      <select id="type">
        <option value="ed25519" selected>ed25519 (recommended)</option>
        <option value="rsa">rsa</option>
        <option value="ecdsa">ecdsa</option>
      </select>
    </label>
    <label class="field">RSA bits / ECDSA bits
      <select id="bits">
        <option>256</option><option>384</option><option selected>4096</option>
      </select>
    </label>
    <label class="field">Comment (-C)<input id="comment" value="deploy@cron2systemd" spellcheck="false"></label>
    <label class="field">Output path (-f)<input id="file" value="~/.ssh/id_ed25519" spellcheck="false"></label>
    <label class="field">KDF rounds (-a, ed25519)<input id="rounds" type="number" value="100" min="16" max="250"></label>
    <label class="field">Passphrase (-N)
      <input id="pass" placeholder="leave empty for -N '' (discouraged)">
    </label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="overwrite"> Overwrite without prompt (-y is not used; we add no -q)</label>
    </div>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>Command</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="8"></textarea>
  <p class="status" id="status"></p>
  <div class="cheatsheet">
    <h2>Next steps</h2>
    <p>Install the public key with <code>ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host</code>
      or append it to <code>~/.ssh/authorized_keys</code>. Prefer ed25519; RSA is here for legacy boxes.</p>
  </div>
</section>
"""

HTML["base64-yaml-secret-encoder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Secret name<input id="name" value="app-secrets" spellcheck="false"></label>
    <label class="field">Namespace<input id="ns" value="default" spellcheck="false"></label>
    <label class="field">Type<input id="type" value="Opaque" spellcheck="false"></label>
    <div class="check-row">
      <label><input type="checkbox" id="asdata" checked> Use data: (base64) rather than stringData</label>
    </div>
  </div>
  <p class="lede" style="margin:0.8rem 0 0.4rem">Keys and values (one pair per block). Values may be multi-line.</p>
  <div id="pairs" class="rows"></div>
  <div class="btn-row">
    <button type="button" class="btn" id="add">Add key</button>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>Secret YAML</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="20"></textarea>
  <p class="status" id="status"></p>
</section>
"""

HTML["curl-to-python-fetch"] = r"""
<section class="panel">
  <label class="field">cURL command
    <textarea id="cmd" rows="8" spellcheck="false">curl -X POST 'https://api.example.com/v1/items' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  --data-raw '{"name":"widget","qty":2}'</textarea>
  </label>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <div class="output-head"><h2>requests</h2>
    <button type="button" class="copy-btn" data-copy="#req">Copy</button></div>
  <textarea id="req" class="output" readonly rows="16"></textarea>
</section>
<section class="panel">
  <div class="output-head"><h2>httpx</h2>
    <button type="button" class="copy-btn" data-copy="#httpx">Copy</button></div>
  <textarea id="httpx" class="output" readonly rows="16"></textarea>
</section>
"""

HTML["json-to-yaml-converter"] = r"""
<section class="panel">
  <label class="field">JSON
    <textarea id="json" rows="14" spellcheck="false">{
  "service": "api",
  "replicas": 2,
  "env": {"PORT": "8080"},
  "ports": [8080, 8443],
  "enabled": true,
  "note": null
}</textarea>
  </label>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <div class="output-head"><h2>YAML</h2>
    <button type="button" class="copy-btn" data-copy="#yaml">Copy</button></div>
  <textarea id="yaml" class="output" readonly rows="16"></textarea>
</section>
"""

HTML["keepalive-timeout-calculator"] = r"""
<section class="panel">
  <div class="form-grid">
    <label class="field">Requests / second<input id="rps" type="number" min="0.01" step="0.01" value="200"></label>
    <label class="field">Average latency (ms)<input id="avg" type="number" min="1" step="1" value="40"></label>
    <label class="field">p99 latency (ms)<input id="p99" type="number" min="1" step="1" value="180"></label>
    <label class="field">Upstream backends<input id="n" type="number" min="1" step="1" value="4"></label>
    <label class="field">Mean response size (KB)<input id="kb" type="number" min="0" step="1" value="12"></label>
    <label class="field">Safety factor<input id="sf" type="number" min="1" max="5" step="0.1" value="1.3"></label>
  </div>
</section>
<section class="panel">
  <dl class="kv" id="kv"></dl>
  <div class="output-head" style="margin-top:0.9rem"><h2>Suggested nginx / proxy snippets</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="16"></textarea>
  <p class="banner note">Little’s law: in-flight ≈ RPS × latency. Keepalive should outlast the typical idle gap on a pooled connection
    but stay under load-balancer idle timeouts (ALB default 60s, many CDNs 100s). These are estimates, not SLAs.</p>
</section>
"""

HTML["dns-record-bind-formatter"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">$ORIGIN<input id="origin" value="example.com." spellcheck="false"></label>
    <label class="field">Default TTL (seconds)<input id="ttl" value="3600"></label>
    <label class="field">SOA MNAME<input id="mname" value="ns1.example.com."></label>
    <label class="field">SOA RNAME (email)<input id="rname" value="hostmaster.example.com."></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="soa" checked> Include SOA + NS skeleton</label>
    </div>
  </div>
  <p class="lede" style="margin:0.9rem 0 0.35rem">Records</p>
  <div id="recs" class="rows"></div>
  <div class="btn-row"><button type="button" class="btn" id="add">Add record</button></div>
</section>
<section class="panel">
  <div class="output-head"><h2>Zone file</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="20"></textarea>
  <p class="status" id="status"></p>
</section>
"""

HTML["systemd-journald-filter-builder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Unit (-u)<input id="unit" value="nginx.service" spellcheck="false"></label>
    <label class="field">Identifier (-t)<input id="ident" placeholder="sshd"></label>
    <label class="field">Priority (-p)
      <select id="pri">
        <option value="">any</option>
        <option>emerg</option><option>alert</option><option>crit</option>
        <option>err</option><option selected>warning</option>
        <option>notice</option><option>info</option><option>debug</option>
      </select>
    </label>
    <label class="field">Since (--since)<input id="since" value="1 hour ago"></label>
    <label class="field">Until (--until)<input id="until" placeholder="now"></label>
    <label class="field">Boot
      <select id="boot">
        <option value="" selected>all boots</option>
        <option value="-b">current boot (-b)</option>
        <option value="-b -1">previous boot (-b -1)</option>
      </select>
    </label>
    <label class="field">Output (-o)
      <select id="outfmt">
        <option>short</option><option>short-iso</option>
        <option>verbose</option><option>json</option>
        <option>json-pretty</option><option>cat</option>
        <option>with-unit</option>
      </select>
    </label>
    <label class="field">Lines (-n)<input id="lines" type="number" value="200" min="0"></label>
    <label class="field">grep<input id="grep" placeholder="error|timeout" spellcheck="false"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="follow"> Follow (-f)</label>
      <label><input type="checkbox" id="reverse"> Reverse (-r)</label>
      <label><input type="checkbox" id="pager" checked> --no-pager</label>
      <label><input type="checkbox" id="kernel"> Kernel only (-k)</label>
      <label><input type="checkbox" id="catalog"> --catalog</label>
    </div>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>journalctl</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="6"></textarea>
</section>
"""

HTML["iptables-rule-builder"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field">Family
      <select id="fam"><option value="iptables">IPv4 (iptables)</option>
      <option value="ip6tables">IPv6 (ip6tables)</option></select>
    </label>
    <label class="field">Command
      <select id="cmd"><option>-A</option><option>-I</option><option>-C</option><option>-D</option></select>
    </label>
    <label class="field">Chain
      <select id="chain"><option>INPUT</option><option>OUTPUT</option><option>FORWARD</option></select>
    </label>
    <label class="field">Action (-j)
      <select id="jump"><option>ACCEPT</option><option>DROP</option><option>REJECT</option><option>LOG</option><option>RETURN</option></select>
    </label>
    <label class="field">Protocol
      <select id="proto"><option value="tcp">tcp</option><option value="udp">udp</option>
      <option value="icmp">icmp</option><option value="all">all</option></select>
    </label>
    <label class="field">Interface (-i / -o)<input id="iface" placeholder="eth0"></label>
    <label class="field">Source<input id="src" placeholder="203.0.113.0/24"></label>
    <label class="field">Destination<input id="dst" placeholder=""></label>
    <label class="field">Sport<input id="sport" placeholder=""></label>
    <label class="field">Dport<input id="dport" value="443"></label>
    <label class="field">State<input id="state" value="NEW,ESTABLISHED"></label>
    <label class="field">Comment<input id="comment" value="allow-https"></label>
    <div class="span-2 check-row">
      <label><input type="checkbox" id="est" checked> conntrack state match</label>
      <label><input type="checkbox" id="persist" checked> also emit iptables-save hint</label>
    </div>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>Rule</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="10"></textarea>
</section>
"""

HTML["uuid-v4-generator"] = r"""
<section class="panel">
  <div class="form-grid">
    <label class="field">Count<input id="n" type="number" min="1" max="500" value="1"></label>
    <div class="check-row">
      <label><input type="checkbox" id="upper"> UPPERCASE</label>
      <label><input type="checkbox" id="hyphens" checked> Keep hyphens</label>
    </div>
  </div>
  <div class="btn-row">
    <button type="button" class="btn primary" id="gen">Generate</button>
    <button type="button" class="btn" id="one">One more</button>
  </div>
</section>
<section class="panel">
  <div class="output-head"><h2>UUIDs</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <textarea id="out" class="output" readonly rows="12"></textarea>
  <label class="field" style="margin-top:0.8rem">Validate a UUID
    <input id="check" placeholder="paste a UUID" spellcheck="false"></label>
  <p class="status" id="status"></p>
</section>
"""

HTML["regex-cheatsheet-tester"] = r"""
<section class="panel">
  <div class="form-grid two">
    <label class="field span-2">Pattern
      <input id="pat" value="^([A-Za-z0-9._-]+)@([A-Za-z0-9.-]+)\.[A-Za-z]{2,}$" spellcheck="false">
    </label>
    <div class="check-row span-2">
      <label><input type="checkbox" id="g" checked> g</label>
      <label><input type="checkbox" id="i"> i</label>
      <label><input type="checkbox" id="m" checked> m</label>
      <label><input type="checkbox" id="s"> s (dotAll)</label>
    </div>
    <label class="field span-2">Test text
      <textarea id="text" rows="8">root@example.com
not-an-email
ops+alerts@cron2systemd.dev</textarea>
    </label>
  </div>
  <p class="status" id="status"></p>
</section>
<section class="panel">
  <div class="output-head"><h2>Matches</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <pre class="output" id="hi" style="min-height:6rem"></pre>
  <textarea id="out" class="output" readonly rows="8"></textarea>
</section>
<section class="cheatsheet">
  <h2>bash / grep / sed notes</h2>
  <table>
    <thead><tr><th>Construct</th><th>JS / PCRE</th><th>grep -E / sed -E</th><th>grep (BRE) / sed</th></tr></thead>
    <tbody>
      <tr><td>Any char</td><td><code>.</code></td><td><code>.</code></td><td><code>.</code></td></tr>
      <tr><td>One or more</td><td><code>+</code></td><td><code>+</code></td><td><code>\+</code></td></tr>
      <tr><td>Optional</td><td><code>?</code></td><td><code>?</code></td><td><code>\?</code></td></tr>
      <tr><td>Group</td><td><code>(ab)</code></td><td><code>(ab)</code></td><td><code>\(ab\)</code></td></tr>
      <tr><td>Or</td><td><code>a|b</code></td><td><code>a|b</code></td><td><code>a\|b</code></td></tr>
      <tr><td>Word chars</td><td><code>\w</code></td><td>often <code>[[:alnum:]_]</code></td><td>same classes</td></tr>
      <tr><td>Replace</td><td>JS <code>replace</code></td><td colspan="2"><code>sed -E 's/foo/bar/g'</code></td></tr>
      <tr><td>grep ERE</td><td></td><td colspan="2"><code>grep -E 'foo|bar' file</code> · GNU <code>grep -P</code> is PCRE if built in</td></tr>
    </tbody>
  </table>
</section>
"""


JS: dict[str, str] = {}

JS["cron-to-systemd-timer"] = r"""
'use strict';
(function () {
  const C = globalThis.CronSystemd;
  const $ = function (id) { return document.getElementById(id); };

  function sanitizeUnit(name) {
    const s = String(name || 'job').trim().toLowerCase().replace(/[^a-z0-9._@-]+/g, '-').replace(/^-+|-+$/g, '');
    return s || 'job';
  }

  function render() {
    const cron = $('cron').value;
    const unit = sanitizeUnit($('unit').value);
    const user = $('user').value.trim();
    const desc = $('desc').value.trim() || unit;
    const exec = $('exec').value.trim();
    const accuracy = $('accuracy').value.trim();
    const workdir = $('workdir').value.trim();
    const persistent = $('persistent').checked;
    const oneshot = $('oneshot').checked;
    $('timer-name').textContent = unit + '.timer';
    $('service-name').textContent = unit + '.service';

    if (!C) {
      $('status').className = 'status error';
      $('status').textContent = 'converter.js failed to load';
      return;
    }
    const result = C.cronToOnCalendar(cron);
    if (result.empty) {
      $('status').className = 'status';
      $('status').textContent = '';
      $('explain').textContent = '';
      $('timer-out').value = '';
      $('service-out').value = '';
      return;
    }
    if (!result.ok) {
      $('status').className = 'status error';
      $('status').textContent = (result.errors && result.errors[0]) || 'Invalid cron';
      $('explain').textContent = '';
      return;
    }
    $('status').className = 'status ok';
    $('status').textContent = result.representable ? 'Mapped to OnCalendar=' : 'Mapped with notes (not a single OnCalendar=)';
    $('explain').textContent = result.explanation || '';

    let calendars = [];
    if (result.outputs && result.outputs.length) {
      calendars = result.outputs;
    } else if (result.output) {
      calendars = result.output.replace(/^OnCalendar=/gm, '').split(/\n/).map(function (s) { return s.trim(); }).filter(Boolean);
    }

    const timer = [
      '[Unit]',
      'Description=' + desc + ' timer',
      'Requires=' + unit + '.service',
      '',
      '[Timer]',
    ];
    calendars.forEach(function (c) { timer.push('OnCalendar=' + c.replace(/^OnCalendar=/, '')); });
    if (persistent) timer.push('Persistent=true');
    if (accuracy) timer.push('AccuracySec=' + accuracy);
    timer.push('Unit=' + unit + '.service');
    timer.push('');
    timer.push('[Install]');
    timer.push('WantedBy=timers.target');
    if (result.warnings && result.warnings.length) {
      timer.push('');
      result.warnings.forEach(function (w) { timer.push('# ' + w.replace(/\n/g, '\n# ')); });
    }
    if (result.notes && result.notes.length) {
      result.notes.forEach(function (w) { timer.push('# ' + String(w).replace(/\n/g, '\n# ')); });
    }
    $('timer-out').value = timer.join('\n') + '\n';

    const svc = [
      '[Unit]',
      'Description=' + desc,
      'After=network-online.target',
      '',
      '[Service]',
      'Type=' + (oneshot ? 'oneshot' : 'simple'),
    ];
    if (user) svc.push('User=' + user);
    if (workdir) svc.push('WorkingDirectory=' + workdir);
    svc.push('ExecStart=' + (exec || '/usr/bin/true'));
    svc.push('');
    svc.push('# Pair with ' + unit + '.timer; do not enable this service for calendar schedules.');
    $('service-out').value = svc.join('\n') + '\n';
  }

  C2S.bindLive(['cron', 'unit', 'user', 'desc', 'exec', 'accuracy', 'workdir', 'persistent', 'oneshot'], render);
  document.querySelectorAll('.preset').forEach(function (btn) {
    btn.addEventListener('click', function () {
      $('cron').value = btn.getAttribute('data-cron');
      render();
    });
  });
})();
"""

JS["crontab-generator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function field(modeEl, valEl) {
    const mode = modeEl.value;
    let raw = valEl.value.trim();
    if (mode === 'every') return '*';
    if (!raw) raw = '*';
    if (mode === 'step') {
      const n = raw.replace(/[^\d]/g, '') || '1';
      return '*/' + n;
    }
    if (mode === 'range') {
      if (raw.indexOf('-') === -1 && /^\d+$/.test(raw)) return raw + '-' + raw;
      return raw.replace(/\s+/g, '');
    }
    return raw.replace(/\s+/g, '');
  }

  function render() {
    const min = field($('min-mode'), $('min-val'));
    const hour = field($('hour-mode'), $('hour-val'));
    const dom = field($('dom-mode'), $('dom-val'));
    const mon = field($('mon-mode'), $('mon-val'));
    const dow = field($('dow-mode'), $('dow-val'));
    const cmd = $('command').value.trim();
    const expr = [min, hour, dom, mon, dow].join(' ');
    $('cron-out').value = cmd ? expr + ' ' + cmd : expr;
    const C = globalThis.CronSystemd;
    if (!C) return;
    const result = C.cronToOnCalendar(expr);
    if (result.ok) {
      $('explain').textContent = result.explanation || '';
      if (result.representable && result.outputs && result.outputs[0]) {
        $('oncal').textContent = 'OnCalendar=' + result.outputs[0];
        $('oncal').className = 'status ok';
      } else if (result.output) {
        $('oncal').textContent = result.output;
        $('oncal').className = 'status warn';
      } else {
        $('oncal').textContent = (result.warnings || []).join(' ');
        $('oncal').className = 'status warn';
      }
    } else {
      $('explain').textContent = (result.errors && result.errors[0]) || '';
      $('oncal').textContent = '';
    }
  }

  const presets = {
    hourly: { mm: ['specific', '0'], hh: ['every', '*'], dd: ['every', '*'], mo: ['every', '*'], dw: ['every', '*'] },
    daily: { mm: ['specific', '0'], hh: ['specific', '0'], dd: ['every', '*'], mo: ['every', '*'], dw: ['every', '*'] },
    weekday: { mm: ['specific', '0'], hh: ['specific', '9'], dd: ['every', '*'], mo: ['every', '*'], dw: ['range', '1-5'] },
    weekly: { mm: ['specific', '0'], hh: ['specific', '0'], dd: ['every', '*'], mo: ['every', '*'], dw: ['specific', '0'] },
    monthly: { mm: ['specific', '0'], hh: ['specific', '0'], dd: ['specific', '1'], mo: ['every', '*'], dw: ['every', '*'] },
    every15: { mm: ['step', '15'], hh: ['every', '*'], dd: ['every', '*'], mo: ['every', '*'], dw: ['every', '*'] },
  };

  document.querySelectorAll('[data-preset]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const p = presets[btn.getAttribute('data-preset')];
      if (!p) return;
      $('min-mode').value = p.mm[0]; $('min-val').value = p.mm[1];
      $('hour-mode').value = p.hh[0]; $('hour-val').value = p.hh[1];
      $('dom-mode').value = p.dd[0]; $('dom-val').value = p.dd[1];
      $('mon-mode').value = p.mo[0]; $('mon-val').value = p.mo[1];
      $('dow-mode').value = p.dw[0]; $('dow-val').value = p.dw[1];
      render();
    });
  });

  C2S.bindLive(['min-mode','min-val','hour-mode','hour-val','dom-mode','dom-val','mon-mode','mon-val','dow-mode','dow-val','command'], render);
})();
"""

JS["systemd-service-builder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    const name = $('name').value.trim() || 'service';
    const lines = [];
    lines.push('# /etc/systemd/system/' + name + '.service');
    lines.push('[Unit]');
    lines.push('Description=' + ($('desc').value.trim() || name));
    const after = $('after').value.trim();
    const wants = $('wants').value.trim();
    if (after) lines.push('After=' + after);
    if (wants) lines.push('Wants=' + wants);
    lines.push('');
    lines.push('[Service]');
    lines.push('Type=' + $('type').value);
    const user = $('user').value.trim();
    const group = $('group').value.trim();
    if (user) lines.push('User=' + user);
    if (group) lines.push('Group=' + group);
    const wd = $('workdir').value.trim();
    if (wd) lines.push('WorkingDirectory=' + wd);
    lines.push('ExecStart=' + ($('exec').value.trim() || '/usr/bin/true'));
    const stop = $('stop').value.trim();
    if (stop) lines.push('ExecStop=' + stop);
    const restart = $('restart').value;
    if (restart && restart !== 'no') {
      lines.push('Restart=' + restart);
      const rs = $('restartsec').value.trim();
      if (rs) lines.push('RestartSec=' + rs);
    }
    const timeout = $('timeout').value.trim();
    if (timeout) lines.push('TimeoutStartSec=' + timeout);
    $('env').value.split(/\n/).forEach(function (row) {
      const t = row.trim();
      if (t) lines.push('Environment=' + t);
    });
    const ef = $('envfile').value.trim();
    if (ef) lines.push('EnvironmentFile=' + ef);
    if ($('privtmp').checked) lines.push('PrivateTmp=true');
    if ($('nonew').checked) lines.push('NoNewPrivileges=true');
    if ($('protect').checked) {
      lines.push('ProtectSystem=strict');
      lines.push('ProtectHome=true');
    }
    if ($('remain').checked) lines.push('RemainAfterExit=true');
    lines.push('');
    lines.push('[Install]');
    lines.push('WantedBy=' + ($('wantedby').value.trim() || 'multi-user.target'));
    $('out').value = lines.join('\n') + '\n';
  }
  C2S.bindLive(['name','type','desc','exec','stop','workdir','user','group','restart','restartsec','after','wants','wantedby','timeout','env','envfile','privtmp','nonew','protect','remain'], render);
})();
"""

JS["chmod-permissions-calculator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  let lock = false;
  const bits = [
    ['ur', 256], ['uw', 128], ['ux', 64],
    ['gr', 32], ['gw', 16], ['gx', 8],
    ['or', 4], ['ow', 2], ['ox', 1]
  ];

  function fromMode(mode) {
    bits.forEach(function (b) { $(b[0]).checked = !!(mode & b[1]); });
    $('suid').checked = !!(mode & 2048);
    $('sgid').checked = !!(mode & 1024);
    $('sticky').checked = !!(mode & 512);
  }
  function fromBoxes() {
    let mode = 0;
    bits.forEach(function (b) { if ($(b[0]).checked) mode |= b[1]; });
    if ($('suid').checked) mode |= 2048;
    if ($('sgid').checked) mode |= 1024;
    if ($('sticky').checked) mode |= 512;
    return mode;
  }
  function toSymbolic(mode) {
    const map = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx'];
    let u = map[(mode >> 6) & 7];
    let g = map[(mode >> 3) & 7];
    let o = map[mode & 7];
    if (mode & 2048) u = u.slice(0, 2) + (u[2] === 'x' ? 's' : 'S');
    if (mode & 1024) g = g.slice(0, 2) + (g[2] === 'x' ? 's' : 'S');
    if (mode & 512) o = o.slice(0, 2) + (o[2] === 'x' ? 't' : 'T');
    return u + g + o;
  }
  function parseSymbolic(text) {
    const t = String(text).trim().replace(/^d|^l|^-/, '');
    const m = t.match(/^([r-][w-][xsS-])([r-][w-][xsS-])([r-][w-][xtT-])$/);
    if (!m) return null;
    function trip(s, execBit, extraOn, extraOff, extraVal) {
      let v = 0;
      if (s[0] === 'r') v |= 4;
      if (s[1] === 'w') v |= 2;
      const c = s[2];
      if (c === 'x' || c === extraOn) v |= 1;
      return { v: v, extra: (c === extraOn || c === extraOff) ? extraVal : 0 };
    }
    const u = trip(m[1], 1, 's', 'S', 2048);
    const g = trip(m[2], 1, 's', 'S', 1024);
    const o = trip(m[3], 1, 't', 'T', 512);
    return (u.v << 6) | (g.v << 3) | o.v | u.extra | g.extra | o.extra;
  }
  function parseOctal(text) {
    const t = String(text).trim();
    if (!/^[0-7]{3,4}$/.test(t)) return null;
    return parseInt(t, 8);
  }
  function octalString(mode) {
    const special = mode > 511;
    return (special ? mode : mode).toString(8).padStart(special ? 4 : 3, '0');
  }
  function describe(mode) {
    const who = [
      ['Owner', (mode >> 6) & 7],
      ['Group', (mode >> 3) & 7],
      ['Other', mode & 7]
    ];
    return who.map(function (w) {
      const r = w[1] & 4 ? 'read' : null;
      const wr = w[1] & 2 ? 'write' : null;
      const x = w[1] & 1 ? 'execute' : null;
      const parts = [r, wr, x].filter(Boolean);
      return w[0] + ': ' + (parts.join(', ') || 'none');
    }).join(' · ');
  }
  function paint(mode, source) {
    lock = true;
    fromMode(mode);
    if (source !== 'octal') $('octal').value = octalString(mode);
    if (source !== 'symbolic') $('symbolic').value = toSymbolic(mode);
    const extra = [];
    if (mode & 2048) extra.push('setuid');
    if (mode & 1024) extra.push('setgid');
    if (mode & 512) extra.push('sticky');
    const oct = octalString(mode);
    $('kv').innerHTML =
      '<dt>ls-style</dt><dd>-' + toSymbolic(mode) + '</dd>' +
      '<dt>Octal</dt><dd>' + oct + '</dd>' +
      '<dt>Python</dt><dd>os.chmod(path, 0o' + oct + ')</dd>' +
      '<dt>Meaning</dt><dd>' + describe(mode) + (extra.length ? ' · ' + extra.join(', ') : '') + '</dd>';
    $('out').value = 'chmod ' + oct + ' path';
    $('status').className = 'status ok';
    $('status').textContent = 'Valid mode';
    lock = false;
  }
  function fromOctal() {
    if (lock) return;
    const m = parseOctal($('octal').value);
    if (m == null) {
      $('status').className = 'status error';
      $('status').textContent = 'Octal must be 3 or 4 digits from 0–7';
      return;
    }
    paint(m, 'octal');
  }
  function fromSymbolic() {
    if (lock) return;
    const m = parseSymbolic($('symbolic').value);
    if (m == null) {
      $('status').className = 'status error';
      $('status').textContent = 'Symbolic must look like rwxr-xr-x';
      return;
    }
    paint(m, 'symbolic');
  }
  function fromChecks() {
    if (lock) return;
    paint(fromBoxes(), 'boxes');
  }
  $('octal').addEventListener('input', fromOctal);
  $('symbolic').addEventListener('input', fromSymbolic);
  ['ur','uw','ux','gr','gw','gx','or','ow','ox','suid','sgid','sticky'].forEach(function (id) {
    $(id).addEventListener('change', fromChecks);
  });
  globalThis.ChmodTool = { parseOctal: parseOctal, parseSymbolic: parseSymbolic, toSymbolic: toSymbolic };
  paint(parseOctal('755'), 'octal');
})();
"""

JS["cidr-subnet-calculator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function ipToInt(ip) {
    const p = String(ip).trim().split('.');
    if (p.length !== 4) return null;
    const n = [];
    for (let i = 0; i < 4; i++) {
      if (!/^\d+$/.test(p[i])) return null;
      const v = Number(p[i]);
      if (v < 0 || v > 255 || v !== (v | 0)) return null;
      n.push(v);
    }
    return ((n[0] << 24) >>> 0) + (n[1] << 16) + (n[2] << 8) + n[3];
  }
  function intToIp(n) {
    n = n >>> 0;
    return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.');
  }
  function maskFromPrefix(p) {
    if (p <= 0) return 0;
    if (p >= 32) return 0xFFFFFFFF >>> 0;
    return (0xFFFFFFFF << (32 - p)) >>> 0;
  }
  function prefixFromMask(mask) {
    let bits = 0;
    const m = mask >>> 0;
    for (let i = 31; i >= 0; i--) {
      if (m & (1 << i)) bits++;
      else break;
    }
    if (maskFromPrefix(bits) !== m) return null;
    return bits;
  }
  function parse(text) {
    const raw = String(text).trim();
    let ip, prefix;
    const slash = raw.match(/^([0-9.]+)\s*\/\s*(\d{1,2})$/);
    if (slash) {
      ip = ipToInt(slash[1]);
      prefix = Number(slash[2]);
      if (ip == null || prefix < 0 || prefix > 32) throw new Error('Invalid IP/CIDR');
    } else {
      const parts = raw.split(/[\s,]+/).filter(Boolean);
      if (parts.length === 2) {
        ip = ipToInt(parts[0]);
        const maybePref = /^\d{1,2}$/.test(parts[1]) ? Number(parts[1]) : null;
        if (maybePref != null) prefix = maybePref;
        else {
          const mask = ipToInt(parts[1]);
          if (mask == null) throw new Error('Invalid netmask');
          prefix = prefixFromMask(mask);
          if (prefix == null) throw new Error('Netmask is not contiguous');
        }
        if (ip == null || prefix < 0 || prefix > 32) throw new Error('Invalid IP/mask');
      } else if (parts.length === 1) {
        ip = ipToInt(parts[0]);
        if (ip == null) throw new Error('Enter dotted IPv4 with /prefix, e.g. 192.168.1.10/24');
        prefix = 32;
      } else {
        throw new Error('Enter IPv4 CIDR such as 10.0.0.0/24');
      }
    }
    const mask = maskFromPrefix(prefix);
    const network = (ip & mask) >>> 0;
    const wildcard = (~mask) >>> 0;
    const broadcast = (network | wildcard) >>> 0;
    const total = prefix === 32 ? 1 : prefix === 31 ? 2 : Math.pow(2, 32 - prefix);
    const usable = prefix >= 31 ? total : Math.max(0, total - 2);
    const first = prefix >= 31 ? network : (network + 1) >>> 0;
    const last = prefix >= 31 ? broadcast : (broadcast - 1) >>> 0;
    const cls = (ip >>> 24) < 128 ? 'A' : (ip >>> 24) < 192 ? 'B' : (ip >>> 24) < 224 ? 'C' : (ip >>> 24) < 240 ? 'D (multicast)' : 'E';
    const priv = (ip >>> 24) === 10
      || ((ip >>> 16) === 0xC0A8)
      || ((ip >>> 20) === 0xAC1)
      || ((ip >>> 24) === 127)
      || ((ip >>> 16) === 0xA9FE);
    return {
      ip: intToIp(ip), prefix: prefix, mask: intToIp(mask), wildcard: intToIp(wildcard),
      network: intToIp(network), broadcast: intToIp(broadcast),
      first: intToIp(first), last: intToIp(last), total: total, usable: usable,
      cls: cls, priv: priv, binary: intToIp(ip).split('.').map(function (o) {
        return Number(o).toString(2).padStart(8, '0');
      }).join('.')
    };
  }
  function row(k, v) { return '<dt>' + k + '</dt><dd>' + v + '</dd>'; }
  function render() {
    try {
      const r = parse($('input').value);
      $('status').className = 'status ok';
      $('status').textContent = r.ip + '/' + r.prefix;
      $('kv').innerHTML = [
        row('Address', r.ip),
        row('Prefix', '/' + r.prefix),
        row('Netmask', r.mask),
        row('Wildcard', r.wildcard),
        row('Network', r.network),
        row('Broadcast', r.broadcast),
        row('First usable', r.first),
        row('Last usable', r.last),
        row('Total addresses', String(r.total)),
        row('Usable hosts', String(r.usable)),
        row('Class / scope', r.cls + (r.priv ? ' · private/special' : ' · public-ish')),
        row('Binary', r.binary)
      ].join('');
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
      $('kv').innerHTML = '';
    }
  }
  globalThis.CidrTool = { parse: parse, ipToInt: ipToInt, intToIp: intToIp };
  C2S.bindLive(['input'], render);
  document.querySelectorAll('.preset').forEach(function (btn) {
    btn.addEventListener('click', function () {
      $('input').value = btn.getAttribute('data-v');
      render();
    });
  });
})();
"""

JS["epoch-unix-timestamp-converter"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  let lock = false;

  function toLocalValue(d) {
    const pad = function (n) { return String(n).padStart(2, '0'); };
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      'T' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
  }
  function rel(ms) {
    const diff = Date.now() - ms;
    const abs = Math.abs(diff);
    const s = Math.round(abs / 1000);
    if (s < 60) return (diff >= 0 ? s + ' seconds ago' : 'in ' + s + ' seconds');
    const m = Math.round(s / 60);
    if (m < 60) return (diff >= 0 ? m + ' minutes ago' : 'in ' + m + ' minutes');
    const h = Math.round(m / 60);
    if (h < 48) return (diff >= 0 ? h + ' hours ago' : 'in ' + h + ' hours');
    const d = Math.round(h / 24);
    return (diff >= 0 ? d + ' days ago' : 'in ' + d + ' days');
  }
  function paint(d, source) {
    if (isNaN(d.getTime())) {
      $('status').className = 'status error';
      $('status').textContent = 'Could not parse that date/time';
      return;
    }
    lock = true;
    const ms = d.getTime();
    const sec = Math.floor(ms / 1000);
    if (source !== 'sec') $('sec').value = String(sec);
    if (source !== 'ms') $('ms').value = String(ms);
    if (source !== 'iso') $('iso').value = d.toISOString();
    if (source !== 'local') $('local').value = toLocalValue(d);
    $('kv').innerHTML =
      '<dt>UTC</dt><dd>' + d.toISOString().replace('T', ' ').replace('Z', ' UTC') + '</dd>' +
      '<dt>Local</dt><dd>' + d.toString() + '</dd>' +
      '<dt>Relative</dt><dd>' + rel(ms) + '</dd>' +
      '<dt>ISO 8601</dt><dd>' + d.toISOString() + '</dd>' +
      '<dt>Unix s / ms</dt><dd>' + sec + ' / ' + ms + '</dd>';
    $('status').className = 'status ok';
    $('status').textContent = 'Valid instant';
    lock = false;
  }
  function fromSec() {
    if (lock) return;
    const t = $('sec').value.trim();
    if (!/^-?\d+$/.test(t)) { $('status').className = 'status error'; $('status').textContent = 'Seconds must be an integer'; return; }
    let n = Number(t);
    if (Math.abs(n) > 1e12) n = Math.floor(n / 1000);
    paint(new Date(n * 1000), 'sec');
  }
  function fromMs() {
    if (lock) return;
    const t = $('ms').value.trim();
    if (!/^-?\d+$/.test(t)) { $('status').className = 'status error'; $('status').textContent = 'Milliseconds must be an integer'; return; }
    paint(new Date(Number(t)), 'ms');
  }
  function fromIso() {
    if (lock) return;
    paint(new Date($('iso').value), 'iso');
  }
  function fromLocal() {
    if (lock) return;
    const v = $('local').value;
    if (!v) return;
    paint(new Date(v), 'local');
  }
  $('sec').addEventListener('input', fromSec);
  $('ms').addEventListener('input', fromMs);
  $('iso').addEventListener('input', fromIso);
  $('local').addEventListener('input', fromLocal);
  $('now').addEventListener('click', function () { paint(new Date(), 'now'); });
  paint(new Date(), 'now');
})();
"""

JS["htpasswd-generator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function b64(bytes) {
    let bin = '';
    bytes.forEach(function (b) { bin += String.fromCharCode(b); });
    return btoa(bin);
  }
  function hex(bytes) {
    return Array.from(bytes).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }
  async function shaDigest(algo, text) {
    const buf = await crypto.subtle.digest(algo, new TextEncoder().encode(text));
    return new Uint8Array(buf);
  }
  async function generate(user, password, scheme) {
    if (!user || /:/.test(user) || /\s/.test(user)) throw new Error('Username must be non-empty and contain no colon or space');
    if (!password) throw new Error('Password is empty');
    if (scheme === 'sha256') {
      const h = hex(await shaDigest('SHA-256', password));
      return { line: user + ':{SHA256}' + h, note: 'Non-standard SHA-256 hex digest. Apache httpd does not treat {SHA256} as a native htpasswd scheme.' };
    }
    const h = await shaDigest('SHA-1', password);
    return { line: user + ':{SHA}' + b64(h), note: 'Apache {SHA} format (unsalted SHA-1).' };
  }
  async function run() {
    const user = $('user').value.trim();
    const p1 = $('pass').value;
    const p2 = $('pass2').value;
    $('status').className = 'status';
    if (p1 !== p2) {
      $('status').className = 'status error';
      $('status').textContent = 'Passwords do not match';
      return;
    }
    try {
      const out = await generate(user, p1, $('scheme').value);
      $('out').value = out.line + '\n';
      $('status').className = 'status ok';
      $('status').textContent = out.note;
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
    }
  }
  $('go').addEventListener('click', run);
  ['user','pass','pass2','scheme'].forEach(function (id) {
    $(id).addEventListener('change', run);
  });
  globalThis.HtpasswdTool = { generate: generate };
  run();
})();
"""

JS["docker-run-to-compose"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function yamlVal(v) {
    return C2S.yamlString(v);
  }
  function parseDockerRun(input) {
    const tokens = C2S.tokenize(input);
    let i = 0;
    if (tokens[i] === 'sudo') i++;
    if (tokens[i] === 'docker' && tokens[i + 1] === 'run') i += 2;
    else if (tokens[i] === 'docker' && tokens[i + 1] === 'container' && tokens[i + 2] === 'run') i += 3;
    else if (tokens[i] === 'run') i++;
    const spec = {
      name: '', image: '', command: [], ports: [], env: [], volumes: [],
      restart: '', network: '', networks: [], workdir: '', user: '',
      labels: [], hostname: '', memory: '', cpus: '', entrypoint: null,
      privileged: false, init: false, tty: false, stdin_open: false,
      read_only: false, expose: [], cap_add: [], cap_drop: [], extra_hosts: [],
      devices: [], platform: '', pull: '', log_driver: '', log_opts: [],
      shm_size: '', pid: '', runtime: '', sysctls: [], tmpfs: [],
      security_opt: [], ulimits: [], healthcmd: '', stop_signal: '',
      cgroup_parent: '', mac: '', dns: [], dns_search: [], add_host: [],
      publish_all: false, rm: false, detach: false
    };
    const takes = {
      '--name': 'name', '--hostname': 'hostname', '-h': 'hostname',
      '--user': 'user', '-u': 'user', '--workdir': 'workdir', '-w': 'workdir',
      '--restart': 'restart', '--network': 'network', '--net': 'network',
      '--memory': 'memory', '-m': 'memory', '--cpus': 'cpus',
      '--entrypoint': 'entrypoint', '--platform': 'platform', '--pull': 'pull',
      '--log-driver': 'log_driver', '--shm-size': 'shm_size', '--pid': 'pid',
      '--runtime': 'runtime', '--stop-signal': 'stop_signal',
      '--cgroup-parent': 'cgroup_parent', '--mac-address': 'mac',
      '--health-cmd': 'healthcmd'
    };
    const lists = {
      '-p': 'ports', '--publish': 'ports', '-e': 'env', '--env': 'env',
      '-v': 'volumes', '--volume': 'volumes', '--mount': 'volumes',
      '-l': 'labels', '--label': 'labels', '--expose': 'expose',
      '--cap-add': 'cap_add', '--cap-drop': 'cap_drop', '--add-host': 'extra_hosts',
      '--device': 'devices', '--log-opt': 'log_opts', '--sysctl': 'sysctls',
      '--tmpfs': 'tmpfs', '--security-opt': 'security_opt', '--ulimit': 'ulimits',
      '--dns': 'dns', '--dns-search': 'dns_search'
    };
    function eatValue() {
      i++;
      if (i >= tokens.length) throw new Error('Flag is missing a value');
      return tokens[i];
    }
    while (i < tokens.length) {
      let t = tokens[i];
      if (t === '--') { spec.command = tokens.slice(i + 1); break; }
      if (!t.startsWith('-') || t === '-') {
        spec.image = t;
        spec.command = tokens.slice(i + 1);
        break;
      }
      if (t === '-it' || t === '-ti') { spec.tty = true; spec.stdin_open = true; i++; continue; }
      if (t === '-dit' || t === '-idt' || t === '-tid') { spec.detach = true; spec.tty = true; spec.stdin_open = true; i++; continue; }
      if (/^-[a-zA-Z]{2,}$/.test(t) && t.indexOf('--') !== 0) {
        const chars = t.slice(1).split('');
        let consumed = false;
        for (let c = 0; c < chars.length; c++) {
          const f = '-' + chars[c];
          if (f === '-d') spec.detach = true;
          else if (f === '-i') spec.stdin_open = true;
          else if (f === '-t') spec.tty = true;
          else if (f === '-P') spec.publish_all = true;
          else if (lists[f]) {
            const rest = chars.slice(c + 1).join('');
            const val = rest ? rest : eatValue();
            spec[lists[f]].push(val);
            consumed = true;
            break;
          } else if (takes[f]) {
            const rest = chars.slice(c + 1).join('');
            spec[takes[f]] = rest ? rest : eatValue();
            consumed = true;
            break;
          } else {
            throw new Error('Unknown short flag cluster ' + t);
          }
        }
        if (!consumed) { i++; continue; }
        i++; continue;
      }
      const eq = t.indexOf('=');
      let flag = t, inline = null;
      if (eq > 1 && t.startsWith('--')) {
        flag = t.slice(0, eq);
        inline = t.slice(eq + 1);
      }
      if (flag === '-d' || flag === '--detach') spec.detach = true;
      else if (flag === '--rm') spec.rm = true;
      else if (flag === '-i' || flag === '--interactive') spec.stdin_open = true;
      else if (flag === '-t' || flag === '--tty') spec.tty = true;
      else if (flag === '--privileged') spec.privileged = true;
      else if (flag === '--init') spec.init = true;
      else if (flag === '--read-only') spec.read_only = true;
      else if (flag === '-P' || flag === '--publish-all') spec.publish_all = true;
      else if (takes[flag]) spec[takes[flag]] = inline != null ? inline : eatValue();
      else if (lists[flag]) spec[lists[flag]].push(inline != null ? inline : eatValue());
      else throw new Error('Unsupported flag: ' + flag + ' (add it as a comment in YAML if needed)');
      i++;
    }
    if (!spec.image) throw new Error('No image found. Expected: docker run [flags] image [cmd]');
    return spec;
  }
  function envToMap(list) {
    const obj = {};
    const arr = [];
    list.forEach(function (e) {
      const n = e.indexOf('=');
      if (n === -1) arr.push(e);
      else obj[e.slice(0, n)] = e.slice(n + 1);
    });
    return { obj: obj, passthrough: arr };
  }
  function indent(s, n) {
    const pad = '  '.repeat(n);
    return s.split('\n').map(function (line) { return line ? pad + line : line; }).join('\n');
  }
  function toCompose(spec, key) {
    const svc = key || spec.name || spec.image.split(':')[0].split('/').pop().replace(/[^a-zA-Z0-9._-]/g, '-') || 'app';
    const lines = ['services:', '  ' + svc + ':'];
    function add(k, v) { lines.push('    ' + k + ': ' + v); }
    add('image', yamlVal(spec.image));
    if (spec.name) add('container_name', yamlVal(spec.name));
    if (spec.hostname) add('hostname', yamlVal(spec.hostname));
    if (spec.user) add('user', yamlVal(spec.user));
    if (spec.workdir) add('working_dir', yamlVal(spec.workdir));
    if (spec.restart) add('restart', yamlVal(spec.restart));
    if (spec.privileged) add('privileged', 'true');
    if (spec.init) add('init', 'true');
    if (spec.tty) add('tty', 'true');
    if (spec.stdin_open) add('stdin_open', 'true');
    if (spec.read_only) add('read_only', 'true');
    if (spec.platform) add('platform', yamlVal(spec.platform));
    if (spec.pull) add('pull_policy', yamlVal(spec.pull));
    if (spec.memory || spec.cpus) {
      lines.push('    deploy:');
      lines.push('      resources:');
      lines.push('        limits:');
      if (spec.memory) lines.push('          memory: ' + yamlVal(spec.memory));
      if (spec.cpus) lines.push('          cpus: ' + yamlVal(spec.cpus));
    }
    if (spec.network) {
      add('network_mode', yamlVal(spec.network));
    }
    if (spec.entrypoint != null) add('entrypoint', yamlVal(spec.entrypoint));
    if (spec.command.length) {
      lines.push('    command:');
      spec.command.forEach(function (c) { lines.push('      - ' + yamlVal(c)); });
    }
    if (spec.ports.length) {
      lines.push('    ports:');
      spec.ports.forEach(function (p) { lines.push('      - ' + yamlVal(p)); });
    }
    if (spec.expose.length) {
      lines.push('    expose:');
      spec.expose.forEach(function (p) { lines.push('      - ' + yamlVal(p)); });
    }
    const env = envToMap(spec.env);
    if (Object.keys(env.obj).length) {
      lines.push('    environment:');
      Object.keys(env.obj).forEach(function (k) {
        lines.push('      ' + k + ': ' + yamlVal(env.obj[k]));
      });
    }
    env.passthrough.forEach(function (k) {
      /* host passthrough */
    });
    if (env.passthrough.length) {
      if (!Object.keys(env.obj).length) lines.push('    environment:');
      env.passthrough.forEach(function (k) { lines.push('      - ' + yamlVal(k)); });
    }
    if (spec.volumes.length) {
      lines.push('    volumes:');
      spec.volumes.forEach(function (v) { lines.push('      - ' + yamlVal(v)); });
    }
    if (spec.labels.length) {
      lines.push('    labels:');
      spec.labels.forEach(function (l) {
        const n = l.indexOf('=');
        if (n === -1) lines.push('      - ' + yamlVal(l));
        else lines.push('      ' + l.slice(0, n) + ': ' + yamlVal(l.slice(n + 1)));
      });
    }
    ['cap_add','cap_drop','devices','extra_hosts','dns','tmpfs','security_opt'].forEach(function (k) {
      if (spec[k] && spec[k].length) {
        lines.push('    ' + k + ':');
        spec[k].forEach(function (v) { lines.push('      - ' + yamlVal(v)); });
      }
    });
    if (spec.log_driver) {
      lines.push('    logging:');
      lines.push('      driver: ' + yamlVal(spec.log_driver));
      if (spec.log_opts.length) {
        lines.push('      options:');
        spec.log_opts.forEach(function (o) {
          const n = o.indexOf('=');
          if (n === -1) lines.push('        ' + yamlVal(o) + ': "true"');
          else lines.push('        ' + o.slice(0, n) + ': ' + yamlVal(o.slice(n + 1)));
        });
      }
    }
    if (spec.healthcmd) {
      lines.push('    healthcheck:');
      lines.push('      test: ' + yamlVal(spec.healthcmd));
    }
    if (spec.rm) lines.push('    # --rm has no Compose equivalent; containers persist after stop.');
    if (spec.publish_all) lines.push('    # -P / --publish-all is not expressed in Compose; map ports explicitly.');
    return lines.join('\n') + '\n';
  }
  function render() {
    try {
      const spec = parseDockerRun($('cmd').value);
      $('out').value = toCompose(spec, $('svc').value.trim());
      $('status').className = 'status ok';
      $('status').textContent = 'Parsed image ' + spec.image;
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
    }
  }
  globalThis.DockerRunTool = { parseDockerRun: parseDockerRun, toCompose: toCompose };
  C2S.bindLive(['cmd', 'svc'], render);
})();
"""

JS["nginx-reverse-proxy-builder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    const name = $('server').value.trim() || 'example.com';
    const listen = $('listen').value.trim() || '80';
    const up = $('upstream').value.trim() || 'http://127.0.0.1:8080';
    const body = $('body').value.trim() || '1m';
    const log = $('log').value.trim();
    const ssl = $('ssl').checked;
    const ipv6 = $('ipv6').checked;
    const ws = $('ws').checked;
    const redir = $('redirect').checked && ssl;
    const cert = $('cert').value.trim() || '/etc/ssl/certs/' + name + '.pem';
    const key = $('key').value.trim() || '/etc/ssl/private/' + name + '.key';
    const blocks = [];
    if (redir) {
      blocks.push('server {');
      blocks.push('    listen 80;');
      if (ipv6) blocks.push('    listen [::]:80;');
      blocks.push('    server_name ' + name + ';');
      blocks.push('    return 301 https://$host$request_uri;');
      blocks.push('}');
      blocks.push('');
    }
    blocks.push('server {');
    if (ssl) {
      blocks.push('    listen 443 ssl http2;');
      if (ipv6) blocks.push('    listen [::]:443 ssl http2;');
      blocks.push('    ssl_certificate     ' + cert + ';');
      blocks.push('    ssl_certificate_key ' + key + ';');
      blocks.push('    ssl_session_timeout 1d;');
      blocks.push('    ssl_session_cache shared:SSL:10m;');
    } else {
      blocks.push('    listen ' + listen + ';');
      if (ipv6) blocks.push('    listen [::]:' + listen + ';');
    }
    blocks.push('    server_name ' + name + ';');
    blocks.push('    client_max_body_size ' + body + ';');
    if (log) blocks.push('    access_log ' + log + ';');
    blocks.push('');
    blocks.push('    location / {');
    blocks.push('        proxy_pass ' + up + ';');
    blocks.push('        proxy_http_version 1.1;');
    blocks.push('        proxy_set_header Host $host;');
    blocks.push('        proxy_set_header X-Real-IP $remote_addr;');
    blocks.push('        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;');
    blocks.push('        proxy_set_header X-Forwarded-Proto $scheme;');
    if (ws) {
      blocks.push('        proxy_set_header Upgrade $http_upgrade;');
      blocks.push('        proxy_set_header Connection "upgrade";');
      blocks.push('        proxy_read_timeout 86400;');
    }
    blocks.push('        proxy_connect_timeout 5s;');
    blocks.push('        proxy_send_timeout 60s;');
    blocks.push('    }');
    blocks.push('}');
    $('out').value = blocks.join('\n') + '\n';
  }
  C2S.bindLive(['server','listen','upstream','body','log','cert','key','ssl','redirect','ws','ipv6'], render);
})();
"""


JS["caddyfile-generator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    let site = $('site').value.trim() || 'localhost';
    const tls = $('tls').value;
    if (tls === 'off' && site.indexOf('://') === -1) site = 'http://' + site;
    const up = $('up').value.trim() || 'localhost:8080';
    const lines = [];
    const email = $('email').value.trim();
    if (email && tls === 'auto') {
      lines.push('{');
      lines.push('    email ' + email);
      lines.push('}');
      lines.push('');
    }
    lines.push(site + ' {');
    if (tls === 'internal') lines.push('    tls internal');
    if (tls === 'files') {
      const cert = $('cert').value.trim() || 'cert.pem';
      const key = $('key').value.trim() || 'key.pem';
      lines.push('    tls ' + cert + ' ' + key);
    }
    if ($('encode').checked) lines.push('    encode gzip zstd');
    if ($('headers').checked) {
      lines.push('    header {');
      lines.push('        X-Content-Type-Options nosniff');
      lines.push('        Referrer-Policy strict-origin-when-cross-origin');
      lines.push('        -Server');
      lines.push('    }');
    }
    if ($('log').checked) {
      lines.push('    log {');
      lines.push('        output file /var/log/caddy/' + site.replace(/[^A-Za-z0-9._-]/g, '_') + '.log');
      lines.push('    }');
    }
    lines.push('    reverse_proxy ' + up);
    lines.push('}');
    $('out').value = lines.join('\n') + '\n';
  }
  C2S.bindLive(['site','up','tls','email','cert','key','encode','headers','log'], render);
})();
"""

JS["ssh-keygen-command-builder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    const type = $('type').value;
    const bits = $('bits').value;
    const comment = $('comment').value;
    const file = $('file').value.trim() || '~/.ssh/id_' + type;
    const rounds = $('rounds').value;
    const pass = $('pass').value;
    const q = C2S.shellQuote;
    const parts = ['ssh-keygen', '-t', type];
    if (type === 'rsa') parts.push('-b', (bits === '4096' || bits === '3072' || bits === '2048') ? bits : '4096');
    if (type === 'ecdsa') {
      const b = (bits === '256' || bits === '384' || bits === '521') ? bits : '256';
      parts.push('-b', b);
    }
    if (type === 'ed25519' && rounds) parts.push('-a', String(rounds));
    parts.push('-C', q(comment));
    parts.push('-f', q(file));
    parts.push('-N', q(pass));
    $('out').value = parts.join(' ') + '\n';
    if (!pass) {
      $('status').className = 'status warn';
      $('status').textContent = 'Empty passphrase (-N \'\'). Fine for automation keys; prefer a passphrase for laptops.';
    } else {
      $('status').className = 'status ok';
      $('status').textContent = 'Passphrase is on the command line (visible in process lists). Prefer an interactive prompt for humans.';
    }
  }
  $('type').addEventListener('change', function () {
    if ($('type').value === 'ed25519' && $('file').value.indexOf('id_') !== -1) $('file').value = '~/.ssh/id_ed25519';
    if ($('type').value === 'rsa') $('file').value = '~/.ssh/id_rsa';
    if ($('type').value === 'ecdsa') $('file').value = '~/.ssh/id_ecdsa';
    render();
  });
  C2S.bindLive(['type','bits','comment','file','rounds','pass'], render);
})();
"""

JS["base64-yaml-secret-encoder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  const pairs = $('pairs');

  function addPair(k, v) {
    const wrap = document.createElement('div');
    wrap.className = 'form-grid two';
    wrap.innerHTML = '<label class="field">Key<input class="k" spellcheck="false"></label>' +
      '<label class="field">Value<textarea class="v" rows="3" spellcheck="false"></textarea></label>';
    wrap.querySelector('.k').value = k || '';
    wrap.querySelector('.v').value = v || '';
    wrap.querySelector('.k').addEventListener('input', render);
    wrap.querySelector('.v').addEventListener('input', render);
    pairs.appendChild(wrap);
  }
  function render() {
    const name = $('name').value.trim() || 'secret';
    const ns = $('ns').value.trim();
    const type = $('type').value.trim() || 'Opaque';
    const asData = $('asdata').checked;
    const items = [];
    pairs.querySelectorAll('.form-grid').forEach(function (row) {
      const k = row.querySelector('.k').value.trim();
      const v = row.querySelector('.v').value;
      if (k) items.push({ k: k, v: v });
    });
    const lines = ['apiVersion: v1', 'kind: Secret', 'metadata:'];
    lines.push('  name: ' + name);
    if (ns) lines.push('  namespace: ' + ns);
    lines.push('type: ' + type);
    if (!items.length) {
      $('out').value = lines.join('\n') + '\n';
      $('status').className = 'status warn';
      $('status').textContent = 'Add at least one key';
      return;
    }
    lines.push(asData ? 'data:' : 'stringData:');
    items.forEach(function (it) {
      if (!asData && it.v.indexOf('\n') !== -1) {
        lines.push('  ' + it.k + ': |');
        it.v.split('\n').forEach(function (line) { lines.push('    ' + line); });
      } else if (asData) {
        lines.push('  ' + it.k + ': ' + C2S.utf8ToB64(it.v));
      } else {
        lines.push('  ' + it.k + ': ' + C2S.yamlString(it.v));
      }
    });
    $('out').value = lines.join('\n') + '\n';
    $('status').className = 'status ok';
    $('status').textContent = asData ? 'Values encoded with UTF-8 then standard Base64 (btoa)' : 'stringData will be encoded by the API server';
  }
  $('add').addEventListener('click', function () { addPair('', ''); render(); });
  C2S.bindLive(['name','ns','type','asdata'], render);
  addPair('username', 'alice');
  addPair('password', 's3cret\nwith newline');
  render();
})();
"""

JS["curl-to-python-fetch"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function parseCurl(input) {
    const tokens = C2S.tokenize(input);
    let i = 0;
    if (tokens[i] === 'sudo') i++;
    if (tokens[i] === 'curl') i++;
    const req = {
      method: null, url: '', headers: [], data: null, jsonRaw: null,
      auth: null, insecure: false, userAgent: null,
      cookie: null, referer: null, location: true, head: false,
      get: false, form: []
    };
    function need() {
      i++;
      if (i >= tokens.length) throw new Error('Flag missing value');
      return tokens[i];
    }
    while (i < tokens.length) {
      let t = tokens[i];
      const eq = t.startsWith('--') ? t.indexOf('=') : -1;
      let flag = t, inline = null;
      if (eq > 1) { flag = t.slice(0, eq); inline = t.slice(eq + 1); }
      function val() { return inline != null ? inline : need(); }
      if (!flag.startsWith('-') || flag === '-') {
        req.url = t;
        i++;
        continue;
      }
      if (flag === '-X' || flag === '--request') req.method = val().toUpperCase();
      else if (flag === '-H' || flag === '--header') req.headers.push(val());
      else if (flag === '-d' || flag === '--data' || flag === '--data-raw' || flag === '--data-ascii') {
        req.data = (req.data ? req.data + '&' : '') + val();
      } else if (flag === '--data-binary') { req.data = val(); }
      else if (flag === '--data-urlencode') {
        req.data = (req.data ? req.data + '&' : '') + val();
      } else if (flag === '--json') {
        req.jsonRaw = val();
        req.headers.push('Content-Type: application/json');
        req.headers.push('Accept: application/json');
      } else if (flag === '-u' || flag === '--user') req.auth = val();
      else if (flag === '-k' || flag === '--insecure') req.insecure = true;
      else if (flag === '--compressed') { /* accept gzip; requests does this by default */ }
      else if (flag === '-A' || flag === '--user-agent') req.userAgent = val();
      else if (flag === '-b' || flag === '--cookie') req.cookie = val();
      else if (flag === '-e' || flag === '--referer') req.referer = val();
      else if (flag === '-L' || flag === '--location') req.location = true;
      else if (flag === '--max-redirs') { val(); }
      else if (flag === '-I' || flag === '--head') { req.head = true; req.method = req.method || 'HEAD'; }
      else if (flag === '-G' || flag === '--get') req.get = true;
      else if (flag === '-F' || flag === '--form' || flag === '--form-string') req.form.push(val());
      else if (flag === '--url') req.url = val();
      else if (flag === '-s' || flag === '--silent' || flag === '-S' || flag === '--show-error' || flag === '-v' || flag === '--verbose' || flag === '-i' || flag === '--include' || flag === '--fail' || flag === '-f' || flag === '--http1.1' || flag === '--http2' || flag === '-#') {
        /* ignore */
      } else if (flag === '-o' || flag === '--output' || flag === '--connect-timeout' || flag === '-m' || flag === '--max-time' || flag === '-x' || flag === '--proxy') {
        val();
      } else {
        throw new Error('Unsupported curl flag: ' + flag);
      }
      i++;
    }
    if (!req.url) throw new Error('No URL found');
    if (!req.method) {
      req.method = (req.data || req.jsonRaw || req.form.length) && !req.get ? 'POST' : (req.head ? 'HEAD' : 'GET');
    }
    if (req.get && req.data) {
      req.url += (req.url.indexOf('?') >= 0 ? '&' : '?') + req.data;
      req.data = null;
    }
    return req;
  }
  function headersObj(list) {
    const o = {};
    list.forEach(function (h) {
      const n = h.indexOf(':');
      if (n === -1) return;
      const key = h.slice(0, n).trim();
      if (o[key] == null) o[key] = h.slice(n + 1).trim();
    });
    return o;
  }
  function pyStr(s) { return JSON.stringify(s); }
  function pyDict(obj) {
    const keys = Object.keys(obj);
    if (!keys.length) return '{}';
    const inner = keys.map(function (k) {
      return '    ' + pyStr(k) + ': ' + pyStr(obj[k]);
    }).join(',\n');
    return '{\n' + inner + '\n}';
  }
  function emit(kind, req) {
    const headers = headersObj(req.headers);
    if (req.userAgent) headers['User-Agent'] = req.userAgent;
    if (req.cookie) headers.Cookie = req.cookie;
    if (req.referer) headers.Referer = req.referer;
    const ct = (headers['Content-Type'] || headers['content-type'] || '').toLowerCase();
    let jsonObj = null;
    let data = req.data;
    if (req.jsonRaw) {
      try { jsonObj = JSON.parse(req.jsonRaw); } catch (e) { data = req.jsonRaw; }
    } else if (data && ct.indexOf('application/json') !== -1) {
      try { jsonObj = JSON.parse(data); data = null; } catch (e) {}
    }
    const lines = [];
    const method = req.method.toLowerCase();
    const fn = ['get','post','put','patch','delete','head','options'].indexOf(method) >= 0 ? method : 'request';
    if (kind === 'requests') {
      lines.push('import requests');
      lines.push('');
      lines.push('url = ' + pyStr(req.url));
      if (Object.keys(headers).length) lines.push('headers = ' + pyDict(headers));
      if (req.auth) {
        const a = req.auth.split(':');
        lines.push('auth = (' + pyStr(a[0]) + ', ' + pyStr(a.slice(1).join(':')) + ')');
      }
      const args = ['url'];
      if (Object.keys(headers).length) args.push('headers=headers');
      if (jsonObj) {
        lines.push('json_body = ' + JSON.stringify(jsonObj, null, 4));
        args.push('json=json_body');
      } else if (data) {
        lines.push('data = ' + pyStr(data));
        args.push('data=data');
      }
      if (req.form.length) {
        lines.push('# multipart -F fields; refine files= as needed');
        lines.push('files = ' + pyStr(req.form));
        args.push('files=files');
      }
      if (req.auth) args.push('auth=auth');
      if (req.insecure) args.push('verify=False');
      if (req.location === false) args.push('allow_redirects=False');
      if (fn === 'request') lines.push('response = requests.request(' + pyStr(req.method) + ', ' + args.join(', ') + ')');
      else lines.push('response = requests.' + fn + '(' + args.join(', ') + ')');
      lines.push('print(response.status_code)');
      lines.push('print(response.text)');
    } else {
      lines.push('import httpx');
      lines.push('');
      lines.push('url = ' + pyStr(req.url));
      if (Object.keys(headers).length) lines.push('headers = ' + pyDict(headers));
      const args = ['url'];
      if (Object.keys(headers).length) args.push('headers=headers');
      if (jsonObj) {
        lines.push('json_body = ' + JSON.stringify(jsonObj, null, 4));
        args.push('json=json_body');
      } else if (data) {
        lines.push('data = ' + pyStr(data));
        args.push('data=data');
      }
      if (req.form.length) {
        lines.push('files = ' + pyStr(req.form));
        args.push('files=files');
      }
      if (req.auth) {
        const a = req.auth.split(':');
        args.push('auth=(' + pyStr(a[0]) + ', ' + pyStr(a.slice(1).join(':')) + ')');
      }
      const clientArgs = [];
      if (req.insecure) clientArgs.push('verify=False');
      lines.push('with httpx.Client(' + clientArgs.join(', ') + ') as client:');
      if (fn === 'request') lines.push('    response = client.request(' + pyStr(req.method) + ', ' + args.join(', ') + ')');
      else lines.push('    response = client.' + fn + '(' + args.join(', ') + ')');
      lines.push('    print(response.status_code)');
      lines.push('    print(response.text)');
    }
    return lines.join('\n') + '\n';
  }
  function render() {
    try {
      const req = parseCurl($('cmd').value);
      $('req').value = emit('requests', req);
      $('httpx').value = emit('httpx', req);
      $('status').className = 'status ok';
      $('status').textContent = req.method + ' ' + req.url;
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
    }
  }
  globalThis.CurlTool = { parseCurl: parseCurl, emit: emit };
  C2S.bindLive(['cmd'], render);
})();
"""

JS["json-to-yaml-converter"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };

  function isObj(v) { return v && typeof v === 'object' && !Array.isArray(v); }
  function yamlKey(k) {
    if (/^[A-Za-z_][A-Za-z0-9_-]*$/.test(k)) return k;
    return JSON.stringify(String(k));
  }
  function dumpYaml(value, indent) {
    indent = indent || 0;
    const pad = '  '.repeat(indent);
    if (value === null) return 'null';
    if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'null';
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'string') return C2S.yamlString(value);
    if (Array.isArray(value)) {
      if (!value.length) return '[]';
      return value.map(function (item) {
        if (isObj(item) && Object.keys(item).length) {
          const inner = dumpYaml(item, indent + 1);
          const lines = inner.split('\n');
          const firstPad = '  '.repeat(indent + 1);
          const first = lines[0].startsWith(firstPad) ? lines[0].slice(firstPad.length) : lines[0];
          return pad + '- ' + first + (lines.length > 1 ? '\n' + lines.slice(1).join('\n') : '');
        }
        if (Array.isArray(item) && item.length) {
          return pad + '-\n' + dumpYaml(item, indent + 1);
        }
        if (isObj(item) && !Object.keys(item).length) return pad + '- {}';
        if (Array.isArray(item) && !item.length) return pad + '- []';
        return pad + '- ' + dumpYaml(item, 0);
      }).join('\n');
    }
    if (isObj(value)) {
      const keys = Object.keys(value);
      if (!keys.length) return '{}';
      return keys.map(function (k) {
        const v = value[k];
        if (v !== null && typeof v === 'object') {
          const empty = Array.isArray(v) ? !v.length : !Object.keys(v).length;
          if (empty) return pad + yamlKey(k) + ': ' + (Array.isArray(v) ? '[]' : '{}');
          return pad + yamlKey(k) + ':\n' + dumpYaml(v, indent + 1);
        }
        return pad + yamlKey(k) + ': ' + dumpYaml(v, 0);
      }).join('\n');
    }
    return C2S.yamlString(String(value));
  }
  function render() {
    try {
      const text = $('json').value.trim();
      if (!text) { $('yaml').value = ''; $('status').textContent = ''; return; }
      const data = JSON.parse(text);
      $('yaml').value = dumpYaml(data, 0) + '\n';
      $('status').className = 'status ok';
      $('status').textContent = 'Converted';
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
    }
  }
  globalThis.YamlTool = { dumpYaml: dumpYaml };
  C2S.bindLive(['json'], render);
})();
"""

JS["keepalive-timeout-calculator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function num(id) { return Number($(id).value); }
  function render() {
    const rps = Math.max(0.001, num('rps') || 0);
    const avg = Math.max(1, num('avg') || 1);
    const p99 = Math.max(avg, num('p99') || avg);
    const n = Math.max(1, Math.floor(num('n') || 1));
    const kb = Math.max(0, num('kb') || 0);
    const sf = Math.max(1, num('sf') || 1.3);
    const inflightAvg = rps * (avg / 1000);
    const inflightP99 = rps * (p99 / 1000);
    const perBackend = Math.ceil((inflightP99 / n) * sf);
    const pool = Math.max(2, Math.min(4096, perBackend));
    const idle = (pool * n) / rps;
    const keepalive = Math.max(15, Math.min(180, Math.round(idle * 3 + 8)));
    const albSafe = Math.min(keepalive, 55);
    const readTimeout = Math.max(60, Math.ceil(p99 * 6 / 1000) + 15);
    const sendTimeout = Math.max(30, Math.ceil(p99 * 3 / 1000) + 5);
    const mbps = (rps * kb * 8) / 1024;
    const recs = [
      ['In-flight (avg)', inflightAvg.toFixed(1) + ' connections (RPS × avg latency)'],
      ['In-flight (p99)', inflightP99.toFixed(1) + ' connections'],
      ['Keepalive pool / backend', String(pool)],
      ['Total pooled conns', String(pool * n)],
      ['Idle gap on a pooled conn', idle.toFixed(3) + ' s'],
      ['Suggested keepalive_timeout', keepalive + 's (cap 180s)'],
      ['ALB-safe idle / keepalive', albSafe + 's (ALB default idle is 60s)'],
      ['proxy_read_timeout', readTimeout + 's'],
      ['Approx payload bitrate', mbps.toFixed(2) + ' Mbit/s']
    ];
    $('kv').innerHTML = recs.map(function (r) {
      return '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>';
    }).join('');
    $('out').value = [
      '# nginx upstream (repeat server lines per backend)',
      'upstream app {',
      '    least_conn;',
      '    keepalive ' + pool + ';',
      '    keepalive_timeout ' + keepalive + 's;',
      '    keepalive_requests 1000;',
      '}',
      '',
      'location / {',
      '    proxy_http_version 1.1;',
      '    proxy_set_header Connection "";',
      '    proxy_connect_timeout 5s;',
      '    proxy_send_timeout ' + sendTimeout + 's;',
      '    proxy_read_timeout ' + readTimeout + 's;',
      '}',
      '',
      '# HAProxy: timeout http-keep-alive ' + keepalive + 's',
      '# Envoy: idle_timeout ' + keepalive + 's · Caddy reverse_proxy uses Go defaults (~3m idle)',
      '# Cloudflare / many CDNs idle ~100s — do not set origin keepalive longer than the edge idle timeout.'
    ].join('\n') + '\n';
  }
  C2S.bindLive(['rps','avg','p99','n','kb','sf'], render);
})();
"""

JS["dns-record-bind-formatter"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  const recs = $('recs');

  function addRec(type, name, prio, value) {
    const row = document.createElement('div');
    row.className = 'row-inline';
    row.innerHTML =
      '<select class="t"><option>A</option><option>AAAA</option><option>CNAME</option><option>TXT</option><option>MX</option><option>NS</option><option>SRV</option></select>' +
      '<input class="n grow" placeholder="www or @" spellcheck="false">' +
      '<input class="v grow" placeholder="value" spellcheck="false">' +
      '<input class="p" placeholder="prio" title="MX / SRV priority">' +
      '<button type="button" class="btn rm">Remove</button>';
    row.querySelector('.t').value = type || 'A';
    row.querySelector('.n').value = name || '';
    row.querySelector('.v').value = value || '';
    row.querySelector('.p').value = prio || '';
    row.querySelectorAll('input,select').forEach(function (el) {
      el.addEventListener('input', render);
      el.addEventListener('change', render);
    });
    row.querySelector('.rm').addEventListener('click', function () { row.remove(); render(); });
    recs.appendChild(row);
  }
  function fmtTxt(value) {
    const raw = String(value).replace(/^"|"$/g, '');
    const bytes = new TextEncoder().encode(raw);
    if (bytes.length <= 255) return '"' + raw.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
    const chunks = [];
    for (let i = 0; i < bytes.length; i += 255) {
      const slice = bytes.subarray(i, i + 255);
      let s = '';
      slice.forEach(function (b) { s += String.fromCharCode(b); });
      chunks.push('"' + s.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"');
    }
    return '(' + chunks.join(' ') + ')';
  }
  function render() {
    const origin = $('origin').value.trim() || 'example.com.';
    const ttl = $('ttl').value.trim() || '3600';
    const lines = ['; BIND zone snippet generated in-browser', '$TTL ' + ttl, '$ORIGIN ' + origin];
    if ($('soa').checked) {
      const mname = $('mname').value.trim() || 'ns1.example.com.';
      const rname = $('rname').value.trim() || 'hostmaster.example.com.';
      const serial = new Date().toISOString().slice(0, 10).replace(/-/g, '') + '01';
      lines.push('@ IN SOA ' + mname + ' ' + rname + ' (');
      lines.push('        ' + serial + ' ; serial');
      lines.push('        3600       ; refresh');
      lines.push('        900        ; retry');
      lines.push('        1209600    ; expire');
      lines.push('        300        ; minimum');
      lines.push('        )');
      lines.push('@ IN NS ' + mname);
    }
    recs.querySelectorAll('.row-inline').forEach(function (row) {
      const type = row.querySelector('.t').value;
      let name = row.querySelector('.n').value.trim() || '@';
      const value = row.querySelector('.v').value.trim();
      const prio = row.querySelector('.p').value.trim();
      if (!value) return;
      let rhs = value;
      if (type === 'TXT') rhs = fmtTxt(value);
      else if (type === 'MX') rhs = (prio || '10') + ' ' + value;
      else if (type === 'SRV') rhs = (prio || '0 5 443') + ' ' + value;
      lines.push([name, 'IN', type, rhs].join(' '));
    });
    $('out').value = lines.join('\n') + '\n';
    $('status').className = 'status';
    $('status').textContent = 'Names ending without a dot are relative to $ORIGIN. Use a trailing dot for FQDNs.';
  }
  $('add').addEventListener('click', function () { addRec('A', '', '', ''); render(); });
  C2S.bindLive(['origin','ttl','mname','rname','soa'], render);
  addRec('A', '@', '', '203.0.113.10');
  addRec('A', 'www', '', '203.0.113.10');
  addRec('MX', '@', '10', 'mail.example.com.');
  addRec('TXT', '@', '', 'v=spf1 mx -all');
  render();
})();
"""

JS["systemd-journald-filter-builder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    const parts = ['journalctl'];
    const unit = $('unit').value.trim();
    const ident = $('ident').value.trim();
    const pri = $('pri').value;
    const since = $('since').value.trim();
    const until = $('until').value.trim();
    const boot = $('boot').value;
    const fmt = $('outfmt').value;
    const lines = $('lines').value.trim();
    const grep = $('grep').value.trim();
    if (unit) parts.push('-u', C2S.shellQuote(unit));
    if (ident) parts.push('-t', C2S.shellQuote(ident));
    if (pri) parts.push('-p', pri);
    if (since) parts.push('--since', C2S.shellQuote(since));
    if (until) parts.push('--until', C2S.shellQuote(until));
    if (boot) {
      boot.split(/\s+/).forEach(function (b) { parts.push(b); });
    }
    if (fmt && fmt !== 'short') parts.push('-o', fmt);
    if (lines && !$('follow').checked) parts.push('-n', lines);
    if ($('follow').checked) parts.push('-f');
    if ($('reverse').checked) parts.push('-r');
    if ($('kernel').checked) parts.push('-k');
    if ($('catalog').checked) parts.push('--catalog');
    if ($('pager').checked) parts.push('--no-pager');
    if (grep) parts.push('-g', C2S.shellQuote(grep));
    $('out').value = parts.join(' ') + '\n';
  }
  C2S.bindLive(['unit','ident','pri','since','until','boot','outfmt','lines','grep','follow','reverse','pager','kernel','catalog'], render);
})();
"""

JS["iptables-rule-builder"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function render() {
    const bin = $('fam').value;
    const cmd = $('cmd').value;
    const chain = $('chain').value;
    const jump = $('jump').value;
    const proto = $('proto').value;
    const iface = $('iface').value.trim();
    const src = $('src').value.trim();
    const dst = $('dst').value.trim();
    const sport = $('sport').value.trim();
    const dport = $('dport').value.trim();
    const state = $('state').value.trim();
    const comment = $('comment').value.trim();
    const parts = [bin, cmd, chain];
    if (iface) parts.push(chain === 'OUTPUT' ? '-o' : '-i', iface);
    if (src) parts.push('-s', src);
    if (dst) parts.push('-d', dst);
    if (proto && proto !== 'all') parts.push('-p', proto);
    if (sport && proto !== 'all' && proto !== 'icmp') parts.push('--sport', sport);
    if (dport && proto !== 'all' && proto !== 'icmp') parts.push('--dport', dport);
    if ($('est').checked && state) parts.push('-m', 'conntrack', '--ctstate', state);
    if (comment) parts.push('-m', 'comment', '--comment', C2S.shellQuote(comment));
    if (jump === 'REJECT') {
      parts.push('-j', 'REJECT', '--reject-with', bin === 'ip6tables' ? 'icmp6-port-unreachable' : 'icmp-port-unreachable');
    } else {
      parts.push('-j', jump);
    }
    const lines = [parts.join(' ')];
    if (chain === 'INPUT' && proto !== 'all' && dport && jump === 'ACCEPT') {
      const out = [bin, cmd, 'OUTPUT'];
      if (iface) out.push('-o', iface);
      if (src) out.push('-d', src);
      if (dst) out.push('-s', dst);
      out.push('-p', proto);
      if (dport) out.push('--sport', dport);
      if ($('est').checked) out.push('-m', 'conntrack', '--ctstate', 'ESTABLISHED');
      out.push('-j', 'ACCEPT');
      lines.push(out.join(' ') + '  # established replies');
    }
    if ($('persist').checked) {
      lines.push('');
      lines.push('# Persist (Debian/Ubuntu): iptables-save > /etc/iptables/rules.v' + (bin === 'ip6tables' ? '6' : '4'));
      lines.push('# Or: netfilter-persistent save');
    }
    $('out').value = lines.join('\n') + '\n';
  }
  C2S.bindLive(['fam','cmd','chain','jump','proto','iface','src','dst','sport','dport','state','comment','est','persist'], render);
})();
"""

JS["uuid-v4-generator"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function uuidv4() {
    if (crypto.randomUUID) return crypto.randomUUID();
    const b = new Uint8Array(16);
    crypto.getRandomValues(b);
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    const h = Array.from(b).map(function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }
  function format(id) {
    let s = id;
    if (!$('hyphens').checked) s = s.replace(/-/g, '');
    if ($('upper').checked) s = s.toUpperCase();
    return s;
  }
  function generate(n) {
    const out = [];
    const count = Math.max(1, Math.min(500, n | 0));
    for (let i = 0; i < count; i++) out.push(format(uuidv4()));
    $('out').value = out.join('\n') + '\n';
  }
  function validate(text) {
    const t = text.trim();
    if (!t) { $('status').textContent = ''; return; }
    const re = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    const compact = /^[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}$/i;
    const ok = re.test(t) || compact.test(t.replace(/-/g, ''));
    $('status').className = 'status ' + (ok ? 'ok' : 'error');
    $('status').textContent = ok ? 'Valid UUID v4 layout' : 'Not a UUID v4 (version nibble must be 4, variant 8/9/a/b)';
  }
  $('gen').addEventListener('click', function () { generate(Number($('n').value)); });
  $('one').addEventListener('click', function () {
    const prev = $('out').value.replace(/\s+$/, '');
    const next = format(uuidv4());
    $('out').value = (prev ? prev + '\n' : '') + next + '\n';
  });
  $('check').addEventListener('input', function () { validate($('check').value); });
  ['n','upper','hyphens'].forEach(function (id) {
    $(id).addEventListener('change', function () { generate(Number($('n').value)); });
  });
  globalThis.UuidTool = { uuidv4: uuidv4 };
  generate(1);
})();
"""

JS["regex-cheatsheet-tester"] = r"""
'use strict';
(function () {
  const $ = function (id) { return document.getElementById(id); };
  function flags() {
    return ($('g').checked ? 'g' : '') + ($('i').checked ? 'i' : '') + ($('m').checked ? 'm' : '') + ($('s').checked ? 's' : '');
  }
  function render() {
    const pat = $('pat').value;
    const text = $('text').value;
    $('hi').textContent = '';
    try {
      const re = new RegExp(pat, flags());
      const matches = [];
      if (re.global) {
        re.lastIndex = 0;
        let m;
        while ((m = re.exec(text)) !== null) {
          matches.push(m);
          if (m[0] === '') re.lastIndex++;
          if (matches.length > 5000) break;
        }
      } else {
        const m = re.exec(text);
        if (m) matches.push(m);
      }
      $('status').className = 'status ok';
      $('status').textContent = matches.length + ' match' + (matches.length === 1 ? '' : 'es');
      const lines = matches.map(function (m, idx) {
        const groups = m.slice(1).map(function (g, i) { return '  $' + (i + 1) + '=' + JSON.stringify(g); }).join('\n');
        return '#' + (idx + 1) + ' index=' + m.index + ' ' + JSON.stringify(m[0]) + (groups ? '\n' + groups : '');
      });
      $('out').value = lines.join('\n') || '(no matches)';
      const ranges = matches.map(function (m) { return [m.index, m.index + m[0].length]; })
        .filter(function (r) { return r[1] >= r[0]; })
        .sort(function (a, b) { return a[0] - b[0]; });
      const frag = document.createDocumentFragment();
      let pos = 0;
      ranges.forEach(function (r) {
        if (r[0] < pos) return;
        if (r[0] > pos) frag.appendChild(document.createTextNode(text.slice(pos, r[0])));
        const mark = document.createElement('mark');
        mark.className = 'match-hit';
        mark.textContent = text.slice(r[0], r[1]);
        frag.appendChild(mark);
        pos = r[1];
      });
      if (pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
      $('hi').appendChild(frag);
    } catch (err) {
      $('status').className = 'status error';
      $('status').textContent = err.message;
      $('out').value = '';
      $('hi').textContent = text;
    }
  }
  C2S.bindLive(['pat','text','g','i','m','s'], render);
})();
"""


HTML["solana-mint-check"] = r"""
<section class="panel">
  <div class="preset-row">
    <button type="button" class="preset" data-mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v">USDC mint</button>
    <button type="button" class="preset" data-mint="So11111111111111111111111111111111111111112">Wrapped SOL</button>
  </div>
  <div class="form-grid two">
    <label class="field span-2">Mint address
      <input id="mint" spellcheck="false" placeholder="base58 mint address" autocomplete="off">
    </label>
    <label class="field span-2">Solana JSON-RPC URL
      <input id="rpc" spellcheck="false" value="https://solana-rpc.publicnode.com" autocomplete="off">
    </label>
  </div>
  <div class="btn-row">
    <button type="button" class="btn primary" id="check">Check authorities</button>
  </div>
  <p class="status" id="status" aria-live="polite"></p>
</section>
<section class="panel" id="result" hidden>
  <p class="verdict pending" id="verdict" aria-live="polite">—</p>
  <dl class="kv" id="kv"></dl>
</section>
<section class="explain">
  <h2>What PASS means</h2>
  <p>PASS only when parsed <code>mintAuthority</code> and <code>freezeAuthority</code> are both JSON <code>null</code> (revoked). Any set pubkey is FAIL. The request is <code>getAccountInfo</code> with <code>encoding: jsonParsed</code> sent from this browser to the RPC URL above. <code>https://api.mainnet-beta.solana.com</code> is the usual public endpoint, but it often answers browsers with HTTP 403, so the box defaults to a CORS-friendly public RPC.</p>
  <p>Token-2022 extensions (permanent delegate, transfer fee, mint close authority) are not part of this verdict. A public RPC can rate-limit or reject the browser; that shows as an error, not a FAIL.</p>
</section>
"""

HTML["safe-mech-decode"] = r"""
<section class="panel">
  <div class="preset-row">
    <button type="button" class="preset" id="example">Example calldata</button>
  </div>
  <div class="form-grid two">
    <label class="field span-2">Transaction hash or raw input
      <textarea id="tx" rows="6" spellcheck="false" placeholder="0x… 32-byte tx hash, or 0x6a761202… execTransaction calldata"></textarea>
    </label>
    <label class="field span-2">Chain JSON-RPC URL (used only for a tx hash)
      <input id="rpc" spellcheck="false" value="https://ethereum.publicnode.com" autocomplete="off">
    </label>
  </div>
  <div class="btn-row">
    <button type="button" class="btn primary" id="decode">Decode</button>
  </div>
  <p class="status" id="status" aria-live="polite"></p>
</section>
<section class="panel" id="result" hidden>
  <div class="output-head"><h2>Decoded fields</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <dl class="kv" id="kv"></dl>
  <textarea id="out" class="output" readonly rows="12" style="margin-top:0.8rem"></textarea>
  <div id="notes"></div>
</section>
<section class="explain">
  <h2>Safe and mech delivery</h2>
  <p>Gnosis Safe runs an inner call by submitting <code>execTransaction</code> (selector <code>0x6a761202</code>). The outer transaction <code>to</code> is the Safe. The decoded <code>to</code>, <code>value</code>, and <code>data</code> are what the Safe will call.</p>
  <p>A mech (for example an Olas delivery agent) is often just the <code>from</code> that lands this Safe transaction. The payload the mech delivers is the inner <code>data</code>, not the outer input. This page does not look up mech registries, request ids, or payment splits.</p>
  <h2>Limitations</h2>
  <ul>
    <li>Manual hex decode of the standard 10-word <code>execTransaction</code> head only. No ABI library, no signature recovery, no EIP-712 SafeTx hash, no nonce check.</li>
    <li>Other selectors (module calls, <code>deliver</code>, a different Safe generation) show the selector and byte length only.</li>
    <li>Inner data that starts with MultiSend <code>0x8d80ff0a</code> is flagged and not expanded.</li>
    <li>A 32-byte hash is loaded with <code>eth_getTransactionByHash</code>. The RPC must allow this browser (CORS). A failed lookup is an error, not a bad decode. Paste the raw input from a block explorer to skip the RPC.</li>
    <li><code>value</code> is wei. Nothing here prices the asset or checks that the transaction succeeded.</li>
  </ul>
</section>
"""

HTML["x402-inspect"] = r"""
<section class="panel">
  <p class="banner note">Browsers often cannot read a cross-origin HTTP 402. The server must send <code>Access-Control-Allow-Origin</code> and expose payment headers with <code>Access-Control-Expose-Headers</code>. If the fetch fails or the fields are empty, paste the raw response from <code>curl -D -</code>.</p>
  <div class="form-grid two">
    <label class="field span-2">URL to try (optional)
      <input id="url" spellcheck="false" placeholder="https://example.com/paid-resource" autocomplete="off">
    </label>
  </div>
  <div class="btn-row">
    <button type="button" class="btn primary" id="fetch">Try fetch</button>
  </div>
  <p class="status" id="fetch-status" aria-live="polite"></p>
</section>
<section class="panel">
  <label class="field">Raw response headers and body
    <textarea id="raw" rows="12" spellcheck="false" placeholder="HTTP/1.1 402 Payment Required
payment-required: …
content-type: application/json

{&quot;accepts&quot;:[{&quot;network&quot;:&quot;base&quot;,&quot;payTo&quot;:&quot;0x…&quot;,&quot;asset&quot;:&quot;0x…&quot;,&quot;maxAmountRequired&quot;:&quot;1000&quot;}]}"></textarea>
  </label>
  <div class="btn-row">
    <button type="button" class="btn primary" id="parse">Parse pasted response</button>
    <button type="button" class="btn" id="sample">Load sample 402</button>
  </div>
  <p class="status" id="status" aria-live="polite"></p>
</section>
<section class="panel" id="result" hidden>
  <p class="verdict pending" id="verdict" aria-live="polite">—</p>
  <div class="req-list" id="reqs"></div>
</section>
<section class="explain">
  <h2>What is parsed</h2>
  <p>The paste box accepts a status line, <code>Name: value</code> headers, a blank line, then a body. JSON objects (body or header) and base64 JSON header values are scanned for <code>network</code>, <code>payTo</code>, <code>asset</code>, and <code>amount</code> / <code>maxAmountRequired</code>. Nested <code>accepts</code> entries are listed separately.</p>
  <p>The fetch button is a best-effort <code>GET</code> in CORS mode. An opaque or blocked response cannot be inspected from this page; use the paste box. This does not pay anyone and does not build an <code>X-PAYMENT</code> payload.</p>
</section>
"""

HTML["discord-bot-offline"] = r"""
<section class="panel">
  <label class="field">Application ID
    <input id="app-id" inputmode="numeric" spellcheck="false" placeholder="123456789012345678" autocomplete="off">
  </label>
  <p class="status" id="id-status" aria-live="polite"></p>
  <h2>Invite scopes</h2>
  <div class="check-row">
    <label><input type="checkbox" id="scope-bot" checked> bot</label>
    <label><input type="checkbox" id="scope-commands" checked> applications.commands</label>
    <label><input type="checkbox" id="scope-cmd-perms"> applications.commands.permissions.update</label>
  </div>
  <label class="field" style="margin-top:0.8rem">Permissions bitfield (integer, used when <code>bot</code> is selected)
    <input id="perms" value="0" spellcheck="false" inputmode="numeric">
  </label>
  <div class="output-head" style="margin-top:0.9rem">
    <h2>Invite URL</h2>
    <button type="button" class="copy-btn" data-copy="#invite">Copy</button>
  </div>
  <textarea id="invite" class="output" readonly rows="4"></textarea>
</section>
<section class="panel">
  <h2>Offline checklist</h2>
  <ul class="checklist">
    <li>
      <label><input type="checkbox" id="chk-scopes"> Invite scopes</label>
      <p>The URL includes <code>bot</code> (and any slash-command scopes you need), and you opened it while logged into Discord to add this application to the server.</p>
    </li>
    <li>
      <label><input type="checkbox" id="chk-content"> Message Content Intent</label>
      <p>Privileged intent in the Developer Portal under Bot. If your library requests message content and the portal toggle is off, the gateway closes and the bot stays offline.</p>
    </li>
    <li>
      <label><input type="checkbox" id="chk-presence"> Presence Intent</label>
      <p>Also privileged. Turn it on only when the process requests presence. Requesting it while it is disabled in the portal is a common disconnect.</p>
    </li>
    <li>
      <label><input type="checkbox" id="chk-gateway"> Gateway running</label>
      <p>The bot process is up, the token belongs to this application, and the logs show a gateway connection rather than a crash loop.</p>
    </li>
    <li>
      <label><input type="checkbox" id="chk-online"> Bot user online</label>
      <p>In the server member list the bot user is online, idle, or dnd. Offline means there is no live gateway session for this bot user.</p>
    </li>
  </ul>
  <p class="verdict pending" id="summary" aria-live="polite" style="margin-top:0.9rem"></p>
  <p class="status" id="next"></p>
</section>
<section class="explain">
  <h2>No Discord API</h2>
  <p>Nothing on this page calls Discord. The invite URL is <code>https://discord.com/api/oauth2/authorize</code> with your application id, the scopes you tick, and a permissions integer. The checklist is local state in this tab. Presence intent is not required for every bot to show online; leave it unchecked until you have confirmed that your code actually requests it.</p>
</section>
"""


JS["solana-mint-check"] = r"""
'use strict';
(function (root) {
  const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

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

  function validMint(text) {
    const bytes = decodeBase58(String(text || '').trim());
    return !!(bytes && bytes.length === 32);
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

  root.SolanaMintCheck = {
    decodeBase58: decodeBase58,
    validMint: validMint,
    classifyMint: classifyMint
  };

  if (!root.document || !root.document.getElementById) return;
  const $ = function (id) { return document.getElementById(id); };

  function setKv(rows) {
    const dl = $('kv');
    dl.replaceChildren();
    rows.forEach(function (row) {
      const dt = document.createElement('dt');
      dt.textContent = row[0];
      const dd = document.createElement('dd');
      dd.textContent = row[1] == null ? '' : String(row[1]);
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
  }

  function showError(msg) {
    $('result').hidden = true;
    $('status').className = 'status error';
    $('status').textContent = msg;
  }

  function programName(owner) {
    if (owner === 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA') return 'SPL Token';
    if (owner === 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb') return 'Token-2022';
    return owner || 'unknown';
  }

  async function check() {
    const mint = $('mint').value.trim();
    const rpc = $('rpc').value.trim();
    $('status').className = 'status';
    $('status').textContent = 'Asking the RPC…';
    $('result').hidden = true;
    if (!validMint(mint)) {
      showError('That does not look like a Solana address (base58, 32 bytes).');
      return;
    }
    let url;
    try {
      url = new URL(rpc);
    } catch (err) {
      showError('The RPC URL is not valid. Use an https:// endpoint such as https://api.mainnet-beta.solana.com.');
      return;
    }
    if (url.protocol !== 'https:' && url.hostname !== 'localhost' && url.hostname !== '127.0.0.1') {
      showError('Use an https:// RPC URL so the browser can call it.');
      return;
    }
    let res;
    try {
      res = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'getAccountInfo',
          params: [mint, { encoding: 'jsonParsed' }]
        })
      });
    } catch (err) {
      showError('The RPC request did not complete. The endpoint may be rate-limiting this browser, blocking cross-origin calls, or temporarily offline. Try again or paste a different HTTPS RPC URL.');
      return;
    }
    let payload = null;
    try {
      payload = await res.json();
    } catch (err) {
      payload = null;
    }
    if (!res.ok) {
      const msg = payload && payload.error && payload.error.message;
      if (res.status === 403) {
        showError('The RPC refused this browser' + (msg ? ' (' + msg + ')' : '') + '. https://api.mainnet-beta.solana.com often returns HTTP 403 to web pages. Switch the RPC URL to another HTTPS endpoint, such as https://solana-rpc.publicnode.com, and try again.');
      } else if (msg) {
        showError('RPC error (HTTP ' + res.status + '): ' + msg);
      } else {
        showError('The RPC returned HTTP ' + res.status + '. No mint data was read.');
      }
      return;
    }
    if (!payload) {
      showError('The RPC response was not JSON, so the mint could not be read.');
      return;
    }
    if (payload.error) {
      const msg = (payload.error && payload.error.message) || 'The RPC returned an error.';
      showError('RPC error: ' + msg);
      return;
    }
    const value = payload.result && payload.result.value;
    if (!value) {
      showError('No account exists at that address on this cluster. Check the mint and that the RPC matches the cluster you expect.');
      return;
    }
    const parsed = value.data && value.data.parsed;
    const info = parsed && parsed.info;
    if (!parsed || parsed.type !== 'mint' || !info) {
      showError('The account exists, but it is not a parsed token mint (owner ' + (value.owner || 'unknown') + '). PASS/FAIL applies only to mint accounts.');
      return;
    }
    const verdict = classifyMint(info);
    if (!verdict) {
      showError('The mint account was returned, but mintAuthority and freezeAuthority were missing from the parsed JSON.');
      return;
    }
    $('result').hidden = false;
    const el = $('verdict');
    if (verdict.pass) {
      el.className = 'verdict pass';
      el.textContent = 'PASS — mintAuthority and freezeAuthority are null (revoked)';
    } else {
      const why = [];
      if (!verdict.mintRevoked) why.push('mintAuthority is still set');
      if (!verdict.freezeRevoked) why.push('freezeAuthority is still set');
      el.className = 'verdict fail';
      el.textContent = 'FAIL — ' + why.join('; ');
    }
    setKv([
      ['mint', mint],
      ['program', programName(value.owner)],
      ['owner', value.owner || ''],
      ['decimals', info.decimals],
      ['supply', info.supply],
      ['mintAuthority', verdict.mintAuthority === null ? 'null (revoked)' : verdict.mintAuthority],
      ['freezeAuthority', verdict.freezeAuthority === null ? 'null (revoked)' : verdict.freezeAuthority],
      ['initialized', info.isInitialized ? 'yes' : 'no']
    ]);
    $('status').className = 'status ok';
    $('status').textContent = 'Read the mint with getAccountInfo (jsonParsed).';
  }

  document.querySelectorAll('[data-mint]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      $('mint').value = btn.getAttribute('data-mint');
      check();
    });
  });
  $('check').addEventListener('click', function () { check(); });
  $('mint').addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter') check();
  });
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""

JS["safe-mech-decode"] = r"""
'use strict';
(function (root) {
  const EXEC_SELECTOR = '6a761202';
  const MULTISEND_SELECTOR = '8d80ff0a';
  const EXAMPLE = '6a76120200000000000000000000000011111111111111111111111111111111111111110000000000000000000000000000000000000000000000000de0b6b3a7640000000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000222222222222222222222222222222222222222200000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000004aabbccdd000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000041111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111100000000000000000000000000000000000000000000000000000000000000';

  function normalizeHex(input) {
    let s = String(input || '').trim().replace(/\s+/g, '');
    if (/^0x/i.test(s)) s = s.slice(2);
    if (!s || /[^0-9a-fA-F]/.test(s) || (s.length % 2) !== 0) return null;
    return s.toLowerCase();
  }

  function isTxHash(hex) {
    return !!hex && hex.length === 64;
  }

  function u256(word) {
    return BigInt('0x' + word);
  }

  function addressOf(word) {
    return '0x' + word.slice(24);
  }

  function dirtyAddress(word) {
    return word.slice(0, 24) !== '000000000000000000000000';
  }

  function readBytes(hex, offsetWord) {
    const offset = u256(offsetWord);
    if (offset > 5000000n) throw new Error('A dynamic offset is larger than this decoder accepts.');
    const start = 8 + Number(offset) * 2;
    if (start < 8 || start + 64 > hex.length) {
      throw new Error('A dynamic bytes offset points past the end of the input.');
    }
    const len = u256(hex.slice(start, start + 64));
    if (len > 2000000n) throw new Error('A bytes length is larger than this decoder accepts.');
    const n = Number(len);
    const dataStart = start + 64;
    const dataEnd = dataStart + n * 2;
    if (dataEnd > hex.length) throw new Error('The bytes payload is shorter than its length word.');
    return { hex: hex.slice(dataStart, dataEnd), length: n };
  }

  function formatWei(dec) {
    const bi = BigInt(dec);
    const sign = bi < 0n ? '-' : '';
    const v = bi < 0n ? -bi : bi;
    const whole = v / 1000000000000000000n;
    let frac = (v % 1000000000000000000n).toString().padStart(18, '0').replace(/0+$/, '');
    const eth = sign + whole.toString() + (frac ? '.' + frac : '');
    return bi.toString() + ' wei (' + eth + ' ETH)';
  }

  function decodeExecTransaction(input) {
    const hex = normalizeHex(input);
    if (!hex) return { ok: false, error: 'Input is not even-length hex.' };
    if (isTxHash(hex)) {
      return { ok: false, needsRpc: true, hash: '0x' + hex, error: 'This is a transaction hash. Add an RPC URL or paste calldata.' };
    }
    if (hex.length < 8) return { ok: false, error: 'Calldata is shorter than a 4-byte selector.' };
    const selector = hex.slice(0, 8);
    const result = {
      ok: true,
      selector: '0x' + selector,
      recognized: selector === EXEC_SELECTOR,
      name: selector === EXEC_SELECTOR ? 'execTransaction' : (selector === MULTISEND_SELECTOR ? 'multiSend' : 'unknown'),
      byteLength: hex.length / 2,
      warnings: []
    };
    if (selector !== EXEC_SELECTOR) {
      result.warnings.push('Selector is not Safe execTransaction (0x6a761202). Only the selector and total calldata length are shown.');
      return result;
    }
    if (hex.length < 8 + 10 * 64) {
      result.recognized = false;
      result.warnings.push('Calldata is shorter than the execTransaction head (selector + 10 words).');
      return result;
    }
    const words = [];
    for (let i = 0; i < 10; i++) words.push(hex.slice(8 + i * 64, 8 + (i + 1) * 64));
    if (dirtyAddress(words[0])) result.warnings.push('The to word has non-zero high bytes (not a clean address).');
    if (dirtyAddress(words[7])) result.warnings.push('The gasToken word has non-zero high bytes.');
    if (dirtyAddress(words[8])) result.warnings.push('The refundReceiver word has non-zero high bytes.');
    let data;
    let sigs;
    try {
      data = readBytes(hex, words[2]);
      sigs = readBytes(hex, words[9]);
    } catch (err) {
      result.recognized = false;
      result.warnings.push(err.message || 'ABI decode failed.');
      return result;
    }
    const operation = u256(words[3]);
    result.to = addressOf(words[0]);
    result.valueWei = u256(words[1]).toString();
    result.dataLength = data.length;
    result.dataHex = data.hex;
    result.dataSelector = data.length >= 4 ? '0x' + data.hex.slice(0, 8) : '';
    result.operation = operation.toString();
    result.operationName = operation === 0n ? 'CALL' : (operation === 1n ? 'DELEGATECALL' : 'unknown');
    result.safeTxGas = u256(words[4]).toString();
    result.baseGas = u256(words[5]).toString();
    result.gasPrice = u256(words[6]).toString();
    result.gasToken = addressOf(words[7]);
    result.refundReceiver = addressOf(words[8]);
    result.signaturesLength = sigs.length;
    if (operation === 1n) {
      result.warnings.push('operation is DELEGATECALL. The Safe would run the inner data in its own storage context.');
    }
    if (result.dataSelector === '0x' + MULTISEND_SELECTOR) {
      result.warnings.push('Inner data starts with MultiSend (0x8d80ff0a). Nested calls are not expanded.');
    }
    return result;
  }

  root.SafeMechDecode = {
    normalizeHex: normalizeHex,
    isTxHash: isTxHash,
    decodeExecTransaction: decodeExecTransaction,
    formatWei: formatWei,
    exampleCalldata: '0x' + EXAMPLE
  };

  if (!root.document || !root.document.getElementById) return;
  const $ = function (id) { return document.getElementById(id); };

  function setKv(rows) {
    const dl = $('kv');
    dl.replaceChildren();
    rows.forEach(function (row) {
      const dt = document.createElement('dt');
      dt.textContent = row[0];
      const dd = document.createElement('dd');
      dd.textContent = row[1] == null ? '' : String(row[1]);
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
  }

  function showError(msg) {
    $('result').hidden = true;
    $('status').className = 'status error';
    $('status').textContent = msg;
  }

  function renderDecoded(decoded, extraRows) {
    const rows = (extraRows || []).slice();
    rows.push(['selector', decoded.selector]);
    rows.push(['function', decoded.name]);
    rows.push(['calldata bytes', String(decoded.byteLength)]);
    if (decoded.recognized && decoded.to) {
      rows.push(['to', decoded.to]);
      rows.push(['value', formatWei(decoded.valueWei)]);
      rows.push(['data length', String(decoded.dataLength) + ' bytes']);
      rows.push(['data selector', decoded.dataSelector || '(shorter than 4 bytes)']);
      rows.push(['operation', decoded.operation + ' (' + decoded.operationName + ')']);
      rows.push(['safeTxGas', decoded.safeTxGas]);
      rows.push(['baseGas', decoded.baseGas]);
      rows.push(['gasPrice', decoded.gasPrice]);
      rows.push(['gasToken', decoded.gasToken]);
      rows.push(['refundReceiver', decoded.refundReceiver]);
      rows.push(['signatures length', String(decoded.signaturesLength) + ' bytes']);
    }
    setKv(rows);
    const lines = rows.map(function (row) { return row[0] + ': ' + row[1]; });
    if (decoded.dataHex) {
      const preview = decoded.dataHex.length > 128 ? decoded.dataHex.slice(0, 128) + '…' : decoded.dataHex;
      lines.push('data hex: 0x' + preview);
    }
    (decoded.warnings || []).forEach(function (w) { lines.push('note: ' + w); });
    $('out').value = lines.join('\n');
    const notes = $('notes');
    notes.replaceChildren();
    (decoded.warnings || []).forEach(function (w) {
      const p = document.createElement('p');
      p.className = 'banner warn';
      p.textContent = w;
      notes.appendChild(p);
    });
    $('result').hidden = false;
    $('status').className = 'status ok';
    $('status').textContent = decoded.recognized
      ? 'Decoded execTransaction locally. This does not prove the Safe executed it.'
      : 'Showed what could be read. See the notes for what was skipped.';
  }

  async function decode() {
    const raw = $('tx').value;
    const hex = normalizeHex(raw);
    $('result').hidden = true;
    if (!hex) {
      showError('Paste a transaction hash or even-length hex calldata (optional 0x prefix).');
      return;
    }
    if (!isTxHash(hex)) {
      const decoded = decodeExecTransaction(hex);
      if (!decoded.ok) {
        showError(decoded.error || 'Could not decode that input.');
        return;
      }
      renderDecoded(decoded, []);
      return;
    }
    const rpc = $('rpc').value.trim();
    let url;
    try {
      url = new URL(rpc);
    } catch (err) {
      showError('That hash needs an https:// JSON-RPC URL, or paste the raw transaction input instead.');
      return;
    }
    if (url.protocol !== 'https:' && url.hostname !== 'localhost' && url.hostname !== '127.0.0.1') {
      showError('Use an https:// RPC URL, or paste the raw input to decode it on this page.');
      return;
    }
    $('status').className = 'status';
    $('status').textContent = 'Loading the transaction…';
    let res;
    try {
      res = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'eth_getTransactionByHash',
          params: ['0x' + hex]
        })
      });
    } catch (err) {
      showError('The RPC request did not complete. The endpoint may be blocking this browser (CORS), rate-limiting, or offline. Paste the raw input hex to decode without an RPC.');
      return;
    }
    if (!res.ok) {
      showError('The RPC returned HTTP ' + res.status + '. No transaction was read.');
      return;
    }
    let payload;
    try {
      payload = await res.json();
    } catch (err) {
      showError('The RPC response was not JSON.');
      return;
    }
    if (payload.error) {
      const msg = (payload.error && payload.error.message) || 'The RPC returned an error.';
      showError('RPC error: ' + msg);
      return;
    }
    if (!payload.result) {
      showError('No transaction with that hash was found on this RPC. It may be the wrong chain, or the node may not have it yet.');
      return;
    }
    const tx = payload.result;
    const input = tx.input || tx.data || '';
    const decoded = decodeExecTransaction(input);
    if (!decoded.ok) {
      showError(decoded.error || 'The transaction input could not be decoded.');
      return;
    }
    let block = tx.blockNumber || 'pending';
    if (typeof block === 'string' && /^0x/i.test(block)) {
      try { block = BigInt(block).toString(); } catch (err) { block = tx.blockNumber; }
    }
    renderDecoded(decoded, [
      ['tx hash', tx.hash || ('0x' + hex)],
      ['from', tx.from || ''],
      ['safe (tx.to)', tx.to || ''],
      ['outer value', formatWei(BigInt(tx.value || '0x0').toString())],
      ['block', String(block)]
    ]);
  }

  $('example').addEventListener('click', function () {
    $('tx').value = '0x' + EXAMPLE;
    decode();
  });
  $('decode').addEventListener('click', function () { decode(); });
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""

JS["x402-inspect"] = r"""
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
      const decoded = new TextDecoder().decode(bytes);
      return tryJson(decoded);
    } catch (err) {
      return null;
    }
  }

  function parseDump(raw) {
    const text = String(raw || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const trimmed = text.trim();
    if (!trimmed) return { status: null, headers: {}, body: '' };
    if (trimmed[0] === '{' || trimmed[0] === '[') {
      return { status: null, headers: {}, body: trimmed };
    }
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
      if (statusMatch) {
        status = Number(statusMatch[1]);
        return;
      }
      const headerMatch = line.match(/^([^:\s][^:]*):\s*(.*)$/);
      if (!headerMatch) return;
      const name = headerMatch[1].trim().toLowerCase();
      const value = headerMatch[2].trim();
      if (Object.prototype.hasOwnProperty.call(headers, name)) headers[name] += ', ' + value;
      else headers[name] = value;
    });
    return { status: status, headers: headers, body: body.trim() };
  }

  function collect(node, found, source) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(function (item) { collect(item, found, source); });
      return;
    }
    const rec = { source: source };
    let any = false;
    Object.keys(node).forEach(function (key) {
      const mapped = FIELD_MAP[String(key).toLowerCase()];
      if (!mapped) return;
      const val = node[key];
      if (val == null || typeof val === 'object') return;
      rec[mapped] = String(val);
      any = true;
    });
    if (any) {
      if (node.scheme != null && typeof node.scheme !== 'object') rec.scheme = String(node.scheme);
      found.push(rec);
    }
    Object.keys(node).forEach(function (key) {
      const child = node[key];
      if (child && typeof child === 'object') collect(child, found, source);
    });
  }

  function dedupe(found) {
    const map = new Map();
    found.forEach(function (rec) {
      const key = [rec.network || '', rec.payTo || '', rec.asset || '', rec.amount || ''].join('|').toLowerCase();
      if (!key.replace(/\|/g, '')) return;
      const prev = map.get(key);
      if (!prev) {
        map.set(key, rec);
        return;
      }
      if (prev.source.indexOf(rec.source) === -1) prev.source += ', ' + rec.source;
      if (!prev.scheme && rec.scheme) prev.scheme = rec.scheme;
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
      if (asJson) {
        collect(asJson, found, 'header ' + name);
        return;
      }
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
    return {
      status: parsed.status,
      requirements: dedupe(found)
    };
  }

  const SAMPLE = [
    'HTTP/1.1 402 Payment Required',
    'content-type: application/json',
    'payment-required: eyJ4NDAyVmVyc2lvbiI6MSwibmV0d29yayI6ImJhc2UiLCJwYXlUbyI6IjB4YWJjMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSIsImFzc2V0IjoiMHh1c2RjMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAyIiwiYW1vdW50IjoiMTAwMCJ9',
    '',
    '{"x402Version":1,"accepts":[{"scheme":"exact","network":"base-sepolia","maxAmountRequired":"2500","payTo":"0xpayto000000000000000000000000000000000001","asset":"0xasset000000000000000000000000000000000002"}]}'
  ].join('\n');

  root.X402Inspect = {
    parseDump: parseDump,
    extractRequirements: extractRequirements,
    sample: SAMPLE
  };

  if (!root.document || !root.document.getElementById) return;
  const $ = function (id) { return document.getElementById(id); };

  function render(parsed, note) {
    const extracted = extractRequirements(parsed);
    const reqs = extracted.requirements;
    const box = $('reqs');
    box.replaceChildren();
    const verdict = $('verdict');
    if (!reqs.length) {
      verdict.className = 'verdict fail';
      verdict.textContent = extracted.status === 402
        ? 'HTTP 402, but no payment fields were found'
        : 'No network, payTo, asset, or amount fields';
    } else {
      verdict.className = 'verdict pass';
      const bits = [];
      if (extracted.status) bits.push('HTTP ' + extracted.status);
      bits.push(reqs.length + ' payment requirement' + (reqs.length === 1 ? '' : 's'));
      verdict.textContent = bits.join(' · ');
    }
    if (note) {
      const p = document.createElement('p');
      p.className = 'banner note';
      p.textContent = note;
      box.appendChild(p);
    }
    if (!reqs.length) {
      const p = document.createElement('p');
      p.className = 'banner warn';
      p.textContent = 'Nothing matched. Paste the full 402 response, including a JSON body or a payment-required header (raw JSON or base64 JSON).';
      box.appendChild(p);
    }
    reqs.forEach(function (rec, idx) {
      const card = document.createElement('article');
      card.className = 'req-card';
      const h = document.createElement('h3');
      h.textContent = 'Requirement ' + (idx + 1) + (rec.scheme ? ' · ' + rec.scheme : '');
      card.appendChild(h);
      const dl = document.createElement('dl');
      dl.className = 'kv';
      [
        ['network', rec.network || '—'],
        ['payTo', rec.payTo || '—'],
        ['asset', rec.asset || '—'],
        ['amount', rec.amount || '—'],
        ['source', rec.source || '']
      ].forEach(function (row) {
        const dt = document.createElement('dt');
        dt.textContent = row[0];
        const dd = document.createElement('dd');
        dd.textContent = row[1];
        dl.appendChild(dt);
        dl.appendChild(dd);
      });
      card.appendChild(dl);
      box.appendChild(card);
    });
    $('result').hidden = false;
    $('status').className = reqs.length ? 'status ok' : 'status warn';
    $('status').textContent = reqs.length
      ? 'Parsed payment fields from the pasted response.'
      : 'Parsed the response, but the payment fields were missing.';
  }

  async function tryFetch() {
    const raw = $('url').value.trim();
    let url;
    try {
      url = new URL(raw);
    } catch (err) {
      $('fetch-status').className = 'status error';
      $('fetch-status').textContent = 'Enter a full http:// or https:// URL, or skip fetch and paste the response below.';
      return;
    }
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      $('fetch-status').className = 'status error';
      $('fetch-status').textContent = 'Only http and https URLs can be fetched from this page.';
      return;
    }
    $('fetch-status').className = 'status';
    $('fetch-status').textContent = 'Fetching… browsers will hide this response if the server does not allow CORS.';
    let res;
    try {
      res = await fetch(url.toString(), { method: 'GET', mode: 'cors', cache: 'no-store', redirect: 'follow' });
    } catch (err) {
      $('fetch-status').className = 'status error';
      $('fetch-status').textContent = 'The browser could not read that URL. That is usually CORS, mixed content, or a network block. Paste the raw 402 from curl -D - into the box below.';
      return;
    }
    const headers = {};
    res.headers.forEach(function (value, key) { headers[String(key).toLowerCase()] = value; });
    let body = '';
    try { body = await res.text(); } catch (err) { body = ''; }
    const headerLines = Object.keys(headers).map(function (name) { return name + ': ' + headers[name]; });
    $('raw').value = ['HTTP/1.1 ' + res.status, headerLines.join('\n'), '', body].join('\n');
    const note = 'Fetch completed with HTTP ' + res.status + '. Browsers only expose CORS-safelisted headers unless the server lists them in Access-Control-Expose-Headers, so payment headers may be missing even when the body is visible.';
    $('fetch-status').className = 'status ok';
    $('fetch-status').textContent = 'Fetched HTTP ' + res.status + ' and copied the readable headers and body into the paste box.';
    render({ status: res.status, headers: headers, body: body }, note);
  }

  $('parse').addEventListener('click', function () {
    render(parseDump($('raw').value), '');
  });
  $('sample').addEventListener('click', function () {
    $('raw').value = SAMPLE;
    render(parseDump(SAMPLE), 'Sample only — a synthetic 402 with a base64 payment-required header and a JSON body.');
  });
  $('fetch').addEventListener('click', function () { tryFetch(); });
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""

JS["discord-bot-offline"] = r"""
'use strict';
(function (root) {
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

  root.DiscordBotOffline = {
    buildInvite: buildInvite,
    selectedScopes: selectedScopes
  };

  if (!root.document || !root.document.getElementById) return;
  const $ = function (id) { return document.getElementById(id); };

  function render() {
    const id = $('app-id').value.trim();
    const idOk = /^\d{15,22}$/.test(id);
    $('id-status').className = 'status ' + (id && !idOk ? 'error' : (idOk ? 'ok' : ''));
    $('id-status').textContent = !id
      ? 'Paste the Application ID from the Discord Developer Portal (General Information).'
      : (idOk
        ? 'Application ID looks like a snowflake.'
        : 'Application IDs are numeric snowflakes, usually 17–20 digits.');
    const flags = {
      bot: $('scope-bot').checked,
      commands: $('scope-commands').checked,
      commandPerms: $('scope-cmd-perms').checked
    };
    $('invite').value = buildInvite(id, flags, $('perms').value);
    const items = [
      ['chk-scopes', 'Invite scopes'],
      ['chk-content', 'Message Content Intent'],
      ['chk-presence', 'Presence Intent'],
      ['chk-gateway', 'Gateway running'],
      ['chk-online', 'Bot user online']
    ];
    const pending = items.filter(function (item) { return !$(item[0]).checked; }).map(function (item) { return item[1]; });
    const summary = $('summary');
    if (!idOk) {
      summary.className = 'verdict fail';
      summary.textContent = 'Add a valid Application ID before using the invite URL';
    } else if (!flags.bot) {
      summary.className = 'verdict fail';
      summary.textContent = 'bot scope is off — this URL will not add a bot user';
    } else if (!pending.length) {
      summary.className = 'verdict pass';
      summary.textContent = 'Checklist complete';
    } else {
      summary.className = 'verdict pending';
      summary.textContent = pending.length + ' item' + (pending.length === 1 ? '' : 's') + ' still open';
    }
    $('next').textContent = pending.length
      ? 'Still to confirm: ' + pending.join(', ') + '.'
      : 'If the member list still shows the bot offline, compare the intents your code requests with the portal toggles, and confirm the host process is using this application’s token.';
  }

  C2S.bindLive([
    'app-id', 'scope-bot', 'scope-commands', 'scope-cmd-perms', 'perms',
    'chk-scopes', 'chk-content', 'chk-presence', 'chk-gateway', 'chk-online'
  ], render);
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""


NEEDS_CONVERTER = {
    "cron-to-systemd-timer",
    "crontab-generator",
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def clean_output() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "assets" / "tools").mkdir(parents=True)


def copy_flagship() -> None:
    dest = OUTPUT / FLAGSHIP["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("converter.js", "app.js", "styles.css", "favicon.svg"):
        shutil.copy2(ROOT / name, dest / name)
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    canon = canonical_for(FLAGSHIP["slug"])
    inject = [
        f'  <link rel="canonical" href="{esc(canon)}">',
        f'  <meta property="og:url" content="{esc(canon)}">',
        f'  <meta property="og:site_name" content="{esc(SITE_NAME)}">',
        '  <meta name="twitter:card" content="summary">',
    ]
    if 'rel="canonical"' not in src:
        src = src.replace("<head>", "<head>\n" + "\n".join(inject), 1)
    banner = (
        '  <p class="util-banner" style="width:min(1120px,calc(100% - 2rem));'
        'margin:0.8rem auto 0;font-size:0.9rem;">'
        '<a href="../">← All cron2systemd tools</a></p>\n'
    )
    if 'class="site-header"' in src:
        src = src.replace('<header class="site-header">', banner + '<header class="site-header">', 1)
    write_text(dest / "index.html", src)


def sitemap_xml(lastmod: str) -> str:
    urls = [canonical_for(None), canonical_for(FLAGSHIP["slug"])]
    urls.extend(canonical_for(t["slug"]) for t in TOOLS)
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        chunks.extend(
            [
                "  <url>",
                f"    <loc>{esc(url)}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "    <changefreq>weekly</changefreq>",
                "  </url>",
            ]
        )
    chunks.append("</urlset>")
    return "\n".join(chunks) + "\n"


def robots_txt() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def hub_title() -> str:
    return "cron2systemd developer utilities"


def hub_description() -> str:
    return (
        "Browser-only DevOps utilities: cron to systemd timers, crontab generator, "
        "nginx reverse proxy, Docker Compose, chmod, CIDR, journalctl, Solana mint "
        "checks, Safe calldata decode, x402 inspect, and a Discord bot checklist. "
        "Includes the flagship OnCalendar ↔ crontab converter."
    )


def build() -> None:
    missing = [t["slug"] for t in TOOLS if t["slug"] not in HTML or t["slug"] not in JS]
    if missing:
        raise SystemExit("Incomplete tool definitions: " + ", ".join(missing))

    clean_output()
    shutil.copy2(ROOT / "favicon.svg", OUTPUT / "assets" / "favicon.svg")
    shutil.copy2(ROOT / "favicon.svg", OUTPUT / "favicon.svg")
    shutil.copy2(ROOT / "converter.js", OUTPUT / "assets" / "converter.js")
    write_text(OUTPUT / "assets" / "site.css", SITE_CSS)
    write_text(OUTPUT / "assets" / "app.js", SHARED_JS)

    write_text(
        OUTPUT / "index.html",
        page(
            slug=None,
            title=hub_title(),
            description=hub_description(),
            body=hub_body(),
        ),
    )

    lookup = _by_slug()
    for tool in TOOLS:
        extra_js: list[str] = []
        if tool["slug"] in NEEDS_CONVERTER:
            extra_js.append("../assets/converter.js")
        extra_js.append(f"../assets/tools/{tool['slug']}.js")
        write_text(OUTPUT / "assets" / "tools" / f"{tool['slug']}.js", JS[tool["slug"]])
        write_text(
            OUTPUT / tool["slug"] / "index.html",
            page(
                slug=tool["slug"],
                title=tool["title"],
                description=tool["description"],
                body=tool_wrap(lookup[tool["slug"]], HTML[tool["slug"]]),
                extra_js=extra_js,
            ),
        )

    copy_flagship()
    lastmod = datetime.now(timezone.utc).date().isoformat()
    write_text(OUTPUT / "sitemap.xml", sitemap_xml(lastmod))
    write_text(OUTPUT / "robots.txt", robots_txt())

    pages = 2 + len(TOOLS)
    print(f"Wrote {pages} HTML pages, sitemap.xml, robots.txt → {OUTPUT}")


if __name__ == "__main__":
    build()
