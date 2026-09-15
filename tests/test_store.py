# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from zcabs.protocol import FORMAT_TEMPLATE, parse_look_block, parse_pair
from zcabs.store import StoreError, look, mint, observe, rotate, store_exists


class StoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name) / "zcabs-home"

    def tearDown(self):
        self._tmp.cleanup()

    def test_mint_look_has_no_integer(self):
        mint(self.home)
        block = look("identity", self.home)
        name, value = observe("identity", self.home)
        self.assertIn(FORMAT_TEMPLATE, block)
        self.assertNotIn(str(value), block)
        self.assertNotIn(name, block.split("LOOK:")[0])
        target, _ = parse_look_block(block)
        self.assertTrue(Path(target).is_file())
        self.assertEqual(parse_pair(Path(target).read_text(encoding="utf-8")), (name, value))

    def test_two_mints_differ(self):
        mint(self.home)
        a = observe("identity", self.home)[1]
        mint(self.home, force=True)
        b = observe("identity", self.home)[1]
        self.assertNotEqual(a, b)

    def test_mint_refuses_without_force(self):
        mint(self.home)
        with self.assertRaises(StoreError):
            mint(self.home)

    def test_observe_unknown_key_does_not_list(self):
        mint(self.home)
        with self.assertRaises(StoreError) as ctx:
            observe("nope", self.home)
        self.assertIn("unknown key", str(ctx.exception))
        self.assertNotIn("canary", str(ctx.exception))
        self.assertNotIn("banana", str(ctx.exception))

    def test_decoys_exist_and_integers_unique(self):
        mint(self.home, num_decoys=16)
        ident = observe("identity", self.home)
        canary = observe("canary", self.home)
        bucket = Path(parse_look_block(look("identity", self.home))[0]).parent
        files = list(bucket.glob("f_*.dat"))
        self.assertGreaterEqual(len(files), 18)
        values = []
        for p in files:
            pair = parse_pair(p.read_text(encoding="utf-8"))
            self.assertIsNotNone(pair)
            values.append(pair[1])
        self.assertEqual(len(values), len(set(values)))
        self.assertIn(ident[1], values)
        self.assertIn(canary[1], values)

    def test_rotate_changes_integer_keeps_path(self):
        mint(self.home)
        path_before = parse_look_block(look("canary", self.home))[0]
        old = observe("canary", self.home)
        rotate("canary", self.home)
        path_after = parse_look_block(look("canary", self.home))[0]
        new = observe("canary", self.home)
        self.assertEqual(path_before, path_after)
        self.assertEqual(old[0], new[0])
        self.assertNotEqual(old[1], new[1])

    def test_look_without_store(self):
        self.assertFalse(store_exists(self.home))
        block = look("identity", self.home)
        self.assertIn("LOOK: unavailable", block)

    def test_extra_cap(self):
        mint(self.home, extra_caps=("publish",))
        name, value = observe("publish", self.home)
        self.assertEqual(name, "publish")
        self.assertGreaterEqual(value, 100000)


if __name__ == "__main__":
    unittest.main()
