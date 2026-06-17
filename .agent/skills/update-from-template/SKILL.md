---
name: update-from-template
description: Pull later framework improvements (process, gates, skills, hooks, scripts) from the upstream template into this project — without touching project content. Use when the template repo has shipped updates you want to adopt; it syncs only framework-owned paths and stages them for review.
---

A GitHub template is a one-time copy with **no upstream link**, so framework
improvements don't arrive on their own. This skill performs a deliberate, reviewable
sync: it checks out the **framework-owned** paths from the template remote over your
copy and leaves everything **project-owned** untouched.

## What syncs vs. what's yours

- **Synced (framework):** `.claude/`, `.codex/`, `.agent/`, `.github/`,
  `docs/process.md`, `docs/coding-standards.md`, `bootstrap.*`, `.gitattributes`,
  `AGENTS.md`, `CLAUDE.md`.
- **Never touched (yours):** `pixi.toml`, `docs/{spec,adr,spike}/*`, your source,
  `README.md`, and `docs/project-notes.md` — which is exactly why project-specific
  agent instructions live in `docs/project-notes.md`, so `AGENTS.md` / `CLAUDE.md` stay
  syncable.

## Sync

1. **Commit or stash framework changes first.** The helper refuses if any framework
   file is dirty (the checkout would collide). Uncommitted *project* work is fine.
2. **Run the sync** — it stages the updated framework files; it does **not** commit:

   ```bash
   python .agent/scripts/update_from_template.py <template-git-url>   # first time — adds a `template` remote
   python .agent/scripts/update_from_template.py                      # thereafter — reuses it
   ```
   (`--ref <branch>` to track a non-`main` branch.)

3. **Review the staged diff — this is framework code that will run in your repo.**
   `git diff --cached`. The sync only *adds / updates*; it does **not** delete files
   the upstream removed, so scan `git status` for now-stale framework files and delete
   them by hand if the template dropped them.
4. **Regenerate, re-verify, then commit.** The `.claude/` + `.codex/` agent surface is
   gitignored build output, so rebuild it from the synced `.agent/` with
   `python .agent/scripts/gen_agents.py`. Then run `pixi run check` (and re-run the gates
   if you're mid-work), and commit the result as a framework-only change.

## Codex

The same script syncs `.codex/` (it's a framework path). **Trust the repo** so Codex
loads the refreshed `.codex/` layer. See `.codex/README.md`.
