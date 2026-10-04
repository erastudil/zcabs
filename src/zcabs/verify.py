# SPDX-License-Identifier: AGPL-3.0-or-later
"""Host-side invariant. Fail closed. Do not echo the expected integer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .protocol import extract_spoken
from .store import StoreError, observe


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    reason: str
    extracted: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"ok": self.ok, "reason": self.reason}
        if self.ok and self.extracted is not None:
            data["extracted"] = self.extracted
        return data


def verify_text(text: str, key: str, home=None) -> VerifyResult:
    if not text or not str(text).strip():
        return VerifyResult(False, "ERROR: empty candidate")

    try:
        name, expected = observe(key, home)
    except StoreError as e:
        return VerifyResult(False, str(e))

    spoken = extract_spoken(str(text), expected_string=name)
    if not spoken:
        return VerifyResult(False, "ERROR: invariant failed. no structured retrieval in candidate.")

    for item in spoken:
        if item.string.lower() == name.lower() and item.integer == expected:
            return VerifyResult(True, "PASS", extracted=item.integer)

    return VerifyResult(False, "ERROR: invariant failed. candidate does not match store.")


def verify_file(path: Path | str, key: str = "canary", home=None) -> VerifyResult:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        return VerifyResult(False, f"ERROR: file not found: {p}")
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return VerifyResult(False, f"ERROR: failed to read file: {e}")
    return verify_text(text, key, home)
