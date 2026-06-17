#!/usr/bin/env python3
"""PreToolUse hook (Claude Code + OpenAI Codex): deny edits to an *accepted* ADR.

One implementation for both tools — the only difference is how an edit's target path
is expressed, and this handles both:
  - Claude / Codex Edit·Write: `tool_input.file_path`.
  - Codex `apply_patch`: the path lives inside the patch text as `*** Update File:` /
    `*** Add File:` / `*** Delete File:` headers, parsed here.
If an Update/Delete targets an ADR whose on-disk frontmatter is `status: accepted`, it
denies the call (creating a new ADR is allowed). Both tools accept the same
`hookSpecificOutput.permissionDecision` JSON. Self-contained; always exits 0.

Wiring: Claude `.claude/settings.json` PreToolUse (matcher Edit|Write) and Codex
`.codex/config.toml` `[[hooks.PreToolUse]]` (matcher apply_patch|Edit|Write) both run
`python .agent/scripts/adr_immutable.py`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_PATCH_HDR = re.compile(r"^\*\*\*\s+(Update|Add|Delete)\s+File:\s+(.+?)\s*$")


def _is_adr_path(path: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    parts = [p.lower() for p in path.parts]
    return any(
        parts[i] == "docs" and parts[i + 1] == "adr" for i in range(len(parts) - 1)
    )


def _frontmatter_status(text: str) -> str | None:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if sep and key.strip().lower() == "status":
                token = value.split("#", 1)[0].strip().strip("\"'").split()
                return token[0].lower() if token else None
        return None
    for line in lines[:5]:
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() == "status":
            token = value.strip().strip("\"'").split()
            return token[0].lower() if token else None
    return None


def _is_accepted_adr(path: Path) -> bool:
    if not _is_adr_path(path) or not path.exists():
        return False
    try:
        return _frontmatter_status(path.read_text(encoding="utf-8")) == "accepted"
    except OSError:
        return False


def _targets(tool_input, cwd: Path):
    """Yield (op, absolute_path) for every file an edit would touch."""
    if isinstance(tool_input, dict) and tool_input.get("file_path"):
        yield "Edit", (cwd / tool_input["file_path"])
        return
    text = ""
    if isinstance(tool_input, str):
        text = tool_input
    elif isinstance(tool_input, dict):
        for key in ("input", "patch", "command", "content"):
            value = tool_input.get(key)
            if isinstance(value, str):
                text = value
                break
    for line in text.splitlines():
        match = _PATCH_HDR.match(line.strip())
        if match:
            yield match.group(1), (cwd / match.group(2))


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cwd = Path(event.get("cwd") or ".")
    reason = ""
    for op, path in _targets(event.get("tool_input"), cwd):
        if op == "Add":
            continue  # creating a new ADR is allowed
        if _is_accepted_adr(path):
            reason = (
                f"ADR IMMUTABILITY: '{path.as_posix()}' is 'accepted' and cannot be "
                f"modified ({op.lower()}). Amend it by authoring a NEW superseding "
                f"ADR, never by editing the accepted file. Do NOT retry."
            )
            break

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny" if reason else "allow",
        }
    }
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
