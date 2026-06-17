---
name: spec
description: Author or revise a work item's spec at docs/spec/<id>.md before any code is written, then run it through the spec gate. Use when starting a new work item, when a spec needs revision after a spec-gate rejection, or when acceptance criteria must be defined. Produces a fully-signed spec — Goal, Non-goals, evidence-cited claims, stable spec-item IDs, and frozen executable acceptance criteria.
---

A **spec** is the written commitment for one work item (one branch `work/<id>`).
It is authored *before* code and reviewed adversarially by the **spec-gate**
subagent. Code does not start until the gate passes. See `docs/process.md`.

## Author the spec

Copy this skill's `references/spec-template.md` to `docs/spec/<id>.md` and complete every
section. The gate fails a spec that is missing any of them.

- **Goal** — what this work item delivers, bounded.
- **Non-goals** — what's explicitly out of scope. **Required**: without them the
  gate cannot distinguish an authorized deferral from a silent scope cut.
- **Evidence** — every non-trivial claim cites a **concluded** spike (`SPIKE-<n>`),
  a code path (`file:line`), or a doc. Use the `spike` skill for uncertainties.
- **Spec items** — each normative requirement gets a stable ID (`<PREFIX>-<n>`) so
  it is citable in code (an `implements <PREFIX>-1` marker in a comment) and traceable.
- **Acceptance criteria** — executable commands (prefer `pixi run` tasks), written
  verbatim in a fenced block and **frozen here**. Each ties to a spec item. The
  impl gate re-runs them itself; never author criteria that pass without exercising
  real behavior.

A spec is **fully signed** only when every item has all three of: evidence, a
criterion, and spec-gate sign-off.

## Run the spec gate

Invoke the **`spec-gate`** subagent to review the spec (and every ADR it depends
on) adversarially. It hunts for: unauthorized scope cuts, uncited claims, open
questions, and infeasibility. On a `fail`, address each finding by editing the
spec (and/or concluding more spikes) and re-run — do not start implementation.

On a `pass`, present the spec to the **human for sign-off**. Implementation begins
only after the human approves the spec — spec→impl is a human gate, not just an AI one.

## Back-edge

If implementation reveals the spec is wrong, return here: edit the spec and re-run
the spec gate before continuing. The spec is the contract; keep it true.
