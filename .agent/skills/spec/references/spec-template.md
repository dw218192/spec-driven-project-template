# Spec — <title>

Status: draft (pending spec-gate). Work item: `<id>`. Branch: `work/<id>`.
Implements: ADR-<n> (if any).

> Copy this file to `docs/spec/<id>.md` and fill it in. The spec gate reviews it
> adversarially before any code is written. See `docs/process.md` and the `spec` skill.

## Goal

What this work item delivers, in 2–4 sentences. Concrete and bounded.

## Non-goals

Explicitly out of scope. **Required** — without stated non-goals the spec gate
cannot tell an authorized deferral from a silent scope cut.

## Evidence

Back every non-trivial claim. Each entry cites a **concluded** spike
(`SPIKE-<n>`), a code path (`file:line`), or a doc — never an unbacked assertion.

- <claim> — `SPIKE-3` / `path/to/file.py:42` / link

## Spec items

Each normative requirement gets a stable ID (`<PREFIX>-<n>`). Every item needs
evidence + an acceptance criterion + spec-gate sign-off to be "fully signed".

- **<PREFIX>-1** <requirement>. Cited in code as an `implements <PREFIX>-1` comment (`#`, `//`, … per your language).
- **<PREFIX>-2** <requirement>.

## Acceptance criteria

Commands run via the repo tooling, **frozen here** and **re-run by the impl gate**.
Written verbatim in this fenced block so they execute exactly as shown. Each is a single
command — prefer a bare `pixi run <task>`; keep any args / quoting / regex inside the task,
not inline (criteria run without a shell, so they behave identically on every OS).

```text
# <PREFIX>-C1 (<PREFIX>-1): <what it verifies>
pixi run check

# <PREFIX>-C2 (<PREFIX>-2): a NEW test fails if <behavior> regresses — non-vacuous
#   (the criterion fails if that test is absent).
pixi run test
```

All criteria are executable and frozen at the spec gate; the impl gate re-runs
them itself rather than trusting the authoring agent.
