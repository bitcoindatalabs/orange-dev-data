"""
Unit tests for location history: the DST-aware yearly timezone vote and the per-year attribution
rules. Synthetic data, real gazetteer.

    python3 tests/geo/test_geo_history.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")))

from scripts.utils.geo.attribution import resolve_yearly  # noqa: E402
from scripts.utils.geo.signals import compute_email_country_yearly, compute_tz_yearly  # noqa: E402


def _commits(cid, year, spec, email="dev@example.com"):
    """spec: list of (month, offset, count)."""
    rows, i = [], 0
    for month, tz, n in spec:
        for _ in range(n):
            i += 1
            rows.append({"canonical_id": cid, "hash": f"{cid}-{year}-{i}", "date_utc": f"{year}-{month:02d}-15T12:00:00Z",
                         "timezone_offset_minutes": tz, "is_merge": False, "author_email": email})
    return rows


def test_tz_yearly():
    rows = (
        _commits("de", 2020, [(1, 60, 3), (7, 120, 3)])          # CET/CEST
        + _commits("us", 2020, [(1, -300, 3), (7, -240, 3)])     # US Eastern
        + _commits("au", 2020, [(1, 660, 3), (7, 600, 3)])       # Sydney (southern DST)
        + _commits("winter", 2020, [(1, 60, 4)])                 # fits Central Europe and West Africa
        + _commits("winter_prior", 2020, [(1, 60, 4)])
        + _commits("utc", 2020, [(1, 0, 3), (7, 0, 3)])
        + _commits("few", 2020, [(1, 60, 2)])
        + _commits("mixed", 2020, [(1, 60, 3), (1, -300, 3)])
        + _commits("transition", 2020, [(3, 60, 2), (4, 120, 2)])  # March CET, April CEST
    )
    t = compute_tz_yearly(pd.DataFrame(rows), alltime={"winter_prior": {"tz_region": "Europe"}}).set_index("canonical_id")
    expect = {
        "de": ("resolved", "Europe"), "us": ("resolved", "North America"), "au": ("resolved", "Asia Pacific"),
        "winter": ("ambiguous", None), "winter_prior": ("tiebreak", "Europe"), "utc": ("utc", None),
        "few": ("insufficient", None), "mixed": ("mixed", None), "transition": ("resolved", "Europe"),
    }
    for cid, (status, region) in expect.items():
        got = (t.loc[cid, "status"], t.loc[cid, "tz_region"] if isinstance(t.loc[cid, "tz_region"], str) else None)
        assert got == (status, region), f"{cid}: got {got}, expected {(status, region)}"
    assert t.loc["au", "tz_un_region"] == "Oceania"


def test_email_yearly():
    rows = _commits("a", 2015, [(1, 60, 2)], "x@uni-example.de") + _commits("a", 2016, [(1, 60, 2)], "x@gmail.com")
    e = compute_email_country_yearly(pd.DataFrame(rows))
    assert e.to_dict("records") == [{"canonical_id": "a", "year": 2015, "email_iso2": "DE"}], e


def test_resolve_yearly():
    cur = pd.DataFrame([
        {"uuid": u, "geo_country_iso2": iso, "geo_macro_region": reg, "geo_un_macro_region": un,
         "geo_confidence": 0.95, "geo_source": "github_location"}
        for u, iso, reg, un in [
            ("consistent", "DE", "Europe", "Europe"), ("unverified", "DE", "Europe", "Europe"),
            ("moved", "DE", "Europe", "Europe"), ("email", "US", "North America", "North America"),
            ("profile", "US", "North America", "North America"), ("now", "JP", "Asia Pacific", "Asia"),
            ("unknown", None, "Undisclosed", "Undisclosed"),
        ]
    ])
    tz = pd.DataFrame([
        {"canonical_id": "consistent", "year": 2018, "tz_region": "Europe", "tz_un_region": "Europe"},
        {"canonical_id": "moved", "year": 2018, "tz_region": "North America", "tz_un_region": "North America"},
        {"canonical_id": "unknown", "year": 2018, "tz_region": "Asia Pacific", "tz_un_region": "Asia"},
        {"canonical_id": "unverified", "year": 2018, "tz_region": None, "tz_un_region": None},   # unresolved year
    ])
    email = pd.DataFrame([{"canonical_id": "email", "year": 2018, "email_iso2": "CA"}])
    prof = pd.DataFrame([{"uuid": "profile", "year": 2025, "location_raw": "Berlin, Germany"}])
    py = pd.DataFrame({"uuid": ["consistent", "unverified", "moved", "email", "profile", "now", "unknown"],
                       "year": [2018, 2018, 2018, 2018, 2025, 2026, 2018]})
    y = resolve_yearly(py, cur, tz, email, prof, current_year=2026).set_index("uuid")
    expect = {
        "consistent": ("carried_back_tz_consistent", "DE", "Europe"),
        "unverified": ("carried_back_unverified", "DE", "Europe"),
        "moved": ("tz_only", None, "North America"),
        "email": ("observed_email", "CA", "North America"),
        "profile": ("observed_profile", "DE", "Europe"),
        "now": ("current", "JP", "Asia Pacific"),
        "unknown": ("tz_only", None, "Asia Pacific"),
    }
    for u, (basis, iso, region) in expect.items():
        r = y.loc[u]
        got = (r["basis"], r["geo_country_iso2"] if isinstance(r["geo_country_iso2"], str) else None, r["geo_macro_region"])
        assert got == (basis, iso, region), f"{u}: got {got}, expected {(basis, iso, region)}"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"✅ {name}")
