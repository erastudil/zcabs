---
title: "zcabs — Implementation Guide"
version: "1.0.0"
status: normative-adjacent
license: AGPL-3.0-or-later
---

# Implementation Guide

[`docs/SPEC.md`](SPEC.md) defines the protocol. This guide explains how to integrate zcabs into coding agents, test runners, and continuous integration pipelines.

## Installation & Basic Usage

Requires Python 3.10+ // standard library only.

```bash
# Editable install
python -m pip install -e .

# Basic lifecycle
zcabs mint
zcabs look
zcabs wrap -- pytest -q
zcabs verify transcript.txt --key canary
zcabs scan .
```

To run directly from a repository checkout without installing:

```bash
# Unix
PYTHONPATH=src python -m zcabs check

# PowerShell
$env:PYTHONPATH = "src"
python -m zcabs check
```

---

## 1. Coding Agent Integration

Mint a store on the host machine. Always place the store directory outside the project repository:

```bash
zcabs mint --home ~/.zcabs
```

Include the drop-in genome prompt in the agent's system instructions:

```bash
zcabs prompt
```

When an agent turn requires proof of execution:

1. The host executes the test suite through the wrapper:
   ```bash
   zcabs wrap -- <test_command>
   ```
2. The host appends the resulting `LOOK:` and `FORMAT:` headers to the agent's turn.
3. The agent reads the target file or invokes `zcabs observe canary`.
4. The agent emits the required sentence: `the canary number is <integer>`.
5. The host verifies the agent's transcript:
   ```bash
   zcabs verify transcript.txt --key canary
   ```
   If verification fails, the host terminates or rejects the turn as incomplete.

Static numbers must never appear in system prompts. Proof requires active inspection of the dynamic store.

To verify that an agent is operating in a specific deployment environment rather than replaying past golden sessions, verify against `--key identity`.

---

## 2. Agent Tool Definitions

When providing tools directly to an agent, expose an `observe` function:

| Tool Name | Parameters | Returns | Description |
|---|---|---|---|
| `zcabs` | `key: string` | `string=integer` | Retrieves the key-value pair for a known key. Returns `ERROR: unknown key` if absent. |

`observe` performs structured retrieval. The agent identifies the appropriate key from the host-provided `LOOK:` path or instructions. `zcabs look` remains host-side to prevent exposing integers prior to observation.

If the agent has direct file reading capabilities (`read_file`), providing the `LOOK:` path is sufficient.

---

## 3. Command Wrapping

`zcabs wrap` wraps any executable command:

```bash
zcabs wrap -- pytest -q
zcabs wrap -- npm test
zcabs wrap -- cargo test
```

The command executes in the current working directory.
- On failure // non-zero exit code // `wrap` exits with the command's exit code without printing protocol headers.
- On success // exit code 0 // `wrap` rotates the `canary` integer and appends the updated `LOOK:` and `FORMAT:` headers to standard output.

Always verify candidate responses against the entire transcript rather than model-authored summaries.

---

## 4. Continuous Integration

Integrate `zcabs scan` into pull request workflows to prevent accidental leaks of secret store directories, pointer files, or live integers:

```yaml
- uses: erastudil/zcabs/action@v1
  with:
    mode: scan
    path: .
```

Equivalent local command:

```bash
PYTHONPATH=src python -m zcabs scan .
```

Store verification runs on the host that minted the store; store directories must never be uploaded to CI artifacts or public repositories.

---

## 5. Programmatic Harness Integration

Evaluation harnesses and automated test benches use `zcabs.Harness` to manage ephemeral stores:

```python
import zcabs

with zcabs.Harness() as h:
    # Pass ZCABS_HOME to subshells or agent containers
    env = h.env()

    # Retrieve LOOK header for prompt injection
    look_block = h.look("canary")

    # Wrap test commands
    wrap_res = h.wrap(["pytest", "-q"])
    if not wrap_res.ok:
        raise RuntimeError("tests failed")

    # Verify transcript file or text
    ver_res = h.verify(agent_text, key="canary")
    if not ver_res.ok:
        raise AssertionError(ver_res.reason)
```

CLI flags optimize execution inside bash or CI harness scripts:

- Pass candidate text directly: `zcabs verify -t "$AGENT_OUTPUT" --key canary`
- Silence console output for status-code checking: `zcabs verify -t "$AGENT_OUTPUT" -q`
- Output structured results: `zcabs verify -t "$AGENT_OUTPUT" --json`
- Direct wrapped look header to a file: `zcabs wrap --look-file /tmp/look.txt -q -- pytest -q`

---

## 6. JavaScript / Node.js Implementation

[`js/zcabs.js`](../js/zcabs.js) provides a standalone JavaScript implementation of the protocol.
- Default: In-memory store (`createMemoryIO()`).
- Filesystem: Node.js filesystem adapter (`createFsIO()`).
- LOOK targets reference filesystem paths or memory keys.
- Harness: In-memory test environment (`createHarness()`).

Run Node.js conformance tests:

```bash
node --test js/zcabs.test.js
```

---

## 7. Reserved Headers

`LOOK:` and `FORMAT:` are reserved protocol headers. Place each header on its own line. Do not combine them with other colon-delimited text on the same line.

For dialect integration with [progen](https://github.com/erastudil/progen), keep protocol headers distinct from topic-comment dialect structures.

---

## 8. Host Hardening

`zcabs` provides proof of observation; it does not replace process sandboxing:

- Store home directory permissions must be restricted: mode `0700` for directories, `0600` for secret files.
- Do not mount the store directory into container environments where agents can list directory contents.
- Do not record `observe` output into persistent training datasets.
- Rotate capability integers after privileged operations.
