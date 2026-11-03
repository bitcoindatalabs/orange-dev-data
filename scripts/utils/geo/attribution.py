"""
One attribution policy for "where is this contributor", applied at two time scopes.

Current (as of T-1), strongest signal first:
    override         verified curation (private file)
    github_location  self-reported GitHub profile location
    bio              "based in <place>"
    email_tld        institutional email country (all-time majority)
    blog_tld         blog domain country
    flag             a single flag emoji in the bio
    region-only      GitHub location naming only a region, then the all-time commit timezone

Per year (location history). The current location is the latest observation; earlier years need
their own evidence, so every row records its `basis`:
    current                     the year is the current year: the current location
    observed_profile            a GitHub profile snapshot fetched during that year
    observed_email              institutional email country seen in that year's commits
    carried_back_tz_consistent  current location, and that year's commit timezone agrees
    carried_back_unverified     current location, no timezone reading for that year
    tz_only                     that year's commit timezone contradicts (or there is no) current
                                location: macro-region only
    none                        nothing known
A contradicting timezone never lets a carried-back country stand.
"""

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from scripts.utils.geography import REGIONS, TAXONOMY_VERSION, clean_location, get_gazetteer, resolve_location
from scripts.utils.geo.curation import load_curation
from scripts.utils.geo.signals import (
    compute_commit_signals,
    extract_bio_signals,
    extract_blog_cctld,
    tz_compatible,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
GEO_PARQUET_PATH = _PROJECT_ROOT / "data" / "enriched" / "contributor_geography.parquet"
REVIEW_QUEUE_PATH = _PROJECT_ROOT / "data" / "enriched" / "geo_review_queue.csv"

Candidate = Tuple[str, Optional[str], float, Optional[str]]   # (source, iso2, confidence, as_of)


def as_of_t1() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def choose(candidates: Iterable[Candidate]) -> Candidate:
    """The first candidate (in priority order) naming a known country, else ("none", None, 0, None)."""
    gaz = get_gazetteer()
    return next((c for c in candidates if c[1] in gaz.countries_by_iso2), ("none", None, 0.0, None))


# ---------------------------------------------------------------------------------------------
# Current location
# ---------------------------------------------------------------------------------------------

def resolve_current(
    df_unified: pd.DataFrame,
    commit_signals: Dict[str, Dict[str, Any]],
    overrides: Dict[str, Dict[str, Any]],
    legacy_hints: Dict[str, str],
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """One geo_* row per contributor, plus the review-queue rows."""
    gaz = get_gazetteer()
    t1 = as_of_t1()
    out_rows: List[Dict[str, Any]] = []
    review_queue: List[Dict[str, Any]] = []

    for row in df_unified.itertuples(index=False):
        uuid = row.uuid
        raw_loc = clean_location(getattr(row, "github_location", None))
        authored = int(getattr(row, "authored_commits", 0) or 0)
        fetched_at = getattr(row, "github_profile_fetched_at", None)
        profile_date = str(fetched_at)[:10] if fetched_at else None
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
        ov = overrides.get(uuid)
        source, iso2, conf, as_of = choose([
            ("override", ov["iso2"] if ov else None, 1.0, (ov or {}).get("as_of")),
            ("github_location", gh_iso, gh_res.confidence if gh_res.status in ("resolved", "multi") else 0.6, profile_date),
            ("bio", bio_based, 0.6, profile_date),
            ("email_tld", sig.get("email_iso2"), 0.55, t1),
            ("blog_tld", extract_blog_cctld(getattr(row, "github_blog", None)), 0.45, profile_date),
            ("flag", bio_flag, 0.4, profile_date),
        ])
        meta = gaz.countries_by_iso2.get(iso2) if iso2 else None

        if meta:
            status = gh_res.status if source == "github_location" and gh_res.status != "ambiguous" else "resolved"
            macro, un_macro = meta.macro_region, meta.un_macro_region
        elif gh_res.status == "region_only":
            source, status, conf, as_of = "github_location", "region_only", gh_res.confidence, profile_date
            macro, un_macro = gh_res.macro_region, gh_res.un_macro_region
        elif tz_region:
            source, status, conf, as_of = "timezone", "region_only", 0.35, t1
            macro, un_macro = tz_region, tz_un
        else:
            status = gh_res.status
            macro, un_macro = "Undisclosed", "Undisclosed"

        conflicts = []
        if meta and tz_region and not tz_compatible(meta, tz_region):
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
        if conflicts or (hint and hint != iso2) or gh_res.status in ("unparsed", "ambiguous") or (authored >= 20 and not meta):
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
    return pd.DataFrame(out_rows), review_queue


def enrich_unified_geography(df_unified: pd.DataFrame, df_commits: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Returns df_unified with geo_* columns. Writes data/enriched/contributor_geography.parquet and the
    local review queue (names + locations of individuals: never under output/).
    """
    overrides, legacy_hints = load_curation(df_unified)
    commit_signals = compute_commit_signals(df_commits) if df_commits is not None else {}
    df_geo, review_queue = resolve_current(df_unified, commit_signals, overrides, legacy_hints)

    os.makedirs(GEO_PARQUET_PATH.parent, exist_ok=True)
    df_geo.to_parquet(GEO_PARQUET_PATH, index=False)
    review_queue.sort(key=lambda r: (-r["authored_commits"], r["uuid"]))
    fields = ["uuid", "display_name", "github_login", "authored_commits", "github_location_raw", "resolved_iso2",
              "geo_source", "geo_status", "conflict", "tz_signature", "legacy_hint_iso2"]
    with open(REVIEW_QUEUE_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(review_queue)

    df_unified = df_unified.drop(columns=[c for c in df_unified.columns if c.startswith("geo_")])
    df_unified = df_unified.merge(df_geo, on="uuid", how="left")
    _print_kpis(df_unified, commit_signals, len(review_queue))
    return df_unified


def _print_kpis(df: pd.DataFrame, commit_signals: Dict[str, Dict[str, Any]], n_review: int) -> None:
    gaz = get_gazetteer()
    n_total = len(df)
    commits = df["authored_commits"].fillna(0)
    total_commits = max(1, commits.sum())
    has_country = df["geo_country_iso2"].notna()
    has_region = df["geo_macro_region"] != "Undisclosed"
    top100 = df.assign(_c=commits).sort_values("_c", ascending=False).head(100)

    agree = n_cmp = 0
    for uuid, iso2, src in zip(df["uuid"], df["geo_country_iso2"], df["geo_source"]):
        tz = commit_signals.get(uuid, {}).get("tz_region")
        if tz and src == "github_location" and iso2 in gaz.countries_by_iso2:
            n_cmp += 1
            agree += tz_compatible(gaz.countries_by_iso2[iso2], tz)

    print(
        f"  🌍 Geography (taxonomy v{TAXONOMY_VERSION}):\n"
        f"     • Country known: {has_country.sum():,} / {n_total:,} devs ({commits[has_country].sum() / total_commits:.1%} of authored commits)\n"
        f"     • Region known:  {has_region.sum():,} / {n_total:,} devs ({commits[has_region].sum() / total_commits:.1%} of authored commits)\n"
        f"     • Top-100 committers with a country: {top100['geo_country_iso2'].notna().sum()} / 100\n"
        f"     • Sources: {df['geo_source'].value_counts().to_dict()}\n"
        f"     • Unparsed locations: {(df['geo_status'] == 'unparsed').sum()} | conflicts: {int(df['geo_conflict'].sum())}"
        f" | review queue: {n_review} rows -> {REVIEW_QUEUE_PATH.relative_to(_PROJECT_ROOT)}\n"
        f"     • Timezone region agrees with GitHub location: {agree}/{n_cmp} ({agree / max(1, n_cmp):.1%})"
    )


# ---------------------------------------------------------------------------------------------
# Location per year
# ---------------------------------------------------------------------------------------------

_BASIS_CONF = {"carried_back_tz_consistent": 0.9, "carried_back_unverified": 0.6}


def _str(v) -> Optional[str]:
    """A non-empty string, else None (parquet nulls come back as NaN or None)."""
    return v if isinstance(v, str) and v else None


def resolve_yearly(
    person_years: pd.DataFrame,
    current: pd.DataFrame,
    tz_yearly: pd.DataFrame,
    email_yearly: pd.DataFrame,
    profile_years: pd.DataFrame,
    current_year: int,
) -> pd.DataFrame:
    """
    person_years   uuid, year (every year to attribute)
    current        resolve_current output (uuid, geo_country_iso2, geo_macro_region, geo_un_macro_region,
                   geo_confidence, geo_source)
    tz_yearly      compute_tz_yearly output, keyed canonical_id (= uuid), year
    email_yearly   compute_email_country_yearly output
    profile_years  uuid, year, location_raw: the last profile snapshot fetched in that year
    """
    gaz = get_gazetteer()
    cur = current.set_index("uuid")
    tz = tz_yearly.rename(columns={"canonical_id": "uuid"}).set_index(["uuid", "year"])
    em = email_yearly.rename(columns={"canonical_id": "uuid"}).set_index(["uuid", "year"])["email_iso2"]
    prof = profile_years.set_index(["uuid", "year"])["location_raw"]

    def region_of(iso2):
        m = gaz.countries_by_iso2[iso2]
        return m.macro_region, m.un_macro_region

    rows = []
    for uuid, year in person_years[["uuid", "year"]].drop_duplicates().itertuples(index=False):
        key = (uuid, year)
        tz_row = tz.loc[key] if key in tz.index else None
        tz_region = _str(tz_row["tz_region"]) if tz_row is not None else None    # NaN is truthy
        tz_un = _str(tz_row["tz_un_region"]) if tz_row is not None else None
        c = cur.loc[uuid] if uuid in cur.index else None
        cur_iso = _str(c["geo_country_iso2"]) if c is not None else None
        cur_region = (_str(c["geo_macro_region"]) or "Undisclosed") if c is not None else "Undisclosed"
        cur_conf = float(c["geo_confidence"]) if c is not None else 0.0

        def fits(iso2=None, region=None):
            if not tz_region:
                return True
            return tz_compatible(gaz.countries_by_iso2[iso2], tz_region) if iso2 else region == tz_region

        basis, iso2, region, un_region, conf, conflict = "none", None, "Undisclosed", "Undisclosed", 0.0, False

        prof_res = resolve_location(clean_location(prof.get(key))) if key in prof.index else None
        prof_iso = prof_res.iso2 if prof_res is not None and prof_res.status in ("resolved", "multi") else None
        email_iso = em.get(key) if key in em.index else None

        if year >= current_year and c is not None and cur_region != "Undisclosed":
            basis, iso2, conf = "current", cur_iso, cur_conf
            region, un_region = cur_region, c["geo_un_macro_region"]
            conflict = bool(cur_iso and not fits(cur_iso))
        elif prof_iso:
            basis, iso2, conf, conflict = "observed_profile", prof_iso, prof_res.confidence, not fits(prof_iso)
        elif email_iso and fits(email_iso):
            basis, iso2, conf = "observed_email", email_iso, 0.55
        elif cur_region != "Undisclosed" and fits(cur_iso, cur_region):
            basis = "carried_back_tz_consistent" if tz_region else "carried_back_unverified"
            iso2, conf = cur_iso, cur_conf * _BASIS_CONF[basis]
            region, un_region = cur_region, c["geo_un_macro_region"]
        elif tz_region:
            basis, region, un_region, conf = "tz_only", tz_region, tz_un, 0.35

        if iso2 and basis != "current":
            region, un_region = region_of(iso2)
        rows.append({
            "uuid": uuid, "year": int(year),
            "geo_country_iso2": iso2, "geo_macro_region": region if region in REGIONS else "Undisclosed",
            "geo_un_macro_region": un_region, "basis": basis, "confidence": round(conf, 2),
            "tz_region": tz_region, "conflict": bool(conflict),
        })
    return pd.DataFrame(rows)
