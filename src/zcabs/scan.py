# SPDX-License-Identifier: AGPL-3.0-or-later
"""Fail if a store, pointer, or live integer leaked into a tree."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .protocol import is_live_integer
from .store import StoreError, load_all_integers, pointer_path, resolve_home, store_exists

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".eggs",
    "build",
    "dist",
}

POINTER_NAMES = {"zcabs.pointer", "zcahc.pointer"}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".txt",
    ".toml",
    ".cfg",
    ".ini",
    ".rst",
    ".csv",
    ".html",
    ".css",
    ".xml",
    ".sh",
    ".ps1",
    ".bat",
    ".dat",
}

_SIX_DIGIT_RE = re.compile(r"(?<!\d)(\d{6})(?!\d)")


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "path": self.path, "detail": self.detail}


def scan_tree(root: Path | str, home: Path | str | None = None) -> list[Finding]:
    base = Path(root).expanduser().resolve()
    if not base.exists():
        return [Finding("missing", str(base), "path does not exist")]

    live: set[int] = set()
    home_path: Path | None = None
    try:
        home_path = resolve_home(home) if home is not None else (
            resolve_home(None) if store_exists(None) else None
        )
        if home_path is not None and store_exists(home_path):
            live = load_all_integers(home_path)
    except StoreError:
        live = set()

    findings: list[Finding] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        here = Path(dirpath)
        if here.name == ".zcabs":
            findings.append(Finding("store-dir", str(here), "committed store directory"))
            dirnames[:] = []
            continue
        if home_path is not None:
            try:
                here.relative_to(home_path)
                continue
            except ValueError:
                pass
        for name in filenames:
            path = here / name
            findings.extend(_scan_file(path, live))
    return findings


def _scan_file(path: Path, live: set[int]) -> list[Finding]:
    out: list[Finding] = []
    lname = path.name.lower()
    if lname in POINTER_NAMES:
        out.append(Finding("pointer", str(path), "pointer file in tree"))
        return out
    if lname == "pointer" and _looks_like_pointer(path):
        out.append(Finding("pointer", str(path), "pointer file in tree"))
        return out
    if path.suffix.lower() not in TEXT_SUFFIXES and lname not in {"makefile", "dockerfile", "license", "copyright"}:
        if not _is_probably_text(path):
            return out
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return out
    if live:
        seen: set[int] = set()
        for m in _SIX_DIGIT_RE.finditer(text):
            val = int(m.group(1))
            if val in live and val not in seen and is_live_integer(val):
                seen.add(val)
                out.append(Finding("leak", str(path), str(val)))
    return out


def _looks_like_pointer(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        return line.lower().startswith("identity=")
    return False


def _contains_int(text: str, n: int) -> bool:
    s = str(n)
    start = 0
    while True:
        i = text.find(s, start)
        if i < 0:
            return False
        before = text[i - 1] if i > 0 else ""
        after = text[i + len(s)] if i + len(s) < len(text) else ""
        if not (before.isdigit() or after.isdigit()):
            return True
        start = i + len(s)


def _is_probably_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:512]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    return True
