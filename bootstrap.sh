#!/bin/bash
set -e

# Repo setup — ensure pixi is installed, then materialize the environment.
# pixi brings its own Python, so this works on a machine that has neither
# python nor pixi. Mirrors the minimal "install the toolchain on demand,
# then sync" pattern from repokit's old bootstrap.sh.
# Usage: ./bootstrap.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# ── pixi (install if absent) ──────────────────────────────────────────
if command -v pixi >/dev/null 2>&1; then
    PIXI="pixi"
elif [ -x "$HOME/.pixi/bin/pixi" ]; then
    PIXI="$HOME/.pixi/bin/pixi"
else
    echo "Installing pixi..."
    curl -fsSL https://pixi.sh/install.sh | bash
    PIXI="$HOME/.pixi/bin/pixi"
fi

# ── sync the environment ──────────────────────────────────────────────
# A skeleton pixi.toml ships and the tasks/*.py default to a Python toolchain.
"$PIXI" install

# ── generate the agent surface (.claude/.codex from .agent/ — gitignored build output) ──
"$PIXI" exec --with python -- python .agent/scripts/gen_agents.py

echo "OK — environment ready. The test/lint/fmt/build tasks default to pytest/ruff/build"
echo "(tasks/*.py) — run 'pixi add pytest ruff python-build', or adapt them for your stack."
echo "Try: pixi run check"
