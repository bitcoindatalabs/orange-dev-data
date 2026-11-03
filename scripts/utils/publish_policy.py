"""
publish_policy.py — which per-contributor fields may appear in public output.

Per-person artifacts (output/shared/contributors/profiles/*.json) are built from
data/enriched/contributors_unified.parquet. That table also carries internal fields:
inferred geography (country guessed from commit timezone, email or blog domain),
attribution diagnostics and fetch bookkeeping. None of that is the person's own
statement, so it must never be published per person; it feeds only aggregate,
k-anonymised charts.

Every column is classified explicitly. A column in neither set is dropped from
profiles with a warning until someone adds it to PUBLIC_PROFILE_COLUMNS, so a new
pipeline column can never leak by default.
"""

from typing import Iterable, List

PUBLIC_PROFILE_COLUMNS = frozenset({
    # identity and public handles
    "uuid", "display_name", "github_login_final", "delving_username_final", "badges", "roles",
    # commits
    "total_commits", "authored_commits", "tier1_authored_commits", "tier2_authored_commits",
    "merge_commits", "tier1_merge_commits", "tier2_merge_commits", "self_merges",
    "total_additions", "total_deletions", "co_authored_commits",
    "p2016_authored_commits", "modern_authored_commits",
    "first_core_commit", "last_core_commit", "first_ecosystem_commit", "last_ecosystem_commit",
    "first_commit", "last_commit",
    # BIPs
    "bips_authored", "p2016_bips_authored", "modern_bips_authored", "first_bip_date", "last_bip_date",
    # reviews and PRs
    "avg_review_latency_days", "reviews_count", "avg_approval_latency_days", "approvals_count",
    "tier1_reviews_count", "tier2_reviews_count", "p2016_reviews_count", "modern_reviews_count",
    "first_review_date", "last_review_date", "prs_authored", "tier1_prs_authored", "tier2_prs_authored",
    "avg_pr_ack_velocity_days", "avg_concept_lead_time_days", "review_reciprocity",
    # scores
    "hybrid_score", "p2016_hybrid_score", "modern_hybrid_score",
    "impact_score", "p2016_impact_score", "modern_impact_score",
    # discussions
    "threads_started", "replies_sent", "ml_threads", "delving_threads", "ml_responses", "delving_responses",
    "p2016_posts", "modern_posts", "p2016_ml_posts", "p2016_delving_posts", "modern_ml_posts", "modern_delving_posts",
    # activity and classification
    "first_active", "last_active", "global_first_active", "global_last_active", "activity_status",
    "dev_type", "is_engineer", "is_reviewer", "is_researcher", "is_bip_author",
    "expertise_domains", "expertise_by_source", "expertise_domain_scores",
    # the person's own public GitHub profile, as they wrote it
    "github_location", "github_company", "github_bio", "github_twitter", "github_blog", "github_followers",
})

PRIVATE_COLUMNS = frozenset({
    "github_id_final",             # internal join key
    "github_profile_fetched_at",   # fetch bookkeeping
})
PRIVATE_PREFIXES = ("geo_",)       # attribution output: inferred country, timezone signature, diagnostics


def is_private(column: str) -> bool:
    return column in PRIVATE_COLUMNS or column.startswith(PRIVATE_PREFIXES)


def public_profile_columns(columns: Iterable[str]) -> List[str]:
    """The publishable subset of `columns`, in order. Warns about unclassified columns."""
    columns = list(columns)
    unclassified = [c for c in columns if c not in PUBLIC_PROFILE_COLUMNS and not is_private(c)]
    if unclassified:
        print(f"  ⚠️  Not publishing unclassified columns {unclassified}: add them to "
              f"PUBLIC_PROFILE_COLUMNS or PRIVATE_COLUMNS in scripts/utils/publish_policy.py")
    return [c for c in columns if c in PUBLIC_PROFILE_COLUMNS]
