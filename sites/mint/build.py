#!/usr/bin/env python3
"""Build the mint.cron2systemd.dev mini-site into ./output."""

from __future__ import annotations

import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE.parent / "_shared"))
sys.path.insert(0, str(SITE))

from catalog import GROUP_ORDER, PAGES, TOOLS  # noqa: E402
from sitegen import build_site  # noqa: E402


def main() -> None:
    build_site(
        SITE,
        site_id="mint",
        base_url="https://mint.cron2systemd.dev",
        site_name="mint.cron2systemd",
        brand_small="token security",
        hub_title="Solana token security checks",
        hub_description=(
            "Browser-side Solana mint, freeze, LP, holder, and metadata checks. "
            "No account. RPC calls stay in your browser."
        ),
        hub_lede=(
            "Twenty client-side checks for Solana mints: authorities, Token-2022 fees, "
            "LP burn heuristics, holder concentration, pump.fun graduation, and a security checklist. "
            "The flagship reads mintAuthority and freezeAuthority from a public JSON-RPC."
        ),
        group_order=GROUP_ORDER,
        tools=TOOLS,
        pages=PAGES,
        scripts={
            "solana.js": (SITE / "js" / "solana.js").read_text(encoding="utf-8"),
            "tools.js": (SITE / "js" / "tools.js").read_text(encoding="utf-8"),
        },
    )


if __name__ == "__main__":
    main()
