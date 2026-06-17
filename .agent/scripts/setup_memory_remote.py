#!/usr/bin/env python3
"""One-time setup for git-remote memory sync (the `remote-memory` skill).

Initializes the project's machine-local memory directory as a git repo, points it
at a PRIVATE remote, installs a union merge driver for MEMORY.md (so concurrent
edits across machines union instead of conflicting), and does the initial commit +
push. After this, the `memory_push` Stop hook keeps it synced each turn.

Usage:
    python setup_memory_remote.py <remote-url> [--memory-dir PATH]

The memory dir defaults to $CLAUDE_MEMORY_DIR, else the standard Claude Code
location for this project (~/.claude/projects/<project-id>/memory).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path


def derive_memory_dir() -> Path:
    """The Claude Code per-project memory dir for the current working directory."""
    project_id = re.sub(r"[:/\\]", "-", os.path.abspath(os.getcwd()))
    return Path.home() / ".claude" / "projects" / project_id / "memory"


def git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up git-remote memory sync.")
    parser.add_argument("remote", help="the PRIVATE git remote URL for memory")
    parser.add_argument("--memory-dir", default=None, help="override the memory dir")
    args = parser.parse_args()

    if args.memory_dir:
        mem = Path(args.memory_dir)
    elif os.environ.get("CLAUDE_MEMORY_DIR"):
        mem = Path(os.environ["CLAUDE_MEMORY_DIR"])
    else:
        mem = derive_memory_dir()
    mem.mkdir(parents=True, exist_ok=True)
    print(f"memory dir: {mem}")

    if not (mem / ".git").exists():
        git(["init", "-q"], mem)

    # Point at the remote (idempotent).
    if "origin" in git(["remote"], mem).split():
        git(["remote", "set-url", "origin", args.remote], mem)
    else:
        git(["remote", "add", "origin", args.remote], mem)

    # Union merge driver so MEMORY.md merges union both sides instead of conflicting.
    git(
        ["config", "merge.memunion.driver", "git merge-file -p --union %A %O %B > %A"],
        mem,
    )
    attrs = mem / ".gitattributes"
    line = "MEMORY.md merge=memunion\n"
    if not attrs.exists() or line not in attrs.read_text(encoding="utf-8"):
        with attrs.open("a", encoding="utf-8") as f:
            f.write(line)

    # Initial commit + push (commit is a no-op if there is nothing staged).
    git(["add", "-A"], mem)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(mem)).returncode != 0:
        git(["commit", "-m", "memory: init"], mem)
    git(["push", "-u", "origin", "HEAD"], mem)

    print("done — memory is synced; the memory_push Stop hook handles per-turn pushes.")


if __name__ == "__main__":
    main()
