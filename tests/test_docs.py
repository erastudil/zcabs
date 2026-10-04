# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_DOCS = [
    "docs/SPEC.md",
    "docs/IMPLEMENTATION.md",
    "docs/BOUNDARY.md",
    "prompts/genome.md",
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "COVENANT.md",
    "examples/coding-agent.md",
    "examples/wrap.md",
]


class DocsLint(unittest.TestCase):
    def test_tree_has_no_parentheticals_in_prose(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paren_pattern = re.compile(r"(?<!`)\([^`\n\)]+\)(?!`)")
        for rel in _DOCS:
            text = (root / rel).read_text(encoding="utf-8")
            in_code_block = False
            for i, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                # Skip markdown links e.g. [text](link) and images
                clean_line = re.sub(r"!?\[[^\]]*\]\([^\)]+\)", "", line)
                matches = paren_pattern.findall(clean_line)
                self.assertEqual(
                    matches,
                    [],
                    msg=f"{rel}:{i}: Found parenthetical in prose: {matches}",
                )

    def test_readme_does_not_clone_gift_skeleton(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("\n## start\n", text)
        self.assertNotIn("\n## copyleft\n", text)
        self.assertNotIn("\n## contributing\n", text)

    def test_tree_passes_gfc_linter_when_available(self) -> None:
        try:
            gfc_src = Path(__file__).resolve().parents[2] / "gfc" / "src"
            if gfc_src.is_dir() and str(gfc_src) not in sys.path:
                sys.path.insert(0, str(gfc_src))
            from gfc import lint_text
        except ImportError:
            return

        root = Path(__file__).resolve().parents[1]
        for rel in _DOCS:
            text = (root / rel).read_text(encoding="utf-8")
            findings = lint_text(text, mode="educate")
            self.assertEqual(
                findings,
                [],
                msg=f"{rel}: GFC lint findings: {findings}",
            )


if __name__ == "__main__":
    unittest.main()
