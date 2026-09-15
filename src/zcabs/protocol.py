# SPDX-License-Identifier: AGPL-3.0-or-later
"""LOOK/FORMAT protocol. Headers stay colon. Integers never belong here."""

from __future__ import annotations

import re
from dataclasses import dataclass

FORMAT_TEMPLATE = "the {string} number is {integer}"
LOOK_UNAVAILABLE = "unavailable"

INT_MIN = 100_000
INT_MAX = 999_999

_LOOK_RE = re.compile(r"^LOOK:\s*(.*)$", re.MULTILINE)
_FORMAT_RE = re.compile(r"^FORMAT:\s*(.*)$", re.MULTILINE)
_SPOKEN_RE = re.compile(
    r"\bthe\s+([A-Za-z][A-Za-z0-9_\-]*)\s+number\s+is\s+(\d+)\b",
    re.IGNORECASE,
)
_PAIR_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*(\d+)\s*$")
_VALUE_RE = re.compile(r"\bZCABS_VALUE\s*[:=]\s*(\d+)\b", re.IGNORECASE)
_KEY_EQ_RE = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*(\d{6})\b"
)


def is_live_integer(n: int) -> bool:
    return INT_MIN <= n <= INT_MAX


def format_spoken(string: str, integer: int) -> str:
    return f"the {string} number is {integer}"


def emit_look(target: str | None) -> str:
    look = target if target else LOOK_UNAVAILABLE
    return f"LOOK: {look}\nFORMAT: {FORMAT_TEMPLATE}"


def parse_look_block(text: str) -> tuple[str | None, str | None]:
    look_m = _LOOK_RE.search(text)
    fmt_m = _FORMAT_RE.search(text)
    look = look_m.group(1).strip() if look_m else None
    fmt = fmt_m.group(1).strip() if fmt_m else None
    return look, fmt


def parse_pair(text: str) -> tuple[str, int] | None:
    """First string=integer line. Comments and blanks skipped."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _PAIR_RE.match(line)
        if not m:
            continue
        n = int(m.group(2))
        if not is_live_integer(n):
            continue
        return m.group(1), n
    return None


def pair_line(key: str, value: int) -> str:
    if not is_live_integer(value):
        raise ValueError("integer outside live range")
    return f"{key}={value}\n"


@dataclass(frozen=True)
class Spoken:
    string: str
    integer: int
    form: str


def extract_spoken(text: str, expected_string: str | None = None) -> list[Spoken]:
    """Structured candidates only. Bare digits are not retrieval."""
    found: list[Spoken] = []
    seen: set[tuple[str, int, str]] = set()

    def add(string: str, integer: int, form: str) -> None:
        if not is_live_integer(integer):
            return
        item = (string.lower(), integer, form)
        if item in seen:
            return
        seen.add(item)
        found.append(Spoken(string=string, integer=integer, form=form))

    for m in _SPOKEN_RE.finditer(text):
        add(m.group(1), int(m.group(2)), "format")

    for m in _KEY_EQ_RE.finditer(text):
        add(m.group(1), int(m.group(2)), "pair")

    if expected_string:
        for m in _VALUE_RE.finditer(text):
            add(expected_string, int(m.group(1)), "zcabs_value")

    if expected_string:
        want = expected_string.lower()
        preferred = [s for s in found if s.string.lower() == want]
        if preferred:
            return preferred
    return found
