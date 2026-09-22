# Systemd Timer to Cron Converter

A static, browser-only tool that converts **5-field cron** expressions and systemd timer **`OnCalendar=`** calendar events both ways.

Most cron explainers (Crontab Guru and similar) only paraphrase crontab. This page also understands systemd’s calendar syntax (`*-*-* 04:00:00`, `Mon *-*-* 09:00:00`, shortcuts like `hourly` / `weekly`) and **refuses incorrect 1:1 mappings** when the two languages disagree.

Live conversion, clickable presets, plain-English explanations, copy buttons, and validation — no backend and no build step.

## Open locally

Any of these:

```bash
# just open the file
open index.html          # macOS
xdg-open index.html      # Linux
start index.html         # Windows
```

Or serve the folder (useful if a browser restricts `file://` clipboard):

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

Files: `index.html`, `styles.css`, `app.js`, `converter.js`.

Conversion unit tests (Node, no extra packages):

```bash
node tests.js
```

## Utilities hub (`output/`)

`build_utilities.py` is a zero-dependency Python 3 generator (stdlib only). It writes a second static site into `output/` — a hub plus 24 client-side tools — **without modifying** the flagship converter files at the repo root.

```bash
python3 build_utilities.py
python3 -m http.server 8080 --directory output
# then visit http://localhost:8080
```

Each tool lives at `output/{slug}/index.html` (clean URL `/{slug}`). Canonical URLs are `https://cron2systemd.dev/{slug}` with no trailing slash. The hub is `output/index.html` → `https://cron2systemd.dev/`.

The original OnCalendar ↔ crontab converter is copied to `output/oncalendar-cron-converter/` so you can point a host at `output/` without dropping the flagship tool. See `OUTPUT.md` for the file map.

Shared assets (`output/assets/site.css`, `output/assets/app.js`, per-tool JS) load from this repo only: no npm, no CDNs, no Google Fonts (system stacks: Inter / JetBrains Mono).

## Deploy

Two artifact roots exist on purpose:

| What you want live at `/` | Artifact | Notes |
| --- | --- | --- |
| Flagship OnCalendar ↔ crontab converter only | repository root (`.`) | Current layout; no build step |
| Utilities hub + 24 tools + copied converter | `output/` | Run the generator first (or as the Pages build command) |

### Cloudflare Pages — converter only (repo root)

1. Push this repo to GitHub/GitLab.
2. In Cloudflare Pages → **Create a project** → connect the repo.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (or `.`)
4. Deploy. Every push to the production branch republishes.

### Cloudflare Pages — utilities hub (`output/`)

1. Connect the same repo.
2. Build settings:
   - **Framework preset:** None
   - **Build command:** `python3 build_utilities.py`
   - **Build output directory:** `output`
3. Deploy. `/` becomes the hub; `/oncalendar-cron-converter` is the original dual converter; each utility is `/{slug}`.

Alternatively run `python3 build_utilities.py` locally and either upload the `output/` folder or copy its contents to your static host. Do not copy `output/` over the repo root unless you intend to replace `index.html` with the hub.

### Vercel

**Converter only:** Framework Preset Other, empty build command, output directory `.`

**Utilities hub:** Build Command `python3 build_utilities.py`, Output Directory `output`.

You can also drag-and-drop the folder onto [Cloudflare Pages](https://pages.cloudflare.com/) or [Vercel](https://vercel.com/) without git.

## What converts (and what does not)

Follows [systemd.time(7)](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html) and [crontab(5)](https://man7.org/linux/man-pages/man5/crontab.5.html) (Vixie/cronie).

| Cron | OnCalendar |
| --- | --- |
| `0 4 * * *` | `*-*-* 04:00:00` |
| `0 9 * * 1` | `Mon *-*-* 09:00:00` |
| `*/15 * * * *` | `*-*-* *:00/15:00` |
| `0 * * * *` / `@hourly` | `hourly` → `*-*-* *:00:00` |
| `0 0 1 * *` | `*-*-01 00:00:00` / `monthly` |
| `0 0 * * 1` | systemd `weekly` (Monday) |
| `0 0 * * 0` / `@weekly` | `Sun *-*-* 00:00:00` (Sunday — **not** systemd `weekly`) |

Supported field syntax: `*`, numbers, lists (`1,2,3`), ranges (`1-5` vs systemd `1..5`), steps (`*/15`, `1-10/2`, systemd `00/15`), cron month/dow names, systemd weekday names and `Mon..Fri`, systemd shorthands `minutely` `hourly` `daily` `weekly` `monthly` `yearly`/`annually` `quarterly` `semiannually`.

**Intentionally not 1:1**

- Cron **ORs** day-of-month and day-of-week when both are restricted; a single OnCalendar **ANDs** them. The tool emits **two** `OnCalendar=` lines for the cron OR case, and refuses a fake 5-field cron for systemd AND cases such as “first Saturday” (`Sat *-*-01..07`).
- Non-zero **seconds**, **year** filters, and last-day `~` have no standard 5-field cron form.
- `@reboot` is not a calendar event (`OnBootSec=` instead).
- Timezones are noted (`CRON_TZ=`) rather than stuffed into the five fields.

Exotic Quartz fields (`L`, `W`, `#`), 6-field seconds/year crons, and monotonic systemd timers are documented as unsupported rather than guessed.

## License

Use and modify freely.
