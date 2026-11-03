"""
geo_artifacts.py — Phase 4: every published geographic artifact, from Phase 3 geo tables only
(delivery never parses raw location strings). All outputs are aggregates; a country, or a region's
activity totals, is published only for cells with at least K_MIN contributors.

Current location (contributors_unified.parquet, geo_* columns):
  output/tracker/stats_geography.json            top countries by headcount and by authored commits
  output/tracker/stats_geo_decentralization.json  1/HHI and Nakamoto coefficient by country, all-time
                                                  and active contributors

Location per year (build_geo_history.py: activity_events, contributor_location_yearly):
  output/tracker/stats_regional_evolution.json   new contributors per cohort year by the region they
                                                  were in that year (not where they live today)
  output/tracker/stats_emerging_regions.json     the Africa and Latin America cohort series
  output/tracker/stats_geo_trends.json           active contributors, authored commits and reviews per
                                                  year by region and country, coverage and basis per
                                                  year, and decentralization per year
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.utils.geography import REGIONS, TAXONOMY_VERSION, get_gazetteer  # noqa: E402
from scripts.utils.geo.policy import ACTIVE_STATUSES, CORE_REPOS, K_MIN  # noqa: E402

ENRICHED = os.path.join(_PROJECT_ROOT, "data", "enriched")
UNIFIED_FILE = os.path.join(ENRICHED, "contributors_unified.parquet")
EVENTS_FILE = os.path.join(ENRICHED, "activity_events.parquet")
YEARLY_FILE = os.path.join(ENRICHED, "contributor_location_yearly.parquet")

OUT_DIR = os.path.join(_PROJECT_ROOT, "output", "tracker")
GEOGRAPHY_FILE = os.path.join(OUT_DIR, "stats_geography.json")
DECENTRALIZATION_FILE = os.path.join(OUT_DIR, "stats_geo_decentralization.json")
EVOLUTION_FILE = os.path.join(OUT_DIR, "stats_regional_evolution.json")
EMERGING_FILE = os.path.join(OUT_DIR, "stats_emerging_regions.json")
TRENDS_FILE = os.path.join(OUT_DIR, "stats_geo_trends.json")

BASES = ["current", "observed_profile", "observed_email", "carried_back_tz_consistent",
         "carried_back_unverified", "tz_only", "none"]


def _write(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {os.path.relpath(path, _PROJECT_ROOT)}")


def concentration(shares: pd.Series, headcount: pd.Series, top_n: int = 10) -> dict:
    """Effective number of countries (1/HHI), HHI and Nakamoto coefficient (fewest countries holding
    > 50%). All countries count; only those with >= K_MIN contributors are named in top_countries."""
    s = shares[shares > 0].sort_values(ascending=False)
    if s.sum() <= 0:
        return {"countries_represented": 0, "effective_countries_1_over_hhi": 0.0, "hhi": 0.0,
                "nakamoto_coefficient": 0, "top_countries": []}
    probs = s / s.sum()
    hhi = float((probs ** 2).sum())
    named = [i for i in probs.index if headcount.get(i, 0) >= K_MIN][:top_n]
    return {
        "countries_represented": int(len(s)),
        "effective_countries_1_over_hhi": round(1.0 / hhi, 2),
        "hhi": round(hhi, 4),
        "nakamoto_coefficient": int((probs.cumsum() <= 0.50).sum()) + 1,
        "top_countries": [{"country": str(i), "share_pct": round(float(probs[i] * 100), 2), "raw_total": int(s[i])}
                          for i in named],
    }


# ---------------------------------------------------------------------------------------------
# Current location
# ---------------------------------------------------------------------------------------------

def current_artifacts(df: pd.DataFrame) -> None:
    gaz = get_gazetteer()
    total_devs, total_commits = len(df), int(df["authored_commits"].sum())
    known_country = df[df["geo_country_iso2"].notna()].copy()
    known_country["is_active"] = known_country["activity_status"].isin(ACTIVE_STATUSES)
    known_region = df["geo_macro_region"].fillna("Undisclosed") != "Undisclosed"

    # stats_geography.json — charts-health.js reads data[].name / data[].value
    grouped = known_country.groupby("geo_country_iso2", as_index=False).agg(
        value=("uuid", "count"), authored_commits=("authored_commits", "sum"), active_devs=("is_active", "sum"))
    small, grouped = grouped[grouped["value"] < K_MIN], grouped[grouped["value"] >= K_MIN]

    def record(r, weight):
        m = gaz.countries_by_iso2[r.geo_country_iso2]
        rec = {"name": m.display_name, "iso2": m.iso2, "iso3": m.iso3, "flag": m.flag, "macro_region": m.macro_region}
        if weight == "headcount":
            rec.update(value=int(r.value), active_devs=int(r.active_devs), authored_commits=int(r.authored_commits))
        else:
            rec.update(value=int(r.authored_commits), contributors=int(r.value), active_devs=int(r.active_devs))
        return rec

    _write(GEOGRAPHY_FILE, {
        "data": [record(r, "headcount") for r in
                 grouped.sort_values(["value", "authored_commits"], ascending=False).head(15).itertuples(index=False)],
        "data_commit_weighted": [record(r, "commits") for r in
                                 grouped.sort_values(["authored_commits", "value"], ascending=False).head(15).itertuples(index=False)],
        "other_small_countries": {
            "countries": int(len(small)), "contributors": int(small["value"].sum()),
            "authored_commits": int(small["authored_commits"].sum()),
            "rule": f"countries with fewer than {K_MIN} contributors are not listed individually",
        },
        "coverage": {
            "devs_known": int(len(known_country)), "devs_total": total_devs,
            "commit_weighted_known": round(int(known_country["authored_commits"].sum()) / max(1, total_commits), 4),
            "countries_total": int(len(grouped) + len(small)), "taxonomy_version": TAXONOMY_VERSION,
        },
    })

    # stats_geo_decentralization.json
    known_country["country"] = known_country["geo_country_iso2"].map(lambda c: gaz.countries_by_iso2[c].display_name)
    all_head = known_country.groupby("country").size()
    active = known_country[known_country["is_active"]]
    active_head = active.groupby("country").size()
    _write(DECENTRALIZATION_FILE, {
        "taxonomy_version": TAXONOMY_VERSION,
        "coverage": {
            "devs_known_country": int(len(known_country)), "devs_known_region": int(known_region.sum()),
            "devs_total": total_devs,
            "commit_weighted_known_country": round(float(known_country["authored_commits"].sum()) / max(1, total_commits), 4),
            "commit_weighted_known_region": round(float(df.loc[known_region, "authored_commits"].sum()) / max(1, total_commits), 4),
        },
        "all_time": {
            "headcount": concentration(all_head, all_head),
            "commit_weighted": concentration(known_country.groupby("country")["authored_commits"].sum(), all_head),
        },
        "active_modern": {
            "headcount": concentration(active_head, active_head),
            "commit_weighted": concentration(active.groupby("country")["modern_authored_commits"].sum(), active_head),
        },
    })


# ---------------------------------------------------------------------------------------------
# Location per year
# ---------------------------------------------------------------------------------------------

def cohort_artifacts(df: pd.DataFrame, yearly: pd.DataFrame) -> None:
    cohort = pd.to_datetime(df["first_commit"], errors="coerce", utc=True).dt.year.combine_first(
        pd.to_datetime(df["global_first_active"], errors="coerce", utc=True).dt.year)
    c = pd.DataFrame({"uuid": df["uuid"], "year": cohort}).dropna()
    c["year"] = c["year"].astype(int)
    c = c.merge(yearly[["uuid", "year", "geo_macro_region", "basis"]], on=["uuid", "year"], how="left")
    c["region"] = c["geo_macro_region"].fillna("Undisclosed")
    counts = c.groupby(["year", "region"]).size().unstack(fill_value=0).reindex(columns=REGIONS, fill_value=0)
    years = sorted(counts.index)
    known = c["region"] != "Undisclosed"
    coverage = {
        "definition": "new contributors per cohort year (first commit, else first activity), by the region "
                      "they were in during that year",
        "devs_known_region": int(known.sum()), "devs_total": int(len(df)),
        "basis_share": {b: round(float((c.loc[known, "basis"] == b).mean()), 4) for b in BASES if b != "none"},
        "taxonomy_version": TAXONOMY_VERSION,
    }
    _write(EVOLUTION_FILE, {
        "xAxis": [str(y) for y in years],
        "series": [{"name": r, "type": "line", "stack": "total", "areaStyle": {},
                    "data": [int(counts.loc[y, r]) for y in years]} for r in REGIONS],
        "coverage": coverage,
    })
    emerging = [y for y in years if y >= 2012]
    _write(EMERGING_FILE, {
        "xAxis": [str(y) for y in emerging],
        "series": [{"name": r, "type": "bar", "data": [int(counts.loc[y, r]) for y in emerging]}
                   for r in ("Africa", "Latin America")],
        "coverage": coverage,
    })


def trend_artifact(events: pd.DataFrame, yearly: pd.DataFrame, cutoff: pd.Timestamp) -> None:
    gaz = get_gazetteer()
    per = events.pivot_table(index=["uuid", "year"], columns="event_type", values="ref", aggfunc="count", fill_value=0)
    per = per.reindex(columns=["commit", "review", "pr_opened"], fill_value=0).reset_index()
    per = per.merge(yearly, on=["uuid", "year"], how="left")
    per["region"] = per["geo_macro_region"].fillna("Undisclosed")
    per["basis"] = per["basis"].fillna("none")
    years = list(range(int(per["year"].min()), cutoff.year + 1))

    def cell(d):
        n = int(len(d))
        out = {"active_devs": n, "authored_commits": None, "reviews": None, "prs_opened": None}
        if n >= K_MIN:
            out.update(authored_commits=int(d["commit"].sum()), reviews=int(d["review"].sum()),
                       prs_opened=int(d["pr_opened"].sum()))
        return out

    by_year = {y: d for y, d in per.groupby("year")}
    empty = per.iloc[0:0]
    regions = {r: {k: [] for k in ("active_devs", "authored_commits", "reviews", "prs_opened")} for r in REGIONS}
    coverage = {k: [] for k in ("active_devs", "devs_known_region", "devs_known_country",
                                "commit_share_known_region", "review_share_known_region")}
    coverage["basis_share"] = {b: [] for b in BASES}
    countries, decentral = {}, {"headcount": {"effective_countries": [], "nakamoto": []},
                                "commit_weighted": {"effective_countries": [], "nakamoto": []}}

    for y in years:
        d = by_year.get(y, empty)
        for r in REGIONS:
            for k, v in cell(d[d["region"] == r]).items():
                regions[r][k].append(v)
        known = d["region"] != "Undisclosed"
        coverage["active_devs"].append(int(len(d)))
        coverage["devs_known_region"].append(int(known.sum()))
        coverage["devs_known_country"].append(int(d["geo_country_iso2"].notna().sum()))
        coverage["commit_share_known_region"].append(round(float(d.loc[known, "commit"].sum()) / max(1, d["commit"].sum()), 4))
        coverage["review_share_known_region"].append(round(float(d.loc[known, "review"].sum()) / max(1, d["review"].sum()), 4))
        for b in BASES:
            coverage["basis_share"][b].append(round(float((d["basis"] == b).mean()), 4) if len(d) else 0.0)

        kc = d[d["geo_country_iso2"].notna()]
        head = kc.groupby("geo_country_iso2").size()
        commits = kc.groupby("geo_country_iso2")["commit"].sum()
        for weight, shares in (("headcount", head), ("commit_weighted", commits)):
            conc = concentration(shares, head)
            decentral[weight]["effective_countries"].append(conc["effective_countries_1_over_hhi"])
            decentral[weight]["nakamoto"].append(conc["nakamoto_coefficient"])
        listed, small = [], kc[kc["geo_country_iso2"].map(head) < K_MIN]
        for iso2, g in kc[kc["geo_country_iso2"].map(head) >= K_MIN].groupby("geo_country_iso2"):
            m = gaz.countries_by_iso2[iso2]
            listed.append({"iso2": iso2, "name": m.display_name, "flag": m.flag, "macro_region": m.macro_region,
                           **cell(g)})
        listed.sort(key=lambda r: (-r["active_devs"], r["iso2"]))
        countries[str(y)] = {"listed": listed,
                             "other_small_countries": {"countries": int(small["geo_country_iso2"].nunique()), **cell(small)}}

    _write(TRENDS_FILE, {
        "generated_at": cutoff.strftime("%Y-%m-%d"),
        "taxonomy_version": TAXONOMY_VERSION,
        "years": [str(y) for y in years],
        "partial_year": {"year": str(cutoff.year), "through": cutoff.strftime("%Y-%m-%d")},
        "definitions": {
            "scope": f"Core repositories: {', '.join(CORE_REPOS)}",
            "active_dev": "contributor with at least one authored (non-merge) commit, opened PR or review "
                          "(comment or review) in the year; bots excluded",
            "location": "where the contributor was in that year: a profile or email observed that year, or the "
                        "current location carried back when that year's commit timezone agrees or is unknown. "
                        "A contradicting timezone gives the region only. See coverage.basis_share.",
            "privacy": f"countries are listed, and activity totals given, only for cells with at least {K_MIN} "
                       f"contributors; smaller cells show headcount only (totals null)",
        },
        "regions": regions,
        "countries_by_year": countries,
        "decentralization_by_year": decentral,
        "coverage": coverage,
    })


def main():
    for p in (UNIFIED_FILE, EVENTS_FILE, YEARLY_FILE):
        if not os.path.exists(p):
            sys.exit(f"Error: {p} not found. Run unify_contributors.py and build_geo_history.py first.")
    df = pd.read_parquet(UNIFIED_FILE)
    if "geo_macro_region" not in df.columns:
        sys.exit("Error: contributors_unified has no geo_* columns. Run unify_contributors.py first.")
    events = pd.read_parquet(EVENTS_FILE)
    yearly = pd.read_parquet(YEARLY_FILE)
    y = datetime.now(timezone.utc).date() - timedelta(days=1)
    cutoff = pd.Timestamp(year=y.year, month=y.month, day=y.day, tz="UTC")

    current_artifacts(df)
    cohort_artifacts(df, yearly)
    trend_artifact(events, yearly, cutoff)


if __name__ == "__main__":
    main()
