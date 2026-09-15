# zcabs

A model can say "tests passed" without running the tests. It can recite a number that was sitting in the prompt. Weights interpolate. If the proof lives in the context, the proof is free.

**zcabs** makes the proof an observation.

The host generates an integer at mint and hides it in a file. The agent is told **where** to look and **how** to say it. Not the value. The host then checks what the agent spoke. Guessing fails. An empty look fails. A number copied from a README fails, because that number was never this store.

Zero Correlation Anti-Bullshit System. License **AGPL-3.0-or-later**. `LICENSE` · `COVENANT.md`.

## start

```
python -m unittest discover -s tests -v
python -m zcabs check
python -m zcabs prompt
```

From the repo, no install:

```
# unix
PYTHONPATH=src python -m zcabs check

# powershell
$env:PYTHONPATH = "src"
python -m zcabs check
```

Install:

```
python -m pip install -e .
zcabs mint
zcabs look
```

Python 3.10+. stdlib only.

## the protocol

```
LOOK: /absolute/path/to/one/file
FORMAT: the {string} number is {integer}
```

Read that file. Speak the format. The integer is not in git, not in the prompt, not in this README.

```
zcabs wrap -- pytest -q
```

If the command succeeds, zcabs rotates a **canary** and prints LOOK/FORMAT. Verify the transcript. The sentence "all green" is not the proof. The canary is.

```
zcabs scan .
```

Fails if a store, a pointer, or a live integer leaked into the tree.

## tools

```
zcabs mint [--identity banana] [--cap NAME ...] [--force]
zcabs look [--key identity]
zcabs observe KEY
zcabs verify FILE|- [--key canary]
zcabs rotate KEY
zcabs wrap -- CMD [ARGS...]
zcabs scan PATH
zcabs prompt
zcabs check
```

`look` never prints the integer. `observe` is retrieval. `verify` does not echo the expected value on failure. Alias: `zcahc`.

## read

| file | is |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | the protocol. normative |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | coding agent, wrap, CI |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | what this gift is |
| [`prompts/genome.md`](prompts/genome.md) | drop-in system prompt |
| [`spec/zcabs.v1.json`](spec/zcabs.v1.json) | machine twin |

## copyleft

Using LOOK/FORMAT in a prompt is speaking. Copying this spec, these prompts, or this tooling is AGPL. A hosted modified copy owes its users the source.

No dual-license. No company seat. Official copy stays $0. `COVENANT.md`.

## contribute

`CONTRIBUTING.md`. DCO. tests on every SPEC change. house sediment stays out.
