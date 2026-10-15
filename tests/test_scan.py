# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.scan import scan_tree
from zcabs.store import mint, observe


class ScanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.proj = self.root / "proj"
        self.proj.mkdir()
        mint(self.home)
        (self.proj / "README.md").write_text(
            "FORMAT: the {string} number is {integer}\n", encoding="utf-8"
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_clean_tree(self):
        findings = scan_tree(self.proj, home=self.home)
        self.assertEqual(findings, [])

    def test_planted_integer(self):
        n = observe("canary", self.home)[1]
        (self.proj / "oops.md").write_text(f"nonce {n} leaked\n", encoding="utf-8")
        findings = scan_tree(self.proj, home=self.home)
        kinds = {f.kind for f in findings}
        self.assertIn("leak", kinds)

    def test_pointer_file(self):
        (self.proj / "zcabs.pointer").write_text("identity=/tmp/x.dat\n", encoding="utf-8")
        findings = scan_tree(self.proj, home=self.home)
        self.assertTrue(any(f.kind == "pointer" for f in findings))

    def test_store_dir_name(self):
        zdir = self.proj / ".zcabs"
        zdir.mkdir()
        (zdir / "pointer").write_text("identity=/tmp/x.dat\n", encoding="utf-8")
        findings = scan_tree(self.proj, home=self.home)
        self.assertTrue(any(f.kind == "store-dir" for f in findings))

    def test_store_home_at_dot_zcabs_excluded_while_committed_dir_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            td_root = Path(td).resolve()
            dot_home = (td_root / ".zcabs").resolve()
            mint(dot_home)
            p = (td_root / "proj").resolve()
            p.mkdir()
            (p / "test.py").write_text("print('clean')\n", encoding="utf-8")
            committed = (p / "nested" / ".zcabs").resolve()
            committed.mkdir(parents=True)
            (committed / "pointer").write_text("identity=/tmp/fake\n", encoding="utf-8")
            findings = scan_tree(td_root, home=dot_home)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "store-dir")
            self.assertEqual(Path(findings[0].path).resolve(), committed)


if __name__ == "__main__":
    unittest.main()
