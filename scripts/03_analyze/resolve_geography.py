"""
resolve_geography.py — Phase 3 geographic attribution per contributor.

Called from unify_contributors.py (enrich_unified_geography) or run standalone on the
unified parquet. Signals, strongest first:

    1. override          verified entries of metadata/geo/curated_geography.json (private,
                         gitignored) — human-researched, country only
    2. github_location   the contributor's self-reported GitHub profile location
    3. bio               "based in <place>" in the GitHub bio
    4. email_tld         country-code domain of institutional commit emails
    5. blog_tld          country-code domain of the profile's blog URL
    6. flag              a single flag emoji in the bio (often support, not residence)
    7. timezone          commit timezone over winter and summer — macro-region only, never a
                         country; also the cross-check that flags conflicting locations

Produces:
- data/enriched/contributor_geography.parquet (keyed by uuid)
- data/enriched/geo_review_queue.csv (local only: unparsed / ambiguous / conflicting / unknown
  high-impact contributors, ranked by authored commits, for curating overrides)
"""

import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.utils.geography import (
    REGIONS,
    TAXONOMY_VERSION,
    clean_location,
    extract_flag_iso2,
    get_gazetteer,
    resolve_location,
)

CURATION_PATH = _PROJECT_ROOT / "metadata" / "geo" / "curated_geography.json"
GEO_PARQUET_PATH = _PROJECT_ROOT / "data" / "enriched" / "contributor_geography.parquet"
REVIEW_QUEUE_PATH = _PROJECT_ROOT / "data" / "enriched" / "geo_review_queue.csv"

# Vanity / Generic TLDs that do NOT indicate geographic residency
_VANITY_CCTLD = {
    "io", "co", "me", "ai", "tv", "cc", "sh", "ly", "gg", "fm", "to", "xyz",
    "dev", "app", "org", "com", "net", "edu", "gov", "mil", "int", "info",
    "biz", "name", "pro", "tech", "online", "site", "top", "club", "link",
    "work", "WTF", "wtf", "ws", "nu", "tk", "ml", "ga", "cf", "gq", "is",
    "vc", "la", "ac", "im", "ms", "ag", "sc", "bz", "gs", "cx", "ht", "st",
}

# Institutional / high-signal country ccTLDs mapped to ISO2
_VALID_CCTLD_TO_ISO2 = {
    "uk": "GB", "de": "DE", "fr": "FR", "nl": "NL", "ch": "CH", "at": "AT",
    "es": "ES", "pt": "PT", "it": "IT", "se": "SE", "no": "NO", "dk": "DK",
    "fi": "FI", "pl": "PL", "cz": "CZ", "sk": "SK", "hu": "HU", "ro": "RO",
    "bg": "BG", "ua": "UA", "ru": "RU", "by": "BY", "ie": "IE", "be": "BE",
    "lu": "LU", "gr": "GR", "hr": "HR", "rs": "RS", "si": "SI", "ee": "EE",
    "lv": "LV", "lt": "LT", "tr": "TR", "cy": "CY", "il": "IL", "ae": "AE",
    "ir": "IR", "cn": "CN", "hk": "HK", "tw": "TW", "jp": "JP", "kr": "KR",
    "in": "IN", "pk": "PK", "bd": "BD", "lk": "LK", "np": "NP", "sg": "SG",
    "my": "MY", "th": "TH", "vn": "VN", "id": "ID", "ph": "PH", "au": "AU",
    "nz": "NZ", "ca": "CA", "br": "BR", "ar": "AR", "mx": "MX", "cl": "CL",
    "co": "CO", "pe": "PE", "ve": "VE", "uy": "UY", "py": "PY", "bo": "BO",
    "ec": "EC", "sv": "SV", "cr": "CR", "pa": "PA", "gt": "GT", "ke": "KE",
    "ng": "NG", "za": "ZA", "gh": "GH", "et": "ET", "eg": "EG", "ma": "MA",
    "tn": "TN", "dz": "DZ", "sn": "SN", "ug": "UG", "tz": "TZ", "rw": "RW",
}

_WEBMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "protonmail.com", "proton.me", "pm.me", "icloud.com", "me.com", "mac.com",
    "aol.com", "zoho.com", "yandex.com", "mail.com", "gmx.com", "gmx.net",
    "fastmail.com", "fastmail.fm", "tutanota.com", "tuta.io", "hey.com",
    "users.noreply.github.com", "bitcoin.org", "bitcoincore.org", "chaincode.com",
    "blockstream.com", "blockstream.io", "lightning.engineering", "acinq.fr",
    "spiral.xyz", "brink.dev", "opensats.org", "mit.edu",
    # Privacy mail providers on a country domain, used worldwide.
    "protonmail.ch", "proton.ch", "tutanota.de", "tutamail.com", "posteo.de", "posteo.net",
    "mailbox.org", "danwin1210.de", "danwin1210.me", "disroot.org", "riseup.net", "cock.li",
}

# Commit timezone (winter offset, summer offset in minutes) -> (legacy chart region, UN macro-region).
# Only pairs that identify one region: European/North American DST pairs, and no-DST zones whose
# offset belongs to one region. +60/+60 is West/Central Africa (Nigeria, Algeria, Angola); +120/+120
# (South Africa, Egypt, Libya…), +180/+180 (Kenya, Turkey, Moscow) and +240/+240 (Gulf, Mauritius,
# Caucasus) span regions -> no answer.
_TZ_REGIONS: Dict[Tuple[int, int], Tuple[str, str]] = {
    (0, 60): ("Europe", "Europe"), (60, 120): ("Europe", "Europe"), (120, 180): ("Europe", "Europe"),
    (60, 60): ("Africa", "Africa"),
    (-300, -240): ("North America", "North America"), (-360, -300): ("North America", "North America"),
    (-420, -360): ("North America", "North America"), (-480, -420): ("North America", "North America"),
    (-540, -480): ("North America", "North America"), (-240, -180): ("North America", "North America"),
    (-420, -420): ("North America", "North America"),
    (-180, -180): ("Latin America", "Latin America & Caribbean"),
    (-300, -300): ("Latin America", "Latin America & Caribbean"),
    (-180, -240): ("Latin America", "Latin America & Caribbean"),   # Chile (southern DST)
    (330, 330): ("Asia Pacific", "Asia"), (345, 345): ("Asia Pacific", "Asia"),
    (420, 420): ("Asia Pacific", "Asia"), (540, 540): ("Asia Pacific", "Asia"),
    (210, 210): ("Asia Pacific", "Asia"),
    (480, 480): ("Asia Pacific", "Asia"),
    (660, 600): ("Asia Pacific", "Oceania"), (600, 600): ("Asia Pacific", "Oceania"),
    (630, 570): ("Asia Pacific", "Oceania"), (780, 720): ("Asia Pacific", "Oceania"),
}
_TZ_MIN_COMMITS_PER_SEASON = 5
_TZ_MIN_PURITY = 0.70
_WINTER, _SUMMER = {12, 1, 2}, {6, 7, 8}


def _tz_compatible(meta, tz_region: str) -> bool:
    """European DST pairs are shared by the eastern Mediterranean (Israel, Lebanon, Egypt, Cyprus)."""
    if meta.macro_region == tz_region:
        return True
    return tz_region == "Europe" and meta.m49_subregion in ("Western Asia", "Northern Africa")


def _as_of_t1() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def load_curation(df_unified: pd.DataFrame) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    """
    The private curation file (hand-edited, never written by the pipeline; gitignored because it
    names a country per person and this repo is public). Returns:

      overrides     uuid -> {iso2, as_of, source} for `verified` entries. They win over every
                    other signal. Only verify someone whose location is stated publicly, and
                    note that source and the date checked.
      legacy_hints  uuid -> iso2 for unverified entries (legacy tracker data). Never used for
                    attribution; shown in the review queue as candidates to verify.

    Entries match by uuid, falling back to the GitHub login (uuids change when identities merge).
    A missing file is an error: published aggregates would silently change by machine.
    """
    if not CURATION_PATH.exists():
        raise FileNotFoundError(
            f"{CURATION_PATH} not found. It is private (gitignored); copy it from the curation "
            f"source onto this machine before running the pipeline."
        )
    with open(CURATION_PATH, encoding="utf-8") as f:
        entries = json.load(f).get("entries", [])

    known = set(df_unified["uuid"])
    login_to_uuid = {}
    if "github_login_final" in df_unified.columns:
        login_to_uuid = {str(l).lower(): u for l, u in zip(df_unified["github_login_final"], df_unified["uuid"])
                         if isinstance(l, str) and l}
    gaz = get_gazetteer()

    overrides: Dict[str, Dict[str, Any]] = {}
    hints: Dict[str, str] = {}
    unmatched = bad_iso = 0
    for e in entries:
        uuid = e.get("uuid") if e.get("uuid") in known else login_to_uuid.get(str(e.get("login") or "").lower())
        iso2 = str(e.get("iso2") or "").upper()
        if not iso2:
            continue          # researched, no public location found
        if not uuid:
            unmatched += 1
            continue
        if iso2 not in gaz.countries_by_iso2:
            bad_iso += 1
            print(f"  [warn] curated entry has unknown iso2 {iso2!r} (uuid {uuid})")
            continue
        if e.get("verified") is True:
            overrides[uuid] = {"iso2": iso2, "as_of": e.get("as_of"), "source": e.get("source_note")}
        else:
            hints[uuid] = iso2
    print(f"  Curation: {len(overrides)} verified overrides, {len(hints)} unverified hints"
          f" ({unmatched} entries match no contributor, {bad_iso} bad iso2)")
    return overrides, hints


def compute_commit_signals(df_commits: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Per canonical_id from non-merge commits:
      tz_signature  "<winter>/<summer>" modal offsets (minutes), each season >= 70% pure
      tz_region     legacy chart region and tz_un_region UN macro-region for unambiguous pairs
      email_iso2    country of institutional commit-email domains (webmail / privacy mail excluded)
    """
    if df_commits is None or df_commits.empty or "timezone_offset_minutes" not in df_commits.columns:
        return {}

    cols = [c for c in ["canonical_id", "hash", "date_utc", "timezone_offset_minutes", "is_merge", "author_email"]
            if c in df_commits.columns]
    c = df_commits[cols].drop_duplicates(["canonical_id", "hash"])
    if "is_merge" in c.columns:
        c = c[~c["is_merge"].fillna(False).astype(bool)]
    c = c[c["timezone_offset_minutes"].notna() & c["canonical_id"].notna()].copy()
    c["canonical_id"] = c["canonical_id"].astype(str)
    c["tz"] = c["timezone_offset_minutes"].astype(int)
    c["month"] = pd.to_datetime(c["date_utc"], errors="coerce", utc=True).dt.month

    signals: Dict[str, Dict[str, Any]] = {}

    # Timezone: modal offset and its purity per season, both seasons required.
    season = c["month"].map(lambda m: "w" if m in _WINTER else ("s" if m in _SUMMER else None))
    seasonal = c.assign(season=season).dropna(subset=["season"])
    counts = seasonal.groupby(["canonical_id", "season", "tz"]).size().rename("n").reset_index()
    totals = counts.groupby(["canonical_id", "season"])["n"].transform("sum")
    counts["purity"] = counts["n"] / totals
    counts["total"] = totals
    modal = counts.sort_values(["canonical_id", "season", "n", "tz"], ascending=[True, True, False, True]) \
                  .drop_duplicates(["canonical_id", "season"])
    modal = modal[(modal["total"] >= _TZ_MIN_COMMITS_PER_SEASON) & (modal["purity"] >= _TZ_MIN_PURITY)]
    wide = modal.pivot(index="canonical_id", columns="season", values="tz").dropna()
    for cid, row in wide.iterrows():
        w, s = int(row["w"]), int(row["s"])
        if w == 0 and s == 0:   # UTC: servers and CI, not a place
            continue
        legacy, un = _TZ_REGIONS.get((w, s), (None, None))
        signals[cid] = {"tz_signature": f"{w:+d}/{s:+d}", "tz_region": legacy, "tz_un_region": un}

    # Institutional email country.
    if "author_email" in c.columns:
        dom = c["author_email"].astype(str).str.lower().str.split("@").str[1]
        tld = dom.str.rsplit(".", n=1).str[-1]
        ok = dom.notna() & ~dom.isin(_WEBMAIL_DOMAINS) & tld.isin(_VALID_CCTLD_TO_ISO2.keys()) & ~tld.isin(_VANITY_CCTLD)
        for cid, tlds in tld[ok].groupby(c.loc[ok, "canonical_id"]):
            iso, _ = Counter(_VALID_CCTLD_TO_ISO2[t] for t in tlds).most_common(1)[0]
            signals.setdefault(cid, {})["email_iso2"] = iso

    return signals


def extract_blog_cctld(blog: Any) -> Optional[str]:
    if not blog or not isinstance(blog, str):
        return None
    blog_clean = blog.strip().lower()
    if not blog_clean:
        return None
    m = re.search(r"(?:https?://)?(?:www\.)?[\w.-]+\.([a-z]{2})(?:/|$|:)", blog_clean)
    if not m:
        return None
    tld = m.group(1)
    if tld in _VANITY_CCTLD:
        return None
    return _VALID_CCTLD_TO_ISO2.get(tld)


def extract_bio_signals(bio: Any) -> Tuple[Optional[str], Optional[str]]:
    """(country from "based in <place>", country from a single flag emoji)."""
    if not bio or not isinstance(bio, str):
        return None, None
    gaz = get_gazetteer()
    based = None
    m = re.search(r"\b(?:based in|located in|living in|live in)\s+([A-Z][\w\s,.-]{2,40})", bio)
    if m:
        res = resolve_location(m.group(1).split(".")[0])
        if res.iso2 and res.status == "resolved" and res.confidence >= 0.85:
            based = res.iso2
    flags = list(dict.fromkeys(f for f in extract_flag_iso2(bio) if f in gaz.countries_by_iso2))
    return based, (flags[0] if len(flags) == 1 else None)


def enrich_unified_geography(
    df_unified: pd.DataFrame,
    df_commits: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Returns df_unified with geo_* columns. Writes data/enriched/contributor_geography.parquet
    and the local review queue.
    """
    gaz = get_gazetteer()
    overrides, legacy_hints = load_curation(df_unified)
    commit_signals = compute_commit_signals(df_commits) if df_commits is not None else {}
    t1 = _as_of_t1()

    out_rows: List[Dict[str, Any]] = []
    review_queue: List[Dict[str, Any]] = []

    for row in df_unified.itertuples(index=False):
        uuid = row.uuid
        raw_loc = clean_location(getattr(row, "github_location", None))
        authored = int(getattr(row, "authored_commits", 0) or 0)
        fetched_at = getattr(row, "github_profile_fetched_at", None)
        sig = commit_signals.get(uuid, {})
        tz_region, tz_un = sig.get("tz_region"), sig.get("tz_un_region")

        gh_res = resolve_location(raw_loc)
        gh_iso = gh_res.iso2 if gh_res.status in ("resolved", "multi") else None
        # "Georgia", "Victoria"…: let the timezone pick between the readings.
        if gh_res.status == "ambiguous" and tz_region:
            fits = [a for a in gh_res.alternatives
                    if a in gaz.countries_by_iso2 and gaz.countries_by_iso2[a].macro_region == tz_region]
            if len(fits) == 1:
                gh_iso = fits[0]

        bio_based, bio_flag = extract_bio_signals(getattr(row, "github_bio", None))
        blog_iso = extract_blog_cctld(getattr(row, "github_blog", None))
        email_iso = sig.get("email_iso2")
        ov = overrides.get(uuid)

        # Strongest available signal wins.
        candidates = [
            ("override", ov["iso2"] if ov else None, 1.0, (ov or {}).get("as_of")),
            ("github_location", gh_iso, gh_res.confidence if gh_res.status in ("resolved", "multi") else 0.6,
             str(fetched_at)[:10] if fetched_at else None),
            ("bio", bio_based, 0.6, str(fetched_at)[:10] if fetched_at else None),
            ("email_tld", email_iso, 0.55, t1),
            ("blog_tld", blog_iso, 0.45, str(fetched_at)[:10] if fetched_at else None),
            ("flag", bio_flag, 0.4, str(fetched_at)[:10] if fetched_at else None),
        ]
        source, iso2, conf, as_of = next(((s, i, c, a) for s, i, c, a in candidates if i in gaz.countries_by_iso2),
                                         ("none", None, 0.0, None))
        meta = gaz.countries_by_iso2.get(iso2) if iso2 else None

        if meta:
            status = gh_res.status if source == "github_location" and gh_res.status != "ambiguous" else "resolved"
            macro, un_macro = meta.macro_region, meta.un_macro_region
        elif gh_res.status == "region_only":
            source, status, conf, as_of = "github_location", "region_only", gh_res.confidence, (str(fetched_at)[:10] if fetched_at else None)
            macro, un_macro = gh_res.macro_region, gh_res.un_macro_region
        elif tz_region:
            source, status, conf, as_of = "timezone", "region_only", 0.35, t1
            macro, un_macro = tz_region, tz_un
        else:
            status = gh_res.status
            macro, un_macro = "Undisclosed", "Undisclosed"

        # Conflict: the commit timezone says another region than the chosen country.
        conflicts = []
        if meta and tz_region and not _tz_compatible(meta, tz_region):
            conflicts.append(f"timezone {sig['tz_signature']} is {tz_region}")
        if ov and gh_iso and gh_iso != ov["iso2"]:
            conflicts.append(f"github says {gh_iso}")

        out_rows.append({
            "uuid": uuid,
            "geo_country_iso2": meta.iso2 if meta else None,
            "geo_country_iso3": meta.iso3 if meta else None,
            "geo_country_name": meta.display_name if meta else None,
            "geo_sovereign_iso2": meta.sovereign_iso2 if meta else None,
            "geo_m49_subregion": meta.m49_subregion if meta else None,
            "geo_macro_region": macro if macro in REGIONS else "Undisclosed",
            "geo_un_macro_region": un_macro,
            "geo_wb_income": (meta.wb_income or None) if meta else None,
            "geo_flag": meta.flag if meta else None,
            "geo_status": status,
            "geo_source": source,
            "geo_confidence": round(float(conf), 2),
            "geo_conflict": bool(conflicts),
            "geo_tz_signature": sig.get("tz_signature"),
            "geo_location_raw": raw_loc,
            "geo_as_of": as_of,
            "geo_taxonomy_version": TAXONOMY_VERSION,
        })

        # Unverified legacy curation that adds or contradicts a country is a candidate to verify.
        hint = legacy_hints.get(uuid) if not ov else None
        hint_differs = bool(hint) and hint != iso2
        if conflicts or hint_differs or gh_res.status in ("unparsed", "ambiguous") or (authored >= 20 and not meta):
            review_queue.append({
                "uuid": uuid,
                "display_name": getattr(row, "display_name", ""),
                "github_login": getattr(row, "github_login_final", ""),
                "authored_commits": authored,
                "github_location_raw": raw_loc or "",
                "resolved_iso2": iso2 or "",
                "geo_source": source,
                "geo_status": status,
                "conflict": "; ".join(conflicts),
                "tz_signature": sig.get("tz_signature") or "",
                "legacy_hint_iso2": hint or "",
            })

    df_geo = pd.DataFrame(out_rows)

    os.makedirs(GEO_PARQUET_PATH.parent, exist_ok=True)
    df_geo.to_parquet(GEO_PARQUET_PATH, index=False)

    # Review queue: local only (names + locations of individuals never go to output/).
    review_queue.sort(key=lambda r: (-r["authored_commits"], r["uuid"]))
    with open(REVIEW_QUEUE_PATH, "w", newline="", encoding="utf-8") as f:
        fields = ["uuid", "display_name", "github_login", "authored_commits", "github_location_raw",
                  "resolved_iso2", "geo_source", "geo_status", "conflict", "tz_signature", "legacy_hint_iso2"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(review_queue)

    # Merge columns into df_unified (drop any existing geo_* columns first so re-runs are idempotent)
    existing_geo_cols = [c for c in df_unified.columns if c.startswith("geo_")]
    if existing_geo_cols:
        df_unified = df_unified.drop(columns=existing_geo_cols)
    df_unified = df_unified.merge(df_geo, on="uuid", how="left")

    _print_kpis(df_unified, commit_signals, gaz, len(review_queue))
    return df_unified


def _print_kpis(df: pd.DataFrame, commit_signals: Dict[str, Dict[str, Any]], gaz, n_review: int) -> None:
    n_total = len(df)
    commits = df["authored_commits"].fillna(0)
    total_commits = max(1, commits.sum())
    has_country = df["geo_country_iso2"].notna()
    has_region = df["geo_macro_region"] != "Undisclosed"
    top100 = df.assign(_c=commits).sort_values("_c", ascending=False).head(100)

    # How often the timezone region agrees with a GitHub-located country (target >= 90%).
    agree = n_cmp = 0
    for uuid, iso2, src in zip(df["uuid"], df["geo_country_iso2"], df["geo_source"]):
        tz = commit_signals.get(uuid, {}).get("tz_region")
        if tz and src == "github_location" and iso2 in gaz.countries_by_iso2:
            n_cmp += 1
            agree += _tz_compatible(gaz.countries_by_iso2[iso2], tz)

    print(
        f"  🌍 Geography (taxonomy v{TAXONOMY_VERSION}):\n"
        f"     • Country known: {has_country.sum():,} / {n_total:,} devs ({commits[has_country].sum() / total_commits:.1%} of authored commits)\n"
        f"     • Region known:  {has_region.sum():,} / {n_total:,} devs ({commits[has_region].sum() / total_commits:.1%} of authored commits)\n"
        f"     • Top-100 committers with a country: {top100['geo_country_iso2'].notna().sum()} / 100\n"
        f"     • Sources: {df['geo_source'].value_counts().to_dict()}\n"
        f"     • Unparsed locations: {(df['geo_status'] == 'unparsed').sum()} | conflicts: {int(df['geo_conflict'].sum())}"
        f" | review queue: {n_review} rows -> {REVIEW_QUEUE_PATH.relative_to(_PROJECT_ROOT)}\n"
        f"     • Timezone region agrees with GitHub location: {agree}/{n_cmp}"
        f" ({agree / max(1, n_cmp):.1%})"
    )


def main() -> None:
    unified_path = _PROJECT_ROOT / "data" / "enriched" / "contributors_unified.parquet"
    commits_path = _PROJECT_ROOT / "data" / "enriched" / "commits_resolved.parquet"

    if not unified_path.exists():
        print(f"Error: {unified_path} not found.")
        sys.exit(1)

    df_unified = pd.read_parquet(unified_path)
    df_commits = pd.read_parquet(commits_path) if commits_path.exists() else None

    df_unified = enrich_unified_geography(df_unified, df_commits)
    df_unified.to_parquet(unified_path, index=False)
    print(f"✅ Updated {unified_path} with geo_* columns.")


if __name__ == "__main__":
    main()
