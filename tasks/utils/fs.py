"""Filesystem helpers: content-addressed writes and touch."""

from __future__ import annotations

from pathlib import Path


def write_if_changed(path: Path | str, content: str) -> bool:
    """Write *content* to *path* only if it differs from what's already there.

    Returns True iff it wrote. Skipping the no-op write avoids bumping the mtime — which
    keeps formatters, build systems, and git diffs from churning on regenerated-but-
    identical files. (Newlines are normalized by text mode, so the compare is platform-
    stable.)
    """
    p = Path(path)
    if p.is_file() and p.read_text(encoding="utf-8") == content:
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        content, encoding="utf-8", newline="\n"
    )  # LF on every OS (stable across platforms)
    return True


def touch(path: Path | str) -> None:
    """Ensure *path* exists (making parent dirs); update its mtime if it already does."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()
