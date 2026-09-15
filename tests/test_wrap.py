# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

from zcabs.protocol import format_spoken, parse_look_block
from zcabs.store import mint, observe
from zcabs.verify import verify_text
from zcabs.wrap import wrap_command


class WrapTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"
        mint(self.home)

    def tearDown(self):
        self._tmp.cleanup()

    def test_success_prints_look_without_integer_and_verifies(self):
        before = observe("canary", self.home)[1]
        out = io.StringIO()
        err = io.StringIO()
        rc = wrap_command(
            [sys.executable, "-c", "print('ok')"],
            home=self.home,
            stdout=out,
            stderr=err,
        )
        self.assertEqual(rc, 0)
        block = out.getvalue()
        after = observe("canary", self.home)
        self.assertNotEqual(before, after[1])
        self.assertNotIn(str(after[1]), block)
        self.assertNotIn(str(before), block)
        target, _ = parse_look_block(block)
        self.assertTrue(Path(target).is_file())
        spoken = format_spoken(after[0], after[1])
        self.assertTrue(verify_text(spoken, "canary", self.home).ok)
        self.assertFalse(verify_text(format_spoken(after[0], before), "canary", self.home).ok)

    def test_failure_does_not_rotate(self):
        before = observe("canary", self.home)[1]
        out = io.StringIO()
        rc = wrap_command(
            [sys.executable, "-c", "raise SystemExit(3)"],
            home=self.home,
            stdout=out,
            stderr=io.StringIO(),
        )
        self.assertEqual(rc, 3)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(observe("canary", self.home)[1], before)

    def test_empty_command(self):
        rc = wrap_command([], home=self.home, stdout=io.StringIO(), stderr=io.StringIO())
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
