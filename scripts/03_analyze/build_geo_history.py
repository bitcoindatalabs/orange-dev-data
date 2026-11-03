"""
build_geo_history.py — Phase 3: activity events and contributor location per year.

Runs after unify_contributors.py (needs contributors_unified.parquet with geo_* columns and
contributor_geography.parquet). All outputs are private (data/enriched/, gitignored); only
k-anonymised aggregates built from them are published (scripts/04_deliver/geo_artifacts.py).

Outputs:
  data/enriched/activity_events.parquet
      One row per activity event in the Core repos (bitcoin/bitcoin, gui, secp256k1), cut at T-1:
      uuid, ts, year, event_type (commit | pr_opened | review), repository_name, ref,
      tz_offset_minutes (commits). Commits are authored (non-merge), each hash once per person.
  data/enriched/contributor_tz_yearly.parquet
      Commit-timezone macro-region per contributor per year (DST-aware; see
      scripts/utils/geo/signals.compute_tz_yearly). Uses commits in every tracked repo, since
      any commit is evidence of where its author was.
  data/enriched/contributor_location_yearly.parquet
      Location per contributor per year with its basis (scripts/utils/geo/attribution.resolve_yearly),
      for every active year and the contributor's cohort year.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.utils.geo.attribution import resolve_yearly  # noqa: E402
from scripts.utils.geo.policy import CORE_REPOS, REVIEW_EVENT_TYPES  # noqa: E402
from scripts.utils.geo.signals import (  # noqa: E402
    compute_commit_signals,
    compute_email_country_yearly,
    compute_tz_yearly,
)

ENRICHED = _PROJECT_ROOT / "data" / "enriched"
UNIFIED_PATH = ENRICHED / "contributors_unified.parquet"
GEO_PATH = ENRICHED / "contributor_geography.parquet"
COMMITS_PATH = ENRICHED / "commits_resolved.parquet"
PRS_PATH = ENRICHED / "enriched_prs.parquet"
REVIEWS_PATH = ENRICHED / "enriched_reviews.parquet"
SNAPSHOTS_PATH = _PROJECT_ROOT / "data" / "raw" / "github_profile_snapshots.parquet"

EVENTS_OUT = ENRICHED / "activity_events.parquet"
TZ_YEARLY_OUT = ENRICHED / "contributor_tz_yearly.parquet"
LOCATION_YEARLY_OUT = ENRICHED / "contributor_location_yearly.parquet"


def t1_cutoff() -> pd.Timestamp:
    """End of yesterday, UTC: metrics never include the partial current day."""
    y = datetime.now(timezone.utc).date() - timedelta(days=1)
    return pd.Timestamp(year=y.year, month=y.month, day=y.day, hour=23, minute=59, second=59, tz="UTC")


def _require(path: Path) -> None:
    if not path.exists():
        sys.exit(f"Error: {path} not found (run the earlier pipeline phases first).")


def build_activity_events(commits: pd.DataFrame, known: set, cutoff: pd.Timestamp) -> pd.DataFrame:
    c = commits[commits["repository_name"].isin(CORE_REPOS) & ~commits["is_merge"].fillna(False).astype(bool)]
    c = c.dropna(subset=["canonical_id"]).drop_duplicates(["canonical_id", "hash"])
    ev_commits = pd.DataFrame({
        "uuid": c["canonical_id"].astype(str), "ts": pd.to_datetime(c["date_utc"], utc=True, errors="coerce"),
        "event_type": "commit", "repository_name": c["repository_name"], "ref": c["hash"],
        "tz_offset_minutes": c["timezone_offset_minutes"],
    })

    prs = pd.read_parquet(PRS_PATH, columns=["repository_name", "pr_number", "uuid", "created_at"])
    prs = prs[prs["repository_name"].isin(CORE_REPOS)].dropna(subset=["uuid"])
    ev_prs = pd.DataFrame({
        "uuid": prs["uuid"].astype(str), "ts": pd.to_datetime(prs["created_at"], utc=True, errors="coerce"),
        "event_type": "pr_opened", "repository_name": prs["repository_name"], "ref": prs["pr_number"].astype(str),
        "tz_offset_minutes": pd.NA,
    })

    rev = pd.read_parquet(REVIEWS_PATH, columns=["repository_name", "pr_number", "uuid", "timestamp", "event_type"])
    rev = rev[rev["repository_name"].isin(CORE_REPOS) & rev["event_type"].isin(REVIEW_EVENT_TYPES)].dropna(subset=["uuid"])
    ev_rev = pd.DataFrame({
        "uuid": rev["uuid"].astype(str), "ts": pd.to_datetime(rev["timestamp"], utc=True, errors="coerce"),
        "event_type": "review", "repository_name": rev["repository_name"], "ref": rev["pr_number"].astype(str),
        "tz_offset_minutes": pd.NA,
    })

    ev = pd.concat([ev_commits, ev_prs, ev_rev], ignore_index=True)
    dropped_unknown = int((~ev["uuid"].isin(known)).sum())
    ev = ev[ev["uuid"].isin(known) & ev["ts"].notna() & (ev["ts"] <= cutoff)].copy()
    ev["year"] = ev["ts"].dt.year.astype(int)
    ev["tz_offset_minutes"] = ev["tz_offset_minutes"].astype("Int64")
    print(f"  activity_events: {len(ev):,} events "
          f"({ev['event_type'].value_counts().to_dict()}); {dropped_unknown:,} from bots / unknown ids dropped")
    return ev[["uuid", "ts", "year", "event_type", "repository_name", "ref", "tz_offset_minutes"]]


def profile_locations_by_year(unified: pd.DataFrame) -> pd.DataFrame:
    """Last profile snapshot fetched in each year, per contributor: uuid, year, location_raw."""
    cols = ["uuid", "year", "location_raw"]
    if not SNAPSHOTS_PATH.exists():
        print(f"  [warn] {SNAPSHOTS_PATH} not found: no observed profile history")
        return pd.DataFrame(columns=cols)
    snaps = pd.read_parquet(SNAPSHOTS_PATH, columns=["github_id", "fetched_at", "location"])
    gid_to_uuid = {str(g): u for g, u in zip(unified["github_id_final"], unified["uuid"]) if isinstance(g, str)}
    snaps["uuid"] = snaps["github_id"].astype(str).map(gid_to_uuid)
    snaps["fetched"] = pd.to_datetime(snaps["fetched_at"], utc=True, errors="coerce")
    snaps = snaps.dropna(subset=["uuid", "fetched"]).sort_values("fetched")
    snaps["year"] = snaps["fetched"].dt.year.astype(int)
    last = snaps.drop_duplicates(["uuid", "year"], keep="last").rename(columns={"location": "location_raw"})
    return last[cols]


def main() -> None:
    for p in (UNIFIED_PATH, GEO_PATH, COMMITS_PATH, PRS_PATH, REVIEWS_PATH):
        _require(p)
    cutoff = t1_cutoff()
    print(f"Building geographic history (cutoff {cutoff:%Y-%m-%d}, T-1)...")

    unified = pd.read_parquet(UNIFIED_PATH, columns=["uuid", "github_id_final", "first_commit", "global_first_active"])
    known = set(unified["uuid"])
    commits = pd.read_parquet(COMMITS_PATH, columns=[
        "hash", "repository_name", "date_utc", "timezone_offset_minutes", "is_merge", "author_email", "canonical_id"])
    commits = commits[pd.to_datetime(commits["date_utc"], utc=True, errors="coerce") <= cutoff]

    events = build_activity_events(commits, known, cutoff)
    events.to_parquet(EVENTS_OUT, index=False)

    alltime = compute_commit_signals(commits)
    tz_yearly = compute_tz_yearly(commits, alltime)
    tz_yearly.to_parquet(TZ_YEARLY_OUT, index=False)
    print(f"  contributor_tz_yearly: {len(tz_yearly):,} person-years; status {tz_yearly['status'].value_counts().to_dict()}")

    # Years to attribute: every active year, plus the cohort year (first commit, else first activity).
    cohort = pd.to_datetime(unified["first_commit"], errors="coerce", utc=True).dt.year.combine_first(
        pd.to_datetime(unified["global_first_active"], errors="coerce", utc=True).dt.year)
    person_years = pd.concat([
        events[["uuid", "year"]],
        pd.DataFrame({"uuid": unified["uuid"], "year": cohort}).dropna(),
    ]).drop_duplicates()
    person_years["year"] = person_years["year"].astype(int)
    person_years = person_years[person_years["year"] <= cutoff.year]

    current = pd.read_parquet(GEO_PATH)
    yearly = resolve_yearly(
        person_years, current, tz_yearly, compute_email_country_yearly(commits),
        profile_locations_by_year(pd.read_parquet(UNIFIED_PATH, columns=["uuid", "github_id_final"])),
        current_year=cutoff.year,
    )
    yearly.to_parquet(LOCATION_YEARLY_OUT, index=False)
    _print_kpis(yearly, events)


def _print_kpis(yearly: pd.DataFrame, events: pd.DataFrame) -> None:
    commits = events[events["event_type"] == "commit"].groupby(["uuid", "year"]).size().rename("commits")
    active = events.groupby(["uuid", "year"]).size().rename("events").reset_index()
    df = active.merge(yearly, on=["uuid", "year"], how="left").merge(commits.reset_index(), on=["uuid", "year"], how="left")
    df["commits"] = df["commits"].fillna(0)
    known = df["geo_macro_region"].fillna("Undisclosed") != "Undisclosed"
    print(f"  contributor_location_yearly: {len(yearly):,} person-years; basis {yearly['basis'].value_counts().to_dict()}"
          f"; tz conflicts {int(yearly['conflict'].sum())}")
    print("  Coverage of active person-years (region known: devs | share of commits):")
    for y in sorted(df["year"].unique())[-12:]:
        d = df[df["year"] == y]
        k = known[d.index]
        print(f"     {y}: {k.sum():>4}/{len(d):<4} devs | {d.loc[k, 'commits'].sum() / max(1, d['commits'].sum()):.0%} of commits")


if __name__ == "__main__":
    main()
