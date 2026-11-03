"""
No published artifact may carry per-person private fields (inferred geography,
timezone signatures, internal ids). Scans every JSON file under output/.

    python3 tests/test_publish_policy.py
"""

import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.utils.publish_policy import is_private

# Aggregate artifacts may name these as metadata keys (e.g. a coverage block), never per person.
_ALLOWED_KEYS = {"geo_taxonomy_version"}


def _private_keys(obj, found):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and is_private(k) and k not in _ALLOWED_KEYS:
                found.add(k)
            _private_keys(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _private_keys(v, found)
    return found


def run():
    offenders = {}
    for path in (_PROJECT_ROOT / "output").rglob("*.json"):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        keys = _private_keys(data, set())
        if keys:
            offenders[str(path.relative_to(_PROJECT_ROOT))] = sorted(keys)
    if offenders:
        print(f"❌ {len(offenders)} published files carry private fields, e.g.:")
        for p, keys in list(offenders.items())[:10]:
            print(f"   {p}: {keys}")
        sys.exit(1)
    print("✅ No private per-person fields in output/")


def test_no_private_fields_published():
    run()


if __name__ == "__main__":
    run()
