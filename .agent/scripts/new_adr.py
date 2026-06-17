#!/usr/bin/env python3
"""Create the next sequentially-numbered ADR from the template (collision-proof).

Bookkeeping only — computes the next `ADR-<n>`, copies the skill's template
byte-exact, stamps the id / title / date, and REFUSES to overwrite. The decision
content (Context/Decision/Consequences) and whether to supersede stay with you: open
the printed path and fill it in, then set `status: accepted` at sign-off.

Usage:
    python .agent/scripts/new_adr.py <slug> ["<title>"]
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

_TEMPLATE = Path(__file__).resolve().parent.parent / "skills" / "adr" / "references" / "adr-template.md"
_DOCS = Path("docs/adr")
_NUM = re.compile(r"^(\d+)-")


def _next_n() -> int:
    nums = [int(m.group(1)) for p in _DOCS.glob("*.md") if (m := _NUM.match(p.name))]
    return max(nums, default=0) + 1


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('usage: new_adr.py <slug> ["<title>"]')
    slug = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "<decision title>"
    n = _next_n()
    dest = _DOCS / f"{n}-{slug}.md"
    if dest.exists():
        raise SystemExit(f"refusing to overwrite existing {dest}")
    text = (
        _TEMPLATE.read_text(encoding="utf-8")
        .replace("ADR-0", f"ADR-{n}")
        .replace("<decision title>", title)
        .replace("date: <YYYY-MM>", f"date: {datetime.now():%Y-%m}")
    )
    _DOCS.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(dest.as_posix())


if __name__ == "__main__":
    main()
