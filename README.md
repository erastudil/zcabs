# zcabs

Language models interpolate context. An agent can claim all tests passed without running a single command. It can repeat a confirmation token if that token was already in the prompt. When proof of execution lives entirely in the conversation context, the proof costs nothing to fake.

**zcabs** turns proof of execution into a real-world observation.

The host generates a unique integer and stores it in an isolated local file. The agent receives only the target file path and the required output format. To prove it completed the work, the agent must inspect the file and speak the value. Guessing fails. Reading an empty path fails. Quoting a static number from documentation fails because live numbers are generated dynamically per installation and task.

The license is AGPL-3.0-or-later. See [`LICENSE`](LICENSE) and [`COVENANT.md`](COVENANT.md).

[progen](https://github.com/erastudil/progen) is how an agent thinks. [gfc](https://github.com/erastudil/gfc) is how it writes for humans. This is how it proves execution.

---

## How the protocol works

The host emits two reserved headers to the model:

```text
LOOK: /absolute/path/to/one/file
FORMAT: the {string} number is {integer}
```

The model reads the target file and speaks the formatted phrase. Live integers never appear in system prompts, repository files, or documentation.

Wrap commands to verify execution automatically:

```bash
zcabs wrap -- pytest -q
```

When the command exits with code 0, `zcabs wrap` rotates the canary capability and prints the `LOOK:` and `FORMAT:` headers to standard output. The resulting canary proves that the command ran to completion.

Scan a repository to verify no stores or live integers have leaked into source files:

```bash
zcabs scan .
```

`scan` exits with code 0 on a clean tree and non-zero if store directories, pointer files, or live store integers are detected.

---

## Setup and self-check

Runtime requirements: Python 3.10+ using only standard library modules.

```bash
# editable package install
python -m pip install -e .

# run protocol conformance check
zcabs check
```

Running straight from the repository tree:

```bash
# unix
PYTHONPATH=src python -m zcabs check

# powershell
$env:PYTHONPATH = "src"
python -m zcabs check

# run full test suite
python -m unittest discover -s tests -v
```

---

## CLI commands

Inspect, mint, verify, and wrap operations:

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
- `observe`: retrieves the active `string=integer` pair for a key // used by tools or hosts.
- `verify`: compares candidate text against the store; fails closed without echoing expected integers.
- `wrap`: executes a command and, upon exit code 0, rotates `canary` and prints the updated `LOOK:` block.
- `scan`: scans directory trees for store paths, pointer files, and leaked integers.
- CLI alias: `zcahc`.

---

## Programmatic harness usage

In Python test runners and evaluation harnesses:

```python
import zcabs

# Ephemeral store managed via context manager
with zcabs.Harness() as h:
    # Environment mapping for child processes
    env = h.env()

    # Prompt header for the agent
    look_block = h.look("canary")

    # Run command through wrapper
    wrap_result = h.wrap(["pytest", "-q"])
    assert wrap_result.ok

    # Verify agent transcript
    result = h.verify("the canary number is 123456", key="canary")

    # Scan project tree for leaks
    findings = h.scan(".")
    assert not findings
```

CLI flags for automated harnesses:

- `--json`: machine-readable JSON output on `mint`, `look`, `observe`, `verify`, `rotate`, `wrap`, `scan`, and `check`.
- `-q`, `--quiet`: suppress stdout, returning exit code only // exit 0 on success, 1 on invariant failure.
- `-t`, `--text`: pass candidate text directly to `zcabs verify` without creating intermediate files.
- `--look-file`: write the post-wrap `LOOK:` block directly to a specified file path.

---

## Documentation

| Document | Purpose |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | Normative protocol specification |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | Integration guide for coding agents, test runners, and CI |
| [`docs/BOUNDARY.md`](docs/BOUNDARY.md) | Repository scope and technical boundaries |
| [`prompts/genome.md`](prompts/genome.md) | Drop-in agent system prompt |
| [`spec/zcabs.v1.json`](spec/zcabs.v1.json) | Machine-readable specification schema |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Guidelines for patches, DCO sign-offs, and test rules |
| [`COVENANT.md`](COVENANT.md) | Un-enclosure commitment and AGPL copyleft terms |
