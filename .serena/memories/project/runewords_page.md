# D4 S15 Runewords page

- Repo `tectiv3/runewords`, deployed at https://tectiv3.github.io/runewords/ (GitHub Pages, `main` root, push-to-deploy).
- Single-file `index.html`, vanilla JS/CSS, no deps. Single source of truth = `<script id="rw-data" type="application/json">` block. Update workflow: edit that JSON block, commit, push. Footer stamp (`asof` field) must be bumped with data changes.
- Data policy: consensus of d4guides.gg + Sportskeeda (patch 3.2.1 datamine, normal-tier recipes; ancestral ≈ 2×). aoeah.com's article (original source) has multiple errors: ~2× values, wrong Ancient's Pledge/Zephyr stats, wrong base lists. `|?` suffix in effect strings = unconfirmed (renders ⚠).
- Spec + critic findings: `docs/plans/spec.md`.
- Verification harness: jsdom runtime test at /tmp/rwtest/domtest.js (25 assertions) — page is JS-rendered, so grep for static markers only (title, `id="rw-data"`), never `data as of` (client-rendered).
- Images hotlinked from d4guides CDN (HEAD requests are blocked there; use GET to verify).
