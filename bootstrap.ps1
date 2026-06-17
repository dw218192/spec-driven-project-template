$ErrorActionPreference = "Stop"

# Repo setup — ensure pixi is installed, then materialize the environment.
# pixi brings its own Python, so this works on a machine that has neither
# python nor pixi. Mirrors the minimal "install the toolchain on demand,
# then sync" pattern from repokit's old bootstrap.ps1.
# Usage: ./bootstrap.ps1

$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $Root

# ── pixi (install if absent) ──────────────────────────────────────────
$Pixi = (Get-Command pixi -ErrorAction SilentlyContinue).Source
if (-not $Pixi) { $Pixi = "$env:USERPROFILE\.pixi\bin\pixi.exe" }
if (-not (Test-Path $Pixi)) {
    Write-Host "Installing pixi..."
    Invoke-RestMethod -UseBasicParsing https://pixi.sh/install.ps1 | Invoke-Expression
    $Pixi = "$env:USERPROFILE\.pixi\bin\pixi.exe"
}

# ── sync the environment ──────────────────────────────────────────────
# A skeleton pixi.toml ships and the tasks/*.py default to a Python toolchain.
& $Pixi install

# ── generate the agent surface (.claude/.codex from .agent/ — gitignored build output) ──
& $Pixi exec --with python -- python .agent/scripts/gen_agents.py

Write-Host "OK - environment ready. The test/lint/fmt/build tasks default to pytest/ruff/build"
Write-Host "(tasks/*.py) - run 'pixi add pytest ruff python-build', or adapt them for your stack."
Write-Host "Try: pixi run check"
