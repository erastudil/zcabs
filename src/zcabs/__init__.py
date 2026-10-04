# SPDX-License-Identifier: AGPL-3.0-or-later
"""zcabs: LOOK/FORMAT retrieval. Fail closed."""

from .harness import EphemeralStore, Harness, WrapResult
from .protocol import FORMAT_TEMPLATE, emit_look, format_spoken, parse_look_block, parse_pair
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
    "VerifyResult",
    "WrapResult",
    "emit_look",
    "format_spoken",
    "look",
    "mint",
    "observe",
    "parse_look_block",
    "parse_pair",
    "rotate",
    "scan_tree",
    "verify_file",
    "verify_text",
    "wrap_command",
    "__version__",
]
