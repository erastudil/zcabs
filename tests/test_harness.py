# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.harness import EphemeralStore, Harness
from zcabs.protocol import format_spoken, parse_look_block


class HarnessTests(unittest.TestCase):
    def test_context_manager_lifecycle(self):
        home_path: Path
        with Harness() as h:
            home_path = h.home
            self.assertTrue(home_path.is_dir())
            env = h.env()
            self.assertIn("ZCABS_HOME", env)
            self.assertEqual(env["ZCABS_HOME"], str(home_path))

            # Look & Observe
            look_block = h.look("identity")
            self.assertIn("LOOK:", look_block)
            self.assertIn("FORMAT:", look_block)
            name, val = h.observe("identity")
            self.assertNotIn(str(val), look_block)

            # Verification
            spoken = format_spoken(name, val)
            self.assertTrue(h.verify(spoken, "identity").ok)
            self.assertEqual(h.format_expected("identity"), spoken)
            self.assertFalse(h.verify(format_spoken(name, val + 1), "identity").ok)

        # Cleaned up automatically
        self.assertFalse(home_path.exists())

    def test_verify_file(self):
        with Harness() as h, tempfile.TemporaryDirectory() as td:
            name, val = h.observe("identity")
            cand_path = Path(td) / "resp.txt"
            cand_path.write_text(format_spoken(name, val) + "\n", encoding="utf-8")
            res = h.verify_file(cand_path, "identity")
            self.assertTrue(res.ok)
            self.assertEqual(res.extracted, val)

            # Missing file fails closed
            res_missing = h.verify_file(Path(td) / "nonexistent.txt", "identity")
            self.assertFalse(res_missing.ok)
            self.assertIn("not found", res_missing.reason)

    def test_rotate(self):
        with Harness() as h:
            name, val_before = h.observe("canary")
            h.rotate("canary")
            _, val_after = h.observe("canary")
            self.assertNotEqual(val_before, val_after)
            self.assertFalse(h.verify(format_spoken(name, val_before), "canary").ok)
            self.assertTrue(h.verify(format_spoken(name, val_after), "canary").ok)

    def test_wrap_success_and_failure(self):
        with Harness() as h, tempfile.TemporaryDirectory() as td:
            look_file = Path(td) / "look.txt"
            wrap_res = h.wrap(
                [sys.executable, "-c", "print('hello world')"],
                key="canary",
                look_file=look_file,
            )
            self.assertTrue(wrap_res.ok)
            self.assertEqual(wrap_res.exit_code, 0)
            self.assertIn("LOOK:", wrap_res.look_block)
            self.assertTrue(look_file.is_file())
            self.assertEqual(look_file.read_text(encoding="utf-8").strip(), wrap_res.look_block.strip())

            name, canary_val = h.observe("canary")
            self.assertTrue(h.verify(format_spoken(name, canary_val), "canary").ok)

            # Failing command
            fail_res = h.wrap(
                [sys.executable, "-c", "raise SystemExit(7)"],
                key="canary",
                look_file=look_file,
            )
            self.assertFalse(fail_res.ok)
            self.assertEqual(fail_res.exit_code, 7)
            # look_file cleaned up on failure
            self.assertFalse(look_file.exists())

    def test_scan_and_prompt(self):
        with Harness() as h, tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "proj"
            proj.mkdir()
            (proj / "doc.txt").write_text("clean file", encoding="utf-8")
            self.assertEqual(h.scan(proj), [])

            # Plant leak
            _, val = h.observe("identity")
            (proj / "leak.txt").write_text(f"number {val}", encoding="utf-8")
            findings = h.scan(proj)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "leak")

            prompt = h.genome_prompt()
            self.assertIn("LOOK", prompt)
            self.assertIn("FORMAT", prompt)

    def test_ephemeral_store_alias(self):
        self.assertIs(EphemeralStore, Harness)


if __name__ == "__main__":
    unittest.main()
