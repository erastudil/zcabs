# SPDX-License-Identifier: AGPL-3.0-or-later
"""Run a command. On success, rotate canary and print LOOK/FORMAT."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from .store import StoreError, ensure_cap, look, mint, rotate, store_exists


CANARY = "canary"


def wrap_command(
    argv: list[str],
    home: Path | str | None = None,
    stdin=None,
    stdout=None,
    stderr=None,
) -> int:
    if not argv:
        print("ERROR: wrap needs a command", file=stderr or sys.stderr)
        return 2

    out = stdout or sys.stdout
    err = stderr or sys.stderr

    try:
        if not store_exists(home):
            mint(home)
            print("zcabs: minted default store", file=err)
        ensure_cap(CANARY, home)
    except StoreError as e:
        print(str(e), file=err)
        return 2

    cmd = list(argv)
    executable = shutil.which(cmd[0]) or cmd[0]
    try:
        proc = subprocess.run([executable, *cmd[1:]], stdin=stdin)
        if proc.returncode != 0:
            return int(proc.returncode)
    except FileNotFoundError:
        print(f"ERROR: command not found: {cmd[0]}", file=err)
        return 127
    except OSError as e:
        print(f"ERROR: failed to execute {cmd[0]}: {e}", file=err)
        return 126

    try:
        rotate(CANARY, home)
        block = look(CANARY, home)
    except StoreError as e:
        print(str(e), file=err)
        return 2

    if not block.endswith("\n"):
        block += "\n"
    out.write(block)
    return 0
