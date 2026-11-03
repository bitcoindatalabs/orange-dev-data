#!/usr/bin/env python3
"""
extend_geo_countries.py — add any ISO 3166-1 country missing from metadata/geo/countries.csv.

Existing rows are hand-curated (display names, the legacy macro_region buckets used by the
public charts, World Bank income group, sovereign roll-ups) and are never modified. Missing
codes are appended with fields derived mechanically from the vendored reference table:

    metadata/geo/reference/iso3166_m49.csv
        ISO 3166-1 codes with UN M49 regions, from
        https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes (CC BY-SA 4.0)

Derivation for appended rows:
    m49_subregion   intermediate region if present (e.g. "South America"), else sub-region
    macro_region    legacy chart bucket: Northern America -> North America, rest of Americas ->
                    Latin America, Europe -> Europe, Asia/Oceania -> Asia Pacific, Africa -> Africa
    un_macro_region Northern America -> North America, rest of Americas -> Latin America &
                    Caribbean, otherwise the M49 region (Europe, Asia, Oceania, Africa)
    sovereign_iso2  the administering country for dependent territories, else the code itself
    wb_income       left blank (not in the reference)

Usage (from the repo root):
    python scripts/maintenance/extend_geo_countries.py            # writes countries.csv
    python scripts/maintenance/extend_geo_countries.py --dry-run
"""

import argparse
import csv
import re

COUNTRIES = "metadata/geo/countries.csv"
REFERENCE = "metadata/geo/reference/iso3166_m49.csv"

# Uninhabited or no M49 region: not places a contributor lives.
SKIP = {"AQ", "BV", "HM"}

DISPLAY_NAMES = {
    "CD": "DR Congo", "CG": "Congo", "KP": "North Korea", "LA": "Laos", "PS": "Palestine",
    "SY": "Syria", "FM": "Micronesia", "VA": "Vatican City", "BQ": "Caribbean Netherlands",
    "SH": "Saint Helena", "MF": "Saint Martin", "UM": "U.S. Minor Outlying Islands",
    "VI": "U.S. Virgin Islands", "IO": "British Indian Ocean Territory", "TL": "Timor-Leste",
    "CV": "Cabo Verde", "SZ": "Eswatini",
}

SOVEREIGN = {
    **{c: "US" for c in ("AS", "GU", "MP", "UM", "VI")},
    **{c: "GB" for c in ("AI", "FK", "GS", "IO", "MS", "PN", "SH", "TC")},
    **{c: "NL" for c in ("AW", "BQ", "CW", "SX")},
    **{c: "FR" for c in ("BL", "GF", "GP", "MF", "MQ", "NC", "PF", "PM", "RE", "TF", "WF", "YT")},
    **{c: "AU" for c in ("CC", "CX", "NF")},
    **{c: "NZ" for c in ("CK", "NU", "TK")},
    "FO": "DK", "GL": "DK", "SJ": "NO", "AX": "FI",
}


def flag(iso2: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in iso2)


def display_name(iso2: str, ref_name: str) -> str:
    if iso2 in DISPLAY_NAMES:
        return DISPLAY_NAMES[iso2]
    name = re.sub(r"\s*\(.*?\)", "", ref_name).strip()
    return name.split(", ")[0] if ", " in name else name


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(COUNTRIES, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    have = {r["iso2"] for r in rows}
    # Reuse the existing spelling of a sub-region ("South-Eastern Asia") when one exists.
    known_sub = {r["m49_subregion"].lower(): r["m49_subregion"] for r in rows}

    with open(REFERENCE, encoding="utf-8") as f:
        ref = list(csv.DictReader(f))

    added = []
    for r in ref:
        iso2 = r["alpha-2"]
        if iso2 in have or iso2 in SKIP or not r["region"]:
            continue
        region, sub = r["region"], r["sub-region"]
        subregion = r["intermediate-region"] or sub
        subregion = known_sub.get(subregion.lower(), subregion)
        northern = sub == "Northern America"
        legacy = ("North America" if northern else "Latin America") if region == "Americas" else \
                 "Asia Pacific" if region in ("Asia", "Oceania") else region
        un = ("North America" if northern else "Latin America & Caribbean") if region == "Americas" else region
        added.append({
            "iso2": iso2, "iso3": r["alpha-3"], "m49": r["country-code"],
            "display_name": display_name(iso2, r["name"]),
            "m49_region": region, "m49_subregion": subregion,
            "macro_region": legacy, "un_macro_region": un,
            "sovereign_iso2": SOVEREIGN.get(iso2, iso2), "wb_income": "", "flag": flag(iso2),
        })

    print(f"{len(rows)} existing rows; appending {len(added)}: " + " ".join(a["iso2"] for a in added))
    if args.dry_run or not added:
        return
    with open(COUNTRIES, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows + added)
    print(f"Wrote {COUNTRIES}")


if __name__ == "__main__":
    main()
