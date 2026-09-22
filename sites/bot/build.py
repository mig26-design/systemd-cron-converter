#!/usr/bin/env python3
"""Build the bot.cron2systemd.dev mini-site into ./output."""

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
        site_id="bot",
        base_url="https://bot.cron2systemd.dev",
        site_name="bot.cron2systemd",
        brand_small="discord bot ops",
        hub_title="Discord bot operations checks",
        hub_description="Browser-side Discord bot invite, intent, permission, and error-code tools. No Discord API.",
        hub_lede=(
            "Twenty client-side tools for Discord bot invites, privileged intents, "
            "permission bits, and common API errors. The flagship builds an invite URL "
            "and walks the usual reasons a bot looks offline. Nothing calls Discord."
        ),
        group_order=GROUP_ORDER,
        tools=TOOLS,
        pages=PAGES,
        scripts={
            "ui.js": (SHARED / "ui.js").read_text(encoding="utf-8"),
            "discord.js": (SITE / "js" / "discord.js").read_text(encoding="utf-8"),
            "tools.js": (SITE / "js" / "tools.js").read_text(encoding="utf-8"),
        },
    )


if __name__ == "__main__":
    main()
