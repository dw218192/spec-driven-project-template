#!/usr/bin/env python3
"""Pull framework updates from the upstream template into this project.

A GitHub template repo is a one-time copy with no upstream link, so template updates
don't arrive automatically. This does a deliberate sync: fetch the template and check
out the FRAMEWORK-owned paths over your copy, leaving PROJECT-owned files (pixi.toml,
your specs/ADRs/spikes, README, source, docs/project-notes.md) untouched. It stages
the changes for you to review and commit — it does not commit.

Usage:
    python .agent/scripts/update_from_template.py [<template-url-or-remote>] [--ref main]

With no argument it uses a git remote named 'template'; pass a URL the first time and
it adds that remote. Updates/adds framework files; it does not delete files removed
upstream (git status shows what changed — remove stale ones by hand if needed).
"""

from __future__ import annotations

import argparse
import subprocess
import sys

# Framework-owned paths — synced from upstream. Everything else is project-owned and
# never touched: pixi.toml, docs/{spec,adr,spike}/*, README.md, your source, and
# docs/project-notes.md (where your project-specific instructions live).
FRAMEWORK_PATHS = [
    ".claude", ".codex", ".github", ".agent",
    "docs/process.md", "docs/coding-standards.md",
    "bootstrap.sh", "bootstrap.ps1", ".gitattributes",
    "AGENTS.md", "CLAUDE.md",
]


def git(*args, check=True, capture=False):
    return subprocess.run(["git", *args], text=True, capture_output=capture, check=check)


def _is_url(s: str) -> bool:
    return "://" in s or "@" in s or s.endswith(".git")


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync framework files from the upstream template.")
    ap.add_argument("template", nargs="?", help="template git URL, or an existing remote name (default: 'template')")
    ap.add_argument("--ref", default="main", help="template branch/ref to sync (default: main)")
    args = ap.parse_args()

    # Refuse only if FRAMEWORK files are dirty — the checkout would collide with them.
    # (Uncommitted project work elsewhere is fine and left alone.)
    dirty = git("status", "--porcelain", "--", *FRAMEWORK_PATHS, capture=True).stdout.strip()
    if dirty:
        sys.exit("framework files have uncommitted changes — commit or stash first:\n" + dirty)

    remote = "template"
    if args.template and _is_url(args.template):
        remotes = git("remote", capture=True).stdout.split()
        git("remote", "set-url" if remote in remotes else "add", remote, args.template)
    elif args.template:
        remote = args.template

    git("fetch", "--quiet", remote)
    ref = f"{remote}/{args.ref}"

    for path in FRAMEWORK_PATHS:
        if git("checkout", ref, "--", path, check=False, capture=True).returncode != 0:
            print(f"  (skipped {path}: not present in {ref})", file=sys.stderr)

    diff = git("diff", "--cached", "--stat", capture=True).stdout
    if diff.strip():
        print(diff.rstrip())
        print(f"\nFramework files updated from {ref}; project files untouched.")
        print("Review with `git diff --cached`, then commit.")
    else:
        print(f"Already up to date with {ref}.")


if __name__ == "__main__":
    main()
