"""Shared, language-agnostic helpers for this project's `tasks/*.py` scripts.

Importable because pixi runs tasks as `python tasks/<name>.py`, which puts `tasks/`
first on `sys.path` — so a task can just `from utils import run`. Project-owned (the
template sync never touches `tasks/`): extend these freely as the project grows.

    proc.run             echo + run a command, propagate its exit code (the criterion contract)
    git.tracked_files    source files respecting .gitignore (git ls-files)
    git.repo_root        the repo's top-level directory
    fs.write_if_changed  write a file only when content differs (no needless touch)
    fs.touch             create-or-update a file (parents made as needed)
    gen.Manifest         track generated outputs: write-on-change + drift detection
"""

from __future__ import annotations

from .fs import touch, write_if_changed
from .gen import Manifest, content_hash
from .git import repo_root, tracked_files
from .proc import run

__all__ = [
    "run",
    "tracked_files",
    "repo_root",
    "write_if_changed",
    "touch",
    "Manifest",
    "content_hash",
]
