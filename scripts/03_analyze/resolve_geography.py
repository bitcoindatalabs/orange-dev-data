"""
resolve_geography.py — current geographic attribution per contributor, standalone.

unify_contributors.py runs the same step (scripts.utils.geo.attribution.enrich_unified_geography)
as part of the grand join; this script re-runs it on an existing contributors_unified.parquet.
Policy and signals: scripts/utils/geo/.

Produces:
- geo_* columns in data/enriched/contributors_unified.parquet
- data/enriched/contributor_geography.parquet (keyed by uuid)
- data/enriched/geo_review_queue.csv (local only, ranked by authored commits, for curation)
"""

import sys
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

from scripts.utils.geo.attribution import enrich_unified_geography  # noqa: E402


def main() -> None:
    unified_path = _PROJECT_ROOT / "data" / "enriched" / "contributors_unified.parquet"
    commits_path = _PROJECT_ROOT / "data" / "enriched" / "commits_resolved.parquet"
    if not unified_path.exists():
        sys.exit(f"Error: {unified_path} not found.")

    df_unified = pd.read_parquet(unified_path)
    df_commits = pd.read_parquet(commits_path) if commits_path.exists() else None
    df_unified = enrich_unified_geography(df_unified, df_commits)
    df_unified.to_parquet(unified_path, index=False)
    print(f"✅ Updated {unified_path} with geo_* columns.")


if __name__ == "__main__":
    main()
