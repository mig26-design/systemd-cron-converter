#!/usr/bin/env python3
"""Build the safe.cron2systemd.dev mini-site into ./output."""

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
        site_id="safe",
        base_url="https://safe.cron2systemd.dev",
        site_name="safe.cron2systemd",
        brand_small="safe decoding",
        hub_title="Safe and transaction decoders",
        hub_description="Browser-side Gnosis Safe and calldata decoders. RPC calls stay in your browser.",
        hub_lede=(
            "Twenty client-side tools for Safe execTransaction, owners, nonce, modules, "
            "guards, token transfers, and event logs. The flagship separates a mech’s "
            "outer transaction from the inner call the Safe actually makes."
        ),
        group_order=GROUP_ORDER,
        tools=TOOLS,
        pages=PAGES,
        scripts={
            "keccak.js": (SHARED / "keccak.js").read_text(encoding="utf-8"),
            "ui.js": (SHARED / "ui.js").read_text(encoding="utf-8"),
            "evm.js": (SITE / "js" / "evm.js").read_text(encoding="utf-8"),
            "tools.js": (SITE / "js" / "tools.js").read_text(encoding="utf-8"),
        },
    )


if __name__ == "__main__":
    main()
