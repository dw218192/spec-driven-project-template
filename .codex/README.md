# Codex surface

This `.codex/` directory realizes the same spec/ADR/spike process for OpenAI Codex
that `.claude/` does for Claude Code. `AGENTS.md` (repo root) is the shared,
Codex-native instruction layer — read it and `docs/process.md` first.

## What's here

| Path | Role |
|---|---|
| `agents/spec_gate.toml`, `agents/impl_gate.toml` | The adversarial reviewer subagents (the gates) |
| `../.agent/scripts/adr_immutable.py` | PreToolUse hook (shared with Claude) — denies edits to an *accepted* ADR |
| `../.agent/scripts/memory_push.py --codex` | Stop hook (shared) — pushes `~/.codex/memories` to its git remote |
| `config.toml` | Wires the two hooks; agent definitions load by-name from `agents/` |

## Gotchas (verified against the Codex source)

- **Trust the project.** Codex ignores a project's `.codex/` (config, hooks, agents)
  until you mark the repo trusted. An untrusted clone runs none of this.
- **Invoke gates by name.** Agent *definitions* load automatically, but Codex never
  *delegates* on its own — ask for `spec_gate` / `impl_gate` explicitly at each gate.
- **No workflow FSM.** Codex has no deterministic workflow primitive, so the loop's
  *sequencing* is enforced by the `AGENTS.md` instructions, not control flow. The
  gates and the ADR-immutability hook are the same as on Claude.
- **Sandbox (note the asymmetry).** `spec_gate` is `read-only`; `impl_gate` is
  `workspace-write` so it can *run* the criteria (which may write caches), restrained
  from editing source by instruction. (Claude's impl-gate is no-edit by *tool
  allowlist* instead — same intent, different enforcement.)

## Memory

Codex Memories live in `~/.codex/memories` (OFF by default — enable
`features.memories`). Use the **`remote-memory` skill** to set up its git remote — it
takes a `--memory-dir` for the Codex store.

### Push fallback (`notify`)

Codex hooks are implemented on Windows but have an open regression where they may not
fire on recent builds. If the `Stop` hook does not push, use the cross-platform
`notify` mechanism — but **`notify` is forbidden in project config**, so it goes in
your **user** `~/.codex/config.toml`:

```toml
notify = ["python3", "/ABSOLUTE/PATH/TO/REPO/.agent/scripts/memory_push.py", "--codex"]
```

With `--codex`, `memory_push.py` ignores stdin/argv, so it works unchanged as a `Stop`
hook or a `notify` target.
