# Mini-sites

Four static sites, each with its own hub, 20 tools, sitemap, and robots file. They do not add paths to the main `cron2systemd.dev` DevOps hub (`build_utilities.py` at the repo root).

| Directory | Canonical host | Flagship |
| --- | --- | --- |
| `sites/mint` | `https://mint.cron2systemd.dev` | `solana-mint-check` |
| `sites/safe` | `https://safe.cron2systemd.dev` | `safe-mech-decode` |
| `sites/x402` | `https://x402.cron2systemd.dev` | `x402-inspect` |
| `sites/bot` | `https://bot.cron2systemd.dev` | `discord-bot-offline` |

Shared chrome (dark terminal UI, AdSense client `ca-pub-7911637649628733`, Buy Me a Coffee tip jar, Open Graph, JSON-LD) lives in `sites/_shared`. Each site is stdlib Python 3 only.

## Build

From the repository root, or from the site directory:

```bash
python3 sites/mint/build.py
python3 sites/safe/build.py
python3 sites/x402/build.py
python3 sites/bot/build.py
```

Output is `sites/<name>/output/` (gitignored). Re-running deletes and rewrites that folder.

```bash
python3 -m http.server 8081 --directory sites/mint/output
python3 -m http.server 8082 --directory sites/safe/output
python3 -m http.server 8083 --directory sites/x402/output
python3 -m http.server 8084 --directory sites/bot/output
```

Tool URLs are `https://<host>/{slug}` with no trailing slash. The hub is `https://<host>/`.

## Cloudflare Pages

Use **four projects** (simplest) or **four production branches**. Each project binds one custom domain. Do not attach these domains to the main DevOps project.

### Four projects

Create one Pages project per site, all connected to this repo.

| Project | Root directory | Build command | Output directory | Custom domain |
| --- | --- | --- | --- | --- |
| mint | `sites/mint` | `python3 build.py` | `output` | `mint.cron2systemd.dev` |
| safe | `sites/safe` | `python3 build.py` | `output` | `safe.cron2systemd.dev` |
| x402 | `sites/x402` | `python3 build.py` | `output` | `x402.cron2systemd.dev` |
| bot | `sites/bot` | `python3 build.py` | `output` | `bot.cron2systemd.dev` |

Framework preset: None. Pages clones the full repo, then runs the build in the root directory, so `../_shared` is available.

DNS: add a CNAME for each hostname to that project (`mint` → mint project, and so on). In the project, **Custom domains** → set up `mint.cron2systemd.dev` (and the other three on their projects).

If a project cannot use a subdirectory as root, leave the root as the repo and set:

- Build command: `python3 sites/mint/build.py` (swap the folder)
- Output directory: `sites/mint/output`

### Four production branches

Alternatively, one Pages project per branch, each branch containing the same repo (or a branch whose build command is pinned to one site):

1. Branch `production-mint` → build `python3 sites/mint/build.py`, output `sites/mint/output`, domain `mint.cron2systemd.dev`.
2. Branch `production-safe` → `sites/safe`, domain `safe.cron2systemd.dev`.
3. Branch `production-x402` → `sites/x402`, domain `x402.cron2systemd.dev`.
4. Branch `production-bot` → `sites/bot`, domain `bot.cron2systemd.dev`.

Four projects on `main` is less branch bookkeeping. Both layouts publish the same `output/` tree.

The existing cron2systemd.dev project stays on the repo-root DevOps hub (`python3 build_utilities.py`, output `output`, or the root converter). Do not point `mint` / `safe` / `x402` / `bot` at that project.
