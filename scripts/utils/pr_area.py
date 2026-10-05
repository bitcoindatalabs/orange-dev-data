"""
pr_area.py — single source of truth for "where in the code" a pull request lands.

Used by every report that charts PRs by area (State of Bitcoin Core monthly, TWIB weekly), so the
same PR is always counted in the same bucket.

Resolution order:
  1. GitHub labels applied by Bitcoin Core maintainers (~87% of merged bitcoin/bitcoin PRs have one).
  2. The PR title prefix ("wallet: ...", "test: ...") for unlabelled PRs.
  3. "Other".

This is a different question from the LLM `impact_category` in pr_summaries_cache.json
("why it matters"), which is for narrative, not for share-of-merges charts.
"""

import re

# Display order for charts and tables. Domain areas first, then engineering-practice areas.
AREAS = [
    "Consensus & Validation",
    "Mempool & Policy",
    "P2P & Network",
    "Wallet",
    "Mining",
    "RPC & Interfaces",
    "Node & Storage",
    "Tests & QA",
    "Build & CI",
    "Maintenance",
    "Other",
]

# When a PR carries several labels, the most specific (earliest) area wins:
# a PR labelled "Wallet" + "RPC/REST/ZMQ" is a wallet change; "Tests" + "Wallet" is wallet work.
_PRECEDENCE = {a: i for i, a in enumerate(AREAS)}

# Maintainer GitHub labels -> area. Labels absent here (e.g. "CI failed", "Bug", "Review club",
# "Needs Backport (x)") describe status, not location, and are ignored.
LABEL_TO_AREA = {
    "Consensus": "Consensus & Validation",
    "Validation": "Consensus & Validation",
    "Mempool": "Mempool & Policy",
    "TX fees and policy": "Mempool & Policy",
    "P2P": "P2P & Network",
    "Private Broadcast": "P2P & Network",
    "Wallet": "Wallet",
    "PSBT": "Wallet",
    "Descriptors": "Wallet",
    "Mining": "Mining",
    "RPC/REST/ZMQ": "RPC & Interfaces",
    "interfaces": "RPC & Interfaces",
    "GUI": "RPC & Interfaces",
    "IPC": "Node & Storage",
    "Utils/log/libs": "Node & Storage",
    "UTXO Db and Indexes": "Node & Storage",
    "Block storage": "Node & Storage",
    "Resource usage": "Node & Storage",
    "Tests": "Tests & QA",
    "Fuzzing": "Tests & QA",
    "Build system": "Build & CI",
    "Windows": "Build & CI",
    "macOS": "Build & CI",
    "Docs": "Maintenance",
    "Refactoring": "Maintenance",
    "Backport": "Maintenance",
    "Upstream": "Maintenance",
    "Scripts and tools": "Maintenance",
}

# Title-prefix tokens -> area (fallback for unlabelled PRs). Exact token match on the part before ":".
_PREFIX_TOKENS = [
    ("Consensus & Validation", {"consensus", "validation", "script", "merkle", "chain"}),
    ("Mempool & Policy", {"mempool", "policy", "txgraph", "cluster mempool", "clusterlin", "fees", "feefrac"}),
    ("P2P & Network", {"p2p", "net", "net_processing", "i2p", "tor", "private broadcast", "addrman", "netbase"}),
    ("Wallet", {"wallet", "walletdb", "psbt", "miniscript", "descriptors", "silent payments", "qt", "gui",
                "coinselection", "coin selection", "musig"}),
    ("Mining", {"mining", "miner", "sv2"}),
    ("RPC & Interfaces", {"rpc", "rest", "http", "cli", "zmq", "bitcoin-util", "bitcoin-cli", "interfaces"}),
    ("Node & Storage", {"kernel", "chainstate", "index", "node", "init", "util", "log", "logging", "common",
                        "argsman", "dbwrapper", "coins", "[ibd] coins", "chainparams", "multiprocess", "ipc",
                        "subprocess", "crypto", "key", "blockstorage", "streams",
                        "argsmanager", "help", "settings", "random"}),
    ("Tests & QA", {"test", "tests", "qa", "fuzz", "bench"}),
    ("Build & CI", {"build", "ci", "guix", "cmake", "depends", "lint", "iwyu", "clang-format", "clang-tidy"}),
    ("Maintenance", {"doc", "docs", "contrib", "refactor", "scripted-diff", "release", "backport"}),
]
_HOUSEKEEPING_RE = re.compile(r"backports?\b|subtree to latest|^release:|^\[\d+\.x\]", re.IGNORECASE)


def _labels(labels):
    if labels is None:
        return []
    if isinstance(labels, str):
        return [x.strip() for x in labels.split("|") if x.strip() and x.strip().lower() != "nan"]
    try:
        return [str(x).strip() for x in labels if str(x).strip()]
    except TypeError:
        return []


def area_from_labels(labels) -> str:
    areas = {LABEL_TO_AREA[l] for l in _labels(labels) if l in LABEL_TO_AREA}
    return min(areas, key=_PRECEDENCE.get) if areas else None


def area_from_title(title: str) -> str:
    t = (title or "").strip().lower()
    if _HOUSEKEEPING_RE.search(t):
        return "Maintenance"
    if ":" not in t:
        return None
    prefix = t.split(":", 1)[0].strip()
    tokens = {p.strip() for p in re.split(r"[,/+&]| and ", prefix) if p.strip()}
    tokens.add(prefix)
    for area, keys in _PREFIX_TOKENS:
        if tokens & keys:
            return area
    return None


def pr_area(labels, title: str) -> str:
    """Area for one PR: maintainer labels first, title prefix second, else "Other"."""
    return area_from_labels(labels) or area_from_title(title) or "Other"


def pr_area_source(labels, title: str) -> str:
    """'label' | 'title' | 'none' — for coverage diagnostics."""
    if area_from_labels(labels):
        return "label"
    return "title" if area_from_title(title) else "none"
