# Agent instructions

This repo runs a spec-driven, gated process. **Read [`docs/process.md`](docs/process.md)
before starting work** — it is the source of truth.

**Project-specific instructions** (domain rules, conventions, gotchas) live in
[`docs/project-notes.md`](docs/project-notes.md) — read it too. That file is
project-owned; this file and the rest of the framework stay in sync with the template.

## Bootstrap (once, on adoption)

**Run `./bootstrap.{sh,ps1}` first.** Besides installing pixi + the env, it generates the
`.claude/` + `.codex/` gate & skill surface from `.agent/` — that surface is **gitignored
build output**, so `.agent/` is the one committed source. If it is ever missing or stale,
rebuild it with `python .agent/scripts/gen_agents.py`.

This template ships a **skeleton `pixi.toml`** plus **`tasks/{test,lint,fmt,build}.py`**
that default to a Python toolchain (pytest / ruff / build). Before the first work item,
**make them real for this project**: `pixi add pytest ruff python-build` (or edit `tasks/*.py`
for a non-Python stack), and pick the right `channels` / `platforms` / `[dependencies]`.
Those `pixi run <task>` commands are exactly what specs freeze as criteria and what the
impl gate re-runs (`check` runs `lint` + `test`).

## Project tools (`tasks/utils/`)

Shared, language-agnostic helpers for your task scripts live in the `tasks/utils/`
package: `run` (echo + run + propagate exit code), `tracked_files` (`.gitignore`-aware
file lists), `write_if_changed` / `touch`, and `Manifest` (track generated files by
content hash — write-on-change + drift detection). A task imports them as
`from utils import run` (pixi runs tasks as `python tasks/<name>.py`, so `tasks/` is on
`sys.path`). **Route project codegen and helpers through this package, and extend it
freely** — it's project-owned and never synced. `Manifest` is stdlib-only and
project-agnostic, so you can reuse it in your own codegen tools. Keep the framework
(`.agent/scripts/*.py`) **self-contained** (stdlib only, no `tasks/utils` import) — it
runs before bootstrap.

**Scope recursive tools to your code.** Formatters/linters that walk the filesystem also
see the in-tree pixi env (`.pixi/`) and the vendored framework dirs (`.agent/`, `.claude/`,
`.codex/`). The default `lint`/`fmt` tasks already exclude the framework; for a tool that
respects neither `.gitignore` nor a project model (e.g. `gofmt`), scope it to
`tracked_files(...)` rather than `.`.

## Environment, packages & tools — always via pixi

pixi owns this project's **tooling environment** — the toolchain, the linters / formatters
/ test & build runners your criteria invoke, and the Python the framework scripts need —
all pinned in `pixi.lock` (`pixi.toml`, or `pyproject.toml` `[tool.pixi]`). **Route every
tool through it**: never `pip install`, and never call `python` / `pytest` / a tool
directly — run it inside the env. **One exception:** the framework's own stdlib-only
helper scripts (`.agent/scripts/*.py`) run directly with `python` (no project env, even
before bootstrap).

**pixi is the tooling layer, not automatically your runtime dependency manager.** On a
pure-Python/conda project pixi owns both. On a Rust/Go/Node stack, runtime libraries
belong to the native manager (`Cargo.toml`, `go.mod`, `package.json`) with its own
lockfile — pixi just *provides the toolchain* (`pixi add rust`/`go`/`nodejs`) and runs the
criteria. So don't `pixi add` a project runtime library that belongs in the native manager.

- **Run** through the env: `pixi run <task|cmd>`, `pixi shell` (interactive), or
  `pixi exec --with <pkg> <tool>` (one-off, ephemeral — nothing added to the project).
- **Add / remove deps via the CLI** — not by hand-editing the manifest, which desyncs
  `pixi.lock`:

  | Need | Command |
  |---|---|
  | conda-forge package (preferred) | `pixi add <pkg>` · pin: `pixi add "<pkg>>=x.y"` |
  | PyPI-only package | `pixi add --pypi <pkg>` |
  | dep only some envs need (dev/test/…) | `pixi add --feature <f> <pkg>` |
  | remove | `pixi remove [--pypi] <pkg>` |

- **Define commands as tasks:** `pixi task add <name> "<cmd>" [--depends-on <t>]`. Tasks
  are the project's runnable commands — and a spec's **criteria are `pixi run` tasks**.

**The two cases you'll hit most:**
- **A framework helper script (`.agent/scripts/…`) needs a package** → `pixi add`
  it, and run the script via `pixi run`. Do **not** `pip install` into some other env.
- **You're building a project-level tool that needs a package** → add the package as a
  dependency **and** expose a `pixi run` task for the tool. (A machine-wide CLI unrelated
  to this project is the only `pixi global install` case.)

**Lockfile:** `pixi.lock` is committed and is the reproducibility record — adding a dep
updates it; commit the lock change with your work. `pixi install --locked` installs
exactly the locked versions.

**Discovery — prefer machine-readable:** `pixi task list --json` (what can I run?),
`pixi info --json` (envs/workspace), `pixi list --json` (installed packages). The
manifest validates against pixi's JSON Schema (SchemaStore registers `pixi.toml`).

## The loop

`note → spec → impl → review → done`, one branch (`work/<id>`) per work item.

1. **Spec.** Author `docs/spec/<id>.md` from the `spec` skill's
   `references/spec-template.md` (Goal, Non-goals, Evidence, Spec items with stable
   IDs, executable Acceptance criteria). Back every non-trivial claim with a
   **concluded spike**, a cited code path, or a doc — use the `spike` skill for
   uncertainties. Freeze the criteria as `pixi run` tasks.
2. **Spec gate + sign-off.** Have the spec gate reviewer (`spec-gate` on Claude,
   `spec_gate` on Codex) adversarially review the spec; do not proceed until it passes. Then **ask the human to approve the
   spec** — implementation does not begin until they sign off.
3. **Impl.** Implement exactly what the approved spec says — no scope cuts, no
   error-hiding, no fake/stub implementations, no defensive fallbacks
   (see [`docs/coding-standards.md`](docs/coding-standards.md)). Cite spec-item IDs in code
   (an `implements WF-3` marker in a comment — `# …` in Python, `// …` in C/Go/Rust/JS).
   Make the frozen criteria genuinely pass.
4. **Impl gate.** Have the impl gate reviewer (`impl-gate` on Claude, `impl_gate` on
   Codex) adversarially review the implementation; it re-runs the criteria itself.
5. **Review → done.** Present the diff + criteria results + both verdicts and ask
   the human to sign off. On approval, merge `work/<id>` → `main` with an
   `Approved-by:` trailer.

## Rules

- **Accepted ADRs are never edited** — supersede additively (a new ADR with
  `supersedes: [ADR-N]`; the `adr_immutable` hook enforces it; reverse links are
  derived). Use the `adr` skill.
- **Criteria are executed, never self-reported** — the impl gate re-runs them; an
  approved spec has **no open questions** (spike and conclude first).
- **Memory** auto-syncs to a git remote (the `memory_push` Stop hook; `remote-memory`
  skill to set up).

Full rationale is in `docs/process.md`.

## Skills

`spec`, `adr`, `spike`, `remote-memory`, `update-from-template` — see `.claude/skills/`.

## Codex

On Codex the reviewers are subagents in `.codex/agents/` — invoke them **explicitly
by name** (`spec_gate`, `impl_gate`); Codex never auto-delegates. ADR immutability
and the memory push are wired as `.codex/` hooks. **Trust the project** so Codex
loads `.codex/` (an untrusted repo's `.codex/` layer is ignored). See `.codex/README.md`.
