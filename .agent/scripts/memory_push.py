#!/usr/bin/env python3
"""Stop hook (Claude Code + OpenAI Codex): commit + push the memory dir to its remote.

One implementation for both tools — only the memory *location* differs, resolved here:
  --memory-dir PATH   explicit
  --codex             Codex Memories: $CODEX_HOME/memories (default ~/.codex/memories)
  (default)           Claude: the `memory/` sibling of the Stop event's transcript_path,
                      or $CLAUDE_MEMORY_DIR

If the resolved dir is a git repo with a remote and has uncommitted changes, it commits
and pushes (commit-only-on-change is the natural debounce). Always exits 0; never blocks
a turn; fails soft. One-time git setup lives in the `remote-memory` skill.

Wiring: Claude `.claude/settings.json` Stop -> `python .agent/scripts/memory_push.py`;
Codex `.codex/config.toml` Stop (or `notify`) -> `python .agent/scripts/memory_push.py --codex`.
`parse_known_args` ignores Codex `notify`'s extra JSON argv.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _resolve(args, event: dict) -> Path | None:
    if args.memory_dir:
        return Path(args.memory_dir).expanduser()
    if args.codex:
        base = os.environ.get("CODEX_HOME")
        return (Path(base) if base else Path.home() / ".codex") / "memories"
    env = os.environ.get("CLAUDE_MEMORY_DIR")
    if env:
        return Path(env)
    transcript = event.get("transcript_path")
    return Path(transcript).parent / "memory" if transcript else None


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex", action="store_true")
    ap.add_argument("--memory-dir", default=None)
    args, _ = ap.parse_known_args()

    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    mem = _resolve(args, event)
    if mem is None or not (mem / ".git").exists():
        sys.exit(0)  # not set up — no-op (see the remote-memory skill)
    try:
        if not _git(["remote"], mem).stdout.strip():
            sys.exit(0)
        _git(["add", "-A"], mem)
        if _git(["diff", "--cached", "--quiet"], mem).returncode == 0:
            sys.exit(0)
        _git(["commit", "-m", "memory: sync"], mem)
        _git(["push", "--quiet"], mem)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
