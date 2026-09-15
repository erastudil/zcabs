---
title: "zcabs — this tree"
summary: "public LOOK/FORMAT protocol + tooling. AGPL-3.0-or-later."
---

# zcabs

you are in the public zcabs tree. protocol SoT: `docs/SPEC.md`. license: AGPL-3.0-or-later.

## law

1. SPEC is the protocol. do not fork it into a second markdown.
2. tools prove SPEC. a stub that claims done is a hole.
3. house sediment stays out. `docs/BOUNDARY.md`.
4. no license change. no dual-license. no CLA.
5. integers are generated at mint. never bake them into source, prompts, or docs as live values.
6. `look` stdout must not contain the integer.
7. `python -m unittest discover -s tests -v` and `python -m zcabs check` before claiming verify or scan works.

## layout

| path | is |
|---|---|
| `docs/SPEC.md` | normative protocol |
| `docs/IMPLEMENTATION.md` | coding agent, wrap, CI |
| `docs/BOUNDARY.md` | what this gift is |
| `prompts/genome.md` | drop-in LOOK/FORMAT genome |
| `spec/zcabs.v1.json` | machine twin |
| `src/zcabs/` | mint · look · observe · verify · rotate · wrap · scan |
| `js/` | protocol port |

identity: load no house card. this repo is the card.
