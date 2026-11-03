"""
Bot / automation account filter — the single definition for the whole pipeline.

Used by TWIB (scripts/utils/twib_data.py) and loaded by path from
python/automation/jobs/orange_dev/monthly_state.py, so the weekly and monthly
reports always count the same humans.
"""

BOT_LOGINS = {
    "DrahtBot", "auto_drahtbot", "bitcoin", "Copilot", "github-actions",
    "dependabot", "merge-script", "ghost",
}


def is_bot(login) -> bool:
    """True for automation accounts. Exact-match list + GitHub's '[bot]' suffix
    (a substring match on 'bot' would also drop humans whose login contains it)."""
    u = str(login or "")
    return (not u) or u in BOT_LOGINS or u.endswith("[bot]")
