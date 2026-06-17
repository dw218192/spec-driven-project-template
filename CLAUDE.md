# Claude Code entry point

This repo's agent instructions are the cross-tool source of truth in `AGENTS.md`.
Read it, and the full process, before working.

@AGENTS.md
@docs/process.md
@docs/project-notes.md

## Claude-specific notes

- **Gates** are subagents in `.claude/agents/` — invoke `spec-gate` (before impl)
  and `impl-gate` (before review) by name. **Skills** live in `.claude/skills/`.
- **Hooks** (`.claude/settings.json`): `adr_immutable` (PreToolUse) + `memory_push`
  (Stop). **Criteria** run via `pixi run check` (and `test` / `lint` / `fmt`).
