# SPDX-License-Identifier: AGPL-3.0-or-later
"""Emit the drop-in genome. No integers."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_prompt(name: str = "genome") -> str:
    if name != "genome":
        raise ValueError("ERROR: unknown prompt")
    path = repo_root() / "prompts" / "genome.md"
    return path.read_text(encoding="utf-8")
