# SPDX-License-Identifier: AGPL-3.0-or-later
"""zcabs: LOOK/FORMAT retrieval. Fail closed."""

from .harness import EphemeralStore, Harness, WrapResult
from .protocol import (
    FORMAT_TEMPLATE,
    LOOK_UNAVAILABLE,
    Spoken,
    emit_look,
    extract_spoken,
    format_spoken,
    pair_line,
    parse_look_block,
    parse_pair,
)
from .scan import Finding, scan_tree
from .store import look, mint, observe, rotate
from .verify import VerifyResult, verify_file, verify_text
from .wrap import CANARY, wrap_command

__version__ = "1.0.0"
__all__ = [
    "CANARY",
    "EphemeralStore",
    "Finding",
    "FORMAT_TEMPLATE",
    "Harness",
    "LOOK_UNAVAILABLE",
    "Spoken",
    "VerifyResult",
    "WrapResult",
    "emit_look",
    "extract_spoken",
    "format_spoken",
    "look",
    "mint",
    "observe",
    "pair_line",
    "parse_look_block",
    "parse_pair",
    "rotate",
    "scan_tree",
    "verify_file",
    "verify_text",
    "wrap_command",
    "__version__",
]
