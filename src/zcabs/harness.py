# SPDX-License-Identifier: AGPL-3.0-or-later
"""Programmatic test and evaluation harness for zcabs."""

from __future__ import annotations

import io
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .prompt import load_prompt
from .protocol import format_spoken, parse_look_block
from .scan import Finding, scan_tree
from .store import (
    DEFAULT_CAPS,
    DEFAULT_IDENTITY,
    DECOY_COUNT,
    MintResult,
    StoreError,
    ensure_cap,
    look,
    mint,
    observe,
    rotate,
    store_exists,
)
from .verify import VerifyResult, verify_file, verify_text
from .wrap import CANARY, wrap_command


@dataclass(frozen=True)
class WrapResult:
    exit_code: int
    look_block: str = ""
    target: str | None = None
    format: str | None = None

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "look_block": self.look_block,
            "target": self.target,
            "format": self.format,
        }


class Harness:
    """Ephemeral or persistent zcabs store environment for test and eval harnesses."""

    def __init__(
        self,
        home: Path | str | None = None,
        identity: str = DEFAULT_IDENTITY,
        extra_caps: tuple[str, ...] = DEFAULT_CAPS,
        decoys: int = DECOY_COUNT,
        auto_clean: bool | None = None,
        force_mint: bool = False,
    ) -> None:
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        if home is None:
            self._temp_dir = tempfile.TemporaryDirectory(prefix="zcabs_harness_")
            self._home = Path(self._temp_dir.name) / "store_home"
            self._auto_clean = True if auto_clean is None else auto_clean
        else:
            self._home = Path(home).expanduser().resolve()
            self._auto_clean = False if auto_clean is None else auto_clean

        self._identity = identity
        self._extra_caps = extra_caps
        self._decoys = decoys

        if force_mint or not store_exists(self._home):
            self.mint(force=force_mint)

    @property
    def home(self) -> Path:
        return self._home

    def env(self) -> dict[str, str]:
        """Environment mapping providing ZCABS_HOME for child processes."""
        return {"ZCABS_HOME": str(self._home)}

    def mint(self, force: bool = True) -> MintResult:
        return mint(
            home=self._home,
            identity_key=self._identity,
            extra_caps=self._extra_caps,
            num_decoys=self._decoys,
            force=force,
        )

    def look(self, key: str = "identity") -> str:
        return look(key=key, home=self._home)

    def observe(self, key: str = "identity") -> tuple[str, int]:
        return observe(key=key, home=self._home)

    def rotate(self, key: str = CANARY) -> None:
        rotate(key=key, home=self._home)

    def ensure_cap(self, key: str) -> None:
        ensure_cap(key=key, home=self._home)

    def verify(self, candidate: str, key: str = CANARY) -> VerifyResult:
        return verify_text(candidate, key=key, home=self._home)

    def verify_file(self, path: Path | str, key: str = CANARY) -> VerifyResult:
        return verify_file(path, key=key, home=self._home)

    def format_expected(self, key: str = "identity") -> str:
        name, val = self.observe(key)
        return format_spoken(name, val)

    def scan(self, path: Path | str = ".") -> list[Finding]:
        return scan_tree(path, home=self._home)

    def wrap(
        self,
        argv: list[str],
        key: str = CANARY,
        look_file: Path | str | None = None,
        quiet: bool = True,
        stdin: Any = None,
        stdout: Any = None,
        stderr: Any = None,
    ) -> WrapResult:
        captured_out = io.StringIO() if (stdout is None and quiet) else stdout
        rc = wrap_command(
            argv=argv,
            home=self._home,
            stdin=stdin,
            stdout=captured_out,
            stderr=stderr,
            key=key,
            look_file=look_file,
            quiet=quiet and (stdout is not None or captured_out is not None),
        )
        if rc == 0:
            block = self.look(key)
            target, fmt = parse_look_block(block)
            return WrapResult(exit_code=0, look_block=block, target=target, format=fmt)
        return WrapResult(exit_code=rc)

    def genome_prompt(self) -> str:
        return load_prompt("genome")

    def cleanup(self) -> None:
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None
        elif self._auto_clean and self._home.exists():
            shutil.rmtree(self._home, ignore_errors=True)

    def __enter__(self) -> Harness:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._auto_clean:
            self.cleanup()


EphemeralStore = Harness
