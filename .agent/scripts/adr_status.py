#!/usr/bin/env python3
"""Derive the ADR supersession graph from the only stored edge (`supersedes`).

Accepted ADRs are immutable — we never write a reverse `superseded_by` link or flip
an old ADR to `status: superseded`. Both are DERIVED here: scan every docs/adr/*.md,
read each ADR's `supersedes` list, and invert it. Think of this as a tiny query tool
the agent runs to answer "is ADR-N superseded, and by whom?".

Usage:
    python adr_status.py [adr_dir]      # default: docs/adr

Prints one line per ADR (id, on-disk status, derived superseded-by) and flags any
`supersedes` pointing at a missing ADR. Exit 0, or 1 if a dangling reference exists.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ADR_ID = re.compile(r"ADR-[0-9]+")


def _frontmatter(text: str) -> dict[str, str]:
    """Parse the leading `--- ... ---` block into a flat {key: raw-value} dict."""
    out: dict[str, str] = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip().lower()] = value.split("#", 1)[0].strip()
    return out


def main() -> None:
    adr_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/adr")
    if not adr_dir.is_dir():
        print(f"no ADR directory: {adr_dir}")
        sys.exit(0)

    status: dict[str, str] = {}
    supersedes: dict[str, list[str]] = {}
    for path in sorted(adr_dir.glob("*.md")):
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        adr_id = fm.get("id", "")
        if not adr_id:
            continue
        status[adr_id] = fm.get("status", "?")
        supersedes[adr_id] = _ADR_ID.findall(fm.get("supersedes", ""))

    # Invert the `supersedes` edges to get the derived reverse links.
    superseded_by: dict[str, list[str]] = {a: [] for a in status}
    dangling = 0
    for newer, olds in supersedes.items():
        for old in olds:
            if old in superseded_by:
                superseded_by[old].append(newer)
            else:
                print(f"{newer}: dangling supersedes -> {old} (no such ADR)")
                dangling += 1

    for adr_id in sorted(status, key=lambda s: int(s.split("-")[1])):
        by = superseded_by[adr_id]
        suffix = f"  (superseded by {', '.join(by)})" if by else ""
        print(f"{adr_id}  status={status[adr_id]}{suffix}")

    sys.exit(1 if dangling else 0)


if __name__ == "__main__":
    main()
