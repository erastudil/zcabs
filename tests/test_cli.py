# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def run_cli(args: list[str], home: Path, input_text: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["ZCABS_HOME"] = str(home)
    return subprocess.run(
        [sys.executable, "-m", "zcabs", *args],
        cwd=str(ROOT),
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
    )


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "home"

    def tearDown(self):
        self._tmp.cleanup()

    def test_mint_look_observe_verify_check(self):
        minted = run_cli(["mint"], self.home)
        self.assertEqual(minted.returncode, 0, minted.stderr)
        self.assertIn("minted", minted.stdout)
        self.assertNotRegex(minted.stdout, r"\b\d{6}\b")

        looked = run_cli(["look"], self.home)
        self.assertEqual(looked.returncode, 0, looked.stderr)
        self.assertIn("LOOK:", looked.stdout)
        self.assertIn("FORMAT:", looked.stdout)

        observed = run_cli(["observe", "identity"], self.home)
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertRegex(observed.stdout.strip(), r"^[A-Za-z][A-Za-z0-9_\-]*=\d{6}$")
        name, raw = observed.stdout.strip().split("=")
        spoken = f"the {name} number is {raw}\n"

        verified = run_cli(["verify", "-", "--key", "identity"], self.home, input_text=spoken)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertIn("PASS", verified.stdout)

        unknown = run_cli(["observe", "missing"], self.home)
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown key", unknown.stderr)
        self.assertNotIn("canary", unknown.stderr)

        check = run_cli(["check"], self.home)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_scan_self(self):
        scanned = run_cli(["scan", str(ROOT)], self.home)
        self.assertEqual(scanned.returncode, 0, scanned.stdout + scanned.stderr)


if __name__ == "__main__":
    unittest.main()
