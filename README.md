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

## Deploy

This is a plain static site. Point a static host at the repository root (or upload these files). There is no `npm run build`.

### Cloudflare Pages

1. Push this repo to GitHub/GitLab.
2. In Cloudflare Pages → **Create a project** → connect the repo.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (or `.`)
4. Deploy. Every push to the production branch republishes.

### Vercel

1. Import the repo in Vercel.
2. **Framework Preset:** Other
3. **Build Command:** leave empty
4. **Output Directory:** `.`
5. Deploy.

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
