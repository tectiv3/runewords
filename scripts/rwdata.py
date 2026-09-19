"""Shared rw-data extraction + invariant checks for scripts/sync.py and scripts/verify.py.

The rw-data block lives in index.html between:
    <script id="rw-data" type="application/json"> ... </script>
data.json (repo root) is the editing source of truth and must stay byte-identical
to that embedded block. stdlib only.
"""

from __future__ import annotations

import json
import re

OPEN_TAG = b'<script id="rw-data" type="application/json">'
CLOSE_TAG = b"</script>"

# Counts that are fixed by the game (cube runewords + rune alphabet in S15).
# Class-slice counts are NOT asserted here: they grow as slices get added.
RUNEWORD_COUNT = 19
RUNE_COUNT = 16

# cls value of the pre-row-9 Legacy slice: its acquisition is generic
# (uniquesnotes banner), so `drop` is not required for it.
LEGACY_CLS = "Legacy"

_CLS_RE = re.compile(r"^[A-Z][a-zA-Z]+$")

REQUIRED_FIELDS = ("name", "slot", "effect")


class DataError(Exception):
    """Raised on any structural invariant violation or malformed markup."""


def extract_block(html: bytes) -> bytes:
    """Return the exact bytes between the rw-data script tags."""
    try:
        i = html.index(OPEN_TAG) + len(OPEN_TAG)
        j = html.index(CLOSE_TAG, i)
    except ValueError as e:
        raise DataError(f"rw-data script tags not found in index.html: {e}") from e
    return html[i:j]


def parse_block(block: bytes) -> dict:
    try:
        return json.loads(block.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise DataError(f"rw-data block is not valid UTF-8 JSON: {e}") from e


def check_invariants(data: dict) -> list[tuple[str, int]]:
    """Assert structural invariants; return [(cls, count)] sorted for the summary.

    Invariants:
      - top-level keys: asof, patch, tier, runewords, runes, howto, uniques, uniquesnotes
      - exactly 19 runewords, 16 runes (fixed by the game)
      - unique names are unique across uniques
      - every unique has non-empty name, slot, effect; drop required unless cls=Legacy
      - cls values: single capitalized word, and each distinct value used by >=2
        uniques (typo guard; slices are added wholesale, so a singleton cls is
        almost certainly a misspelling of an existing class)
    """
    expected_keys = {
        "asof",
        "patch",
        "tier",
        "runewords",
        "runes",
        "howto",
        "uniques",
        "uniquesnotes",
        "bosses",
    }
    if set(data.keys()) != expected_keys:
        raise DataError(
            f"top-level keys mismatch: got {sorted(data.keys())}, "
            f"want {sorted(expected_keys)}"
        )

    # Bosses (cross-reference tab): structure only — `match` (drop-field
    # substring for loot lookup) and `note` are optional; WN capstones rely on
    # notes instead of loot matches.
    for b in data["bosses"]:
        for field in ("name", "tier", "loc"):
            if not b.get(field):
                raise DataError(f"boss {b.get('name') or '<missing>'}: missing {field}")

    if len(data["runewords"]) != RUNEWORD_COUNT:
        raise DataError(f"expected {RUNEWORD_COUNT} runewords, got {len(data['runewords'])}")
    if len(data["runes"]) != RUNE_COUNT:
        raise DataError(f"expected {RUNE_COUNT} runes, got {len(data['runes'])}")

    # Legacy uniques have no per-item `drop` (their acquisition is generic,
    # served by the slice banner); the banner source key must exist and be live.
    notes = data["uniquesnotes"]
    if not isinstance(notes, dict) or not notes.get("acquisition"):
        raise DataError("uniquesnotes.acquisition (Legacy drop-source banner) missing or empty")
    for key, value in notes.items():
        if not isinstance(value, str) or not value.strip():
            raise DataError(f"uniquesnotes.{key} must be a non-empty string")

    uniques = data["uniques"]
    names: set[str] = set()
    cls_counts: dict[str, int] = {}
    for u in uniques:
        where = u.get("name") or "<missing name>"
        for field in REQUIRED_FIELDS:
            if not u.get(field):
                raise DataError(f"unique '{where}': missing or empty '{field}'")
        if u["name"] in names:
            raise DataError(f"duplicate unique name: '{u['name']}'")
        names.add(u["name"])
        cls = u.get("cls")
        if not cls or not _CLS_RE.fullmatch(cls):
            raise DataError(f"unique '{where}': bad cls value {cls!r}")
        if cls != LEGACY_CLS and not u.get("drop"):
            raise DataError(f"unique '{where}' (cls={cls}): missing or empty 'drop'")
        cls_counts[cls] = cls_counts.get(cls, 0) + 1

    for cls, count in sorted(cls_counts.items()):
        if count < 2:
            raise DataError(
                f"cls '{cls}' used by only {count} unique(s) — typo or stray slice? "
                f"(known classes: {', '.join(sorted(cls_counts))})"
            )

    return sorted(cls_counts.items(), key=lambda kv: (-kv[1], kv[0]))


def summary(cls_counts: list[tuple[str, int]], data: dict) -> str:
    parts = [f"{cls} {n}" for cls, n in cls_counts]
    return (
        f"runewords: {len(data['runewords'])}, runes: {len(data['runes'])}, "
        f"uniques: {len(data['uniques'])} "
        f"(asof {data['asof']}, patch {data['patch']}, tier {data['tier']})\n"
        f"cls counts: {', '.join(parts)}"
    )
