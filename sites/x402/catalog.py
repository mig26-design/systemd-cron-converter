"""x402 mini-site copy. Flagship first, required slug order."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
from sitegen import tool_shell  # noqa: E402

GROUP_ORDER = ["Parse", "Price", "Probe", "Checklist"]

RAW = """<label class="field span-2">Raw response, headers, or JSON
      <textarea id="raw" rows="10" spellcheck="false" placeholder="HTTP/1.1 402 Payment Required"></textarea></label>"""

SAMPLE = """<div class="preset-row"><button type="button" class="preset" id="sample">Load sample 402</button></div>"""


def page(fields, explain, button="Parse", presets=""):
    return tool_shell(fields, explain, button=button, presets=presets)


TOOLS = [
    {"slug": "x402-inspect", "title": "x402 payment inspector", "nav": "Inspect 402", "group": "Parse",
     "description": "Parse an HTTP 402 or x402 challenge for network, payTo, asset, and amount. Fetch is best-effort because of CORS."},
    {"slug": "payment-required-header-decode", "title": "payment-required header", "nav": "Header decode", "group": "Parse",
     "description": "Decode a payment-required header from raw JSON or base64 JSON."},
    {"slug": "payto-address-extract", "title": "payTo address extract", "nav": "payTo extract", "group": "Parse",
     "description": "List every payTo value and checksum 20-byte hex addresses."},
    {"slug": "x402-network-id-check", "title": "x402 network check", "nav": "Network id", "group": "Parse",
     "description": "Check a requirement network against a local list of chain ids and known USDC addresses."},
    {"slug": "usdc-atomic-amount-decode", "title": "Atomic USDC amount", "nav": "Atomic amount", "group": "Price",
     "description": "Turn an atomic token amount into a human amount. USDC uses 6 decimals."},
    {"slug": "accept-payment-challenge-parse", "title": "Accept challenge parse", "nav": "Accepts array", "group": "Parse",
     "description": "List payment requirements from an accepts array or payment headers."},
    {"slug": "x402-resource-price-table", "title": "Resource price table", "nav": "Price table", "group": "Price",
     "description": "Table resource, network, and amount from one or more requirements."},
    {"slug": "base-usdc-payto-verify", "title": "Base USDC payTo verify", "nav": "USDC payTo", "group": "Price",
     "description": "Check that payTo is an address and the asset matches known USDC for that network."},
    {"slug": "x402-facilitator-hint", "title": "Facilitator hint", "nav": "Facilitator", "group": "Parse",
     "description": "Show extra facilitator-like fields from a challenge. Does not call a facilitator."},
    {"slug": "max-timeout-seconds-check", "title": "maxTimeoutSeconds check", "nav": "Timeout", "group": "Parse",
     "description": "Flag a payment timeout under 5 seconds or over an hour."},
    {"slug": "mime-type-payment-match", "title": "MIME type match", "nav": "MIME match", "group": "Parse",
     "description": "Compare the requirement mimeType with the type you expect to receive after paying."},
    {"slug": "x402-vs-402-plain", "title": "x402 versus plain 402", "nav": "x402 vs plain", "group": "Parse",
     "description": "Tell an x402 challenge apart from a plain HTTP 402 that has no payment fields."},
    {"slug": "walletforge-endpoint-probe", "title": "Paywall endpoint probe", "nav": "Endpoint probe", "group": "Probe",
     "description": "GET a URL and report whether the browser can see an HTTP 402 challenge."},
    {"slug": "paid-200-vs-402-diff", "title": "Paid 200 versus 402", "nav": "200 vs 402", "group": "Probe",
     "description": "Compare an unpaid challenge paste with a paid response paste."},
    {"slug": "x402-scheme-up-eip3009", "title": "exact scheme / EIP-3009", "nav": "exact scheme", "group": "Parse",
     "description": "Check for scheme exact and the extra name/version used with EIP-3009 USDC."},
    {"slug": "paywall-header-pretty", "title": "Paywall header pretty print", "nav": "Pretty headers", "group": "Parse",
     "description": "Pretty-print response headers from a pasted HTTP message."},
    {"slug": "multi-resource-price-compare", "title": "Compare resource prices", "nav": "Compare prices", "group": "Price",
     "description": "Compare amounts across several pasted challenges, separated by blank lines."},
    {"slug": "x402-llms-txt-finder", "title": "llms.txt payment finder", "nav": "llms.txt", "group": "Probe",
     "description": "Highlight llms.txt lines that mention 402, x402, or payment. Fetch when CORS allows."},
    {"slug": "settlement-network-mismatch", "title": "Settlement network mismatch", "nav": "Network mismatch", "group": "Price",
     "description": "Flag a requirement whose network is not the network you expect to settle on."},
    {"slug": "x402-client-checklist", "title": "x402 client checklist", "nav": "Client checklist", "group": "Checklist",
     "description": "A local checklist for building a client that can read a 402 and retry after paying."},
]

PAGES = {
    "x402-inspect": page(
        """<label class="field span-2">URL to try (optional)
      <input id="url" spellcheck="false" placeholder="https://example.com/resource" autocomplete="off"></label>
    <div class="span-2"><button type="button" class="btn" id="fetch">Try fetch</button></div>""" + RAW,
        "<h2>CORS</h2><p>Browsers often cannot read a cross-origin 402 unless the server sends <code>Access-Control-Allow-Origin</code> and exposes payment headers. Paste <code>curl -D -</code> output when fetch fails. This page does not pay anyone.</p>",
        "Parse pasted response", SAMPLE),
    "payment-required-header-decode": page(RAW, "<h2>Header</h2><p>Looks for <code>payment-required</code>, <code>x-payment-required</code>, or <code>x-payment</code>. Values may be JSON or base64 JSON.</p>", "Decode header", SAMPLE),
    "payto-address-extract": page(RAW, "<h2>payTo</h2><p>Every payTo is listed. 20-byte hex addresses are EIP-55 checksummed. Other strings are shown raw.</p>", "Extract payTo"),
    "x402-network-id-check": page(RAW, "<h2>Local list</h2><p>Known names include base, base-sepolia, ethereum, polygon, avalanche, and solana. An unknown name is a fail, not a claim that the network is fake.</p>", "Check network"),
    "usdc-atomic-amount-decode": page(RAW + """<label class="field">Atomic amount override
      <input id="amount" spellcheck="false" placeholder="uses the paste when empty"></label>
    <label class="field">Decimals
      <input id="decimals" value="6" spellcheck="false"></label>""",
        "<h2>Decimals</h2><p>Default 6 matches USDC. The page does not prove the asset is USDC.</p>", "Decode amount"),
    "accept-payment-challenge-parse": page(RAW, "<h2>accepts</h2><p>Walks JSON objects and headers for network, payTo, asset, and amount, including nested <code>accepts</code> entries.</p>", "Parse accepts", SAMPLE),
    "x402-resource-price-table": page(RAW, "<h2>Table</h2><p>One row per requirement. The human column assumes 6 decimals.</p>", "Build table"),
    "base-usdc-payto-verify": page(RAW, "<h2>Match</h2><p>PASS when payTo is 20-byte hex and the asset equals the known USDC address for that network. Base mainnet and Base Sepolia are in the list, along with a few other USDC deployments.</p>", "Verify"),
    "x402-facilitator-hint": page(RAW, "<h2>Hint only</h2><p>Prints <code>extra</code> and notes if the JSON mentions a facilitator. No facilitator is contacted.</p>", "Read extra"),
    "max-timeout-seconds-check": page(RAW + """<label class="field">Seconds override
      <input id="seconds" spellcheck="false" placeholder="uses the paste when empty"></label>""",
        "<h2>Window</h2><p>Under 5 seconds or over 3600 seconds is a warning. Missing values fail.</p>", "Check timeout"),
    "mime-type-payment-match": page(RAW + """<label class="field">Expected MIME
      <input id="mime" value="application/json" spellcheck="false"></label>""",
        "<h2>After payment</h2><p>Compares the challenge <code>mimeType</code> with what you expect the paid response to be.</p>", "Compare MIME"),
    "x402-vs-402-plain": page(RAW, "<h2>Classification</h2><p>x402-style means HTTP 402 plus network, payTo, or asset. A 402 without those fields is a plain 402.</p>", "Classify", SAMPLE),
    "walletforge-endpoint-probe": page("""<label class="field span-2">Endpoint URL
      <input id="url" spellcheck="false" placeholder="https://example.com/paid" autocomplete="off"></label>""",
        "<h2>Probe</h2><p>One CORS GET. Use this on a paywalled URL, including WalletForge-style endpoints you already have. If the browser cannot read the response, paste it into the inspector instead. Nothing is paid.</p>", "Probe"),
    "paid-200-vs-402-diff": page("""<label class="field span-2">Unpaid response
      <textarea id="unpaid" rows="8" spellcheck="false"></textarea></label>
    <label class="field span-2">Paid response
      <textarea id="paid" rows="8" spellcheck="false"></textarea></label>""",
        "<h2>Diff</h2><p>Compares status and how many payment requirements each paste still contains. The paid side should usually not still be a challenge.</p>", "Compare"),
    "x402-scheme-up-eip3009": page(RAW, "<h2>exact</h2><p>Looks for <code>scheme: exact</code> and <code>extra.name</code> / <code>extra.version</code>. It does not sign EIP-3009 authorization.</p>", "Check scheme"),
    "paywall-header-pretty": page(RAW, "<h2>Headers</h2><p>Status line plus <code>Name: value</code> lines. A blank line starts the body, which is not reprinted here.</p>", "Pretty print"),
    "multi-resource-price-compare": page(RAW, "<h2>Several pastes</h2><p>Split challenges with a blank line. Each requirement becomes a row tagged with which paste it came from.</p>", "Compare"),
    "x402-llms-txt-finder": page("""<label class="field span-2">Site URL (optional)
      <input id="url" spellcheck="false" placeholder="https://example.com" autocomplete="off"></label>""" + RAW.replace("Raw response, headers, or JSON", "Or paste llms.txt"),
        "<h2>llms.txt</h2><p>Fetches <code>/llms.txt</code> on the origin when the paste box is empty. CORS often blocks that. Matching lines mention 402, x402, payment, or payto.</p>", "Find lines"),
    "settlement-network-mismatch": page(RAW + """<label class="field">Expected network
      <input id="expected" value="base" spellcheck="false"></label>""",
        "<h2>Mismatch</h2><p>FAIL when any requirement names a different network than the one you typed. Settlement on the wrong network pays the wrong asset.</p>", "Compare network"),
    "x402-client-checklist": """
<section class="panel">
  <ul class="checklist">
    <li><label><input type="checkbox" id="chk-402"> Read the 402</label><p>You can see status 402, not only a generic network error. If the browser hides it, you have a server-side or curl path.</p></li>
    <li><label><input type="checkbox" id="chk-fields"> network, payTo, asset, amount</label><p>All four are present on the requirement you intend to pay.</p></li>
    <li><label><input type="checkbox" id="chk-asset"> Asset matches the chain</label><p>The asset address is USDC (or the token you expect) on that network, not a lookalike.</p></li>
    <li><label><input type="checkbox" id="chk-timeout"> Timeout is usable</label><p>maxTimeoutSeconds gives the wallet enough time to sign and submit.</p></li>
    <li><label><input type="checkbox" id="chk-cors"> Retry path exists</label><p>After paying, the client can send the payment header and read the 200. CORS is solved for that hop too.</p></li>
    <li><label><input type="checkbox" id="chk-pay"> You are not auto-paying</label><p>A human or an explicit policy confirms payTo and amount before any signature.</p></li>
    <li><label><input type="checkbox" id="chk-retry"> 200 is checked</label><p>You compared a paid response with the challenge so a still-402 is not treated as success.</p></li>
  </ul>
  <p class="verdict pending" id="summary" style="margin-top:0.9rem"></p>
</section>
<section class="explain"><h2>Local only</h2><p>Ticks stay in this tab. This checklist does not send a payment.</p></section>
""",
}
