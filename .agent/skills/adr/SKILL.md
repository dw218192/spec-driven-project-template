---
name: adr
description: Record a new architectural decision, or supersede an existing one, as a plain-markdown ADR under docs/adr/. Use when making a significant or hard-to-reverse design decision, or when an accepted decision must change (which requires a NEW superseding ADR — accepted ADRs are immutable). Handles the frontmatter schema, numbering, and the additive supersede workflow (accepted ADRs are never edited — reverse links are derived).
---

An **ADR** (Architecture Decision Record) captures one significant, hard-to-reverse
decision as plain markdown under `docs/adr/`. ADRs are immutable once accepted; the
durable record is git. See `docs/process.md`.

## Author a new ADR

Run `python .agent/scripts/new_adr.py <slug> "<title>"` to create
`docs/adr/<n>-<slug>.md` from the template with id / title / date stamped (it computes
the next number and refuses to clobber). Then fill the body; the frontmatter looks
like:

```yaml
id: ADR-<n>
title: <decision title>
status: proposed            # proposed | accepted  (superseded is derived, not stored)
date: <YYYY-MM>
supersedes: []              # forward edge only: [ADR-<k>] this ADR replaces
```

There is **no `rejected`** status — a rejected ADR is simply never committed. Body
sections: **Context** (forces, constraints, cited evidence), **Decision** (what we
will do), **Consequences** (trade-offs, follow-on work).

Back claims with evidence exactly as a spec does (concluded spikes, code paths,
docs).

## Acceptance

An ADR is accepted by the human at sign-off; set `status: accepted` then. Once
accepted, the **`adr_immutable` hook denies any edit** to the file.

## Supersede (additive — never edit the old ADR)

Accepted ADRs are immutable; the `adr_immutable` hook **denies any edit** to one, so
superseding is purely **additive**:

1. Author a **new** ADR that makes the new decision; set its `supersedes: [ADR-<n>]`.
   That forward edge is the *only* stored link.
2. Do **not** touch ADR-<n> — it stays `accepted` and immutable in git history.

The reverse link ("who superseded ADR-<n>?") and the *superseded* status are
**derived**, not stored. Run the helper to compute them from the `supersedes` edges:

```bash
python .agent/scripts/adr_status.py
```

It prints each ADR's status + what (if anything) supersedes it, and flags dangling
`supersedes` references.
