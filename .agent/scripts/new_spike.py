#!/usr/bin/env python3
"""Create the next sequentially-numbered spike from the template (collision-proof).

Bookkeeping only — computes the next `SPIKE-<n>`, copies the skill's template
byte-exact, stamps the id, and REFUSES to overwrite an existing file. All judgment
(the question, the investigation, the findings) stays with you: open the printed
path and write them, then set `status: concluded`.

Usage:
    python .agent/scripts/new_spike.py ["<short title>"]
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

_TEMPLATE = Path(__file__).resolve().parent.parent / "skills" / "spike" / "references" / "spike-template.md"
_DOCS = Path("docs/spike")
_NUM = re.compile(r"SPIKE-(\d+)", re.IGNORECASE)


def _next_n() -> int:
    nums = [int(m.group(1)) for p in _DOCS.glob("SPIKE-*.md") if (m := _NUM.search(p.name))]
    return max(nums, default=0) + 1


def main() -> None:
    title = sys.argv[1] if len(sys.argv) > 1 else None
    n = _next_n()
    dest = _DOCS / f"SPIKE-{n}.md"
    if dest.exists():
        raise SystemExit(f"refusing to overwrite existing {dest}")
    text = (
        _TEMPLATE.read_text(encoding="utf-8")
        .replace("id: SPIKE-0", f"id: SPIKE-{n}")
        .replace("refs/spike-0/", f"refs/spike-{n}/")
        .replace("date: <YYYY-MM-DD>", f"date: {datetime.now():%Y-%m-%d}")
    )
    if title:
        text = text.replace("<short title>", title)
    _DOCS.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(dest.as_posix())


if __name__ == "__main__":
    main()
