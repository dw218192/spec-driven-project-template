---
name: remote-memory
description: Set up and operate the git-remote sync of the agent's machine-local memory directory. Use to configure the memory remote the first time, to push or pull memory manually, to onboard a new machine, or to resolve a memory merge conflict. The memory_push Stop hook handles routine per-turn pushes automatically once setup is done.
---

The agent's durable memory lives **outside this repo** in its machine-local memory
directory, and is kept in a **git remote** so it survives machine loss and follows
you across machines. Routine syncing is automatic — the `memory_push` Stop hook
(`.agent/scripts/memory_push.py`) commits and pushes on each turn-end. This skill
covers the one-time setup and the manual operations the hook does not.

## Where the memory dir is

Claude Code stores per-project memory at
`~/.claude/projects/<project-id>/memory/` (the same dir for every worktree of the
repo). The `memory_push` hook locates it from the Stop event's `transcript_path`
(its sibling `memory/` dir), or honors `CLAUDE_MEMORY_DIR` if set.

## One-time setup (per project, per remote)

Make the memory dir its own git repo and point it at a **private** remote keyed on
this project's identity (a dedicated repo, or a per-project branch). Run the helper:

```bash
python .agent/scripts/setup_memory_remote.py <your-private-memory-remote>
```

…or do the equivalent by hand:

```bash
cd ~/.claude/projects/<project-id>/memory
git init
git remote add origin <your-private-memory-remote>
git add -A && git commit -m "memory: init"
git push -u origin HEAD
```

Until a remote exists, the Stop hook is a silent no-op.

### MEMORY.md merge safety

`MEMORY.md` is an append-y index that two machines may edit concurrently. Install a
union merge driver so syncs don't clobber:

```bash
git config merge.memunion.driver "git merge-file -p --union %A %O %B > %A"
printf 'MEMORY.md merge=memunion\n' >> .gitattributes
```

## Manual operations

- **Push now:** `cd <memory-dir> && git add -A && git commit -m "memory: sync" && git push`
- **Onboard a new machine / pull latest:** clone the memory remote *into* the
  memory dir (or `git pull` if already initialized) before starting a session.
- **Resolve a conflict:** with the union driver above most merges auto-resolve;
  otherwise edit `MEMORY.md`/topic files, keeping both sides' facts.

## Privacy

Memory accumulates sensitive repo and user context. Use a **private** remote, and
keep anything that must never leave the machine out of the memory files (or in a
path the hook does not track).

## Codex

Codex's memory store is `~/.codex/memories/` (off by default — enable
`features.memories`). Point the setup helper at it —
`python .agent/scripts/setup_memory_remote.py <remote> --memory-dir ~/.codex/memories`
— and Codex pushes it via the same `.agent/scripts/memory_push.py --codex` (a `Stop` hook, or a
`notify` target). See `.codex/README.md`.
