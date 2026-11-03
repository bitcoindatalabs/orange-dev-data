"""
Bus factor: the smallest number of people who together authored >= 50% of
bitcoin/bitcoin commits in a period.

- Authored (non-merge) commits only: a merge records who pressed the button, not who wrote code.
- Each commit counted once (commits_resolved has one row per commit per code category).
- Headline: trailing 12 months ending at the weekly anchor (Sunday 23:59:59 UTC).
- Historical: complete calendar years, then the trailing-12-month window as the final point.
"""
import json
import os
import sys

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from scripts.utils.twib_data import get_week_close_timestamp  # noqa: E402

COMMITS_FILE = os.path.join(ROOT_DIR, "data", "enriched", "commits_resolved.parquet")
OUTPUT_FILE = os.path.join(ROOT_DIR, "output", "tracker", "stats_bus_factor.json")
CORE_REPO = "bitcoin/bitcoin"


def bus_factor(authors: pd.Series):
    """authors: one row per commit (identity of the author). Returns (factor, top identities, people)."""
    counts = authors.value_counts()
    if counts.empty:
        return 0, [], 0
    cumulative = counts.cumsum()
    factor = int((cumulative < counts.sum() / 2.0).sum()) + 1
    return factor, list(counts.index[:factor]), int(len(counts))


def calculate_bus_factor():
    commits = pd.read_parquet(
        COMMITS_FILE,
        columns=["hash", "repository_name", "date_utc", "is_merge", "canonical_id", "canonical_name", "author_name"],
    )
    commits = commits[(commits["repository_name"] == CORE_REPO) & ~commits["is_merge"]]
    commits = commits.drop_duplicates("hash")
    commits["date_utc"] = pd.to_datetime(commits["date_utc"], utc=True)
    commits["who"] = commits["canonical_id"].fillna(commits["author_name"])
    names = (commits.dropna(subset=["canonical_name"]).drop_duplicates("who")
             .set_index("who")["canonical_name"].to_dict())

    anchor = get_week_close_timestamp()
    commits = commits[commits["date_utc"] <= anchor]

    window = commits[commits["date_utc"] > anchor - pd.Timedelta(days=365)]
    headline, top_ids, _ = bus_factor(window["who"])

    historical_x, historical_bf, historical_people = [], [], []
    for year, grp in commits[commits["date_utc"].dt.year < anchor.year].groupby(commits["date_utc"].dt.year):
        f, _, people = bus_factor(grp["who"])
        historical_x.append(str(year))
        historical_bf.append(f)
        historical_people.append(people)

    # Final point = the headline window, so the page's "vs previous" compares it with last full year
    historical_x.append("Last 12 mo")
    historical_bf.append(headline)
    historical_people.append(int(window["who"].nunique()))

    output_data = {
        "headline": {
            "bus_factor": headline,
            "window": "trailing_12_months",
            "period": f"{(anchor - pd.Timedelta(days=365)).strftime('%Y-%m-%d')} to {anchor.strftime('%Y-%m-%d')}",
            "top_contributors": [names.get(i, i) for i in top_ids],
            "basis": "authored (non-merge) bitcoin/bitcoin commits",
        },
        "historical": {
            "xAxis": historical_x,
            "bus_factor": historical_bf,
            "total_contributors": historical_people,
        },
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated {OUTPUT_FILE}")
    print(f"Bus factor (trailing 12 months to {anchor.date()}): {headline}")
    print(f"Top contributors: {output_data['headline']['top_contributors']}")


if __name__ == "__main__":
    calculate_bus_factor()
