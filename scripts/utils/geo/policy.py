"""Publication and activity rules shared by every geographic artifact."""

# A country (or a region's commit/review totals) is published only for cells with at least K_MIN
# contributors: a 2-person country with thousands of commits identifies the person.
K_MIN = 5

# activity_status values counted as "active" in the all-time lenses.
ACTIVE_STATUSES = {"Active", "New", "Rising"}

# "Core" = these three repositories, commit hashes set-unioned (orange-dev-data rule).
CORE_REPOS = ("bitcoin/bitcoin", "bitcoin-core/gui", "bitcoin-core/secp256k1")

# Review activity = comments and reviews; passive events (mentioned, subscribed) are not activity.
REVIEW_EVENT_TYPES = ("commented", "reviewed")
