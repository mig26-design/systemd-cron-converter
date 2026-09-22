"""Mint mini-site copy. Flagship is first, in the required slug order."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
from sitegen import tool_shell  # noqa: E402

GROUP_ORDER = ["Mint", "Liquidity", "Holders", "Metadata", "Summary"]

RPC = """<label class="field span-2">Solana JSON-RPC
      <input id="rpc" spellcheck="false" value="https://solana-rpc.publicnode.com" autocomplete="off"></label>"""

MINT = """<label class="field span-2">Mint address
      <input id="mint" spellcheck="false" placeholder="base58 mint" autocomplete="off"></label>"""

ADDR = """<label class="field span-2">Account address
      <input id="mint" spellcheck="false" placeholder="base58 account" autocomplete="off"></label>"""


def _page(fields: str, explain: str, button: str, presets: str = "") -> str:
    return tool_shell(fields, explain, button=button, presets=presets)


TOOLS = [
    {
        "slug": "solana-mint-check",
        "title": "Solana mint authority check",
        "nav": "Mint authorities",
        "description": "Paste a Solana mint and see whether mintAuthority and freezeAuthority are both revoked.",
        "group": "Mint",
    },
    {
        "slug": "freeze-authority-check",
        "title": "Freeze authority check",
        "nav": "Freeze authority",
        "description": "Check whether a mint can still freeze holder accounts, including Token-2022 default account state.",
        "group": "Mint",
    },
    {
        "slug": "lp-burn-or-lock",
        "title": "LP burn or lock check",
        "nav": "LP burn check",
        "description": "See whether LP token supply sits at a known burn address. Unlisted holders are not treated as locks.",
        "group": "Liquidity",
    },
    {
        "slug": "token-2022-fee-check",
        "title": "Token-2022 fee check",
        "nav": "Token-2022 fee",
        "description": "Read a Token-2022 transferFeeConfig and show the fee in basis points.",
        "group": "Mint",
    },
    {
        "slug": "top10-holder-concentration",
        "title": "Top holder concentration",
        "nav": "Top holders",
        "description": "Sum the largest token accounts against total supply and flag concentrated holdings.",
        "group": "Holders",
    },
    {
        "slug": "deployer-wallet-holdings",
        "title": "Deployer wallet holdings",
        "nav": "Wallet holdings",
        "description": "Show how much of a mint a wallet still holds, as a share of supply.",
        "group": "Holders",
    },
    {
        "slug": "honeypot-transfer-sim",
        "title": "Honeypot transfer signals",
        "nav": "Honeypot signals",
        "description": "Flag freeze, delegate, and transfer-fee controls, and optionally ask Jupiter for a sell quote.",
        "group": "Holders",
    },
    {
        "slug": "pump-fun-graduated-check",
        "title": "pump.fun graduated check",
        "nav": "pump.fun curve",
        "description": "Derive the pump.fun bonding curve and read whether its complete flag is set.",
        "group": "Liquidity",
    },
    {
        "slug": "raydium-pool-ownership",
        "title": "Raydium pool ownership",
        "nav": "Raydium owner",
        "description": "Check whether an account is owned by a known Raydium AMM, CPMM, or CLMM program.",
        "group": "Liquidity",
    },
    {
        "slug": "meteora-lp-status",
        "title": "Meteora LP status",
        "nav": "Meteora owner",
        "description": "Check whether an account is owned by a known Meteora DLMM or DAMM program.",
        "group": "Liquidity",
    },
    {
        "slug": "mint-revoke-history",
        "title": "Mint revoke history",
        "nav": "Revoke history",
        "description": "Scan recent transactions for setAuthority instructions and show the mint’s current authorities.",
        "group": "Mint",
    },
    {
        "slug": "freeze-enable-risk",
        "title": "Freeze enable risk",
        "nav": "Freeze risk",
        "description": "Score freeze authority, default frozen state, permanent delegate, and transfer fees.",
        "group": "Mint",
    },
    {
        "slug": "bundled-snipe-flag",
        "title": "Bundled snipe flag",
        "nav": "Same-slot spike",
        "description": "Flag a mint whose recent signatures cluster in a single slot. A heuristic, not proof of a bundle.",
        "group": "Holders",
    },
    {
        "slug": "update-authority-check",
        "title": "Update authority check",
        "nav": "Update authority",
        "description": "Read Metaplex metadata and show whether the update authority is revoked.",
        "group": "Metadata",
    },
    {
        "slug": "metadata-mutable-check",
        "title": "Metadata mutable check",
        "nav": "Metadata mutable",
        "description": "Read the Metaplex isMutable flag so you can see whether name, symbol, or URI can still change.",
        "group": "Metadata",
    },
    {
        "slug": "tax-bps-decoder",
        "title": "Tax basis-points decoder",
        "nav": "Tax bps",
        "description": "Turn basis points into a fee and a net amount. Uses the mint’s transfer fee when the mint has one.",
        "group": "Mint",
    },
    {
        "slug": "ca-vs-ticker-lookup",
        "title": "CA versus ticker",
        "nav": "CA vs ticker",
        "description": "Show the mint address next to the on-chain symbol. A ticker is not the contract.",
        "group": "Metadata",
    },
    {
        "slug": "rugcheck-summary-card",
        "title": "Security summary card",
        "nav": "Summary card",
        "description": "One card for authorities, metadata mutability, holder concentration, and transfer fee. Not a third-party score.",
        "group": "Summary",
    },
    {
        "slug": "jupiter-organic-score",
        "title": "Jupiter organic score",
        "nav": "Organic score",
        "description": "Read Jupiter’s organicScore for a mint, or paste the JSON if the browser cannot fetch it.",
        "group": "Metadata",
    },
    {
        "slug": "sol-token-security-checklist",
        "title": "Solana token security checklist",
        "nav": "Security checklist",
        "description": "Walk mint, freeze, metadata, LP, holders, fees, and contract-address checks before you buy.",
        "group": "Summary",
    },
]

_PRESETS = """<div class="preset-row">
    <button type="button" class="preset" data-mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v">USDC mint</button>
    <button type="button" class="preset" data-mint="So11111111111111111111111111111111111111112">Wrapped SOL</button>
  </div>"""

PAGES = {
    "solana-mint-check": _page(
        RPC + MINT,
        "<h2>What PASS means</h2><p>PASS only when parsed <code>mintAuthority</code> and <code>freezeAuthority</code> are both JSON <code>null</code>. The call is <code>getAccountInfo</code> with <code>jsonParsed</code>. <code>https://api.mainnet-beta.solana.com</code> often returns HTTP 403 to browsers, so the box defaults to a CORS-friendly public RPC. Token-2022 extensions are not part of this verdict.</p>",
        "Check authorities",
        _PRESETS,
    ),
    "freeze-authority-check": _page(
        RPC + MINT,
        "<h2>Scope</h2><p>PASS means <code>freezeAuthority</code> is null and there is no Token-2022 default frozen account state. A mint authority can still exist.</p>",
        "Check freeze",
    ),
    "lp-burn-or-lock": _page(
        RPC + MINT.replace("Mint address", "LP mint"),
        "<h2>Burn versus lock</h2><p>Known burn addresses are the incinerator and the system program. A burned verdict requires at least 95% of supply there. Other programs are shown as unlisted, not as locks.</p>",
        "Check LP mint",
    ),
    "token-2022-fee-check": _page(
        RPC + MINT,
        "<h2>Fee source</h2><p>Reads <code>transferFeeConfig.newerTransferFee.transferFeeBasisPoints</code> from parsed mint JSON. Classic SPL Token mints do not have this extension.</p>",
        "Read fee",
    ),
    "top10-holder-concentration": _page(
        RPC + MINT,
        "<h2>What is counted</h2><p>Uses <code>getTokenLargestAccounts</code> and <code>getTokenSupply</code>. The rows are token accounts, not necessarily wallets. A 50% share is flagged. Exchanges and AMMs can look concentrated.</p>",
        "Measure holders",
    ),
    "deployer-wallet-holdings": _page(
        RPC + MINT + """<label class="field span-2">Wallet
      <input id="wallet" spellcheck="false" placeholder="deployer or holder pubkey" autocomplete="off"></label>""",
        "<h2>Share of supply</h2><p><code>getTokenAccountsByOwner</code> filtered by mint, divided by <code>getTokenSupply</code>. This does not prove the wallet deployed the mint.</p>",
        "Check wallet",
    ),
    "honeypot-transfer-sim": _page(
        RPC + MINT + """<label class="field">Quote amount (base units)
      <input id="amount" value="1000000" spellcheck="false"></label>""",
        "<h2>What is simulated</h2><p>High flags are freeze authority, nonTransferable, permanentDelegate, and a transfer fee of at least 1000 bps. A Jupiter lite quote is attempted and may fail CORS. Neither result is a signed sell.</p>",
        "Check signals",
    ),
    "pump-fun-graduated-check": _page(
        RPC + MINT,
        "<h2>Layout</h2><p>Searches the first bonding-curve PDA bumps for program <code>6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P</code> and reads the <code>complete</code> byte after the discriminator and five <code>u64</code>s. Pump can change that layout.</p>",
        "Check curve",
    ),
    "raydium-pool-ownership": _page(
        RPC + ADDR,
        "<h2>Programs</h2><p>Matches the account owner to Raydium AMM v4, CPMM, or CLMM. It does not decode pool reserves or LP lock status.</p>",
        "Check owner",
    ),
    "meteora-lp-status": _page(
        RPC + ADDR,
        "<h2>Programs</h2><p>Matches Meteora DLMM, Dynamic AMM, and DAMM v2 owners. Bin liquidity and lock status are out of scope.</p>",
        "Check owner",
    ),
    "mint-revoke-history": _page(
        RPC + MINT,
        "<h2>Sample window</h2><p>Fetches up to 12 signatures and parses 6 transactions for <code>setAuthority</code>. Current authorities are always shown. Older revokes can sit outside this window.</p>",
        "Scan recent txs",
    ),
    "freeze-enable-risk": _page(
        RPC + MINT,
        "<h2>Score</h2><p>Points add up for a live freeze authority, a frozen default account state, a permanent delegate, a non-transferable extension, and a transfer fee. HIGH starts at 40.</p>",
        "Score freeze risk",
    ),
    "bundled-snipe-flag": _page(
        RPC + MINT,
        "<h2>Heuristic</h2><p>Groups the newest signatures by slot. Four or more in one slot is a spike. This is not proof of a Jito bundle, and old mints will not show their creation slot here.</p>",
        "Check slots",
    ),
    "update-authority-check": _page(
        RPC + MINT,
        "<h2>Revoked</h2><p>Metaplex treats the system program (<code>11111111111111111111111111111111</code>) as a revoked update authority. The page searches the first metadata PDA bumps.</p>",
        "Read update authority",
    ),
    "metadata-mutable-check": _page(
        RPC + MINT,
        "<h2>Mutable</h2><p>FAIL when <code>isMutable</code> is true. Immutable metadata can still be a copy of another project’s name. Always compare the mint address.</p>",
        "Read mutable flag",
    ),
    "tax-bps-decoder": _page(
        RPC + """<label class="field span-2">Mint (optional, Token-2022)
      <input id="mint" spellcheck="false" placeholder="leave blank to use the bps field" autocomplete="off"></label>
    <label class="field">Basis points
      <input id="bps" value="100" spellcheck="false"></label>
    <label class="field">Amount in base units
      <input id="amount" value="1000000" spellcheck="false"></label>""",
        "<h2>Math</h2><p>Fee = amount × bps / 10000, integer division. 100 bps is 1%. If the mint has <code>transferFeeConfig</code>, that bps replaces the manual field.</p>",
        "Decode fee",
    ),
    "ca-vs-ticker-lookup": _page(
        RPC + MINT.replace("base58 mint", "mint address, not a ticker"),
        "<h2>Why this exists</h2><p>Symbols collide. This page refuses a non-address and, for a real mint, prints the on-chain symbol beside the full contract address.</p>",
        "Compare",
    ),
    "rugcheck-summary-card": _page(
        RPC + MINT,
        "<h2>Not a hosted score</h2><p>The card combines authorities, a metadata read, top-holder share, and transfer fee from the RPC you choose. It does not call RugCheck or any other scorer.</p>",
        "Build card",
    ),
    "jupiter-organic-score": _page(
        RPC + MINT + """<label class="field span-2">Or paste Jupiter JSON
      <textarea id="paste" rows="6" spellcheck="false" placeholder='[{"id":"…","symbol":"…","organicScore":0}]'></textarea></label>""",
        "<h2>Source</h2><p>Fetches <code>lite-api.jup.ag/tokens/v2/search</code> when the paste box is empty. If CORS blocks it, paste the JSON. The score is displayed, not recomputed.</p>",
        "Read score",
    ),
    "sol-token-security-checklist": """
<section class="panel">
  <div class="form-grid two">
    """ + RPC + MINT + """
  </div>
  <div class="btn-row"><button type="button" class="btn primary" id="go">Read mint signals</button></div>
  <p class="status" id="status" aria-live="polite"></p>
  <p id="hints" class="lede"></p>
  <ul class="checklist">
    <li><label><input type="checkbox" id="chk-mint"> Mint authority revoked</label><p>You confirmed mintAuthority is null, or you accept that more supply can be minted.</p></li>
    <li><label><input type="checkbox" id="chk-freeze"> Freeze authority revoked</label><p>freezeAuthority is null and you are not relying on a frozen default account state.</p></li>
    <li><label><input type="checkbox" id="chk-meta"> Metadata immutable and update authority revoked</label><p>Name, symbol, and URI cannot be swapped out from under you.</p></li>
    <li><label><input type="checkbox" id="chk-lp"> LP burn or lock understood</label><p>You checked where the LP mint supply sits, and you are not treating an unlisted wallet as a lock.</p></li>
    <li><label><input type="checkbox" id="chk-holders"> Holder concentration reviewed</label><p>You looked at the largest accounts and know if one wallet can dump.</p></li>
    <li><label><input type="checkbox" id="chk-fee"> Transfer fee acceptable</label><p>Token-2022 fee, if any, is a number you actually accept.</p></li>
    <li><label><input type="checkbox" id="chk-ca"> Contract address matched, not just the ticker</label><p>The mint you are buying is the mint you read here.</p></li>
  </ul>
  <p class="verdict pending" id="summary" style="margin-top:0.9rem"></p>
</section>
<section class="explain">
  <h2>Local checklist</h2>
  <p>Ticks stay in this tab. “Read mint signals” fills the hint line from the mint account and does not tick boxes for you.</p>
</section>
""",
}
