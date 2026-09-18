# D4 Season 15 Runewords — single-page reference

Status: v2 spec — revised after scout verification + plan-critic review. Data as of 2026-09-18.

## Decisions

| # | Branch | Decision |
|---|--------|----------|
| 1 | Data authority | **Resolution rule:** canonical = d4guides + Sportskeeda agreement (both derive from patch 3.2.1 client datamine); disagreement → publish majority + per-stat ⚠; single-source claims → ⚠ mandatory; unknown values (`?`) → shown as ⚠ unknown. Global banner: values are datamined, partially unverified in-game. |
| 2 | Scope | **Rebranded as full S15 reference** (user decision, 2026-09-18): Runewords | Runes | Uniques tabs. Uniques tab = the 10 Legacy Uniques (world drops, patch-note values, 4 items carry client-data dispute marks) + Monarch base note + charms footnote. Talisman charms = possible future tab. Runewords/runes data unchanged (S15 cube system only). |
| 3 | Inventory | Personal rune tally (+/− per rune). Cards show craftable ✓ or full missing list ("missing Ber×1, Mal×1"). "Craftable" filter chip (only active when inventory has ≥1 rune). Persisted in localStorage (`rw-inv-v2`, try/catch-wrapped for iOS private mode). |
| 4 | Ranking | No power tiers. Sorts: A–Z (default), rune count, slot-group chips. |
| 5 | Images | Hotlink verified-200 d4guides/maxroll URLs as expandable thumbnails; `referrerpolicy="no-referrer"`, `loading="lazy"`, `onerror` hides silently. |
| 6 | Views | Two tabs: **Runewords** and **Runes**. Runes tab: category (Invocation/Ritual/old), socketed effect (game8 — single source, noted), rarity (disputed — noted), drop sources, "used by" links, doubles as inventory tally pad. |
| 7 | Hosting | GitHub Pages on `main` root, repo `tectiv3/runewords` (remote added by user; push for this deliverable is user-approved). Enable Pages idempotently (GET before POST); verify with retry loop + content grep. |
| 8 | Updates | Manual edits to the embedded JSON block; footer stamps "data as of <date>". |

## Data notes (from scout cross-verification)

- aoeah's published values were frequently ~2× consensus — consistent with them listing **ancestral** recipes unlabeled. Page shows **normal-tier** consensus values; how-to explains ancestral doubles.
- aoeah-only errors corrected: Ancient's Pledge stats, Zephyr (D2 copy-paste), base-item lists (84 total variants across the set), "sword/staff" claims.
- Rune order: 3 sources say cube order matters, aoeah says no → recipes shown in d4guides order + ⚠ note.
- Rune naming: canonical `Amn` (not "Am"); schema assertion: every recipe rune ∈ runes array.
- Categories renamed: **Invocation** (not "Evocation") per standard usage.

## Architecture

- `index.html` — single self-contained file, no dependencies, mobile-first.
- Single source of truth: `<script id="rw-data" type="application/json">` block, embedded verbatim from handoff `data.json` (deleted only after deep-equal check passes).
- Runeword schema: `{name, groups[], bases[], baseCount, runes[{n,x?}] (ordered), effects[] (strings; suffix "\|?" = unconfirmed), uses, tags[], img?}`
  - groups enum: `1H | 2H | Ranged | Chest | Helm | Offhand` (multi-group OR matching)
  - assertion: Σ baseCount = 84
- Rune schema: `{n, cat: inv|rit|old, fx (socketed effect text), rare, drops}`
- Implementation: two sequential worker runs with main-thread checkpoint:
  - **Run A:** data embed + Runewords tab rebuild (search/groups/sorts/⚠/images/how-to copy/footer).
  - **Run B:** Runes tab + inventory subsystem (localStorage, craftability, craftable filter).
- Verification: JSON schema assertions, node syntax check, HTMLParser, **runtime DOM test** (jsdom via nix: renders 19 cards, tab switch, chip filter, localStorage persist, image element), then commit + deploy.

## How-to copy (authored, verbatim into page)

Craft: 1) White (Common) base of a valid type — Item Power carries to the result, use high-IP bases for expensive recipes. 2) Horadric Cube (requires Lord of Hatred campaign), base + runes in listed order (order reported to matter ⚠ disputed). 3) Transmute; unknown recipes preview as ???.
Notes: result is a Unique — enchant OK (single source ⚠), tempering not possible, masterwork unconfirmed ⚠; every recipe has normal & ancestral versions (ancestral ≈ 2× values — normal shown); salvage may return runes ⚠; seasonal quest reportedly grants chest base + Tal + Eth ⚠; class access via base item (Spiritborn excluded from most 1H recipes); datamined from patch 3.2.1 client, Blizzard never documented the system — found by players (Dioxide first).
Farm: Waking Nightmares (primary, game8) · Countess (~5/kill ⚠) · jeweler 3:1 rune ladder (Ber/Ith reachable ⚠) · Helltide/NMD elites · Purveyor · trade · Rebirth.
