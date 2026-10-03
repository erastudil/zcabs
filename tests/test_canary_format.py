# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import unittest
from pathlib import Path
import tempfile

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.protocol import extract_spoken, format_spoken, is_live_integer, INT_MIN, INT_MAX
from zcabs.store import mint, observe
from zcabs.verify import verify_text


class TestCanaryFormat(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_canary_format_and_verify(self):
        """Mint, observe canary, verify format and live range, verify positive text passes."""
        mint(home=self.home)
        name, val = observe("canary", home=self.home)
        self.assertEqual(name, "canary")
        self.assertTrue(INT_MIN <= val <= INT_MAX)
        self.assertTrue(is_live_integer(val))

        spoken = format_spoken(name, val)
        self.assertEqual(spoken, f"the {name} number is {val}")

        # Verification of formatted sentence against store must succeed
        res = verify_text(spoken, "canary", home=self.home)
        self.assertTrue(res.ok)
        self.assertEqual(res.extracted, val)

    def test_rejected_forms_must_fail(self):
        """A rejected form must fail: non-token keys, out-of-range integers (0, 42)."""
        mint(home=self.home)

        # Non-token keys rejected by extract_spoken
        self.assertEqual(extract_spoken("the 123key number is 100000"), [])
        self.assertEqual(extract_spoken("the key.with.dots number is 100000"), [])

        # Integers outside live range (including 0, 42, 99999, 1000000) rejected
        self.assertEqual(extract_spoken("the canary number is 0"), [])
        self.assertEqual(extract_spoken("the canary number is 42"), [])
        self.assertEqual(extract_spoken("the canary number is 99999"), [])
        self.assertEqual(extract_spoken("the canary number is 1000000"), [])

        # verify_text fails when candidate has out-of-range or rejected forms
        res_zero = verify_text("the canary number is 0", "canary", home=self.home)
        self.assertFalse(res_zero.ok)

        res_42 = verify_text("the canary number is 42", "canary", home=self.home)
        self.assertFalse(res_42.ok)

        res_invalid_key = verify_text("the 123bad number is 500000", "canary", home=self.home)
        self.assertFalse(res_invalid_key.ok)


if __name__ == "__main__":
    unittest.main()
