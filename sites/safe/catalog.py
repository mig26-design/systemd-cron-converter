"""Safe mini-site copy. Flagship first, required slug order."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
from sitegen import tool_shell  # noqa: E402

GROUP_ORDER = ["Safe", "Calldata", "Logs", "Checklist"]

CHAIN = """<label class="field">Chain preset
      <select id="chain">
        <option value="https://ethereum.publicnode.com">Ethereum</option>
        <option value="https://rpc.gnosischain.com">Gnosis</option>
        <option value="https://base.publicnode.com">Base</option>
        <option value="https://arbitrum-one.publicnode.com">Arbitrum</option>
      </select></label>
    <label class="field span-2">JSON-RPC URL
      <input id="rpc" spellcheck="false" value="https://ethereum.publicnode.com" autocomplete="off"></label>"""

GNOSIS = CHAIN.replace(
    'value="https://ethereum.publicnode.com">Ethereum',
    'value="https://ethereum.publicnode.com">Ethereum',
).replace(
    '<option value="https://rpc.gnosischain.com">Gnosis</option>',
    '<option value="https://rpc.gnosischain.com" selected>Gnosis</option>',
).replace(
    'value="https://ethereum.publicnode.com" autocomplete',
    'value="https://rpc.gnosischain.com" autocomplete',
)

TX = """<label class="field span-2">Transaction hash or raw input
      <textarea id="tx" rows="5" spellcheck="false" placeholder="0x hash, or 0x6a761202… calldata"></textarea></label>"""

SAFE = """<label class="field span-2">Safe address
      <input id="safe" spellcheck="false" placeholder="0x…" autocomplete="off"></label>"""

EXAMPLE = """<div class="preset-row"><button type="button" class="preset" id="example">Example calldata</button></div>"""


def page(fields, explain, button, presets=""):
    return tool_shell(fields, explain, button=button, presets=presets)


TOOLS = [
    {"slug": "safe-mech-decode", "title": "Safe mech delivery decode", "nav": "Mech delivery", "group": "Safe",
     "description": "Decode a Safe execTransaction and separate the outer sender from the inner call a mech delivers."},
    {"slug": "safe-exec-transaction-decode", "title": "execTransaction decode", "nav": "execTransaction", "group": "Safe",
     "description": "Decode Safe execTransaction calldata: to, value, data length, operation, gas fields, and signature blob length."},
    {"slug": "gnosis-safe-multisig-summary", "title": "Safe multisig summary", "nav": "Multisig summary", "group": "Safe",
     "description": "Read owners, threshold, nonce, version, and guard from a Safe with eth_call."},
    {"slug": "safe-nonce-gap-check", "title": "Safe nonce gap", "nav": "Nonce gap", "group": "Safe",
     "description": "Compare the on-chain Safe nonce with the nonce you last saw."},
    {"slug": "safe-owner-threshold-card", "title": "Owner and threshold card", "nav": "Owners", "group": "Safe",
     "description": "Show the owner list and threshold. Threshold 1 is called out."},
    {"slug": "safe-module-list", "title": "Safe module list", "nav": "Modules", "group": "Safe",
     "description": "Page through enabled modules with getModulesPaginated."},
    {"slug": "safe-guard-status", "title": "Safe guard status", "nav": "Guard", "group": "Safe",
     "description": "Read getGuard and show whether a transaction guard is installed."},
    {"slug": "eth-tx-input-decoder", "title": "Transaction input decoder", "nav": "Input words", "group": "Calldata",
     "description": "Split transaction input into a selector and 32-byte words, marking clean addresses."},
    {"slug": "calldata-4byte-lookup", "title": "4-byte selector lookup", "nav": "4-byte lookup", "group": "Calldata",
     "description": "Match a selector against a local list and, when CORS allows, the public 4byte directory."},
    {"slug": "erc20-transfer-decode", "title": "ERC-20 transfer decode", "nav": "ERC-20 transfer", "group": "Calldata",
     "description": "Decode transfer, approve, and transferFrom amounts with a decimals scaler."},
    {"slug": "erc721-transfer-decode", "title": "ERC-721 transfer decode", "nav": "ERC-721 transfer", "group": "Calldata",
     "description": "Decode safeTransferFrom and flag the transferFrom selector shared with ERC-20."},
    {"slug": "internal-tx-trace-summary", "title": "Trace and receipt summary", "nav": "Trace summary", "group": "Logs",
     "description": "Summarize a transaction receipt and, if you opt in, a callTracer debug trace."},
    {"slug": "safe-event-log-parser", "title": "Safe event log parser", "nav": "Safe events", "group": "Logs",
     "description": "Label receipt logs that match known Safe events such as ExecutionSuccess and AddedOwner."},
    {"slug": "mech-job-id-from-tx", "title": "Mech job id candidate", "nav": "Job id candidate", "group": "Calldata",
     "description": "Show the first 32-byte word of execTransaction inner data as a candidate job id."},
    {"slug": "deliver-payload-size", "title": "Delivery payload size", "nav": "Payload size", "group": "Calldata",
     "description": "Classify inner calldata size as small, typical, large, or very large."},
    {"slug": "gnosis-chain-tx-status", "title": "Gnosis Chain tx status", "nav": "Gnosis tx status", "group": "Logs",
     "description": "Read a transaction and receipt from a Gnosis Chain RPC, or any RPC you paste."},
    {"slug": "safe-signature-count", "title": "Safe signature count", "nav": "Signature count", "group": "Safe",
     "description": "Count 65-byte chunks in an execTransaction signature blob. This does not recover signers."},
    {"slug": "approve-hash-vs-exec", "title": "approveHash versus exec", "nav": "approveHash vs exec", "group": "Safe",
     "description": "Tell approveHash apart from execTransaction so an approval is not mistaken for execution."},
    {"slug": "batch-tx-unroll", "title": "Batch transaction unroll", "nav": "MultiSend unroll", "group": "Calldata",
     "description": "Unpack MultiSend transactions into operation, to, value, and data length."},
    {"slug": "safe-tx-security-checklist", "title": "Safe transaction checklist", "nav": "Tx checklist", "group": "Checklist",
     "description": "A local checklist to walk before you sign a Safe transaction."},
]

PAGES = {
    "safe-mech-decode": page(CHAIN + TX, "<h2>Mech delivery</h2><p>The outer transaction <code>to</code> is the Safe. The decoded <code>to</code> and <code>data</code> are what gets called. A mech is often the <code>from</code>. No signature recovery, no registry lookup, no MultiSend expansion.</p>", "Decode", EXAMPLE),
    "safe-exec-transaction-decode": page(CHAIN + TX, "<h2>Limitations</h2><p>Manual decode of selector <code>0x6a761202</code>. Delegatecall is flagged. Hashes are loaded with <code>eth_getTransactionByHash</code> and need a CORS-friendly RPC.</p>", "Decode", EXAMPLE),
    "gnosis-safe-multisig-summary": page(CHAIN + SAFE, "<h2>Calls</h2><p><code>getOwners</code>, <code>getThreshold</code>, <code>nonce</code>, <code>VERSION</code>, and <code>getGuard</code> via <code>eth_call</code>. The Safe must be on the chain that RPC serves.</p>", "Read Safe"),
    "safe-nonce-gap-check": page(CHAIN + SAFE + """<label class="field">Nonce you last saw
      <input id="seen" inputmode="numeric" placeholder="optional" spellcheck="false"></label>""",
        "<h2>Gap</h2><p>On-chain nonce minus your number. Leave the field blank to only read the nonce.</p>", "Compare nonce"),
    "safe-owner-threshold-card": page(CHAIN + SAFE, "<h2>Threshold</h2><p>Reads owners and threshold only. It does not list pending signatures.</p>", "Read owners"),
    "safe-module-list": page(CHAIN + SAFE + """<label class="field">Start cursor
      <input id="start" value="0x0000000000000000000000000000000000000001" spellcheck="false"></label>
    <label class="field">Page size
      <input id="size" value="20" spellcheck="false"></label>""",
        "<h2>Pagination</h2><p><code>getModulesPaginated</code> returns modules greater than the cursor. Start at <code>0x1</code> for the first page.</p>", "List modules"),
    "safe-guard-status": page(CHAIN + SAFE, "<h2>Guard</h2><p>A zero address means no guard. A set guard is displayed, not audited.</p>", "Read guard"),
    "eth-tx-input-decoder": page(CHAIN + TX, "<h2>Words</h2><p>Shows up to 24 words after the selector. A word with 12 leading zero bytes is also shown as an address. Dynamic offsets are not followed on this page.</p>", "Split input"),
    "calldata-4byte-lookup": page(CHAIN + """<label class="field">Selector
      <input id="selector" spellcheck="false" placeholder="0xa9059cbb"></label>""" + TX,
        "<h2>Sources</h2><p>The local list covers Safe, MultiSend, and common token selectors. The 4byte directory is optional and may be blocked by CORS.</p>", "Look up"),
    "erc20-transfer-decode": page(CHAIN + TX + """<label class="field">Decimals
      <input id="decimals" value="18" spellcheck="false"></label>""",
        "<h2>Shared selector</h2><p><code>transferFrom</code> is also used by ERC-721. The scaled amount uses the decimals you type, default 18. USDC is often 6.</p>", "Decode"),
    "erc721-transfer-decode": page(CHAIN + TX, "<h2>NFT selectors</h2><p><code>safeTransferFrom</code> is specific. <code>transferFrom</code> is ambiguous with ERC-20, so the third word is labeled token id or amount.</p>", "Decode"),
    "internal-tx-trace-summary": page(CHAIN + """<label class="field span-2">Transaction hash
      <input id="tx" spellcheck="false" placeholder="0x…"></label>
    <div class="span-2 check-row"><label><input type="checkbox" id="trace"> Also try debug_traceTransaction</label></div>""",
        "<h2>Traces</h2><p>The receipt is the reliable part. Debug traces are off on many public RPCs. Leave the box unchecked unless you trust the endpoint.</p>", "Read receipt"),
    "safe-event-log-parser": page(CHAIN + """<label class="field span-2">Transaction hash
      <input id="tx" spellcheck="false" placeholder="0x…"></label>""",
        "<h2>Events</h2><p>Matches topic0 for ExecutionSuccess, ExecutionFailure, owner and threshold changes, modules, guard, ApproveHash, and SafeReceived. Other logs stay unknown.</p>", "Parse logs"),
    "mech-job-id-from-tx": page(CHAIN + TX, "<h2>Not a registry</h2><p>The first inner word is a candidate only. Different mech versions put the request id in different places.</p>", "Show candidate"),
    "deliver-payload-size": page(CHAIN + TX, "<h2>Buckets</h2><p>Empty, under 1 KB, under 8 KB, under 24 KB, or larger. For execTransaction the size is the inner data, not the outer input.</p>", "Measure"),
    "gnosis-chain-tx-status": page(GNOSIS + """<label class="field span-2">Transaction hash
      <input id="tx" spellcheck="false" placeholder="0x…"></label>""",
        "<h2>Chain</h2><p>The default RPC is Gnosis Chain. A hash from Ethereum will not resolve here until you change the RPC.</p>", "Check status"),
    "safe-signature-count": page(CHAIN + TX, "<h2>Chunks</h2><p>Divides the signature blob by 65. A remainder means it is not a clean list of ECDSA signatures. Signers are not recovered.</p>", "Count"),
    "approve-hash-vs-exec": page(CHAIN + TX, "<h2>Why it matters</h2><p><code>approveHash</code> stores an approval. <code>execTransaction</code> performs the call. Mixing them up is how a queued approval gets treated as already executed.</p>", "Classify"),
    "batch-tx-unroll": page(CHAIN + TX, "<h2>Packed bytes</h2><p>Accepts <code>multiSend</code> calldata or an <code>execTransaction</code> whose inner data is <code>multiSend</code>. Each record is operation, to, value, data length, and the inner selector.</p>", "Unroll", EXAMPLE),
    "safe-tx-security-checklist": """
<section class="panel">
  <ul class="checklist">
    <li><label><input type="checkbox" id="chk-to"> Destination</label><p>The inner <code>to</code> is the contract you expect, not a lookalike.</p></li>
    <li><label><input type="checkbox" id="chk-value"> Value</label><p>ETH value leaving the Safe is the amount you meant, including zero.</p></li>
    <li><label><input type="checkbox" id="chk-op"> Operation</label><p>You know whether this is CALL or DELEGATECALL. Delegatecall runs code against the Safe’s storage.</p></li>
    <li><label><input type="checkbox" id="chk-data"> Inner data</label><p>You decoded the selector and, if it is a batch, each inner call.</p></li>
    <li><label><input type="checkbox" id="chk-sig"> Signers</label><p>The signature count meets the threshold, and you are not treating approveHash as execution.</p></li>
    <li><label><input type="checkbox" id="chk-nonce"> Nonce</label><p>The nonce matches the Safe you are signing for. A gap means another transaction landed.</p></li>
    <li><label><input type="checkbox" id="chk-guard"> Guard and modules</label><p>You know whether a guard or module can change what execution does.</p></li>
  </ul>
  <p class="verdict pending" id="summary" style="margin-top:0.9rem"></p>
</section>
<section class="explain"><h2>Local only</h2><p>Nothing is sent. Use the decode tools on this site, then tick the boxes in this tab.</p></section>
""",
}
