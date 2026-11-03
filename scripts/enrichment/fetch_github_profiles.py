#!/usr/bin/env python3
"""
fetch_github_profiles.py
========================
Fetches GitHub profile data for every GitHub account active in the pipeline by
calling the GitHub REST API by numeric id (GET /user/{id}), which keeps working
after a login is renamed.

Accounts covered: everyone in github_id_map.json plus every PR author and every
active reviewer/commenter in the raw PR and review parquets (passive mentioned /
subscribed events are not activity).

Refresh policy: never-fetched accounts first (most active first), then profiles
older than --ttl-days (oldest first), up to --max-requests per run, so the weekly
run keeps every profile at most ~ttl days old without a long API burst.

Outputs:
    metadata/github_profiles.json              current profile per github_id (schema below)
    data/raw/github_profile_snapshots.parquet  append-only history: a row whenever a
                                               tracked field changes (location history)

Run from the repository root:
    python3 scripts/enrichment/fetch_github_profiles.py                 # weekly budget
    python3 scripts/enrichment/fetch_github_profiles.py --max-requests 6000
    python3 scripts/enrichment/fetch_github_profiles.py --token ghp_xxx  # else GITHUB_TOKEN

Schema of each profile entry (keyed by github_id string):
    {
        "github_id":        "548488",
        "login":            "sipa",
        "name":             "Pieter Wuille",
        "email":            null,
        "location":         "US",
        "company":          "Chaincode Labs",
        "blog":             "https://...",
        "bio":              null,
        "public_repos":     42,
        "public_gists":     0,
        "followers":        5000,
        "following":        10,
        "created_at":       "2010-01-01T00:00:00Z",
        "updated_at":       "2026-01-01T00:00:00Z",
        "twitter_username": null,
        "hireable":         null,
        "fetched_at":       "2026-04-18T12:00:00Z",
        "status":           "ok"           # or "not_found"
    }
"""

import argparse
import json
import os
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import pandas as pd
import pyarrow.parquet as pq

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Use certifi's CA bundle when available (required on macOS python.org builds)
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

# ── Paths (relative to repo root) ─────────────────────────────────────────────

INPUT_PATH     = "metadata/github_id_map.json"
OUTPUT_PATH    = "metadata/github_profiles.json"
SNAPSHOTS_PATH = "data/raw/github_profile_snapshots.parquet"
ACTIVITY_FILES = {
    "data/raw/github_pr_metadata.parquet":   "author",
    "data/raw/bips_pr_metadata.parquet":     "author",
    "data/raw/github_review_events.parquet": "user",
    "data/raw/bips_review_events.parquet":   "user",
}
ACTIVE_EVENT_TYPES = {"commented", "reviewed"}   # same definition as review_metrics.py

# Fields whose change adds a row to the snapshot history.
SNAPSHOT_FIELDS = ["login", "name", "email", "location", "company", "blog", "bio",
                   "twitter_username", "status"]

# ── API settings ───────────────────────────────────────────────────────────────

API_BY_ID         = "https://api.github.com/user/{github_id}"
RATE_LIMIT_FLOOR  = 10          # sleep when remaining requests fall to this value
PROGRESS_INTERVAL = 50          # print a progress line / checkpoint every N profiles
MAX_RETRIES       = 3           # max retries on 403 / 429
BASE_BACKOFF_S    = 2.0         # initial backoff in seconds (doubles each retry)
DEFAULT_TTL_DAYS  = 90
DEFAULT_MAX_REQ   = 1500


# ── Helpers ────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_request(url: str, token: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept":        "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent":    "orange-dev-data/fetch_github_profiles",
        },
    )


def _check_rate_limit(headers: dict) -> None:
    """
    Inspect X-RateLimit-Remaining; if we're at/below the floor, sleep until
    X-RateLimit-Reset (plus a small buffer) so we never exhaust the quota.
    """
    try:
        remaining = int(headers.get("X-RateLimit-Remaining", 999))
        reset_ts  = int(headers.get("X-RateLimit-Reset", 0))
    except (TypeError, ValueError):
        return

    if remaining <= RATE_LIMIT_FLOOR:
        now   = time.time()
        sleep = max(reset_ts - now + 5, 1)
        print(
            f"  [rate-limit] {remaining} requests remaining — "
            f"sleeping {sleep:.0f}s until reset..."
        )
        time.sleep(sleep)


def _fetch_profile(github_id: str, token: str) -> dict:
    """
    Call GET /user/{id} with exponential backoff on 403/429.
    Returns the parsed profile dict, or {"status": "not_found"} on 404 (deleted account).
    Raises RuntimeError after MAX_RETRIES exhausted.
    """
    url = API_BY_ID.format(github_id=github_id)

    for attempt in range(1, MAX_RETRIES + 1):
        req = _build_request(url, token)
        try:
            with urllib.request.urlopen(req, context=_SSL_CTX) as resp:
                _check_rate_limit(resp.headers)
                body = json.loads(resp.read().decode("utf-8"))
            return body

        except urllib.error.HTTPError as exc:
            _check_rate_limit(exc.headers)

            if exc.code == 404:
                return {"status": "not_found"}

            if exc.code in (403, 429):
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_S * (2 ** (attempt - 1))
                    retry_after = exc.headers.get("Retry-After")
                    if retry_after:
                        try:
                            backoff = max(backoff, float(retry_after))
                        except ValueError:
                            pass
                    print(
                        f"  [backoff] HTTP {exc.code} for id {github_id} — "
                        f"attempt {attempt}/{MAX_RETRIES}, sleeping {backoff:.1f}s..."
                    )
                    time.sleep(backoff)
                    continue
                raise RuntimeError(
                    f"HTTP {exc.code} for id {github_id} after {MAX_RETRIES} retries"
                ) from exc

            # Any other HTTP error: propagate immediately
            raise RuntimeError(f"HTTP {exc.code} for id {github_id}: {exc.reason}") from exc

    # Should never be reached, but satisfies type checkers
    raise RuntimeError(f"Exhausted retries for id {github_id}")


def _extract_fields(raw: dict, github_id: str, login: str, fetched_at: str) -> dict:
    """Normalise the GitHub API response into our target schema."""
    return {
        "github_id":        github_id,
        "login":            raw.get("login", login),
        "name":             raw.get("name"),
        "email":            raw.get("email") or None,
        "location":         raw.get("location") or None,
        "company":          raw.get("company") or None,
        "blog":             raw.get("blog") or None,
        "bio":              raw.get("bio") or None,
        "public_repos":     raw.get("public_repos"),
        "public_gists":     raw.get("public_gists"),
        "followers":        raw.get("followers"),
        "following":        raw.get("following"),
        "created_at":       raw.get("created_at"),
        "updated_at":       raw.get("updated_at"),
        "twitter_username": raw.get("twitter_username"),
        "hireable":         raw.get("hireable"),
        "fetched_at":       fetched_at,
        "status":           "ok",
    }


# ── I/O ────────────────────────────────────────────────────────────────────────

def _load_accounts(id_map_path: str) -> dict:
    """github_id -> {"login": str, "activity": int} for every account worth a profile."""
    accounts: dict = {}

    if os.path.exists(id_map_path):
        with open(id_map_path, encoding="utf-8") as f:
            for e in json.load(f).get("entries", []):
                gid, login = str(e.get("github_id") or "").strip(), str(e.get("login") or "").strip()
                if gid and login:
                    accounts.setdefault(gid, {"login": login, "activity": 0})

    for path, login_col in ACTIVITY_FILES.items():
        if not os.path.exists(path):
            print(f"  [warn] {path} not found — skipping")
            continue
        cols = [login_col, "github_id"] + (["event_type"] if "review_events" in path else [])
        df = pd.read_parquet(path, columns=cols)
        if "event_type" in df.columns:
            df = df[df["event_type"].isin(ACTIVE_EVENT_TYPES)]
        df = df.dropna(subset=["github_id"])
        df["github_id"] = df["github_id"].astype(str).str.strip()
        df = df[~df["github_id"].isin(["", "None", "nan"])]
        for (gid, login), n in df.groupby(["github_id", login_col]).size().items():
            acc = accounts.setdefault(gid, {"login": str(login), "activity": 0})
            acc["activity"] += int(n)
    return accounts


def _load_existing_profiles(path: str) -> dict:
    """Return profiles dict from existing output file, or {} if none."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("profiles", {})
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  [warn] could not read existing {path}: {exc} — starting fresh")
        return {}


def _save_profiles(path: str, profiles: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    output = {
        "generated":    _now_iso(),
        "total_fetched": len(profiles),
        "profiles":     profiles,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)   # atomic: a crash mid-write never leaves a truncated file


def _snapshot_row(profile: dict) -> dict:
    row = {"github_id": str(profile.get("github_id")), "fetched_at": profile.get("fetched_at")}
    for k in SNAPSHOT_FIELDS:
        v = profile.get(k)
        row[k] = None if v is None else str(v)
    return row


class SnapshotLog:
    """Append-only profile history: one row per github_id whenever a tracked field changes."""

    def __init__(self, path: str, seed_profiles: dict):
        self.path = path
        if os.path.exists(path):
            self.df = pd.read_parquet(path)
        else:
            # First run: start the history from the profiles already on disk, so the values
            # fetched earlier survive the refresh that is about to overwrite them.
            rows = [_snapshot_row(p) for p in seed_profiles.values() if p.get("fetched_at")]
            self.df = pd.DataFrame(rows, columns=["github_id", "fetched_at"] + SNAPSHOT_FIELDS)
            print(f"  Seeded profile history with {len(self.df):,} existing profiles")
        self._latest = {
            r["github_id"]: {k: r[k] for k in SNAPSHOT_FIELDS}
            for r in self.df.sort_values("fetched_at").to_dict("records")
        }
        self._new: list = []

    def record(self, profile: dict) -> None:
        row = _snapshot_row(profile)
        state = {k: row[k] for k in SNAPSHOT_FIELDS}
        if self._latest.get(row["github_id"]) != state:
            self._new.append(row)
            self._latest[row["github_id"]] = state

    def save(self) -> None:
        if self._new:
            self.df = pd.concat([self.df, pd.DataFrame(self._new)], ignore_index=True)
            self._new = []
        # The history cannot be re-fetched from GitHub. It only grows, so a save that would
        # shrink the file on disk means another copy (another machine) got ahead: refuse.
        if os.path.exists(self.path):
            on_disk = pq.ParquetFile(self.path).metadata.num_rows
            if len(self.df) < on_disk:
                raise RuntimeError(
                    f"Refusing to overwrite {self.path}: it has {on_disk:,} rows, this run has "
                    f"{len(self.df):,}. Another copy of the profile history is newer; reconcile first."
                )
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self._backup_previous()
        tmp = self.path + ".tmp"
        self.df.to_parquet(tmp, index=False)
        os.replace(tmp, self.path)

    def _backup_previous(self, keep: int = 8) -> None:
        """Keep a dated copy of the history before the first save of each day (last `keep` days)."""
        if not os.path.exists(self.path):
            return
        backup_dir = os.path.join(os.path.dirname(self.path), "..", "backups", "profile_snapshots")
        os.makedirs(backup_dir, exist_ok=True)
        dest = os.path.join(backup_dir, f"github_profile_snapshots_{datetime.now(timezone.utc):%Y%m%d}.parquet")
        if not os.path.exists(dest):
            shutil.copy2(self.path, dest)
        for old in sorted(f for f in os.listdir(backup_dir) if f.endswith(".parquet"))[:-keep]:
            os.remove(os.path.join(backup_dir, old))


# ── Summary ────────────────────────────────────────────────────────────────────

def _print_summary(profiles: dict, accounts: dict, ttl_days: int) -> None:
    ok_profiles    = [p for p in profiles.values() if p.get("status") == "ok"]
    not_found      = sum(1 for p in profiles.values() if p.get("status") == "not_found")
    has_email      = sum(1 for p in ok_profiles if p.get("email"))
    has_location   = sum(1 for p in ok_profiles if p.get("location"))
    has_company    = sum(1 for p in ok_profiles if p.get("company"))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ttl_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    covered = sum(1 for gid in accounts if profiles.get(gid, {}).get("fetched_at"))
    fresh   = sum(1 for gid in accounts if (profiles.get(gid, {}).get("fetched_at") or "") >= cutoff)

    print()
    print("─" * 52)
    print(f"  Active accounts         : {len(accounts)}")
    print(f"  With a profile          : {covered}  ({covered/max(len(accounts),1)*100:.1f}%)")
    print(f"  Fetched within {ttl_days:>3} days : {fresh}  ({fresh/max(len(accounts),1)*100:.1f}%)")
    print(f"  Status ok               : {len(ok_profiles)}")
    print(f"  Not found (404)         : {not_found}")
    print(f"  Have public email       : {has_email}  ({has_email/max(len(ok_profiles),1)*100:.1f}%)")
    print(f"  Have location           : {has_location}  ({has_location/max(len(ok_profiles),1)*100:.1f}%)")
    print(f"  Have company            : {has_company}  ({has_company/max(len(ok_profiles),1)*100:.1f}%)")
    print("─" * 52)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch/refresh GitHub profiles for every active GitHub account"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub Personal Access Token (falls back to GITHUB_TOKEN env var)",
    )
    parser.add_argument("--ttl-days", type=int, default=DEFAULT_TTL_DAYS,
                        help=f"Refresh profiles older than this (default: {DEFAULT_TTL_DAYS})")
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQ,
                        help=f"API calls per run (default: {DEFAULT_MAX_REQ})")
    parser.add_argument("--input", default=INPUT_PATH, metavar="PATH",
                        help=f"Path to github_id_map.json (default: {INPUT_PATH})")
    parser.add_argument("--output", default=OUTPUT_PATH, metavar="PATH",
                        help=f"Path for output github_profiles.json (default: {OUTPUT_PATH})")
    args = parser.parse_args()

    if not args.token:
        sys.exit(
            "ERROR: GitHub token is required.\n"
            "  Pass --token ghp_xxx  or  set the GITHUB_TOKEN environment variable."
        )

    # ── Load inputs ────────────────────────────────────────────────────────────
    print("Collecting active GitHub accounts...")
    accounts = _load_accounts(args.input)
    print(f"  {len(accounts):,} accounts.")

    profiles  = _load_existing_profiles(args.output)
    snapshots = SnapshotLog(SNAPSHOTS_PATH, profiles)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.ttl_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    never  = sorted((g for g in accounts if not profiles.get(g, {}).get("fetched_at")),
                    key=lambda g: -accounts[g]["activity"])
    stale  = sorted((g for g in accounts if g not in never and profiles[g]["fetched_at"] < cutoff),
                    key=lambda g: profiles[g]["fetched_at"])
    queue  = (never + stale)[: max(args.max_requests, 0)]
    print(f"  {len(never):,} never fetched, {len(stale):,} older than {args.ttl_days} days; "
          f"fetching {len(queue):,} this run.")

    # ── Fetch loop ─────────────────────────────────────────────────────────────
    fetched_this_run = 0

    for github_id in queue:
        login = profiles.get(github_id, {}).get("login") or accounts[github_id]["login"]
        try:
            raw = _fetch_profile(github_id, args.token)
        except RuntimeError as exc:
            print(f"  [error] {exc} — skipping")
            continue

        fetched_at = _now_iso()

        if raw.get("status") == "not_found":
            profiles[github_id] = {
                "github_id": github_id,
                "login":     login,
                "status":    "not_found",
                "fetched_at": fetched_at,
            }
        else:
            profiles[github_id] = _extract_fields(raw, github_id, login, fetched_at)
        snapshots.record(profiles[github_id])

        fetched_this_run += 1

        # Progress print + checkpoint every PROGRESS_INTERVAL fetches
        if fetched_this_run % PROGRESS_INTERVAL == 0:
            print(f"  Fetched {fetched_this_run}/{len(queue)} ({profiles[github_id].get('login')})...")
            _save_profiles(args.output, profiles)
            snapshots.save()

    # ── Final save ─────────────────────────────────────────────────────────────
    _save_profiles(args.output, profiles)
    snapshots.save()
    print(f"\nDone. {fetched_this_run} profiles fetched this run.")
    print(f"Output written to {args.output} and {SNAPSHOTS_PATH}")

    _print_summary(profiles, accounts, args.ttl_days)


if __name__ == "__main__":
    main()
