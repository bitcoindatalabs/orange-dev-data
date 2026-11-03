"""The private curation file: metadata/geo/curated_geography.json (gitignored, hand-edited)."""

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

from scripts.utils.geography import get_gazetteer

CURATION_PATH = Path(__file__).resolve().parents[3] / "metadata" / "geo" / "curated_geography.json"


def load_curation(df_unified: pd.DataFrame) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    """
    Gitignored because it names a country per person and this repo is public. Never written by the
    pipeline. Returns:

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
