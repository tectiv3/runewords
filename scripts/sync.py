#!/usr/bin/env python3
"""Embed data.json into index.html's rw-data block (the ONLY writer of that block).

Edit data.json, then run this script. Never hand-edit the embedded block.
Round-trip safe: re-extracts the block after writing and asserts byte-equality.
Exits non-zero on malformed JSON, invariant violations, or mismatch. stdlib only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rwdata  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "data.json"
INDEX_HTML = ROOT / "index.html"


def main() -> int:
    try:
        data_bytes = DATA_JSON.read_bytes()
        html_bytes = INDEX_HTML.read_bytes()

        data = rwdata.parse_block(data_bytes)
        cls_counts = rwdata.check_invariants(data)

        block = rwdata.extract_block(html_bytes)
        if block == data_bytes:
            print("no-op: index.html rw-data block is byte-identical to data.json (in sync)")
            print(rwdata.summary(cls_counts, data))
            return 0

        open_tag = rwdata.OPEN_TAG
        i = html_bytes.index(open_tag) + len(open_tag)
        j = html_bytes.index(rwdata.CLOSE_TAG, i)
        new_html = html_bytes[:i] + data_bytes + html_bytes[j:]

        # Prove the round trip before touching the file on disk.
        rewritten = rwdata.extract_block(new_html)
        if rewritten != data_bytes:
            print("ERROR: re-extracted block does not match data.json — aborting, "
                  "index.html left unchanged", file=sys.stderr)
            return 1

        INDEX_HTML.write_bytes(new_html)
        print(f"embedded data.json ({len(data_bytes)} bytes) into index.html rw-data block")
        print(rwdata.summary(cls_counts, data))
        return 0
    except (OSError, rwdata.DataError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
