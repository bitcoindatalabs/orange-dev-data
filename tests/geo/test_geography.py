"""
test_geography.py — Golden Test Suite for Enterprise Geographic Attribution Engine.
Verifies:
1. Substring collision prevention (`, ca` vs `, Canada`, `uk` vs `Ukraine`/`Fukuoka`/`Phuket`, `New Mexico` vs `Mexico`).
2. Admin1 + City contextual disambiguation (`Perth, WA` -> Australia, `London, ON` -> Canada, `Austin, TX` -> USA).
3. Non-geographic / Joke string filtering (`Earth`, `Remote`, `Mempool`, `127.0.0.1`, `::1`, `/dev/null`).
4. Flag emoji & Endonym resolution (`Deutschland` -> Germany, `Brasil` -> Brazil, `Türkiye` -> Turkey, `🇪🇸` -> Spain).
5. Region-only fallbacks (`Europe` -> Europe, `Scandinavia` -> Europe, `EU` -> Europe).
6. ISO-faithful territories (`Hong Kong` -> Hong Kong (`HKG`), `Puerto Rico` -> Puerto Rico (`PRI`), `Taiwan` -> Taiwan (`TWN`)).
"""

import os
import sys

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_TEST_DIR, "../.."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.utils.geography import resolve_country, resolve_location, resolve_region


GOLDEN_COUNTRY_CASES = [
    # 1. Previously Broken Substring Collisions (Must have 100% precision)
    ("Toronto, Canada", "Canada", "CA", "North America"),
    ("Vancouver, Canada", "Canada", "CA", "North America"),
    ("Montreal, QC, Canada", "Canada", "CA", "North America"),
    ("Victoria, Canada", "Canada", "CA", "North America"),
    ("Kitchener, Ontario, Canada", "Canada", "CA", "North America"),
    ("British Columbia, Canada", "Canada", "CA", "North America"),
    ("Beautiful British Columbia, Canada", "Canada", "CA", "North America"),
    ("London, ON", "Canada", "CA", "North America"),
    ("Toronto, ON", "Canada", "CA", "North America"),
    ("Vancouver, BC", "Canada", "CA", "North America"),

    ("Kyiv, Ukraine", "Ukraine", "UA", "Europe"),
    ("Ukraine", "Ukraine", "UA", "Europe"),
    ("Kropyvnytskyi, Ukraine", "Ukraine", "UA", "Europe"),
    ("Fukuoka", "Japan", "JP", "Asia Pacific"),
    ("Fukuoka, Japan", "Japan", "JP", "Asia Pacific"),
    ("Phuket, Thailand", "Thailand", "TH", "Asia Pacific"),

    ("New Mexico", "USA", "US", "North America"),
    ("Albuquerque, New Mexico", "USA", "US", "North America"),
    ("Santa Fe, NM", "USA", "US", "North America"),
    ("Mexico", "Mexico", "MX", "Latin America"),
    ("Mexico City, Mexico", "Mexico", "MX", "Latin America"),

    ("Perth, WA", "Australia", "AU", "Asia Pacific"),
    ("Perth, Western Australia", "Australia", "AU", "Asia Pacific"),
    ("Melbourne, AU", "Australia", "AU", "Asia Pacific"),
    ("Sydney, Australia", "Australia", "AU", "Asia Pacific"),
    ("The Great Southern Land", "Australia", "AU", "Asia Pacific"),
    ("Seattle, WA", "USA", "US", "North America"),
    ("Redmond, WA, USA", "USA", "US", "North America"),

    ("Costa Rica", "Costa Rica", "CR", "Latin America"),
    ("San Jose, Costa Rica", "Costa Rica", "CR", "Latin America"),
    ("Mauritania", "Mauritania", "MR", "Africa"),
    ("Gwalior, Madhya Pradesh, India", "India", "IN", "Asia Pacific"),
    ("Västmanland, Sweden", "Sweden", "SE", "Europe"),
    ("Algeria", "Algeria", "DZ", "Africa"),

    # 2. ISO-Faithful Special Jurisdictions
    ("Hong Kong", "Hong Kong", "HK", "Asia Pacific"),
    ("Hongkong, China", "Hong Kong", "HK", "Asia Pacific"),
    ("Taiwan", "Taiwan", "TW", "Asia Pacific"),
    ("Taipei, Taiwan", "Taiwan", "TW", "Asia Pacific"),
    ("Puerto Rico", "Puerto Rico", "PR", "Latin America"),
    ("British Virgin Islands", "British Virgin Islands", "VG", "Latin America"),
    ("Isle of Man", "Isle of Man", "IM", "Europe"),

    # 3. Endonyms, Nicknames, & Flag Emojis
    ("NYC", "USA", "US", "North America"),
    ("SF Bay Area", "USA", "US", "North America"),
    ("ATX", "USA", "US", "North America"),
    ("Menlo Park CA", "USA", "US", "North America"),
    ("Cambridge, MA", "USA", "US", "North America"),
    ("Washington, D.C.", "USA", "US", "North America"),
    ("Wisconsin", "USA", "US", "North America"),
    ("Las Vegas, NV", "USA", "US", "North America"),
    ("Decatur, Al", "USA", "US", "North America"),

    ("Deutschland", "Germany", "DE", "Europe"),
    ("München", "Germany", "DE", "Europe"),
    ("Nürnberg", "Germany", "DE", "Europe"),
    ("Karlsruhe", "Germany", "DE", "Europe"),
    ("Zürich", "Switzerland", "CH", "Europe"),
    ("Zurich, CH", "Switzerland", "CH", "Europe"),
    ("Zug, Switzerland", "Switzerland", "CH", "Europe"),
    ("Luzern; Switzerland", "Switzerland", "CH", "Europe"),
    ("Based in Madrid, Spain 🇪🇸", "Spain", "ES", "Europe"),
    ("BCN", "Spain", "ES", "Europe"),
    ("Braga, Portugal", "Portugal", "PT", "Europe"),
    ("Oslo", "Norway", "NO", "Europe"),
    ("Copenhagen", "Denmark", "DK", "Europe"),
    ("Rotterdam", "Netherlands", "NL", "Europe"),
    ("Groningen, The Netherlands", "Netherlands", "NL", "Europe"),
    ("Eindhoven", "Netherlands", "NL", "Europe"),
    ("Krakow, Poland", "Poland", "PL", "Europe"),
    ("Prague, Czech Republic", "Czechia", "CZ", "Europe"),
    ("Split, Croatia", "Croatia", "HR", "Europe"),
    ("Limassol, Cyprus", "Cyprus", "CY", "Europe"),
    ("Turkiye", "Turkey", "TR", "Europe"),
    ("Tbilisi, Georgia", "Georgia", "GE", "Europe"),
    ("Atlanta, GA", "USA", "US", "North America"),

    ("Bengaluru", "India", "IN", "Asia Pacific"),
    ("Bangalore, India", "India", "IN", "Asia Pacific"),
    ("Kolkata", "India", "IN", "Asia Pacific"),
    ("Bhubaneswar, Odisha", "India", "IN", "Asia Pacific"),
    ("IIT Roorkee", "India", "IN", "Asia Pacific"),
    ("Seoul, Republic of Korea", "South Korea", "KR", "Asia Pacific"),
    ("Tokyo, Japan", "Japan", "JP", "Asia Pacific"),
    ("Shanghai, P.R.China", "China", "CN", "Asia Pacific"),
    ("Krung Thep\u200b Maha\u200b Nakhon (Bangkok), Thailand", "Thailand", "TH", "Asia Pacific"),
    ("Hanoi, Vietnam", "Vietnam", "VN", "Asia Pacific"),
    ("Kuala Lumpur", "Malaysia", "MY", "Asia Pacific"),
    ("Tehran, Iran", "Iran", "IR", "Asia Pacific"),
    ("Tel Aviv", "Israel", "IL", "Asia Pacific"),
    ("TLV", "Israel", "IL", "Asia Pacific"),
    ("Abu-Dhabi, UAE", "UAE", "AE", "Asia Pacific"),
    ("Aotearoa  | New Zealand", "New Zealand", "NZ", "Asia Pacific"),

    ("Brasil", "Brazil", "BR", "Latin America"),
    ("Brasília, DF, Brazil", "Brazil", "BR", "Latin America"),
    ("Santa Catarina, Brazil", "Brazil", "BR", "Latin America"),
    ("Buenos Aires, Argentina", "Argentina", "AR", "Latin America"),
    ("San Isidro, Lima, Peru", "Peru", "PE", "Latin America"),
    ("Nassau, Bahamas", "Bahamas", "BS", "Latin America"),

    ("Lagos State, Nigeria", "Nigeria", "NG", "Africa"),
    ("Nairobi, Kenya", "Kenya", "KE", "Africa"),
    ("Addis Ababa, Ethiopia", "Ethiopia", "ET", "Africa"),
    ("Cape Town", "South Africa", "ZA", "Africa"),
    ("CPT", "South Africa", "ZA", "Africa"),
    ("Mauritius", "Mauritius", "MU", "Africa"),
    ("Zimbabwe", "Zimbabwe", "ZW", "Africa"),

    # 4. Noise + Real Location ("Barcelona | Remote" -> Spain)
    ("Barcelona | Remote", "Spain", "ES", "Europe"),
    ("Milan and everywhere", "Italy", "IT", "Europe"),
]

GOLDEN_NONGEO_CASES = [
    "Earth",
    "Planet Earth",
    "The Blue Planet",
    "Remote",
    "Mempool",
    "The Internet",
    "Internet",
    "Cyberspace",
    "127.0.0.1",
    "::1",
    "localhost",
    "root@localhost",
    "/dev/null",
    "/dev/fd0",
    "The Matrix",
    "The Ether",
    "Mars",
    "Venus",
    "Solar System",
    "Cosmos",
    "Hyperborea",
    "port 8333",
    "₿:8333",
    "TCP/IP",
    "P2P Space",
    "blockchain",
    "bitcoin",
    "No Public Data",
    "UTC:  in subreality",
    "8CAC20548B2B7B850B0BEA957C7A2BD5DFA9B490",
    "https://webchat.freenode.net/?channels=opentransactions&uio=d4",
    "₿ pavol@rusnak.io",
    None,
    "",
    "   ",
]

GOLDEN_REGION_ONLY_CASES = [
    ("Europe", "Europe"),
    ("EU", "Europe"),
    ("Scandinavia", "Europe"),
    ("Latin America", "Latin America"),
    ("Asia", "Asia Pacific"),
    ("Africa", "Africa"),
    ("North America", "North America"),
]


# Regressions found in the 2026-10-20 review: (raw, expected iso2 or None for "no country").
# Flags are support, not residence; a trailing US state beats a homonym city or an ISO code;
# endonyms / ISO3 words only count as a whole segment; codes that are both a country and a
# US state stay ambiguous when written alone.
REGRESSION_CASES = [
    ("Berlin 🇺🇦", "DE"), ("Austin, TX 🇸🇻", "US"), ("Toronto, Canada 🇮🇳", "CA"), ("🇸🇻", "SV"),
    ("Paris, TX", "US"), ("Athens, GA", "US"), ("Dublin, OH", "US"), ("Moscow, Idaho", "US"),
    ("Melbourne, FL", "US"), ("Mexico, NY", "US"), ("Berlin, NH", "US"), ("Lebanon, NH", "US"),
    ("Rome, GA", "US"), ("Cairo, GA", "US"), ("Perth, Scotland", "GB"), ("Sydney, Nova Scotia", "CA"),
    ("Missoula, MT", "US"), ("Boise, ID", "US"), ("Louisville, KY", "US"), ("Bloomington, IN", "US"),
    ("Birmingham, AL", "US"), ("Little Rock, AR", "US"), ("Wilmington, DE", "US"), ("Omaha, NE", "US"),
    ("Smallville, KS", "US"), ("Atlanta, Georgia", "US"), ("Tbilisi, Georgia", "GE"),
    ("Hamburg, DE", "DE"), ("Tel Aviv, IL", "IL"), ("Medellin, CO", "CO"), ("Patna, BR", "IN"),
    ("Smalltown, BR", "BR"), ("Zurich, CH", "CH"), ("Podgorica, ME", "ME"),
    ("Long Island", "US"), ("Long Island, NY", "US"), ("Staten Island", "US"), ("Jersey City", "US"),
    ("New England", "US"), ("Satoshi's Island", None), ("Where you are", None), ("Neuilly sur Seine, France", "FR"),
    ("CA", None), ("IL", None), ("DE", None), ("NL", "NL"), ("UK", "GB"), ("NY", "US"),
    ("Madrid | Amsterdam", "ES"), ("NYC / Berlin", "US"), ("Berlin, Germany / San Francisco, USA", "DE"),
    ("Guinea", "GN"), ("Papua New Guinea", "PG"), ("Niger", "NE"), ("Sudan", "SD"), ("South Sudan", "SS"),
    ("DR Congo", "CD"), ("Dominica", "DM"), ("Москва", "RU"), ("Київ", "UA"), ("北京", "CN"), ("서울", "KR"),
    ("Route 19.0760", None),
]


def run_golden_suite() -> None:
    failures = []
    total = 0

    for raw, exp_country, exp_iso2, exp_region in GOLDEN_COUNTRY_CASES:
        total += 1
        res = resolve_location(raw)
        c = resolve_country(raw)
        r = resolve_region(raw)
        if c != exp_country or res.iso2 != exp_iso2 or r != exp_region:
            failures.append(
                f"COUNTRY FAIL: {raw!r} -> got ({c!r}, {res.iso2!r}, {r!r}, status={res.status}), "
                f"expected ({exp_country!r}, {exp_iso2!r}, {exp_region!r})"
            )

    for raw in GOLDEN_NONGEO_CASES:
        total += 1
        c = resolve_country(raw)
        r = resolve_region(raw)
        if c is not None or r != "Undisclosed":
            failures.append(
                f"NONGEO FAIL: {raw!r} -> got country={c!r}, region={r!r} (expected None, 'Undisclosed')"
            )

    for raw, exp_region in GOLDEN_REGION_ONLY_CASES:
        total += 1
        c = resolve_country(raw)
        r = resolve_region(raw)
        if c is not None or r != exp_region:
            failures.append(
                f"REGION_ONLY FAIL: {raw!r} -> got country={c!r}, region={r!r} (expected None, {exp_region!r})"
            )

    for raw, exp_iso2 in REGRESSION_CASES:
        total += 1
        got = resolve_location(raw).iso2
        if got != exp_iso2:
            failures.append(f"REGRESSION FAIL: {raw!r} -> got {got!r}, expected {exp_iso2!r}")

    precision = (total - len(failures)) / total
    print(f"Golden Test Suite: {total - len(failures)}/{total} passed ({precision:.2%})")
    if failures:
        for f in failures:
            print("  ❌", f)
        sys.exit(1)
    print("✅ All golden geographic tests passed with 100% precision!")


def test_golden_suite():
    """pytest entry point (run_golden_suite exits non-zero on any failure)."""
    run_golden_suite()


if __name__ == "__main__":
    run_golden_suite()
