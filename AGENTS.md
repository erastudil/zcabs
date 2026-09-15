---
title: "zcabs — repository instructions"
summary: "Public LOOK/FORMAT protocol and tooling. AGPL-3.0-or-later."
---

# Agents

You are working in the public `zcabs` repository. Protocol source of truth: [`docs/SPEC.md`](docs/SPEC.md). License: AGPL-3.0-or-later.

## Core Rules

1. **Protocol Single Source of Truth**: [`docs/SPEC.md`](docs/SPEC.md) is the normative definition. Do not create divergent protocol documents.
2. **Proof Over Claims**: Tools must verify the specification directly. Placeholders claiming completion without test verification are failures.
3. **Strict Boundaries**: Keep this repository self-contained and focused strictly on the protocol, reference implementations, verifier, and leak detection. See [`docs/BOUNDARY.md`](docs/BOUNDARY.md).
4. **Copyleft Standing**: Maintain AGPL-3.0-or-later across all files. No dual-licensing, commercial exceptions, or CLA additions.
5. **Dynamic Integers Only**: All store integers are generated at mint time. Never commit static integers, golden capability tables, or live credentials.
6. **Information Leak Prevention**: `zcabs look` stdout must never print the target integer.
7. **Verification Invariant**: Run `python -m unittest discover -s tests -v` and conformance checks before claiming tools work.

## Structure

| Path | Purpose |
|---|---|
| `docs/SPEC.md` | Normative protocol specification |
| `docs/IMPLEMENTATION.md` | Integration guide for agents, wrappers, and CI |
| `docs/BOUNDARY.md` | Project scope and boundary rules |
| `prompts/genome.md` | Drop-in reference system prompt |
| `spec/zcabs.v1.json` | Machine-readable specification schema |
| `src/zcabs/` | Python CLI and core modules (mint, look, observe, verify, rotate, wrap, scan) |
| `js/` | JavaScript reference implementation and tests |
