# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.prompt import load_prompt


class PromptTests(unittest.TestCase):
    def test_genome_teaches_look_format_without_integers(self):
        text = load_prompt("genome")
        self.assertIn("LOOK", text)
        self.assertIn("FORMAT", text)
        self.assertIn("DONT_KNOW", text)
        self.assertNotRegex(text, r"\b\d{6}\b")
        self.assertNotRegex(text, re.compile(r"do not (guess|invent|hallucinate).{0,40}do not", re.I))


if __name__ == "__main__":
    unittest.main()
