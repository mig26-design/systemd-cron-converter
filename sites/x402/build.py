#!/usr/bin/env python3
"""Build the x402.cron2systemd.dev mini-site into ./output."""

from __future__ import annotations

import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
SHARED = SITE.parent / "_shared"
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(SITE))

from catalog import GROUP_ORDER, PAGES, TOOLS  # noqa: E402
from sitegen import build_site  # noqa: E402


def main() -> None:
    build_site(
        SITE,
        site_id="x402",
        base_url="https://x402.cron2systemd.dev",
        site_name="x402.cron2systemd",
        brand_small="402 payments",
        hub_title="x402 and HTTP 402 inspectors",
        hub_description="Browser-side parsers for HTTP 402 and x402 payment challenges.",
        hub_lede=(
            "Twenty client-side tools for payment-required headers, payTo, network, "
            "USDC amounts, and client checklists. The flagship parses a pasted 402 "
            "and can try a CORS fetch. Nothing on this site sends a payment."
        ),
        group_order=GROUP_ORDER,
        tools=TOOLS,
        pages=PAGES,
        scripts={
            "keccak.js": (SHARED / "keccak.js").read_text(encoding="utf-8"),
            "ui.js": (SHARED / "ui.js").read_text(encoding="utf-8"),
            "x402.js": (SITE / "js" / "x402.js").read_text(encoding="utf-8"),
            "tools.js": (SITE / "js" / "tools.js").read_text(encoding="utf-8"),
        },
    )


if __name__ == "__main__":
    main()
