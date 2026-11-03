"""
geography.py — Enterprise Geographic Attribution & Normalization Engine.

Single source of truth for contributor geographic classification across:
- attribution and location history (`scripts/utils/geo/`, used by `unify_contributors.py`,
  `resolve_geography.py`, `build_geo_history.py`)
- Phase 4 delivery (`scripts/04_deliver/geo_artifacts.py`)
- Ecosystem scaling (`orange-eco-data`, 50k+ contributors)

Architecture:
1. Reference Taxonomy (`metadata/geo/countries.csv`, `admin1.csv`, `location_aliases.csv`, `nongeo_terms.txt`)
2. Boundary-safe segment & n-gram tokenizer (zero substring collisions: `, ca` never matches `, Canada`,
   `uk` never matches `Ukraine` or `Fukuoka`, `New Mexico` never matches `Mexico`).
3. Disambiguation rules R1–R7 (explicit country constraints, admin1 context checks, population-weighted city ranking,
   multi-location handling, and timezone/TLD signal fusion).
"""

import csv
import json
import os
import re
import unicodedata
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

TAXONOMY_VERSION = "2026.10.1"

# Canonical display regions in presentation order (backward compatible with existing charts)
REGIONS = [
    "North America",
    "Europe",
    "Asia Pacific",
    "Latin America",
    "Africa",
    "Undisclosed",
]

# UN M49 derived 6 macro-regions (splits Oceania, puts Western Asia in Asia)
UN_MACRO_REGIONS = [
    "North America",
    "Latin America & Caribbean",
    "Europe",
    "Asia",
    "Oceania",
    "Africa",
    "Undisclosed",
]

_MODULE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _MODULE_DIR.parent.parent
_GEO_META_DIR = _PROJECT_ROOT / "metadata" / "geo"


@dataclass(frozen=True)
class CountryMeta:
    iso2: str
    iso3: str
    m49: str
    display_name: str
    m49_region: str
    m49_subregion: str
    macro_region: str
    un_macro_region: str
    sovereign_iso2: str
    wb_income: str
    flag: str


@dataclass(frozen=True)
class GeoResult:
    iso2: Optional[str]
    iso3: Optional[str]
    country_name: Optional[str]
    m49_subregion: Optional[str]
    macro_region: str
    un_macro_region: str
    wb_income: Optional[str]
    status: str  # resolved | region_only | ambiguous | multi | non_geographic | unparsed | empty
    confidence: float
    evidence: Tuple[str, ...] = ()
    alternatives: Tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Reference Data Loader
# ---------------------------------------------------------------------------

class GeoGazetteer:
    def __init__(self) -> None:
        self.countries_by_iso2: Dict[str, CountryMeta] = {}
        self.countries_by_name: Dict[str, CountryMeta] = {}
        self.nongeo_terms: Set[str] = set()
        # token -> list of (target_iso2, token_type, admin1_code, pop_weight)
        self.token_map: Dict[str, List[Tuple[str, str, str, int]]] = {}
        # (country_iso2, admin1_code_lower) -> admin1_name
        self.admin1_codes: Dict[Tuple[str, str], str] = {}
        # admin1_code_lower -> list of country_iso2
        self.code2_to_admin1_countries: Dict[str, List[str]] = {}
        self._load()

    def _add_token(self, token: str, target_iso2: str, token_type: str, admin1_code: str = "", pop_weight: int = 80) -> None:
        norm = normalize_text(token).strip()
        if not norm:
            return
        bucket = self.token_map.setdefault(norm, [])
        entry = (target_iso2, token_type, admin1_code.upper(), int(pop_weight))
        if entry not in bucket:
            bucket.append(entry)

    def _load(self) -> None:
        countries_path = _GEO_META_DIR / "countries.csv"
        if countries_path.exists():
            with open(countries_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    meta = CountryMeta(
                        iso2=row["iso2"].strip(),
                        iso3=row["iso3"].strip(),
                        m49=row["m49"].strip(),
                        display_name=row["display_name"].strip(),
                        m49_region=row["m49_region"].strip(),
                        m49_subregion=row["m49_subregion"].strip(),
                        macro_region=row["macro_region"].strip(),
                        un_macro_region=row.get("un_macro_region", row["macro_region"]).strip(),
                        sovereign_iso2=row["sovereign_iso2"].strip(),
                        wb_income=row["wb_income"].strip(),
                        flag=row["flag"].strip(),
                    )
                    self.countries_by_iso2[meta.iso2] = meta
                    self.countries_by_name[meta.display_name.lower()] = meta
                    self._add_token(meta.display_name, meta.iso2, "country", "", 100)
                    self._add_token(meta.iso3, meta.iso2, "iso3", "", 95)

        admin1_path = _GEO_META_DIR / "admin1.csv"
        if admin1_path.exists():
            with open(admin1_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    c_iso2 = row["country_iso2"].strip().upper()
                    a_code = row["admin1_code"].strip().upper()
                    a_name = row["admin1_name"].strip()
                    self.admin1_codes[(c_iso2, a_code.lower())] = a_name
                    self.code2_to_admin1_countries.setdefault(a_code.lower(), []).append(c_iso2)
                    # Register full state/province name
                    # Special handling for "Georgia" (both US state and country GE)
                    if normalize_text(a_name) == "georgia" and c_iso2 == "US":
                        self._add_token(a_name, "US", "admin1", "GA", 85)
                    else:
                        self._add_token(a_name, c_iso2, "admin1", a_code, 90)

        nongeo_path = _GEO_META_DIR / "nongeo_terms.txt"
        if nongeo_path.exists():
            with open(nongeo_path, "r", encoding="utf-8") as f:
                for line in f:
                    t = normalize_text(line.strip())
                    if t and not t.startswith("#"):
                        self.nongeo_terms.add(t)

        aliases_path = _GEO_META_DIR / "location_aliases.csv"
        if aliases_path.exists():
            with open(aliases_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self._add_token(
                        row["token"],
                        row["target_iso2"].strip(),
                        row["token_type"].strip(),
                        row.get("admin1_code", "").strip(),
                        int(row.get("pop_weight", 85) or 85),
                    )


# ---------------------------------------------------------------------------
# Normalization & Tokenization Helpers
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|::1\b")
_HEX_RE = re.compile(r"\b[0-9a-fA-F]{16,}\b")
_COORD_RE = re.compile(r"[-+]?\d{1,2}\.\d+\s*°?\s*[ns]?\s*[,/\s]\s*[-+]?\d{1,3}\.\d+\s*°?\s*[ew]?", re.I)
_SEP_RE = re.compile(r"\s*(?:[,;|/·•()]|\s[-–—]\s|\band\b|&)\s*")
_LIST_SEP_RE = re.compile(r"[;|/·•&]|\s[-–—]\s|\band\b")  # separators that list places, unlike commas
_PREFIX_NOISE_RE = re.compile(r"^(?:based in|located in|living in|currently in|from|near|greater)\s+", re.I)
_SUFFIX_NOISE_RE = re.compile(r"\s+(?:area|metro|metropolitan area|region)$", re.I)

_LEGACY_TO_UN_REGION = {"Latin America": "Latin America & Caribbean", "Asia Pacific": "Asia"}

# A trailing 2-letter code that is a state/province code in several countries goes to the
# country with by far the most contributors ("Smalltown, WA" is far more likely Washington).
_ADMIN1_PRIORITY = ["US", "CA", "AU", "IN", "BR", "DE", "GB"]


def _whole_segment_only(token_type: str, token: str) -> bool:
    """Token types that only count when they are a whole segment: ISO3 codes ("ARE", "BEN",
    "SUR" are also ordinary words), endonyms ("Island" is Iceland in German, so "Long Island"
    must not match), and short nicknames ("SF", "OZ")."""
    return token_type in ("iso3", "endonym") or (token_type == "nickname" and len(token) <= 3)


def clean_location(location: Any) -> Optional[str]:
    """
    Sanitizes raw location inputs across DataFrame/Parquet/JSON boundaries.
    Guarantees returning a non-empty stripped string, or None for all missing/invalid values.
    """
    if location is None:
        return None
    try:
        if pd.isna(location):
            return None
    except Exception:
        pass

    if not isinstance(location, str):
        return None

    cleaned = location.strip()
    return cleaned if cleaned else None


def extract_flag_iso2(text: str) -> List[str]:
    """
    Extracts ISO2 country codes from Unicode Regional Indicator Symbol pairs (flag emojis).
    For example: 🇩🇪 -> 'DE', 🇺🇸 -> 'US', 🇬🇧 -> 'GB'.
    """
    flags: List[str] = []
    chars = list(text)
    i = 0
    while i < len(chars) - 1:
        c1, c2 = ord(chars[i]), ord(chars[i + 1])
        if 0x1F1E6 <= c1 <= 0x1F1FF and 0x1F1E6 <= c2 <= 0x1F1FF:
            iso2 = chr(c1 - 0x1F1E6 + ord("A")) + chr(c2 - 0x1F1E6 + ord("A"))
            if iso2 == "UK":
                iso2 = "GB"
            flags.append(iso2)
            i += 2
        else:
            i += 1
    return flags


def normalize_text(text: str) -> str:
    """
    Normalizes unicode text by removing zero-width characters, accents/diacritics, and lowercasing.
    Handles special Nordic/Germanic characters (ø->o, ł->l, ß->ss, æ->ae).
    """
    # Strip zero-width spaces
    text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
    # Replace special Latin letters that NFD doesn't decompose to ASCII
    text = (
        text.replace("ø", "o").replace("Ø", "o")
        .replace("ł", "l").replace("Ł", "l")
        .replace("ß", "ss")
        .replace("æ", "ae").replace("Æ", "ae")
        .replace("đ", "d").replace("Đ", "d")
    )
    decomposed = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return decomposed.lower().strip()


_GAZETTEER: Optional[GeoGazetteer] = None


def get_gazetteer() -> GeoGazetteer:
    global _GAZETTEER
    if _GAZETTEER is None:
        _GAZETTEER = GeoGazetteer()
    return _GAZETTEER


def _make_empty_result(status: str = "empty") -> GeoResult:
    return GeoResult(
        iso2=None,
        iso3=None,
        country_name=None,
        m49_subregion=None,
        macro_region="Undisclosed",
        un_macro_region="Undisclosed",
        wb_income=None,
        status=status,
        confidence=0.0,
    )


def _make_country_result(
    iso2: str,
    status: str = "resolved",
    confidence: float = 0.9,
    evidence: Tuple[str, ...] = (),
    alternatives: Tuple[str, ...] = (),
) -> GeoResult:
    gaz = get_gazetteer()
    meta = gaz.countries_by_iso2.get(iso2)
    if not meta:
        return _make_empty_result("unparsed")
    return GeoResult(
        iso2=meta.iso2,
        iso3=meta.iso3,
        country_name=meta.display_name,
        m49_subregion=meta.m49_subregion,
        macro_region=meta.macro_region,
        un_macro_region=meta.un_macro_region,
        wb_income=meta.wb_income,
        status=status,
        confidence=confidence,
        evidence=evidence,
        alternatives=alternatives,
    )


@lru_cache(maxsize=16384)
def resolve_location(raw: Optional[str]) -> GeoResult:
    """
    Core deterministic classifier for a single raw location string.
    Applies normalization, non-geographic filtering, segment tokenization,
    n-gram hash lookup, and disambiguation rules R1–R7.

    Flag emoji are only a fallback: "Berlin 🇺🇦" or "Austin, TX 🇸🇻" usually express support,
    not residence, so a flag decides the country only when the text names no place.
    """
    cleaned = clean_location(raw)
    if not cleaned:
        return _make_empty_result("empty")

    gaz = get_gazetteer()
    flag_isos = list(dict.fromkeys(f for f in extract_flag_iso2(cleaned) if f in gaz.countries_by_iso2))
    res = _resolve_text(cleaned)

    if not flag_isos:
        return res
    if res.status in ("empty", "non_geographic", "unparsed"):
        return _make_country_result(flag_isos[0], "resolved", 0.70, (f"flag:{flag_isos[0]}",), tuple(flag_isos[1:]))
    extra = tuple(f for f in flag_isos if f != res.iso2 and f not in res.alternatives)
    return replace(res, alternatives=res.alternatives + extra) if extra else res


def _resolve_text(cleaned: str) -> GeoResult:
    gaz = get_gazetteer()

    # Strip URLs, emails, IPs, hex strings
    s = _URL_RE.sub(" ", cleaned)
    s = _EMAIL_RE.sub(" ", s)
    s = _IP_RE.sub(" ", s)
    s = _HEX_RE.sub(" ", s)

    norm = normalize_text(s)
    # Remove emoji / symbols except word chars, spaces, commas, periods, hyphens, slashes, pipes
    norm = re.sub(r"[^\w\s,.;|/·•()&-]", " ", norm)
    norm = re.sub(r"\s+", " ", norm).strip(" ,.;|-")

    if not norm:
        return _make_empty_result("non_geographic")

    # Whole-string exact check against nongeo_terms
    if norm in gaz.nongeo_terms:
        return _make_empty_result("non_geographic")

    # Whole-string exact check in gazetteer before splitting. A bare city is less certain than
    # a country name ("Valencia" and "San Jose" have homonyms abroad).
    if norm in gaz.token_map:
        hits = gaz.token_map[norm]
        if len(hits) == 1 and not hits[0][0].startswith("REGION:"):
            conf = 0.85 if hits[0][1] in ("city", "nickname") else 0.95
            return _make_country_result(hits[0][0], "resolved", conf, (f"exact:{norm}",))

    # Split into segments by comma / pipe / slash / parens / hyphen
    raw_segs = [seg.strip(" .") for seg in _SEP_RE.split(norm) if seg.strip(" .")]
    segs: List[str] = []
    had_nongeo = False
    for seg in raw_segs:
        seg_clean = _PREFIX_NOISE_RE.sub("", seg).strip(" .")
        seg_clean = _SUFFIX_NOISE_RE.sub("", seg_clean).strip(" .")
        if not seg_clean or seg_clean in gaz.nongeo_terms:
            had_nongeo = True
            continue
        segs.append(seg_clean)

    if not segs:
        return _make_empty_result("non_geographic")

    # Collect candidates across segments
    # Each candidate: (seg_idx, is_whole_seg, is_last_seg, token, target_iso2, token_type, admin1_code, pop_weight)
    candidates: List[Tuple[int, bool, bool, str, str, str, str, int]] = []

    for idx, seg in enumerate(segs):
        is_last = idx == len(segs) - 1

        # 1. Try whole segment first
        if seg in gaz.token_map:
            for target_iso2, token_type, admin1_code, pop_weight in gaz.token_map[seg]:
                candidates.append((idx, True, is_last, seg, target_iso2, token_type, admin1_code, pop_weight))
            continue

        # 2. Check if segment is a 2-letter code (Rule R2)
        if len(seg) == 2 and seg.isalpha():
            candidates.append((idx, True, is_last, seg, f"CODE2:{seg}", "code2", seg.upper(), 75))
            continue

        # 3. Try n-grams (4, 3, 2, 1 words) within segment, longest first
        # Once a multi-word n-gram matches a span of words, mark those words covered so "new mexico"
        # never also matches "mexico", and "united kingdom" never also matches "uk".
        words = [w.strip(".") for w in seg.split() if w.strip(".")]
        covered = [False] * len(words)
        for n in range(min(4, len(words)), 0, -1):
            for start in range(len(words) - n + 1):
                if any(covered[start : start + n]):
                    continue
                gram = " ".join(words[start : start + n])
                if gram in gaz.nongeo_terms:
                    for k in range(start, start + n):
                        covered[k] = True
                    had_nongeo = True
                    continue
                whole = n == len(words)
                hits = [h for h in gaz.token_map.get(gram, []) if whole or not _whole_segment_only(h[1], gram)]
                if hits:
                    for target_iso2, token_type, admin1_code, pop_weight in hits:
                        candidates.append((idx, whole, is_last, gram, target_iso2, token_type, admin1_code, pop_weight))
                    for k in range(start, start + n):
                        covered[k] = True
                elif n == 1 and len(gram) == 2 and gram.isalpha() and len(words) > 1 and start == len(words) - 1:
                    # Trailing 2-letter code in a space-separated string like "Menlo Park CA" or "Chicago, IL USA"
                    candidates.append((idx, False, is_last, gram, f"CODE2:{gram}", "code2", gram.upper(), 70))
                    covered[start] = True

    if not candidates:
        return _make_empty_result("non_geographic" if had_nongeo else "unparsed")

    # Separate region-only candidates
    region_cands = [c for c in candidates if c[4].startswith("REGION:")]
    geo_cands = [c for c in candidates if not c[4].startswith("REGION:")]

    if not geo_cands and region_cands:
        reg_name = region_cands[0][4].split(":", 1)[1]
        # Region aliases point at the legacy chart buckets; give the UN macro-region its own name.
        un_name = "Oceania" if region_cands[0][3] == "oceania" else _LEGACY_TO_UN_REGION.get(reg_name, reg_name)
        return GeoResult(
            iso2=None,
            iso3=None,
            country_name=None,
            m49_subregion=None,
            macro_region=reg_name,
            un_macro_region=un_name,
            wb_income=None,
            status="region_only",
            confidence=0.75,
            evidence=(f"region:{region_cands[0][3]}",),
        )

    # Resolve CODE2 candidates using Rule R2 (preceding city/admin1 context)
    resolved_cands: List[Tuple[int, bool, bool, str, str, str, str, int]] = []
    prior_cities = [(c[4], c[6]) for c in geo_cands if c[5] in ("city", "nickname", "admin1") and not c[4].startswith("CODE2:")]
    standalone_ambiguous: Tuple[str, ...] = ()

    for c in geo_cands:
        seg_idx, is_whole, is_last, tok, target, ttype, adm1, weight = c
        if not target.startswith("CODE2:"):
            resolved_cands.append(c)
            continue

        code_lower = tok.lower()
        code_upper = tok.upper()
        matched_via_context = False

        # Rule R2a: Does a preceding city have this admin1 code? (e.g., "Perth, WA" -> AU-WA, "London, ON" -> CA-ON, "Austin, TX" -> US-TX)
        for city_country, city_adm1 in prior_cities:
            if city_adm1 == code_upper or (city_country, code_lower) in gaz.admin1_codes:
                resolved_cands.append((seg_idx, is_whole, is_last, tok, city_country, "admin1_code", code_upper, 96))
                matched_via_context = True
                break

        if matched_via_context:
            continue

        # Rule R2b: Is it a valid ISO2 country code following a city in that country? (e.g., "Melbourne, AU" -> AU, "Zurich, CH" -> CH, "London, UK" -> GB)
        iso_lookup = "GB" if code_upper == "UK" else code_upper
        if any(city_country == iso_lookup for city_country, _ in prior_cities):
            resolved_cands.append((seg_idx, is_whole, is_last, tok, iso_lookup, "country_code", "", 98))
            continue

        admin_countries = gaz.code2_to_admin1_countries.get(code_lower, [])
        is_iso = iso_lookup in gaz.countries_by_iso2
        # "Town, ST" is overwhelmingly a US habit, so only a US state code outranks the ISO country
        # it collides with ("MT" Montana not Malta, "AL" Alabama not Albania); other countries'
        # state codes ("BR" Bihar, "CH" Chandigarh, "NL" Newfoundland) yield to the ISO country.
        us_state = "US" in admin_countries
        admin_country = next((p for p in _ADMIN1_PRIORITY if p in admin_countries), admin_countries[0]) if admin_countries else None

        # Rule R2c: trailing code after an unknown place ("Missoula, MT", "Smallville KS", "Lyon, FR").
        if (len(segs) > 1 and is_last) or not is_whole:
            if us_state or (admin_country and not is_iso):
                resolved_cands.append((seg_idx, is_whole, is_last, tok, "US" if us_state else admin_country, "admin1_code", code_upper, 88))
            elif is_iso:
                resolved_cands.append((seg_idx, is_whole, is_last, tok, iso_lookup, "country_code", "", 85))
            continue

        # Rule R7: Standalone 2-letter string ("UK", "NL", "NY"). Only written in capitals (or "uk"/"us")
        # counts, and a code that is both a country and a US state ("CA", "IL", "DE", "IN") stays ambiguous.
        if len(segs) == 1 and is_whole and (cleaned.strip().isupper() or code_lower in ("uk", "us")):
            if is_iso and us_state:
                standalone_ambiguous = (iso_lookup, "US")
            elif is_iso:
                resolved_cands.append((seg_idx, is_whole, is_last, tok, iso_lookup, "country_code", "", 75))
            elif admin_countries:
                country = next((p for p in _ADMIN1_PRIORITY if p in admin_countries), admin_countries[0])
                resolved_cands.append((seg_idx, is_whole, is_last, tok, country, "admin1_code", code_upper, 75))

    if not resolved_cands:
        if standalone_ambiguous:
            return replace(_make_empty_result("ambiguous"), alternatives=standalone_ambiguous)
        return _make_empty_result("unparsed")

    # Rule R0: the rightmost segment decides when it names a state/province or a country. In
    # "Paris, TX", "Mexico, NY" or "Perth, Scotland" the earlier place is a homonym. Only a second,
    # unrelated country elsewhere ("Berlin, Germany / Austin, USA") makes the string multi-location.
    # Applies to comma hierarchies only; "NYC / Berlin" or "Madrid | Amsterdam" list places.
    level = {"country": "country", "endonym": "country", "iso3": "country", "country_code": "country",
             "admin1": "admin1", "admin1_code": "admin1"}
    hierarchical = not _LIST_SEP_RE.search(norm)
    last_idx = len(segs) - 1
    last = [c for c in resolved_cands if c[0] == last_idx and c[5] in level] if hierarchical else []
    last_countries = list(dict.fromkeys(c[4] for c in last))
    if len(segs) > 1 and len(last_countries) > 1:
        # "Atlanta, Georgia" vs "Tbilisi, Georgia": keep the reading the earlier segments support.
        earlier = {c[4] for c in resolved_cands if c[0] != last_idx}
        consistent = [x for x in last_countries if x in earlier]
        if len(consistent) == 1:
            last = [c for c in last if c[4] == consistent[0]]
            last_countries = consistent
    if len(segs) > 1 and len(last_countries) == 1:
        target_c = last_countries[0]
        conflicting = [
            i for i in range(last_idx)
            if not any(c[4] == target_c for c in resolved_cands if c[0] == i)
            and any(c[5] in ("country", "endonym", "iso3", "country_code") for c in resolved_cands if c[0] == i)
        ]
        state_level = all(level[c[5]] == "admin1" for c in last)
        if not conflicting or state_level:
            homonyms = tuple(dict.fromkeys(c[4] for c in resolved_cands if c[4] != target_c))
            return _make_country_result(
                target_c,
                "resolved",
                0.90 if state_level else 0.95,
                tuple(f"{c[5]}:{c[3]}" for c in resolved_cands if c[4] == target_c),
                homonyms,
            )

    # Rule R1: Explicit country / endonym / iso3 / verified country_code tokens
    explicit_countries = [
        c for c in resolved_cands
        if c[5] in ("country", "endonym", "iso3", "country_code")
        and not (c[3] == "georgia" and len(segs) == 1)
    ]

    if explicit_countries:
        distinct_explicit = list(dict.fromkeys(c[4] for c in explicit_countries))

        if len(distinct_explicit) == 1:
            return _make_country_result(
                distinct_explicit[0],
                "resolved",
                0.95,
                tuple(f"{c[5]}:{c[3]}" for c in explicit_countries),
            )
        else:
            # Check if it's "Hongkong, China" -> HK
            if set(distinct_explicit) == {"HK", "CN"}:
                return _make_country_result("HK", "resolved", 0.95, ("country:hong kong",))
            # Multi-country string: e.g. "Hong Kong / Canada / Tropics" -> first listed is primary, status="multi"
            first_c = distinct_explicit[0]
            return _make_country_result(
                first_c,
                "multi",
                0.85,
                tuple(f"{c[5]}:{c[3]}" for c in explicit_countries),
                tuple(distinct_explicit),
            )

    # Check if all candidates agree on a single country (e.g. "San Francisco, CA", "Toronto, ON", "Berlin")
    cand_countries = list(dict.fromkeys(c[4] for c in resolved_cands))
    if len(cand_countries) == 1:
        best_c = max(resolved_cands, key=lambda x: x[7])
        conf = 0.92 if len(resolved_cands) >= 2 else (0.88 if best_c[7] >= 88 else 0.78)
        return _make_country_result(
            cand_countries[0],
            "resolved",
            conf,
            tuple(f"{c[5]}:{c[3]}" for c in resolved_cands),
        )

    # Check if segments are peer cities in different countries (e.g., "Madrid | Amsterdam", "Nuremberg, Horsens, Brasov")
    segs_with_hits = list(dict.fromkeys(c[0] for c in resolved_cands))
    if len(segs_with_hits) > 1:
        first_seg_cands = [c for c in resolved_cands if c[0] == segs_with_hits[0]]
        first_best = max(first_seg_cands, key=lambda x: x[7])
        return _make_country_result(
            first_best[4],
            "multi",
            0.82,
            tuple(f"{c[5]}:{c[3]}" for c in resolved_cands),
            tuple(cand_countries),
        )

    # Single segment naming a country and a state of another country ("Georgia"): ambiguous,
    # left for the timezone tie-break in scripts/utils/geo/attribution.py.
    types = {c[5] for c in resolved_cands}
    if "admin1" in types and types & {"country", "endonym"}:
        top = max(resolved_cands, key=lambda x: x[7])
        return _make_country_result(top[4], "ambiguous", 0.60, (f"{top[5]}:{top[3]}",), tuple(cand_countries))

    # Single segment with multiple candidate countries: pick highest weight, mark ambiguous if close
    sorted_cands = sorted(resolved_cands, key=lambda x: x[7], reverse=True)
    top = sorted_cands[0]
    second = sorted_cands[1]
    if top[7] - second[7] >= 10:
        return _make_country_result(top[4], "resolved", 0.80, (f"{top[5]}:{top[3]}",), tuple(cand_countries))
    else:
        return _make_country_result(top[4], "ambiguous", 0.60, (f"{top[5]}:{top[3]}",), tuple(cand_countries))


# ---------------------------------------------------------------------------
# Public Backward-Compatible Wrappers
# ---------------------------------------------------------------------------

def resolve_country(location: Any) -> Optional[str]:
    """
    Maps an arbitrary raw location (str, None, NaN, float) to a canonical Country display name.
    Returns None if undisclosed, non-geographic, region-only, or unmapped.
    """
    res = resolve_location(clean_location(location))
    return res.country_name


def resolve_region(location: Any) -> str:
    """
    Maps an arbitrary raw location (str, None, NaN, float) to a canonical macro-region.
    Always returns one of REGIONS.
    """
    res = resolve_location(clean_location(location))
    return res.macro_region if res.macro_region in REGIONS else "Undisclosed"
