"""
Location evidence that is not the person's own stated location:

  commit timezone   macro-region only, never a country. All-time signature (current location) and a
                    per-year, DST-aware reading (location history).
  email ccTLD       country of institutional commit-email domains (webmail, privacy mail and
                    employer domains excluded), all-time and per year.
  blog ccTLD, bio   "based in <place>" and a single flag emoji in the GitHub bio.
"""

import re
from collections import Counter
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from scripts.utils.geography import extract_flag_iso2, get_gazetteer, resolve_location

# Generic / vanity TLDs that say nothing about residence.
VANITY_TLDS = {
    "io", "co", "me", "ai", "tv", "cc", "sh", "ly", "gg", "fm", "to", "xyz",
    "dev", "app", "org", "com", "net", "edu", "gov", "mil", "int", "info",
    "biz", "name", "pro", "tech", "online", "site", "top", "club", "link",
    "work", "wtf", "ws", "nu", "tk", "ml", "ga", "cf", "gq", "is",
    "vc", "la", "ac", "im", "ms", "ag", "sc", "bz", "gs", "cx", "ht", "st",
}

# Country-code TLD -> ISO2, for ccTLDs that do indicate a country.
CCTLD_TO_ISO2 = {
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
    "pe": "PE", "ve": "VE", "uy": "UY", "py": "PY", "bo": "BO",
    "ec": "EC", "sv": "SV", "cr": "CR", "pa": "PA", "gt": "GT", "ke": "KE",
    "ng": "NG", "za": "ZA", "gh": "GH", "et": "ET", "eg": "EG", "ma": "MA",
    "tn": "TN", "dz": "DZ", "sn": "SN", "ug": "UG", "tz": "TZ", "rw": "RW",
}

# Email domains that say nothing about where the person lives: webmail, privacy mail on a
# country domain (used worldwide), GitHub noreply, and project / employer domains.
NON_RESIDENCE_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "protonmail.com", "proton.me", "pm.me", "icloud.com", "me.com", "mac.com",
    "aol.com", "zoho.com", "yandex.com", "mail.com", "gmx.com", "gmx.net",
    "fastmail.com", "fastmail.fm", "tutanota.com", "tuta.io", "hey.com",
    "users.noreply.github.com", "bitcoin.org", "bitcoincore.org", "chaincode.com",
    "blockstream.com", "blockstream.io", "lightning.engineering", "acinq.fr",
    "spiral.xyz", "brink.dev", "opensats.org", "mit.edu",
    "protonmail.ch", "proton.ch", "tutanota.de", "tutamail.com", "posteo.de", "posteo.net",
    "mailbox.org", "danwin1210.de", "danwin1210.me", "disroot.org", "riseup.net", "cock.li",
}

# Timezone families: (offset in Dec-Feb, offset in Jun-Aug) in minutes -> (legacy chart region,
# UN macro-region). Only pairs that identify one region: European / North American DST pairs, and
# no-DST zones whose offset belongs to one region. +60/+60 is West/Central Africa.
TZ_REGIONS: Dict[Tuple[int, int], Tuple[str, str]] = {
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
# Zones that span regions (+120 South Africa/Egypt, +180 Kenya/Turkey/Moscow, +240 Gulf/Caucasus) or
# say nothing (UTC: servers and CI). They compete in the yearly vote but never name a region.
TZ_UNPLACEABLE = [(0, 0), (120, 120), (180, 180), (240, 240)]

TZ_MIN_COMMITS_PER_SEASON = 5      # all-time signature: commits per season
TZ_MIN_PURITY = 0.70               # share of commits that must agree
TZ_MIN_COMMITS_PER_YEAR = 3        # yearly reading
_WINTER, _SUMMER = {12, 1, 2}, {6, 7, 8}
_YEAR_B_MONTHS, _YEAR_TRANSITION = {5, 6, 7, 8, 9}, {3, 4, 10, 11}


def tz_compatible(meta, tz_region: str) -> bool:
    """Is a country consistent with a timezone region? European DST pairs are also used in the
    eastern Mediterranean (Israel, Lebanon, Egypt, Cyprus)."""
    if meta.macro_region == tz_region:
        return True
    return tz_region == "Europe" and meta.m49_subregion in ("Western Asia", "Northern Africa")


def _non_merge_commits(df_commits: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["canonical_id", "hash", "date_utc", "timezone_offset_minutes", "is_merge", "author_email"]
            if c in df_commits.columns]
    c = df_commits[cols].drop_duplicates(["canonical_id", "hash"])
    if "is_merge" in c.columns:
        c = c[~c["is_merge"].fillna(False).astype(bool)]
    c = c[c["timezone_offset_minutes"].notna() & c["canonical_id"].notna()].copy()
    c["canonical_id"] = c["canonical_id"].astype(str)
    c["tz"] = c["timezone_offset_minutes"].astype(int)
    dt = pd.to_datetime(c["date_utc"], errors="coerce", utc=True)
    c["month"], c["year"] = dt.dt.month, dt.dt.year
    return c


def _institutional_cctld(emails: pd.Series) -> pd.Series:
    """ISO2 for each email whose domain is an institutional country domain, else NaN."""
    dom = emails.astype(str).str.lower().str.split("@").str[1]
    tld = dom.str.rsplit(".", n=1).str[-1]
    ok = dom.notna() & ~dom.isin(NON_RESIDENCE_EMAIL_DOMAINS) & tld.isin(CCTLD_TO_ISO2.keys()) & ~tld.isin(VANITY_TLDS)
    return tld.where(ok).map(CCTLD_TO_ISO2)


def compute_commit_signals(df_commits: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    All-time signals per canonical_id from non-merge commits:
      tz_signature  "<winter>/<summer>" modal offsets (minutes), each season >= 70% pure
      tz_region     legacy chart region and tz_un_region UN macro-region for unambiguous pairs
      email_iso2    majority country of institutional commit-email domains
    """
    if df_commits is None or df_commits.empty or "timezone_offset_minutes" not in df_commits.columns:
        return {}
    c = _non_merge_commits(df_commits)
    signals: Dict[str, Dict[str, Any]] = {}

    season = c["month"].map(lambda m: "w" if m in _WINTER else ("s" if m in _SUMMER else None))
    seasonal = c.assign(season=season).dropna(subset=["season"])
    counts = seasonal.groupby(["canonical_id", "season", "tz"]).size().rename("n").reset_index()
    totals = counts.groupby(["canonical_id", "season"])["n"].transform("sum")
    counts["purity"] = counts["n"] / totals
    counts["total"] = totals
    modal = counts.sort_values(["canonical_id", "season", "n", "tz"], ascending=[True, True, False, True]) \
                  .drop_duplicates(["canonical_id", "season"])
    modal = modal[(modal["total"] >= TZ_MIN_COMMITS_PER_SEASON) & (modal["purity"] >= TZ_MIN_PURITY)]
    wide = modal.pivot(index="canonical_id", columns="season", values="tz").dropna()
    for cid, row in wide.iterrows():
        w, s = int(row["w"]), int(row["s"])
        if w == 0 and s == 0:   # UTC: servers and CI, not a place
            continue
        legacy, un = TZ_REGIONS.get((w, s), (None, None))
        signals[cid] = {"tz_signature": f"{w:+d}/{s:+d}", "tz_region": legacy, "tz_un_region": un}

    if "author_email" in c.columns:
        iso = _institutional_cctld(c["author_email"])
        for cid, isos in iso.dropna().groupby(c.loc[iso.notna(), "canonical_id"]):
            signals.setdefault(cid, {})["email_iso2"] = Counter(isos).most_common(1)[0][0]
    return signals


def compute_tz_yearly(df_commits: pd.DataFrame, alltime: Optional[Dict[str, Dict[str, Any]]] = None) -> pd.DataFrame:
    """
    Macro-region per contributor per year from commit timezones, aware of daylight saving.

    Each commit is matched against every timezone family: a Dec-Feb commit must carry the family's
    winter offset, a May-Sep commit its summer offset, and a commit in a transition month
    (Mar, Apr, Oct, Nov) either one. The family consistent with the most commits wins if it covers
    >= 70% of the year's commits (>= 3 commits). A tie between families of different regions (a
    year with only winter commits at +60 fits Central Europe and West Africa) is broken by the
    contributor's all-time timezone region, else the year stays unresolved.

    Returns one row per (canonical_id, year) with: n_commits, tz_family, tz_region, tz_un_region,
    support, status (resolved | tiebreak | mixed | ambiguous | utc | insufficient).
    """
    cols = ["canonical_id", "year", "n_commits", "tz_family", "tz_region", "tz_un_region", "support", "status"]
    if df_commits is None or df_commits.empty:
        return pd.DataFrame(columns=cols)
    c = _non_merge_commits(df_commits).dropna(subset=["year"])
    c["year"] = c["year"].astype(int)
    alltime = alltime or {}

    families = [(a, b, *TZ_REGIONS[(a, b)]) for a, b in TZ_REGIONS] + [(a, b, None, None) for a, b in TZ_UNPLACEABLE]
    in_a, in_b, in_t = c["month"].isin(_WINTER), c["month"].isin(_YEAR_B_MONTHS), c["month"].isin(_YEAR_TRANSITION)
    keys = ["canonical_id", "year"]
    support = c[keys].copy()
    for i, (a, b, _, _) in enumerate(families):
        support[i] = ((in_a & (c["tz"] == a)) | (in_b & (c["tz"] == b)) | (in_t & c["tz"].isin((a, b)))).astype(int)
    per_year = support.groupby(keys).sum()
    n = c.groupby(keys).size()

    rows = []
    for (cid, year), sup in per_year.iterrows():
        total = int(n.loc[(cid, year)])
        base = {"canonical_id": cid, "year": int(year), "n_commits": total,
                "tz_family": None, "tz_region": None, "tz_un_region": None, "support": 0.0}
        best = int(sup.max())
        if total < TZ_MIN_COMMITS_PER_YEAR or best == 0:
            rows.append({**base, "status": "insufficient"})
            continue
        share = best / total
        winners = [families[i] for i in range(len(families)) if sup[i] == best]
        regions = {w[2] for w in winners}            # None = an unplaceable zone
        a, b, legacy, un = winners[0]
        base.update(support=round(share, 3), tz_family=f"{a:+d}/{b:+d}")
        if share < TZ_MIN_PURITY:
            rows.append({**base, "status": "mixed"})
            continue
        if len(regions) == 1:
            if legacy is None:
                rows.append({**base, "status": "utc" if (a, b) == (0, 0) else "ambiguous"})
            else:
                rows.append({**base, "tz_region": legacy, "tz_un_region": un, "status": "resolved"})
            continue
        prior = alltime.get(cid, {}).get("tz_region")
        pick = next((w for w in winners if w[2] is not None and w[2] == prior), None)
        if pick:
            rows.append({**base, "tz_family": f"{pick[0]:+d}/{pick[1]:+d}", "tz_region": pick[2],
                         "tz_un_region": pick[3], "status": "tiebreak"})
        else:
            rows.append({**base, "status": "ambiguous"})
    return pd.DataFrame(rows, columns=cols)


def compute_email_country_yearly(df_commits: pd.DataFrame) -> pd.DataFrame:
    """Majority institutional email country per (canonical_id, year): columns canonical_id, year, email_iso2."""
    cols = ["canonical_id", "year", "email_iso2"]
    if df_commits is None or df_commits.empty or "author_email" not in df_commits.columns:
        return pd.DataFrame(columns=cols)
    c = _non_merge_commits(df_commits).dropna(subset=["year"])
    c["email_iso2"] = _institutional_cctld(c["author_email"])
    c = c.dropna(subset=["email_iso2"])
    if c.empty:
        return pd.DataFrame(columns=cols)
    out = (c.groupby(["canonical_id", "year"])["email_iso2"]
             .agg(lambda s: Counter(s).most_common(1)[0][0]).reset_index())
    out["year"] = out["year"].astype(int)
    return out[cols]


def extract_blog_cctld(blog: Any) -> Optional[str]:
    if not blog or not isinstance(blog, str):
        return None
    m = re.search(r"(?:https?://)?(?:www\.)?[\w.-]+\.([a-z]{2})(?:/|$|:)", blog.strip().lower())
    if not m or m.group(1) in VANITY_TLDS:
        return None
    return CCTLD_TO_ISO2.get(m.group(1))


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
