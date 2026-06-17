---
id: ADR-0
title: <decision title>
status: proposed          # proposed | accepted  (superseded is derived, not stored)
date: <YYYY-MM>
supersedes: []            # forward edge only: [ADR-2] this ADR replaces
---

# ADR-0 — <decision title>

> Copy to `docs/adr/<n>-<slug>.md`, number sequentially. Once `status: accepted`,
> this file is **immutable** (the `adr_immutable` hook denies edits) — amend only by
> a new superseding ADR. See `docs/process.md` and the `adr` skill.

## Context

The forces at play: what problem, what constraints, what was tried. Cite evidence
(concluded spikes, code paths, docs) the same way a spec does.

## Decision

The decision, stated plainly. What we will do.

## Consequences

What becomes easier and harder. Trade-offs accepted. Follow-on work.

## Supersedes

Accepted ADRs are immutable — supersede by authoring a new ADR with
`supersedes: [ADR-N]`; never edit this file. The reverse link is derived (the `adr`
skill's `adr_status.py`).
