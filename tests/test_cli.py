# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
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

    def test_verify_text_flag_and_quiet(self):
        run_cli(["mint"], self.home)
        observed = run_cli(["observe", "identity"], self.home)
        name, raw = observed.stdout.strip().split("=")
        spoken = f"the {name} number is {raw}"

        # Direct text flag
        res = run_cli(["verify", "-t", spoken, "--key", "identity"], self.home)
        self.assertEqual(res.returncode, 0)
        self.assertIn("PASS", res.stdout)

        # Quiet flag
        quiet_res = run_cli(["verify", "-t", spoken, "--key", "identity", "-q"], self.home)
        self.assertEqual(quiet_res.returncode, 0)
        self.assertEqual(quiet_res.stdout, "")

        # Quiet failure
        bad_quiet = run_cli(["verify", "-t", f"the {name} number is 000000", "--key", "identity", "-q"], self.home)
        self.assertEqual(bad_quiet.returncode, 1)
        self.assertEqual(bad_quiet.stdout, "")

    def test_json_modes(self):
        # mint --json
        minted = run_cli(["mint", "--json"], self.home)
        self.assertEqual(minted.returncode, 0)
        mint_data = json.loads(minted.stdout)
        self.assertTrue(mint_data["ok"])
        self.assertEqual(mint_data["identity"], "banana")
        self.assertIn("canary", mint_data["caps"])

        # look --json
        looked = run_cli(["look", "--json"], self.home)
        self.assertEqual(looked.returncode, 0)
        look_data = json.loads(looked.stdout)
        self.assertTrue(look_data["ok"])
        self.assertTrue(look_data["target"])

        # observe --json
        observed = run_cli(["observe", "identity", "--json"], self.home)
        self.assertEqual(observed.returncode, 0)
        obs_data = json.loads(observed.stdout)
        self.assertTrue(obs_data["ok"])
        self.assertEqual(obs_data["string"], "banana")
        val = obs_data["integer"]

        # verify --json success
        spoken = f"the banana number is {val}"
        ver_ok = run_cli(["verify", "-t", spoken, "--key", "identity", "--json"], self.home)
        self.assertEqual(ver_ok.returncode, 0)
        ver_ok_data = json.loads(ver_ok.stdout)
        self.assertTrue(ver_ok_data["ok"])
        self.assertEqual(ver_ok_data["extracted"], val)

        # verify --json failure (must not echo integer)
        ver_fail = run_cli(["verify", "-t", "the banana number is 999999", "--key", "identity", "--json"], self.home)
        self.assertEqual(ver_fail.returncode, 1)
        ver_fail_data = json.loads(ver_fail.stdout)
        self.assertFalse(ver_fail_data["ok"])
        self.assertNotIn("extracted", ver_fail_data)
        self.assertNotIn(str(val), ver_fail.stdout)

        # scan --json
        scan_res = run_cli(["scan", str(ROOT), "--json"], self.home)
        self.assertEqual(scan_res.returncode, 0)
        scan_data = json.loads(scan_res.stdout)
        self.assertTrue(scan_data["ok"])
        self.assertEqual(scan_data["findings"], [])

        # check --json
        chk_res = run_cli(["check", "--json"], self.home)
        self.assertEqual(chk_res.returncode, 0)
        chk_data = json.loads(chk_res.stdout)
        self.assertTrue(chk_data["ok"])
        self.assertEqual(chk_data["errors"], [])

    def test_scan_self(self):
        scanned = run_cli(["scan", str(ROOT)], self.home)
        self.assertEqual(scanned.returncode, 0, scanned.stdout + scanned.stderr)

    def test_wrap_cli_success_and_failure(self):
        run_cli(["mint"], self.home)
        wrapped = run_cli(
            ["wrap", "--", sys.executable, "-c", "print('worker finished')"],
            self.home,
        )
        self.assertEqual(wrapped.returncode, 0, wrapped.stderr)
        self.assertIn("LOOK:", wrapped.stdout)
        self.assertIn("FORMAT:", wrapped.stdout)

        name, val = run_cli(["observe", "canary"], self.home).stdout.strip().split("=")
        spoken = f"the {name} number is {val}\n"
        verified = run_cli(["verify", "-", "--key", "canary"], self.home, input_text=spoken)
        self.assertEqual(verified.returncode, 0, verified.stdout)
        self.assertIn("PASS", verified.stdout)

        failed = run_cli(
            ["wrap", "--", sys.executable, "-c", "import sys; sys.exit(5)"],
            self.home,
        )
        self.assertEqual(failed.returncode, 5)
        self.assertNotIn("LOOK:", failed.stdout)

    def test_wrap_look_file_and_quiet(self):
        run_cli(["mint"], self.home)
        look_target = Path(self._tmp.name) / "out_look.txt"
        res = run_cli(
            ["wrap", "--look-file", str(look_target), "-q", "--", sys.executable, "-c", "print('done')"],
            self.home,
        )
        self.assertEqual(res.returncode, 0)
        self.assertNotIn("LOOK:", res.stdout)
        self.assertTrue(look_target.is_file())
        self.assertIn("LOOK:", look_target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
