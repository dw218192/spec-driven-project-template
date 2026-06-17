---
id: SPIKE-0                 # ^SPIKE-[0-9]+$   (required)
title: <short title>        # required
question: <the single uncertainty being investigated>   # required
claim: <the exact spec-item assertion + its scope/quantifier this spike backs>   # required once cited
verify: <a `pixi run` command (or a refs/ probe) that RE-DERIVES the finding by invoking the real subject of `question`>   # or: none
reproducible: yes           # yes | no   (no = inherently un-re-runnable; the weakest evidence)
reason: <why it cannot be re-run>   # REQUIRED iff reproducible: no
findings: <the conclusion the `verify` actually demonstrates>   # the evidence
status: open                # open | concluded  (only `concluded` is citable evidence)
date: <YYYY-MM-DD>          # when run (git is the authoritative freeze)
refs:                       # the committed verify script and/or raw-observation transcript
  - refs/spike-0/probe.py   # Python probe run via pixi (locked env = reproducible); may invoke the real subject in any language
---

> Copy via `new_spike.py`. A spike resolves ONE question and is **frozen once
> `concluded`** — if reality changes, write a NEW spike, don't edit this one (git is
> the snapshot). Only a `concluded` spike is evidence. See the `spike` skill.

## Investigation

What you tried, what you observed, why the finding follows. Be concrete. The `verify`
must **actually invoke the subject of `question`** and re-derive `findings` from
reality — a method that hardcodes/echoes the conclusion, or measures a convenient
*neighbour* of `claim` (a smaller input, a mock, the happy path, a proxy metric), is a
**false spike** (fabricated evidence) even if it runs green. State what would make the
finding FALSE, and confirm `verify` would actually show it.
