---
title: "zcabs — this tree"
summary: "public LOOK/FORMAT protocol + tooling. AGPL-3.0-or-later. genome for agents working here."
---

# zcabs

you are in the public zcabs tree. protocol SoT: `docs/SPEC.md`. license: AGPL-3.0-or-later.

## law

1. SPEC is the protocol. one markdown (`docs/SPEC.md`).
2. tools prove SPEC. stub + claim is a hole.
3. this tree is the protocol. `docs/BOUNDARY.md`.
4. patches keep AGPL-3.0-or-later. copyright stays with the authors.
5. dynamic integers only. all store integers generated at mint time. never commit static numbers or golden tables.
6. leak prevention: `zcabs look` stdout never prints the target integer.
7. `python -m zcabs check` and `python -m unittest discover -s tests -v` before claiming mint, verify, wrap, or scan works.

## layout

| path | is |
|---|---|
| `docs/SPEC.md` | normative protocol |
| `docs/IMPLEMENTATION.md` | desk · runner · CI wiring |
| `docs/BOUNDARY.md` | what this gift is |
| `prompts/genome.md` | drop-in reference prompt |
| `spec/zcabs.v1.json` | machine schema |
| `src/zcabs/` | mint · look · observe · verify · rotate · wrap · scan · cli |
| `js/` | standalone javascript port |

identity: this repo is the card.
