# D4 Season 15 Runewords — single-page reference

Status: spec agreed (grill session, 2026-09-18). Source article: aoeah.com/news/4825.

## Decisions

| # | Branch | Decision |
|---|--------|----------|
| 1 | Data authority | Official-first consensus: patch notes > maxroll/wowhead datamines > majority agreement (d4guides/Sportskeeda…). Disputed stats render with a visible ⚠ unconfirmed marker. |
| 2 | Scope | Only the 19 new S15 Horadric Cube runewords. Old socket runewords excluded. |
| 3 | Inventory | Personal rune tally (+/− per rune). Cards show craftable ✓ or "missing Jah×1". "Craftable now" filter. Persisted in localStorage. |
| 4 | Ranking | No power tiers. Rank badges/sort removed. Sorts: A–Z (default), rune count, slot. |
| 5 | Images | Hotlink tooltip screenshots (scout-collected URLs) as expandable thumbnails; `onerror` hides rotted images silently. |
| 6 | Views | Two tabs: **Runewords** (list) and **Runes** (rarity, category, drop source, used-by links; doubles as the inventory tally pad). |
| 7 | Hosting | GitHub Pages, public repo created via `gh repo create` (user-granted push permission for this deliverable only). |
| 8 | Updates | Manual: edit embedded JSON, commit, push. Footer stamps "data as of <date>". |

## Architecture

- `index.html` — single self-contained file, no dependencies, mobile-first (sticky search, chip rows, `<details>` cards).
- Data lives in `<script id="rw-data" type="application/json">` — single source of truth, validated via JSON parse.
- Rune categories: `evo` (new evocation), `rit` (new ritual), `old` (pre-S15 runes).
- Runeword fields: name, slot, group, runes[{n,c,x}], effects[], uses, tags[], optional img (hotlink), optional unconfirmed[] stat indexes.

## Open items

- Scout report (subagent 01a0b44d) integration: stat corrections per decision 1, image URLs per decision 5, "Pledge" naming check, rune rarity/drop data for the Runes tab.
- Deploy after integration + verification.
