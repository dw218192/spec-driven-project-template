# The process — spec / ADR / spike, with adversarial gates

This repo runs a **spec-driven, gated** development process. Its single purpose is
to keep an autonomous coding agent **honest about this repository**: every change
is committed to in writing, every non-trivial claim is backed by evidence, and
every implementation is reviewed by an adversarial AI gate that re-runs the
criteria itself before a human signs off.

It is a *commitment device*, not an orchestration engine. The framework persists
nothing — **git is the durable record**, and the current phase is *derived* by
re-running the gates against the branch.

## Why gates: variance reduction

Agents are high-variance — they cut corners, hide errors, fake implementations,
and write messy code unless constrained. Each gate clamps a specific source of
that variance:

1. **Spec gate** (AI, adversarial, read-only) — stops infeasible, unevidenced, or
   under-scoped designs from ever being executed.
2. **Impl gate** (AI, adversarial, runs the criteria) — stops error-hiding,
   cheating, and corner-cutting in the code.
3. **Human gate** (trust) — human sign-off, required **twice**: to approve the spec
   before impl, and to approve the merge at done. The agent records each.

The AI gates are *high-recall variance reducers* that make the human's job
tractable; they are **not** the trust boundary. A reviewer that rubber-stamps is
just a new variance source, so every `pass` verdict must enumerate what was
checked.

## The lifecycle

**One branch = one work item.** A work item is a branch `work/<id>` with one spec.
There is no unit registry; the agent decides *how* to implement — the process does
not prescribe sub-steps.

| from | to | gate |
|---|---|---|
| note | spec | — create branch + author the spec (gather concluded spikes) |
| spec | impl | **spec-gate pass + human sign-off** + depended-on ADRs accepted |
| impl | review | **impl-gate pass** + criteria pass |
| impl | spec | back-edge: spec wrong → edit + re-gate |
| review | done | **human sign-off** → merge `work/<id>` → `main` |
| review | impl | back-edge: issues found |

`done` is terminal (merged). Nothing is stored: **phase is re-derived** by running
the gates; review verdicts and criteria results are ephemeral session scratch.

## Evidence: spikes

A **spike** resolves one uncertainty during spec authoring and records *re-derivable*
evidence — a `docs/spike/SPIKE-N.md` whose `verify` command/script re-derives the finding
by invoking the real subject. Every non-trivial spec/ADR claim must cite a **concluded**
spike, a cited code path (`file:line`), or a doc; an uncited claim — or one citing an
`open` spike — is a finding.

Spikes are *evidence*, so they get the "don't trust self-reports" treatment one level
earlier than the impl gate: the spec gate **audits the `verify` source** (a method that
hardcodes its conclusion or measures a neighbour of the claim is a **false spike** —
fabricated evidence), checks it exercises the **claim's** actual subject + quantifier,
and a **load-bearing** spike's `verify` is lifted into the acceptance criteria so the
impl gate + CI re-run it (also catching a stale assumption). A `reproducible: no` probe
(live API / timing / manual UX) is the weakest evidence — capped, must commit its raw
observation, never sole evidence for a load-bearing claim. A concluded spike is frozen
(re-spike rather than edit). Use the **`spike`** skill.

## Spec items have stable IDs

Each normative spec item gets a short, stable ID (e.g. `WF-3`, `IMS-1`). IDs make
every requirement:

- **citable in code** — an `implements WF-3` marker in a comment (`# …` or `// …`), checked by the impl gate;
- **validatable** — a spike/criterion ties to a specific item;
- **traceable** — spec item → evidence → criterion (command) → code cite.

A spec is **fully signed** only when every item has all three of: evidence, an
(ideally executable) acceptance criterion, and spec-gate sign-off.

## Criteria are executed, never self-reported

Acceptance criteria are **commands** (here, `pixi run` tasks — see the project's
bootstrapped `pixi.toml`),
authored and **frozen at the spec gate**. The impl gate (and CI) **re-run them
independently** and observe the exit codes — the authoring agent's claim is never
the check. Criteria without a command are human-verified at sign-off.

## ADRs

Architectural Decision Records are plain markdown under `docs/adr/`, with
schema-governed frontmatter (see the `adr` skill's `references/adr-template.md`).
On-disk status is `proposed | accepted` — there is no `rejected` (a rejected ADR is
never committed), and **`superseded` is derived, not stored**.

**Immutability is absolute:** an accepted ADR is **never edited** (the
`adr_immutable` hook denies it). Supersession is **additive** — a *new* ADR whose
`supersedes: [ADR-N]` records the replaced decision; the old file is untouched. The
reverse link and superseded status are derived from the `supersedes` edges (the
`adr` skill's `adr_status.py`). Use the **`adr`** skill.

## Human sign-off (twice)

The human gates the process at **two** transitions:

- **spec → impl.** After the spec gate passes, the agent presents the spec and its
  evidence and **asks the human to approve it**. Implementation does not begin until
  the human signs off — they commit to the spec before any code is written.
- **review → done.** The agent presents the diff + criteria results + both AI
  verdicts and **asks the human** again; on approval it merges `work/<id>` → `main`
  with an `Approved-by:` trailer ("done" = merged).

Both are *trust* points, deliberately small: an unauthorized sign-off is possible —
accepted residual risk. The AI gates + executed criteria + git keep that surface
small.

## Memory

Durable agent memory lives outside the repo (the agent's machine-local memory
directory) and is **synced to a git remote** — committed and pushed on each
turn-end by the `memory_push.py` Stop hook, and pulled on a fresh machine. Use the
**`remote-memory`** skill to set up the remote and sync manually. Keying is by repo
identity, not local path.

## The always-on rubric

[`coding-standards.md`](coding-standards.md) enumerates the AI anti-patterns the
impl gate rejects (defensive fallbacks, error hiding, unnecessary abstractions,
compatibility shims). Treat it as this repo's constitution: it is binding on every
implementation and is what the impl gate measures against.

## How it's realized (no custom runtime)

| Concern | Realization |
|---|---|
| Spec / ADR / spike authoring | the `spec` / `adr` / `spike` skills |
| Spec gate | the `spec-gate` subagent (`.claude/agents/spec-gate.md`) — read-only |
| Impl gate | the `impl-gate` subagent (`.claude/agents/impl-gate.md`) — read-only tools + Bash to re-run criteria |
| Human gate | the agent asks the human to sign off — at spec→impl **and** review→done |
| Criteria | `pixi run` tasks in `pixi.toml`, re-run by the impl gate + CI |
| ADR immutability | the `adr_immutable` PreToolUse hook |
| Memory sync | the `memory_push` Stop hook + the `remote-memory` skill |
| Durable record | git (commits + the sign-off merge) |

Nothing here needs a server, a ledger, or persisted state. **Codex** realizes the
same process from `AGENTS.md` + `.codex/`: the reviewers are
`.codex/agents/{spec_gate,impl_gate}.toml` (invoked by name — Codex never
auto-delegates), ADR immutability is the shared `.agent/scripts/adr_immutable.py` PreToolUse hook
(it parses the `apply_patch` body for the target path), and memory pushes via a
`Stop` hook (or the `notify` fallback). Codex has no deterministic workflow
primitive, so the loop's *sequencing* is instruction-enforced rather than
control-flow-enforced — the gates themselves are identical. See `.codex/README.md`.
