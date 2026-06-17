#!/usr/bin/env python3
"""Run a spec's FROZEN acceptance criteria verbatim and emit the results table.

Extracting the commands straight from the spec's frozen fenced block is what makes
"frozen / verbatim" an executable invariant instead of an honor-system one. The impl
gate (and CI) call this and VERIFY the emitted table rather than hand-transcribing
commands — and a green exit is necessary, not sufficient (the gate still judges
cheating / stubbing behind a passing command).

Usage:
    python .agent/scripts/run_criteria.py docs/spec/<id>.md

Parses the first fenced block under '## Acceptance criteria'. A `# <CRIT> (<ITEM>[, <ITEM>…])`
comment tags the spec item(s) for the command on the following line.

Each criterion must be a SINGLE command — ideally a bare `pixi run <task>` — with **no
inline shell syntax** (pipes / redirects / `&&` / backticks): criteria run WITHOUT a shell
so they behave identically on every OS (cmd.exe and bash would otherwise diverge), and
`pixi` is resolved even when it is not on PATH. Push any quoting / regex / globbing into the
task script. A criterion containing shell metacharacters is reported as a failure.

Streams each criterion's own output to stderr, so stdout carries ONLY a JSON array of
{spec_items, command, exit_code, passed} (spec_items may be empty); exits non-zero if any
criterion failed, so it doubles as the CI gate.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

_TAG = re.compile(r"\(([^)]*)\)")          # the (…) group on a criterion comment
_ITEM = re.compile(r"[A-Za-z]+-\d+")        # spec-item IDs inside that group
_SHELL_OPS = ("|", "&", ";", "<", ">", "`", "$(")


def _resolve_pixi() -> str:
    """Find a pixi executable even when it isn't on PATH (a documented-common state)."""
    found = shutil.which("pixi")
    if found:
        return found
    bindir = Path.home() / ".pixi" / "bin"
    for cand in (bindir / "pixi.exe", bindir / "pixi"):
        if cand.is_file():
            return str(cand)
    return "pixi"  # last resort — fails loudly if pixi is truly absent


def _criteria_block(text: str) -> list[str]:
    """Lines inside the first fenced block under '## Acceptance criteria'."""
    out: list[str] = []
    in_section = in_block = False
    for line in text.splitlines():
        if line.strip().lower().startswith("## acceptance criteria"):
            in_section = True
            continue
        if in_section and line.lstrip().startswith("```"):
            if in_block:
                break  # closing fence
            in_block = True
            continue
        if in_block:
            out.append(line)
    return out


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_criteria.py <spec.md>")
    pixi = _resolve_pixi()
    results = []
    pending: list[str] = []  # spec-item IDs from the comment heading the next command
    for line in _criteria_block(Path(sys.argv[1]).read_text(encoding="utf-8")):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            tag = _TAG.search(stripped)
            ids = _ITEM.findall(tag.group(1)) if tag else []
            if ids:
                pending = ids  # a tag comment (re)sets the pending item(s)
            continue

        items, pending = pending, []  # consume the tag; reset so an untagged criterion is null
        if not items:
            print(f"warning: criterion has no (ITEM) tag: {stripped}", file=sys.stderr)
        if any(op in stripped for op in _SHELL_OPS):
            print(
                f"error: criterion uses shell syntax, won't run cross-platform: {stripped}\n"
                "       criteria must be a single command (ideally `pixi run <task>`) — "
                "move pipes/quoting/regex into the task script.",
                file=sys.stderr,
            )
            results.append({"spec_items": items, "command": stripped, "exit_code": 2, "passed": False})
            continue

        argv = shlex.split(stripped, posix=True)
        if argv and argv[0] == "pixi":
            argv[0] = pixi
        try:
            code = subprocess.run(argv, stdout=sys.stderr).returncode  # keep stdout = JSON only
        except FileNotFoundError:
            print(f"error: command not found: {argv[0] if argv else stripped}", file=sys.stderr)
            code = 127
        results.append({"spec_items": items, "command": stripped, "exit_code": code, "passed": code == 0})

    print(json.dumps(results, indent=2))
    sys.exit(0 if results and all(r["passed"] for r in results) else 1)


if __name__ == "__main__":
    main()
