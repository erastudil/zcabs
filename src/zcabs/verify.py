# SPDX-License-Identifier: AGPL-3.0-or-later
"""Host-side invariant. Fail closed. Do not echo the expected integer."""

from __future__ import annotations

from dataclasses import dataclass

from .protocol import extract_spoken
from .store import StoreError, observe


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    reason: str
    extracted: int | None = None


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
