#!/usr/bin/env python3
"""CI-style check: index.html's rw-data block vs data.json + structural invariants.

Read-only — never modifies anything. Exits non-zero on failure. stdlib only.
If node is on PATH, also runs `node --check` on the extracted block (wrapped as a
parenthesized expression: bare JSON parses as a block with string "labels", which
is a JS SyntaxError; JSON is a subset of JS *expression* syntax).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rwdata  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "data.json"
INDEX_HTML = ROOT / "index.html"


def node_check(block: bytes) -> bool:
    node = shutil.which("node")
    if node is None:
        print("node not found — skipping node --check")
        return True
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as f:
        f.write(b"(" + block + b");")
        path = f.name
    try:
        result = subprocess.run(
            [node, "--check", path], capture_output=True, text=True, timeout=60
        )
    except subprocess.SubprocessError as e:
        print(f"WARN: node --check could not run: {e}", file=sys.stderr)
        return True
    finally:
        Path(path).unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"FAIL: node --check rejected the embedded block:\n{result.stderr}", file=sys.stderr)
        return False
    print("node --check: OK")
    return True


def main() -> int:
    try:
        data_bytes = DATA_JSON.read_bytes()
        html_bytes = INDEX_HTML.read_bytes()
        block = rwdata.extract_block(html_bytes)

        if block != data_bytes:
            print("FAIL: index.html rw-data block is NOT byte-identical to data.json "
                  "(run scripts/sync.py)", file=sys.stderr)
            return 1
        print(f"sync: index.html rw-data block == data.json ({len(data_bytes)} bytes)")

        data = rwdata.parse_block(block)
        cls_counts = rwdata.check_invariants(data)
        print("invariants: OK")
        print(rwdata.summary(cls_counts, data))
    except (OSError, rwdata.DataError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    if not node_check(block):
        return 1
    print("ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
