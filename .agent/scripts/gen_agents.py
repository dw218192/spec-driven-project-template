#!/usr/bin/env python3
"""Generate per-tool subagents from one canonical source (run: `pixi run gen-agents`).

Subagent personas are the one surface whose FORMAT genuinely differs between tools —
Claude wants `.claude/agents/<name>.md` (markdown + YAML frontmatter); Codex wants
`.codex/agents/<name>.toml` (with `developer_instructions`). So one canonical file per
agent under `.agent/agents/` holds the shared, tool-agnostic body plus a flat per-tool
projection (`claude_tools`, `codex_sandbox_mode`, `codex_model_reasoning_effort`), and
this script emits both targets so they can never drift again. The emitted files are
GENERATED — edit `.agent/agents/<name>.md` and re-run, never hand-edit the outputs. It
also mirrors the canonical `.agent/skills/` (one SKILL.md format works on both tools) into
`.claude/skills/` and `.codex/skills/`.

Stdlib only; run with `pixi run gen-agents` or directly with `python`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # repo root (.agent/scripts/gen_agents.py)
SRC = ROOT / ".agent" / "agents"
CLAUDE = ROOT / ".claude" / "agents"
CODEX = ROOT / ".codex" / "agents"


def parse(text: str) -> tuple[dict[str, str], str]:
    """Split a flat `--- ... ---` frontmatter file into (meta, body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SystemExit("source is missing leading '---' frontmatter")
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        key, sep, val = lines[i].partition(":")
        if sep:
            meta[key.strip()] = val.strip()
        i += 1
    return meta, "\n".join(lines[i + 1:]).strip("\n")


def _toml_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main() -> None:
    CLAUDE.mkdir(parents=True, exist_ok=True)
    CODEX.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.md")):
        meta, body = parse(src.read_text(encoding="utf-8"))
        name = meta["name"]                       # e.g. spec-gate
        mark = f"GENERATED from .agent/agents/{src.name} — edit the source, then: pixi run gen-agents"

        # Claude: <name>.md = frontmatter + body (YAML comment carries the marker).
        (CLAUDE / f"{name}.md").write_text(
            f"---\n# {mark}\nname: {name}\n"
            f"description: {meta['description']}\n"
            f"tools: {meta['claude_tools']}\n---\n\n{body}\n",
            encoding="utf-8",
            newline="\n",  # LF on every OS — committed generated files are eol=lf
        )

        # Codex: <name_>.toml = developer_instructions + the per-tool projection.
        codex_name = name.replace("-", "_")
        if "'''" in body:
            raise SystemExit(f"{src.name}: body contains ''' — cannot emit TOML literal")
        (CODEX / f"{codex_name}.toml").write_text(
            f"# {mark}\n"
            f'name = "{codex_name}"\n'
            f'description = "{_toml_str(meta["description"])}"\n'
            f'sandbox_mode = "{meta["codex_sandbox_mode"]}"\n'
            f'model_reasoning_effort = "{meta["codex_model_reasoning_effort"]}"\n'
            f"developer_instructions = '''\n{body}\n'''\n",
            encoding="utf-8",
            newline="\n",  # LF on every OS — committed generated files are eol=lf
        )
        print(f"{src.name} -> .claude/agents/{name}.md, .codex/agents/{codex_name}.toml")

    # Skills are the SAME SKILL.md format on both tools — mirror (copy) the canonical
    # .agent/skills/ source into each tool's skills dir.
    skills = ROOT / ".agent" / "skills"
    if skills.is_dir():
        for target in (ROOT / ".claude" / "skills", ROOT / ".codex" / "skills"):
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(skills, target)
            print(f"skills/ -> {target.relative_to(ROOT).as_posix()}/")


if __name__ == "__main__":
    main()
