# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.protocol import format_spoken
from zcabs.store import mint, observe
from zcabs.verify import verify_text


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"
        mint(self.home)
        self.name, self.value = observe("identity", self.home)

    def tearDown(self):
        self._tmp.cleanup()

    def test_format_passes(self):
        result = verify_text(format_spoken(self.name, self.value), "identity", self.home)
        self.assertTrue(result.ok)

    def test_pair_passes(self):
        result = verify_text(f"{self.name}={self.value}", "identity", self.home)
        self.assertTrue(result.ok)

    def test_wrong_integer_fails_without_echo(self):
        wrong = self.value + 1 if self.value < 999999 else self.value - 1
        result = verify_text(format_spoken(self.name, wrong), "identity", self.home)
        self.assertFalse(result.ok)
        self.assertNotIn(str(self.value), result.reason)

    def test_empty_fails(self):
        result = verify_text("  ", "identity", self.home)
        self.assertFalse(result.ok)

    def test_bare_number_fails(self):
        result = verify_text(f"tests passed {self.value}", "identity", self.home)
        self.assertFalse(result.ok)

    def test_decoy_format_fails(self):
        result = verify_text("the apple number is 123456", "identity", self.home)
        self.assertFalse(result.ok)

    def test_canary_key(self):
        cname, cval = observe("canary", self.home)
        result = verify_text(format_spoken(cname, cval), "canary", self.home)
        self.assertTrue(result.ok)
        ident = verify_text(format_spoken(cname, cval), "identity", self.home)
        self.assertFalse(ident.ok)


if __name__ == "__main__":
    unittest.main()
