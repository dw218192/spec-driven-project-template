# Spec / ADR / Spike — agent process template

A **GitHub template repository** that drops a spec-driven, gated development
process into a new repo — pre-wired for [Claude Code](https://claude.com/claude-code)
(and OpenAI Codex), with [pixi](https://pixi.sh) for the environment and task running.

It exists to keep an autonomous coding agent **honest about this repo**: a
commitment device made of a written spec, evidence-cited claims, and adversarial
AI review gates — *not* an orchestration engine.

## Use it

1. Click **Use this template → Create a new repository** (or copy this tree).
2. (Optional) On the new repo, **Settings → check "Template repository"** to let it seed further repos.
3. Run **`./bootstrap.sh`** (macOS/Linux) or **`./bootstrap.ps1`** (Windows) — installs
   pixi if the machine lacks it (pixi brings its own Python), materializes the env, and
   generates the `.claude/` + `.codex/` agent surface from `.agent/`.
4. Open the repo in your agent and read **[`docs/process.md`](docs/process.md)**. The
   `test`/`lint`/`fmt`/`build` tasks default to a Python toolchain (`tasks/*.py`) — have
   it `pixi add pytest ruff python-build` (or adapt `tasks/*.py` for your stack) and pick
   channels/deps. These commands are what a spec freezes as criteria.

## What's inside

| Path | What |
|---|---|
| [`docs/process.md`](docs/process.md) | The canonical process: lifecycle, gates, evidence, sign-off |
| `bootstrap.{sh,ps1}` | Repo setup — installs pixi (brings its own Python) + materializes the env |
| `.agent/skills/` | Agent skills (source) — `spec` · `adr` · `spike` · `remote-memory` · `update-from-template`; `gen-agents` builds them into `.claude/skills/` + `.codex/skills/` (gitignored; bootstrap runs it) |
| `.agent/agents/` | Reviewer-gate subagent sources; `gen-agents` emits `.claude/agents/*.md` + `.codex/agents/*.toml` (gitignored; bootstrap runs it) |
| `.agent/scripts/` | Cross-tool framework scripts: the `gen_agents` generator, `run_criteria`, `update_from_template`, and the shared `adr_immutable` (PreToolUse) + `memory_push` (Stop) hooks |
| `docs/{spec,adr,spike}/` | Where the agent authors the real specs / ADRs / spikes |
| [`docs/coding-standards.md`](docs/coding-standards.md) | The always-on rubric the impl gate enforces |
| `pixi.toml` + `tasks/*.py` | Skeleton manifest + project-owned `test`/`lint`/`fmt`/`build` scripts (default to pytest/ruff/build; adapt). Your criteria. |
| `AGENTS.md` / `CLAUDE.md` | Cross-tool entry points (Codex reads `AGENTS.md`; `CLAUDE.md` imports it) |

## The loop

`note → spec → impl → review → done`, one branch per work item. A spec is
adversarially reviewed (**spec-gate**) **and human-approved** before any code; the
implementation is adversarially reviewed and its frozen criteria independently
re-run (**impl-gate**) before the human signs off again and merges. Details in
[`docs/process.md`](docs/process.md).

## Updating from the template

A GitHub template is a one-time copy — no automatic upstream link. To pull later framework
improvements (process, gates, skills, hooks), **run the `update-from-template` skill**. It
syncs only the **framework-owned** paths — `.claude/`, `.codex/`, `.agent/`,
`docs/process.md`, `docs/coding-standards.md`, `.github/`, `bootstrap.*`, `AGENTS.md`,
`CLAUDE.md` — and stages them for review; your `pixi.toml`, specs/ADRs/spikes, source, and
`docs/project-notes.md` are never touched (which is exactly why project-specific
instructions live in `docs/project-notes.md`, so `AGENTS.md` / `CLAUDE.md` stay syncable).

## License

[MIT](LICENSE) — permissive on purpose: use this template freely and relicense your
generated project however you like.
