"""
Geographic attribution, shared by Phase 3 (resolve_geography, build_geo_history) and Phase 4 (geo_artifacts).

    scripts/utils/geography.py   gazetteer + location-string parser (taxonomy, R0-R7 rules)
    geo/signals.py               evidence from commits and profiles (timezone, email/blog ccTLD, bio)
    geo/curation.py              the private, hand-verified curation file
    geo/attribution.py           one priority policy -> current location and location per year
    geo/policy.py                publication rules (k-anonymity, Core repos, activity definitions)
"""
