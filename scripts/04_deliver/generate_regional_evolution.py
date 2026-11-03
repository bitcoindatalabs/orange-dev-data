"""
generate_regional_evolution.py — Generates regional evolution stats over contributor cohorts,
emerging region cohort stats, and global geographic decentralization metrics (1/HHI, Nakamoto Coefficient).

Deliverable artifacts:
- output/tracker/stats_regional_evolution.json
- output/tracker/stats_emerging_regions.json
- output/tracker/stats_geo_decentralization.json

Consumes: data/enriched/contributors_unified.parquet (pre-enriched in Phase 3 with `geo_*` columns)
Domain taxonomy: scripts.utils.geography
"""

import json
import os
import sys
import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Ensure project root is on the path so `scripts.utils` is importable
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "../.."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.utils.geography import REGIONS, TAXONOMY_VERSION, get_gazetteer

UNIFIED_FILE = os.path.join(_PROJECT_ROOT, "data", "enriched", "contributors_unified.parquet")
OUTPUT_FILE = os.path.join(_PROJECT_ROOT, "output", "tracker", "stats_regional_evolution.json")
EMERGING_OUTPUT_FILE = os.path.join(_PROJECT_ROOT, "output", "tracker", "stats_emerging_regions.json")
DECENTRALIZATION_OUTPUT_FILE = os.path.join(_PROJECT_ROOT, "output", "tracker", "stats_geo_decentralization.json")

# A country is named in published lists only with at least K_MIN contributors (a 2-person
# country with thousands of commits identifies the person). Concentration metrics still use all.
K_MIN = 5
ACTIVE_STATUSES = {"Active", "New", "Rising"}


def _compute_hhi_and_nakamoto(shares: pd.Series, headcount: pd.Series) -> dict:
    """Computes Effective Number of Countries (1/HHI), HHI, and Nakamoto Coefficient (>50% share).
    `headcount` (contributors per country) decides which countries may be named in top_countries."""
    s = shares[shares > 0].sort_values(ascending=False)
    total = s.sum()
    if total <= 0 or len(s) == 0:
        return {"countries_represented": 0, "effective_countries_1_over_hhi": 0.0, "hhi": 0.0,
                "nakamoto_coefficient": 0, "top_countries": []}
    probs = s / total
    hhi = float((probs ** 2).sum())
    eff = round(1.0 / hhi, 2) if hhi > 0 else 0.0
    cumsum = probs.cumsum()
    nakamoto = int((cumsum <= 0.50).sum()) + 1
    named = [idx for idx in probs.index if headcount.get(idx, 0) >= K_MIN]
    top_list = [
        {"country": str(idx), "share_pct": round(float(probs[idx] * 100), 2), "raw_total": int(s[idx])}
        for idx in named[:10]
    ]
    return {
        "countries_represented": int(len(s)),
        "effective_countries_1_over_hhi": eff,
        "hhi": round(hhi, 4),
        "nakamoto_coefficient": nakamoto,
        "top_countries": top_list,
    }


def main():
    if not os.path.exists(UNIFIED_FILE):
        print(f"Error: {UNIFIED_FILE} not found. Run unify_contributors.py first.")
        sys.exit(1)

    df = pd.read_parquet(UNIFIED_FILE)

    # Derive cohort year: earliest commit year, falling back to earliest overall activity year
    first_commit = pd.to_datetime(df["first_commit"], errors="coerce")
    global_first = pd.to_datetime(df["global_first_active"], errors="coerce")
    cohort_year = first_commit.dt.year.combine_first(global_first.dt.year)

    # Filter to contributors with a known cohort
    valid_mask = cohort_year.notna()
    cohort_df = df[valid_mask].copy()
    cohort_df["cohort_year"] = cohort_year[valid_mask].astype(int)

    # Regions come from the Phase 3 geo_* columns; delivery never parses raw location strings.
    if "geo_macro_region" not in cohort_df.columns:
        print("Error: contributors_unified has no geo_* columns. Run unify_contributors.py first.")
        sys.exit(1)
    cohort_df["region"] = cohort_df["geo_macro_region"].fillna("Undisclosed")

    # 1. Regional Evolution Artifact (`stats_regional_evolution.json`)
    counts = (
        cohort_df.groupby(["cohort_year", "region"])
        .size()
        .unstack(fill_value=0)
    )

    sorted_years = sorted(counts.index.tolist())

    series = []
    for r in REGIONS:
        series.append({
            "name": r,
            "type": "line",
            "stack": "total",
            "areaStyle": {},
            "data": [
                int(counts.loc[y, r]) if (y in counts.index and r in counts.columns) else 0
                for y in sorted_years
            ],
        })

    n_total = len(df)
    n_region_known = int((cohort_df["region"] != "Undisclosed").sum())
    total_commits = int(df["authored_commits"].sum()) if "authored_commits" in df.columns else 0
    known_region_commits = int(
        cohort_df.loc[cohort_df["region"] != "Undisclosed", "authored_commits"].sum()
    ) if "authored_commits" in cohort_df.columns else 0

    output = {
        "xAxis": [str(y) for y in sorted_years],
        "series": series,
        "coverage": {
            "devs_known_region": n_region_known,
            "devs_total": n_total,
            "commit_weighted_known": round(known_region_commits / max(1, total_commits), 4),
            "taxonomy_version": TAXONOMY_VERSION,
        },
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Generated {OUTPUT_FILE} with consolidated categories")

    # 2. Emerging Regions Artifact (`stats_emerging_regions.json`)
    # Consumed by `charts-health.js` -> `loadEmergingRegions()`
    emerging_years = [y for y in sorted_years if y >= 2012]
    emerging_output = {
        "xAxis": [str(y) for y in emerging_years],
        "series": [
            {
                "name": "Africa",
                "type": "bar",
                "data": [
                    int(counts.loc[y, "Africa"]) if (y in counts.index and "Africa" in counts.columns) else 0
                    for y in emerging_years
                ],
            },
            {
                "name": "Latin America",
                "type": "bar",
                "data": [
                    int(counts.loc[y, "Latin America"]) if (y in counts.index and "Latin America" in counts.columns) else 0
                    for y in emerging_years
                ],
            },
        ],
        "coverage": output["coverage"],
    }
    with open(EMERGING_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(emerging_output, f, indent=2)
    print(f"✅ Generated {EMERGING_OUTPUT_FILE}")

    # 3. Geographic Decentralization & Dual-Weighting Artifact (`stats_geo_decentralization.json`)
    gaz = get_gazetteer()
    country_col = df["geo_country_iso2"].map(lambda c: gaz.countries_by_iso2[c].display_name if c in gaz.countries_by_iso2 else None)

    df_known_ctry = df[country_col.notna()].copy()
    df_known_ctry["country"] = country_col[country_col.notna()]

    # Lens A: All-Time Resolved Contributors (Headcount vs Commit-Weighted)
    all_headcount = df_known_ctry.groupby("country").size()
    all_commits = df_known_ctry.groupby("country")["authored_commits"].sum()

    # Lens B: Active Contributors (activity_status Active / New / Rising)
    active_mask = df_known_ctry["activity_status"].isin(ACTIVE_STATUSES) if "activity_status" in df_known_ctry.columns         else pd.Series(False, index=df_known_ctry.index)
    df_active_ctry = df_known_ctry[active_mask]
    active_headcount = df_active_ctry.groupby("country").size()
    active_commits = df_active_ctry.groupby("country")["modern_authored_commits"].sum() if "modern_authored_commits" in df_active_ctry.columns else df_active_ctry.groupby("country")["authored_commits"].sum()

    decentralization = {
        "taxonomy_version": TAXONOMY_VERSION,
        "coverage": {
            "devs_known_country": int(len(df_known_ctry)),
            "devs_known_region": n_region_known,
            "devs_total": n_total,
            "commit_weighted_known_country": round(
                float(df_known_ctry["authored_commits"].sum()) / max(1, total_commits), 4
            ),
            "commit_weighted_known_region": round(known_region_commits / max(1, total_commits), 4),
        },
        "all_time": {
            "headcount": _compute_hhi_and_nakamoto(all_headcount, all_headcount),
            "commit_weighted": _compute_hhi_and_nakamoto(all_commits, all_headcount),
        },
        "active_modern": {
            "headcount": _compute_hhi_and_nakamoto(active_headcount, active_headcount),
            "commit_weighted": _compute_hhi_and_nakamoto(active_commits, active_headcount),
        },
    }
    with open(DECENTRALIZATION_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(decentralization, f, indent=2)
    print(f"✅ Generated {DECENTRALIZATION_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
