#!/usr/bin/env python3
"""Shared static-site generator for the cron2systemd mini-sites.

Stdlib only. Each site's build.py calls build_site().
"""

from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ADSENSE_CLIENT = "ca-pub-7911637649628733"
TIP_JAR = "https://buymeacoffee.com/1126"
SHARED = Path(__file__).resolve().parent
REPO = SHARED.parents[1]

SISTERS = [
    ("mint", "https://mint.cron2systemd.dev/"),
    ("safe", "https://safe.cron2systemd.dev/"),
    ("x402", "https://x402.cron2systemd.dev/"),
    ("bot", "https://bot.cron2systemd.dev/"),
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def tool_shell(fields: str, explain: str, button: str = "Run", presets: str = "") -> str:
    """Standard panel: inputs, Run button, verdict, key/value rows, notes."""
    return f"""
<section class="panel">
  {presets}
  <div class="form-grid two">
    {fields}
  </div>
  <div class="btn-row"><button type="button" class="btn primary" id="go">{esc(button)}</button></div>
  <p class="status" id="status" aria-live="polite"></p>
</section>
<section class="panel" id="result" hidden>
  <div class="output-head"><h2>Result</h2>
    <button type="button" class="copy-btn" data-copy="#out">Copy</button></div>
  <p class="verdict pending" id="verdict" aria-live="polite"></p>
  <dl class="kv" id="kv"></dl>
  <div id="extra"></div>
  <textarea id="out" class="output" readonly rows="8" style="margin-top:0.8rem"></textarea>
</section>
<section class="explain">
  {explain}
</section>
"""


def build_site(
    site_dir: Path,
    *,
    site_id: str,
    base_url: str,
    site_name: str,
    brand_small: str,
    hub_title: str,
    hub_description: str,
    hub_lede: str,
    group_order: list[str],
    tools: list[dict],
    pages: dict[str, str],
    scripts: dict[str, str],
) -> None:
    """Write sites/<id>/output.

    tools: slug, title, nav, description, group. First tool is the flagship.
    pages: slug -> inner HTML.
    scripts: filename -> JS source, written under assets/. Every tool page
    loads every script in insertion order after app.js (pass libs first).
    """
    missing = [t["slug"] for t in tools if t["slug"] not in pages]
    if missing:
        raise SystemExit("Missing HTML for: " + ", ".join(missing))
    if not scripts:
        raise SystemExit("Refusing to build with no JavaScript")
    for name, source in scripts.items():
        if len(source.strip()) < 80:
            raise SystemExit(f"Script {name} looks empty")

    output = site_dir / "output"
    if output.exists():
        shutil.rmtree(output)
    (output / "assets").mkdir(parents=True)

    favicon = REPO / "favicon.svg"
    shutil.copy2(favicon, output / "favicon.svg")
    shutil.copy2(favicon, output / "assets" / "favicon.svg")
    (output / "assets" / "site.css").write_text((SHARED / "site.css").read_text(encoding="utf-8"), encoding="utf-8")
    (output / "assets" / "app.js").write_text((SHARED / "app.js").read_text(encoding="utf-8"), encoding="utf-8")
    script_names = list(scripts)
    for name, source in scripts.items():
        text = source if source.endswith("\n") else source + "\n"
        (output / "assets" / name).write_text(text, encoding="utf-8")

    ctx = _Ctx(base_url, site_name, brand_small, site_id, tools, group_order)

    _write(
        output / "index.html",
        ctx.page(
            slug=None,
            title=hub_title,
            description=hub_description,
            body=ctx.hub(hub_lede),
            scripts=[],
        ),
    )
    for tool in tools:
        _write(
            output / tool["slug"] / "index.html",
            ctx.page(
                slug=tool["slug"],
                title=tool["title"],
                description=tool["description"],
                body=ctx.tool_wrap(tool, pages[tool["slug"]]),
                scripts=script_names,
            ),
        )

    lastmod = datetime.now(timezone.utc).date().isoformat()
    _write(output / "sitemap.xml", ctx.sitemap(lastmod))
    _write(output / "robots.txt", ctx.robots())
    print(f"Wrote {1 + len(tools)} HTML pages → {output}")


class _Ctx:
    def __init__(self, base_url, site_name, brand_small, site_id, tools, group_order):
        self.base_url = base_url.rstrip("/")
        self.site_name = site_name
        self.brand_small = brand_small
        self.site_id = site_id
        self.tools = tools
        self.group_order = group_order

    def canonical(self, slug: str | None) -> str:
        if not slug:
            return self.base_url + "/"
        return f"{self.base_url}/{slug}"

    def href(self, slug: str | None, current: str | None) -> str:
        depth = 0 if current is None else 1
        prefix = "../" if depth else ""
        if slug is None:
            return prefix if depth else "./"
        return f"{prefix}{slug}/"

    def sidebar(self, current: str | None) -> str:
        groups: dict[str, list[dict]] = {}
        for tool in self.tools:
            groups.setdefault(tool["group"], []).append(tool)
        parts = [
            "<h2>Flagship</h2>",
            self._link(self.tools[0]["slug"], current, self.tools[0]["nav"]),
            self._link(None, current, "All tools"),
        ]
        for name in self.group_order:
            items = groups.get(name) or []
            if not items:
                continue
            parts.append(f"<h2>{esc(name)}</h2>")
            for tool in items:
                parts.append(self._link(tool["slug"], current, tool["nav"]))
        return "\n".join(parts)

    def _link(self, slug: str | None, current: str | None, label: str) -> str:
        cur = ' aria-current="page"' if slug == current or (slug is None and current is None) else ""
        return f'<a href="{self.href(slug, current)}"{cur}>{esc(label)}</a>'

    def json_ld(self, name: str, url: str, description: str) -> str:
        payload = {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": name,
            "url": url,
            "description": description,
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "Any",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "publisher": {"@type": "Organization", "name": self.site_name},
        }
        return json.dumps(payload, indent=2)

    def sisters(self) -> str:
        links = []
        for sid, url in SISTERS:
            label = sid + ".cron2systemd.dev"
            if sid == self.site_id:
                links.append(f"<strong>{esc(label)}</strong>")
            else:
                links.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        return " · ".join(links)

    def page(self, *, slug, title, description, body, scripts) -> str:
        canonical = self.canonical(slug)
        depth = 0 if slug is None else 1
        asset = "../assets" if depth else "assets"
        tags = [f'<script src="{asset}/app.js"></script>']
        for name in scripts:
            tags.append(f'<script src="{asset}/{name}"></script>')
        og_title = title if self.site_name.lower() in title.lower() else f"{title} — {self.site_name}"
        data_tool = f' data-tool="{esc(slug)}"' if slug else ""
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
  <meta property="og:site_name" content="{esc(self.site_name)}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(og_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}"
     crossorigin="anonymous"></script>
  <link rel="icon" href="{asset}/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{asset}/site.css">
  <script type="application/ld+json">
{self.json_ld(title, canonical, description)}
  </script>
</head>
<body{data_tool}>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{self.href(None, slug)}">{esc(self.site_name)} <small>{esc(self.brand_small)}</small></a>
      <div class="header-actions">
        <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="sidebar">Menu</button>
        <button type="button" class="theme-toggle" id="theme-toggle">Theme</button>
      </div>
    </div>
  </header>
  <div class="layout">
    <nav class="sidebar" id="sidebar" aria-label="All tools">
      {self.sidebar(slug)}
    </nav>
    <div class="main-panel">
      <main id="main">
        {body}
        <div class="ad-slot" aria-hidden="true">Advertisement placeholder</div>
        <aside class="tip-jar" aria-label="Support this tool">
          <div class="tip-copy">
            <p class="tip-kicker">Support this tool</p>
            <p>If this check saved you a bad signature, you can buy me a coffee.</p>
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
      Static pages on <a href="{esc(self.base_url + '/')}">{esc(self.site_name)}</a>.
      No accounts. RPC and URL checks run in your browser only when you ask.
      · <a href="{TIP_JAR}" target="_blank" rel="noopener noreferrer">Buy me a coffee</a>
    </p>
    <p class="sister-sites">Mini-sites: {self.sisters()}</p>
  </footer>
  {''.join(tags)}
</body>
</html>
"""

    def hub(self, lede: str) -> str:
        cards = []
        for index, tool in enumerate(self.tools):
            klass = "tool-card flagship" if index == 0 else "tool-card"
            kicker = "Flagship" if index == 0 else tool["group"]
            cards.append(
                f"""<a class="{klass}" href="{tool['slug']}/">
        <span class="kicker">{esc(kicker)}</span>
        <h2>{esc(tool['title'])}</h2>
        <p>{esc(tool['description'])}</p>
      </a>"""
            )
        return f"""
      <section class="hero">
        <p class="crumb">{esc(self.base_url.replace('https://', ''))}</p>
        <h1>{esc(self.tools[0]['title'].split('—')[0].strip())} and related checks</h1>
        <p class="lede">{lede}</p>
      </section>
      <section class="tool-grid" aria-label="All tools">
        {''.join(cards)}
      </section>
    """

    def tool_wrap(self, tool: dict, inner: str) -> str:
        return f"""
      <header class="tool-head">
        <p class="crumb"><a href="../">All tools</a> / {esc(tool['group'])}</p>
        <h1>{esc(tool['title'])}</h1>
        <p class="lede">{esc(tool['description'])}</p>
      </header>
      {inner}
    """

    def sitemap(self, lastmod: str) -> str:
        urls = [self.canonical(None)] + [self.canonical(t["slug"]) for t in self.tools]
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

    def robots(self) -> str:
        return f"User-agent: *\nAllow: /\n\nSitemap: {self.base_url}/sitemap.xml\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
