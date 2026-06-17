---
name: spike
description: Resolve an uncertainty during spec authoring by running a throwaway investigation and recording a concluded docs/spike/SPIKE-<n>.md evidence artifact. Use when a spec or ADR makes a design claim that is not yet backed by a concluded spike, a cited code path, or a doc — the spec gate rejects uncited claims and open questions.
---

A **spike** is a throwaway investigation that resolves an uncertainty during spec
authoring. It is an *evidence artifact*, **not a lifecycle phase** — gathering
evidence is part of completing the spec. A spike is edited freely **while `open`**,
but a **`concluded` spike is frozen, reproducible evidence** (see below): every
non-trivial spec/ADR claim must cite one (or existing code / a doc). An uncited claim,
or one citing an `open` spike, is a spec-gate finding.

## When to spike

- A spec/ADR asserts something about how a tool, library, or the codebase behaves
  that you have not verified.
- A design depends on a capability you are assuming exists.
- There is an open question the spec cannot answer without trying something.

If the claim is already backed by a code path you can cite (`file:line`) or an
authoritative doc, cite that instead — do not spike what is already evidenced.

## How to run a spike

1. **Frame the question.** State the single uncertainty in one sentence. One spike
   resolves one question.
2. **Investigate with a re-runnable `verify`.** Probe the *real* subject of the
   question — run the actual tool/command, call the real API, read the cited code.
   Record the exact command (or a script committed under `refs/`) as `verify` so the
   finding can be **re-derived**, and depend on reality: a script that hardcodes/echoes
   the conclusion, or measures a convenient neighbour of the claim, is a *false spike*.
   Prefer a **Python probe driven by `pixi run`** (`refs/spike-<n>/probe.py`): pixi's
   locked deps make the re-derivation reproducible and catch environment drift, while the
   probe can still shell out to the real subject in any language (compile + run a binary,
   call a CLI, hit the API).
3. **Conclude.** Write the finding the `verify` actually demonstrates — the answer,
   not a summary of the attempt. Record the `claim` it backs and its scope (input,
   version, real-vs-mocked). If inconclusive, the spike stays `open` and is not
   evidence yet; keep going.
4. **Record it** — run `python .agent/scripts/new_spike.py "<title>"`
   to create a correctly-numbered `docs/spike/SPIKE-<n>.md` from the template (it
   computes the next number and refuses to clobber an existing file). Write the
   question + investigation into it, set `status: concluded`, and cite its id (e.g.
   `SPIKE-3`) from the spec/ADR claim.

## Frozen, reproducible evidence (anti-deception)

A spike is *evidence*, and evidence the gate cannot re-derive is just an assertion. So:

- **Reproducible by default.** A concluded spike records a `verify` command/script that
  re-derives the finding by invoking the real subject of `question`. **Don't trust the
  prose finding — the `verify` is the check.** A `verify` that hardcodes/echoes its
  conclusion, never invokes the real subject, reads a fixture it authored, or measures a
  *neighbour* of the claim (smaller input, wrong version, a mock, a proxy metric, the
  happy path of a "for all" claim) is a **false spike** — fabricated evidence — even if
  it runs green (`docs/coding-standards.md` §5).
- **`claim` ties evidence to assertion.** Record the exact spec-item assertion (with its
  quantifier/scope) the spike backs; the `verify` must exercise *that* — same input
  domain, version, the real dependency, the claimed metric.
- **Load-bearing ⇒ the `verify` becomes an acceptance criterion** (tagged to the spec
  item it evidences), so the impl gate + CI re-run it — which also catches the
  assumption going stale later.
- **`reproducible: no`** is for genuinely un-re-runnable probes (live external API,
  timing, manual UX) *only*, and is the **weakest** evidence: it must commit the raw
  observation (transcript / capture / annotated screenshot) under `refs`, give a
  `reason`, argue no re-runnable proxy (recorded fixture / sandbox) exists, and it **may
  not be the sole evidence for a load-bearing claim**.
- **Frozen.** A `concluded` spike is immutable in spirit — if reality changes, write a
  NEW spike (next number) rather than editing it; git preserves the snapshot.

Only **`concluded`** spikes are evidence; an approved spec has **no open questions**.
See `docs/process.md`.
