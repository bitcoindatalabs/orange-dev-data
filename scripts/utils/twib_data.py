import pandas as pd
from datetime import datetime, timedelta
import os

from scripts.utils.bots import is_bot

CORE_REPO = "bitcoin/bitcoin"
REVIEW_EVENT_TYPES = ["commented", "reviewed"]


def get_category_from_labels(labels):
    if not isinstance(labels, (list, str)):
        return '🔄 Misc / Other'
    labels_str = str(labels).lower()
    if 'wallet' in labels_str:
        return '👛 Wallet & Keys'
    elif 'p2p' in labels_str or 'network' in labels_str:
        return '⚡ P2P & Network'
    elif 'consensus' in labels_str or 'crypto' in labels_str:
        return '🛡️ Consensus & Cryptography'
    elif 'rpc' in labels_str or 'api' in labels_str or 'zmq' in labels_str or 'rest' in labels_str:
        return '📡 RPC, APIs & ZMQ'
    elif 'gui' in labels_str:
        return '🖥️ GUI'
    elif 'build' in labels_str or 'ci' in labels_str or 'test' in labels_str or 'qa' in labels_str:
        return '🛠️ Build, CI & Testing'
    elif 'doc' in labels_str:
        return '📝 Documentation'
    else:
        return '🔄 Misc / Other'

def get_week_close_timestamp():
    """
    Anchor to the end of the completed week: Sunday 23:59:59 UTC.

    Defaults to the most recent Sunday. Set TWIB_WEEK_END=YYYY-MM-DD (a Sunday) to rebuild a
    past week deterministically; every script that calls this then agrees on the window.
    """
    override = os.environ.get("TWIB_WEEK_END")
    if override:
        day = pd.Timestamp(override)
        return pd.Timestamp(year=day.year, month=day.month, day=day.day,
                            hour=23, minute=59, second=59, tz='UTC')
    now = pd.Timestamp.now(tz='UTC')
    # dayofweek: Monday=0, Sunday=6.
    # If today is Sunday (6), subtract 0 days. If Monday (0), subtract 1 day.
    days_since_sunday = (now.dayofweek + 1) % 7
    most_recent_sunday = now - timedelta(days=days_since_sunday)
    return pd.Timestamp(
        year=most_recent_sunday.year,
        month=most_recent_sunday.month,
        day=most_recent_sunday.day,
        hour=23,
        minute=59,
        second=59,
        tz='UTC'
    )


def _safe_uuid(u):
    return u if pd.notna(u) else None


def get_weekly_activity(root_dir, days_back=7, end_date=None):
    """
    Weekly activity for TWIB. Definitions match the monthly State of Bitcoin Core report:
      - total_merged / total_reviews / new_contributors: bitcoin/bitcoin only, bots excluded.
      - subsystem_merged: bitcoin-core/gui and secp256k1 merges, reported separately.
      - total_reviews: 'commented' + 'reviewed' events by humans.
      - new_contributors: authors whose first-ever merged bitcoin/bitcoin PR lands in the week.
      - total_threads: distinct thread_id (Delving topic / mailing-list thread) with activity.
    PRs are keyed by (repository_name, pr_number) since GUI/secp numbers overlap bitcoin/bitcoin's.
    """
    if end_date is None:
        end_date = get_week_close_timestamp()
    start_date = end_date - timedelta(days=days_back) + timedelta(seconds=1)

    def in_window(ts):
        return ts.notna() & (ts >= start_date) & (ts <= end_date)

    # Pre-load PR data
    pr_path = os.path.join(root_dir, "data/enriched/enriched_prs.parquet")
    try:
        pr_df = pd.read_parquet(pr_path)
        pr_df['merged_at'] = pd.to_datetime(pr_df['merged_at'], utc=True, errors='coerce')
        pr_df['is_bot'] = pr_df['author'].map(is_bot)
    except Exception as e:
        print(f"Error reading PRs: {e}")
        pr_df = pd.DataFrame()

    unique_authors = {}
    total_merged = 0
    subsystem_merged = {}
    total_reviews = 0
    total_threads = 0
    top_reviewers = []
    top_authors = []
    new_contributors = []

    # Human review interactions only (drop passive events like 'subscribed'/'labeled', and bots)
    reviews_path = os.path.join(root_dir, "data/enriched/enriched_reviews.parquet")
    try:
        reviews_df = pd.read_parquet(reviews_path)
        reviews_df['timestamp'] = pd.to_datetime(reviews_df['timestamp'], utc=True, errors='coerce')
        if 'event_type' in reviews_df.columns:
            reviews_df = reviews_df[reviews_df['event_type'].isin(REVIEW_EVENT_TYPES)]
        reviews_df = reviews_df[~reviews_df['user'].map(is_bot)]
    except Exception as e:
        print(f"Error reading reviews: {e}")
        reviews_df = pd.DataFrame()

    IDENTITY_MAP = {}
    try:
        identity_path = os.path.join(root_dir, "data/enriched/contributors_unified.parquet")
        if os.path.exists(identity_path):
            idf = pd.read_parquet(identity_path)
            for _, row in idf.iterrows():
                if pd.notna(row.get('uuid')) and pd.notna(row.get('display_name')):
                    IDENTITY_MAP[str(row['uuid'])] = str(row['display_name'])
    except Exception as e:
        print(f"Warning: Could not load identity map: {e}")

    # 1. Merged PRs
    try:
        merged_prs = pr_df[in_window(pr_df['merged_at'])].copy()
        core_merged = merged_prs[merged_prs['repository_name'] == CORE_REPO]
        total_merged = len(core_merged)
        subsystem_merged = {
            repo: int(n) for repo, n in
            merged_prs[merged_prs['repository_name'] != CORE_REPO]['repository_name'].value_counts().items()
        }

        # Top authors (bitcoin/bitcoin, humans)
        core_human = core_merged[~core_merged['is_bot']]
        author_counts = core_human.groupby(['author', 'uuid'], dropna=False).size().reset_index(name='count')
        author_counts = author_counts.sort_values('count', ascending=False)
        top_authors = [{"user": {"username": row['author'], "uuid": _safe_uuid(row['uuid'])}, "count": row['count']}
                       for row in author_counts.head(5).to_dict('records')]

        for _, row in merged_prs[~merged_prs['is_bot']].iterrows():
            unique_authors[row['author']] = _safe_uuid(row['uuid'])

        # New contributors: first-ever merged bitcoin/bitcoin PR falls in this week
        core_all = pr_df[(pr_df['repository_name'] == CORE_REPO) & pr_df['merged_at'].notna() & ~pr_df['is_bot']]
        first_merges = core_all.sort_values('merged_at').groupby('author').agg(
            merged_at=('merged_at', 'first'), uuid=('uuid', 'first')).reset_index()
        new_contribs_df = first_merges[in_window(first_merges['merged_at'])]
        new_contributors = [{"username": row['author'], "uuid": _safe_uuid(row['uuid'])}
                            for _, row in new_contribs_df.iterrows()]

        # Importance = all-time human review interactions on the PR
        if not reviews_df.empty:
            all_time_pr_counts = reviews_df.groupby(['repository_name', 'pr_number']).size().reset_index(name='importance')
            merged_prs = pd.merge(merged_prs, all_time_pr_counts, on=['repository_name', 'pr_number'], how='left')
            merged_prs['importance'] = merged_prs['importance'].fillna(0).astype(int)
        else:
            merged_prs['importance'] = 0

        merged_prs = merged_prs.sort_values(by=['importance', 'merged_at'], ascending=[False, False])
        merged_prs['category'] = merged_prs['labels'].apply(get_category_from_labels)

        pr_data = merged_prs[['repository_name', 'pr_number', 'title', 'author', 'uuid', 'merged_at', 'category', 'importance']].copy()
        pr_data['merged_at'] = pr_data['merged_at'].dt.strftime('%Y-%m-%d')

        categorized_prs = {}
        for _, row in pr_data.iterrows():
            row_dict = row.to_dict()
            row_dict['author_obj'] = {"username": row['author'], "uuid": _safe_uuid(row['uuid'])}
            del row_dict['uuid']
            categorized_prs.setdefault(row['category'], []).append(row_dict)

    except Exception as e:
        print(f"Error reading PRs: {e}")
        categorized_prs = {}

    # 2. Hot PRs (most human review activity this week)
    try:
        if reviews_df.empty:
            raise ValueError("reviews_df is empty")

        recent_reviews = reviews_df[in_window(reviews_df['timestamp'])].copy()
        total_reviews = int((recent_reviews['repository_name'] == CORE_REPO).sum())

        reviewer_counts = recent_reviews.groupby(['user', 'uuid'], dropna=False).size().reset_index(name='count')
        reviewer_counts = reviewer_counts.sort_values('count', ascending=False)
        top_reviewers = [{"user": {"username": row['user'], "uuid": _safe_uuid(row['uuid'])}, "count": row['count']}
                         for row in reviewer_counts.head(5).to_dict('records')]

        for _, row in recent_reviews.iterrows():
            unique_authors[row['user']] = _safe_uuid(row['uuid'])

        hot_pr_counts = recent_reviews.groupby(['repository_name', 'pr_number']).size().reset_index(name='event_count')
        hot_pr_counts = hot_pr_counts.sort_values(by='event_count', ascending=False).head(5)

        hot_prs = pd.merge(hot_pr_counts, pr_df.drop(columns=['is_bot']), on=['repository_name', 'pr_number'], how='left')
        hot_prs['category'] = hot_prs['labels'].apply(get_category_from_labels)

        hot_pr_data = {}
        for _, row in hot_prs.iterrows():
            if pd.isna(row['title']):
                continue
            hot_pr_data.setdefault(row['category'], []).append({
                'repository_name': row['repository_name'],
                'pr_number': row['pr_number'],
                'title': row['title'],
                'author': row['author'],
                'author_obj': {"username": row['author'], "uuid": _safe_uuid(row['uuid'])},
                'event_count': row['event_count']
            })

    except Exception as e:
        print(f"Error reading hot PRs: {e}")
        hot_pr_data = {}

    # 3. Active social threads (counted per thread_id so "Re:" subject variants don't split a thread)
    try:
        social_path = os.path.join(root_dir, "data/raw/social_combined.parquet")
        social_df = pd.read_parquet(social_path)
        social_df['date'] = pd.to_datetime(social_df['date'], utc=True)
        thread_openers = social_df.sort_values(by=['is_reply', 'date']).groupby('thread_id').first().reset_index()
        opener_map = thread_openers.set_index('thread_id')[['author_name', 'canonical_id', 'subject']].to_dict('index')

        recent_social = social_df[in_window(social_df['date'])].sort_values('date')
        total_threads = int(recent_social['thread_id'].nunique())

        thread_agg = recent_social.groupby('thread_id').agg(
            source=('source', 'first'),
            subject=('subject', 'first'),
            message_count=('message_id', 'count'),
            link=('link', 'first')
        ).reset_index()

        thread_agg = thread_agg.sort_values(by='message_count', ascending=False).head(5)
        social_data = thread_agg.to_dict(orient='records')

        for thread in social_data:
            tid = thread.get('thread_id')
            opener = opener_map.get(tid, {})
            # Prefer the opener's subject (no "Re:" prefix) for display
            if opener.get('subject'):
                thread['subject'] = opener['subject']
            uuid = str(opener.get('canonical_id', ''))
            author_name = opener.get('author_name', 'Unknown')

            if uuid and uuid != 'nan' and uuid != 'None':
                display_name = IDENTITY_MAP.get(uuid, author_name)
                thread['author_obj'] = {"username": display_name, "uuid": uuid}
                thread['author'] = display_name
            else:
                thread['author'] = author_name
    except Exception as e:
        print(f"Error reading social data: {e}")
        social_data = []

    clean_authors = [{"username": u, "uuid": unique_authors[u]} for u in unique_authors if not is_bot(u)]
    clean_authors = sorted(clean_authors, key=lambda x: str(x['username']).lower())

    return {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "categorized_merged_prs": categorized_prs,
        "categorized_hot_prs": hot_pr_data,
        "active_threads": social_data,
        "contributors": clean_authors,
        "total_merged": total_merged,
        "subsystem_merged": subsystem_merged,
        "total_reviews": total_reviews,
        "total_threads": total_threads,
        "top_reviewers": top_reviewers,
        "top_authors": top_authors,
        "new_contributors": new_contributors
    }
