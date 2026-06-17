#!/usr/bin/env python3
"""`pixi run build` — build this project's artifacts.

Skeleton (Python default: the `build` module — sdist + wheel; needs a build backend in
`pyproject.toml`). Edit for your stack; alternatives at the bottom. Project-owned (the
template sync never overwrites `tasks/`).
"""

import sys

from utils import run

sys.exit(run(sys.executable, "-m", "build"))

# Other stacks — swap the line above:
#   C/C++   cmake + ninja (PyPI)  ->  run("cmake", "-S", ".", "-B", "build", "-G", "Ninja")
#                                     then run("cmake", "--build", "build")
#   JS/TS                         ->  run("npm", "run", "build")
#   Go                            ->  run("go", "build", "./...")
#   Rust                          ->  run("cargo", "build", "--release")
