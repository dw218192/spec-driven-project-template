#!/usr/bin/env python3
"""`pixi run lint` — static checks.

Skeleton (Python default: ruff). Edit for your stack; add a type-checker here too
(mypy / pyright). Alternatives at the bottom. Project-owned (the template sync never
overwrites `tasks/`).

Recursive tools scan everything under `.` — including the in-tree pixi env (`.pixi/`,
which ruff skips because it's gitignored) and the vendored framework dirs, which it does
NOT skip. So we exclude the framework; a tool that ignores neither (e.g. gofmt) should be
scoped to `tracked_files(...)` instead (see the Go hint).
"""

import sys

from utils import run

# Vendored framework dirs — never lint these (the template sync owns/overwrites them).
FRAMEWORK = ".agent,.claude,.codex,.github"

sys.exit(run("ruff", "check", ".", f"--extend-exclude={FRAMEWORK}"))

# Other stacks — swap the line above (`pixi add <tool>`, or `pixi add --pypi <tool>`):
#   C/C++   clang-tidy (PyPI)  ->  from utils import tracked_files
#                                  run("clang-tidy", *tracked_files(".c", ".cpp"), "--", *flags)
#   JS/TS   eslint             ->  run("eslint", ".")
#   Go      golangci-lint      ->  run("golangci-lint", "run")   (module-aware; skips .pixi/)
#   Rust    clippy             ->  run("cargo", "clippy", "--", "-D", "warnings")
