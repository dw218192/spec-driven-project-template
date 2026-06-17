"""Git helpers — file enumeration and repo location. Stdlib only, fail-soft off git."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _git(*args: str, cwd: Path | None = None) -> str | None:
    """Run a read-only git command; return stdout, or None if git/the repo is absent."""
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def repo_root(start: Path | None = None) -> Path | None:
    """The repo's top-level directory (None if *start* isn't inside a git work tree)."""
    out = _git("rev-parse", "--show-toplevel", cwd=start)
    return Path(out.strip()) if out else None


def tracked_files(*extensions: str) -> list[str]:
    """Source files with the given suffixes, respecting `.gitignore`.

    Uses `git ls-files` (tracked + untracked-but-not-ignored); falls back to a walk that
    skips dot-directories when this isn't a git repo. Paths are relative to the current
    directory. For tools that don't discover files themselves (clang-format, clang-tidy,
    some linters).
    """
    exts = set(extensions)
    out = _git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    if out is not None:
        return [e for e in out.split("\0") if e and Path(e).suffix in exts]
    root = Path.cwd()
    return [
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix in exts
        and not any(part.startswith(".") for part in p.parts)
    ]


# `python tasks/utils/git.py .c .cpp` — list what tracked_files would hand a tool.
if __name__ == "__main__":
    print("\n".join(tracked_files(*sys.argv[1:])))
