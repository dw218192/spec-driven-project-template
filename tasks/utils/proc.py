"""Run subprocesses the way a pixi task wants: echo, run, propagate the exit code."""

from __future__ import annotations

import subprocess
import sys


def run(*cmd: str) -> int:
    """Echo *cmd*, run it, and return its exit code — use as `sys.exit(run(...))`.

    Printing the command first keeps CI logs legible; the real exit code is propagated
    untouched, so nothing masks a failure. A missing executable fails cleanly with 127
    (the shell's "command not found") and a one-line hint, rather than a traceback.
    """
    print("$", *cmd, flush=True)
    try:
        return subprocess.run(cmd).returncode
    except FileNotFoundError:
        print(
            f"command not found: {cmd[0]} - install it (e.g. pixi add ...)",
            file=sys.stderr,
        )
        return 127
