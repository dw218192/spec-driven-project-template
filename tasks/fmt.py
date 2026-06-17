#!/usr/bin/env python3
"""`pixi run fmt` — verify formatting.

Skeleton (Python default: `ruff format --check`, non-mutating so it works as a
criterion — drop `--check` to format in place). Edit for your stack: replace the active
line below and `pixi add` the tool. Alternatives at the bottom. Project-owned (the
template sync never overwrites `tasks/`).

Recursive formatters scan everything under `.` — including the in-tree pixi env (`.pixi/`,
which ruff skips because it's gitignored) and the vendored framework dirs, which it does
NOT skip. So we exclude the framework; gofmt ignores neither — scope it to
`tracked_files(...)` (see the Go hint).
"""

import sys

from utils import run

# Vendored framework dirs — never format these (the template sync owns/overwrites them).
FRAMEWORK = ".agent,.claude,.codex,.github"

sys.exit(run("ruff", "format", "--check", ".", f"--exclude={FRAMEWORK}"))

# Other stacks — swap the line above (`pixi add <tool>`, or `pixi add --pypi <tool>`):
#   C/C++   clang-format (PyPI)  ->  from utils import tracked_files
#                                    run("clang-format", "--dry-run", "--Werror",
#                                        *tracked_files(".c", ".cc", ".cpp", ".h", ".hpp"))
#   JS/TS   prettier             ->  run("prettier", "--check", ".")
#   Go      gofmt                ->  gofmt -l exits 0 even when unformatted AND recurses into
#                                    .pixi/ — scope to tracked files and fail on any output:
#                                      import subprocess; from utils import tracked_files
#                                      bad = subprocess.run(["gofmt", "-l", *tracked_files(".go")],
#                                                           capture_output=True, text=True).stdout
#                                      print(bad, end=""); sys.exit(1 if bad.strip() else 0)
#   Rust    rustfmt              ->  run("cargo", "fmt", "--check")
