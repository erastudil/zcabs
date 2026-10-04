# SPDX-License-Identifier: AGPL-3.0-or-later
"""Conformance: mint, look leaks nothing, observe+verify, rotate, scan, harness."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .protocol import FORMAT_TEMPLATE, format_spoken, parse_look_block
from .scan import scan_tree
from .store import look, mint, observe, rotate
from .verify import verify_file, verify_text


def run_check(quiet: bool = False, as_json: bool = False) -> int:
    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        home = root / "home"
        mint(home)
        block = look("identity", home)
        if FORMAT_TEMPLATE not in block:
            fail("look missing FORMAT template")
        look_path, _ = parse_look_block(block)
        if not look_path or look_path == "unavailable":
            fail("look missing path")
        name, value = observe("identity", home)
        if str(value) in block:
            fail("look leaked integer")
        if str(value) in look_path:
            fail("LOOK path contained integer")

        spoken = format_spoken(name, value)
        ok = verify_text(spoken, "identity", home)
        if not ok.ok:
            fail("verify rejected true FORMAT")

        # verify_file conformance
        vf_path = root / "candidate.txt"
        vf_path.write_text(spoken + "\n", encoding="utf-8")
        if not verify_file(vf_path, "identity", home).ok:
            fail("verify_file rejected true FORMAT")

        bad = verify_text(format_spoken(name, value + 1 if value < 999_999 else value - 1), "identity", home)
        if bad.ok:
            fail("verify accepted wrong integer")

        decoy = verify_text("the apple number is 123456", "identity", home)
        if decoy.ok:
            fail("verify accepted decoy FORMAT")

        empty = verify_text("", "identity", home)
        if empty.ok:
            fail("verify accepted empty")

        old = value
        rotate("identity", home)
        after = observe("identity", home)[1]
        if after == old:
            fail("rotate did not change integer")
        stale = verify_text(format_spoken(name, old), "identity", home)
        if stale.ok:
            fail("verify accepted rotated-out integer")

        mint(home, force=True)
        n1 = observe("identity", home)[1]
        mint(home, force=True)
        n2 = observe("identity", home)[1]
        if n1 == n2:
            fail("two mints produced the same identity integer")

        tree = root / "proj"
        tree.mkdir()
        (tree / "README.md").write_text("the banana number is a template\n", encoding="utf-8")
        clean = scan_tree(tree, home=home)
        if any(f.kind == "leak" for f in clean):
            fail("scan false-positive on template prose")

        leak = tree / "oops.md"
        leak.write_text(f"leaked {observe('canary', home)[1]}\n", encoding="utf-8")
        dirty = scan_tree(tree, home=home)
        if not any(f.kind == "leak" for f in dirty):
            fail("scan missed planted integer")

        pointer_leak = tree / "zcabs.pointer"
        pointer_leak.write_text("identity=/tmp/nope.dat\n", encoding="utf-8")
        ptr = scan_tree(tree, home=home)
        if not any(f.kind == "pointer" for f in ptr):
            fail("scan missed pointer file")

        # Conformance check for harness
        from .harness import Harness
        with Harness() as h:
            if "ZCABS_HOME" not in h.env():
                fail("harness env missing ZCABS_HOME")
            h_name, h_val = h.observe("identity")
            if not h.verify(format_spoken(h_name, h_val), "identity").ok:
                fail("harness verify failed on valid candidate")

    if as_json:
        print(json.dumps({"ok": len(errors) == 0, "errors": errors}))
        return 0 if not errors else 1

    if errors:
        if not quiet:
            for e in errors:
                print(f"FAIL: {e}")
        return 1
    if not quiet:
        print("PASS")
    return 0
