#!/usr/bin/env python3
"""`pixi run test` — run this project's tests.

Skeleton (Python default: pytest). The impl gate + CI re-run this, so it must exercise
REAL behavior — an empty pass is a criteria-gaming finding (`docs/coding-standards.md`
§5); with no tests pytest exits non-zero, so `pixi run check` stays red until you add
real ones. Edit for your stack; alternatives at the bottom. Project-owned (not synced).
"""

import sys

from utils import run

sys.exit(run("pytest"))

# Other stacks — swap the line above:
#   C/C++   ctest (CMake)  ->  run("ctest", "--test-dir", "build", "--output-on-failure")
#   JS/TS                  ->  run("npm", "test")
#   Go                     ->  run("go", "test", "./...")
#   Rust                   ->  run("cargo", "test")
