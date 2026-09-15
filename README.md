# zcabs

Language models interpolate context. An agent can claim "all tests passed" without running a single command. It can repeat a confirmation code if that code was already in the prompt. When proof of execution lives entirely in the conversation context, the proof costs nothing to fake.

**zcabs** turns proof of execution into a real-world observation.

The host generates a unique integer and stores it in an isolated local file. The agent receives only the file path and the required output format. To prove it completed the work, the agent must inspect the file and speak the value. Guessing fails. Reading an empty path fails. Quoting a static number from documentation fails because live numbers are generated dynamically per installation and task.

Zero Correlation Anti-Bullshit System. AGPL-3.0-or-later. See [`LICENSE`](LICENSE) and [`COVENANT.md`](COVENANT.md).

## Quickstart

Run tests and conformance checks directly from a repository checkout:

```bash
# Run unit tests
python -m unittest discover -s tests -v

# Run protocol conformance check (local checkout)
PYTHONPATH=src python -m zcabs check
```

Install as an editable package:

```bash
python -m pip install -e .

# Conformance and CLI inspection
zcabs check
zcabs mint
zcabs look
```

Requires Python 3.10+ (standard library only).

## The Protocol

The host provides two lines to the model:

```text
LOOK: /absolute/path/to/one/file
FORMAT: the {string} number is {integer}
```

The model reads the target file and speaks the formatted phrase. Live integers are never placed in system prompts, repository files, or documentation.

Wrap commands to verify execution automatically:

```bash
zcabs wrap -- pytest -q
```

When the command exits with code 0, `zcabs wrap` rotates the `canary` capability and emits the `LOOK:` and `FORMAT:` headers on standard output. The resulting canary proves that the command ran to completion.

Scan a repository to verify no stores or live integers have leaked into source files:

```bash
zcabs scan .
```

`scan` exits with code 0 on a clean tree and non-zero if store directories, pointer files, or live store integers are detected.

## CLI Reference

```bash
zcabs mint [--identity banana] [--cap NAME ...] [--force]
zcabs look [--key identity]
zcabs observe KEY
zcabs verify FILE|- [--key canary]
zcabs rotate KEY
zcabs wrap -- CMD [ARGS...]
zcabs scan [PATH]
zcabs prompt
zcabs check
```

- `look`: prints the target file path and required format template without exposing the integer.
- `observe`: retrieves the active `string=integer` pair for a key (used by tools or hosts).
- `verify`: compares candidate text against the store; fails closed without echoing expected integers.
- `wrap`: executes a command and, upon exit code 0, rotates `canary` and prints the updated `LOOK:` block.
- `scan`: scans directory trees for store paths, pointer files, and leaked integers.
- CLI alias: `zcahc`.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | Normative protocol specification |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | Integration guide for coding agents, test runners, and CI |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | Repository scope and technical boundaries |
| [`prompts/genome.md`](prompts/genome.md) | Drop-in agent system prompt |
| [`spec/zcabs.v1.json`](spec/zcabs.v1.json) | Machine-readable specification schema |

## Copyleft & Covenant

Using `LOOK:` and `FORMAT:` headers in prompts is standard protocol usage. Incorporating the specification, prompts, or reference implementations into derivative works requires AGPL-3.0-or-later licensing. Network services providing modified versions of these tools owe their users the corresponding source code under AGPL §13.

No dual-licensing. No corporate copyright assignment. Free software forever. See [`COVENANT.md`](COVENANT.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions require Developer Certificate of Origin (DCO) sign-off and tests matching `docs/SPEC.md`. Keep changes focused strictly on the protocol and tooling.
