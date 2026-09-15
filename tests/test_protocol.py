# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.protocol import (
    FORMAT_TEMPLATE,
    emit_look,
    extract_spoken,
    format_spoken,
    parse_look_block,
    parse_pair,
)


class ProtocolTests(unittest.TestCase):
    def test_emit_look_has_template_not_a_value(self):
        block = emit_look("/tmp/f_abc.dat")
        self.assertIn("LOOK: /tmp/f_abc.dat", block)
        self.assertIn(f"FORMAT: {FORMAT_TEMPLATE}", block)
        self.assertNotIn("=", block.split("FORMAT:")[0])

    def test_emit_look_unavailable(self):
        block = emit_look(None)
        look, fmt = parse_look_block(block)
        self.assertEqual(look, "unavailable")
        self.assertEqual(fmt, FORMAT_TEMPLATE)

    def test_parse_pair_skips_comments(self):
        pair = parse_pair("# comment\nbanana=847291\n")
        self.assertEqual(pair, ("banana", 847291))

    def test_parse_pair_rejects_small_integers(self):
        self.assertIsNone(parse_pair("banana=9999\n"))

    def test_format_spoken(self):
        self.assertEqual(format_spoken("banana", 847291), "the banana number is 847291")

    def test_extract_prefers_matching_string(self):
        text = "the apple number is 111111\nthe banana number is 847291\n"
        found = extract_spoken(text, expected_string="banana")
        self.assertEqual([(s.string.lower(), s.integer) for s in found], [("banana", 847291)])

    def test_extract_ignores_bare_digits(self):
        found = extract_spoken("all tests passed 847291")
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
