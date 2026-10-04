# Command Wrapper Examples

An agent can claim its code passed every test. Without an observation mechanism, that claim costs nothing to fabricate.

When you run tests through `zcabs wrap`, the host monitors the child process:

1. The test runner executes.
2. If the exit code is non-zero, the command fails and nothing prints.
3. If the exit code is 0, the host changes the canary integer stored on disk and emits updated protocol headers:

```text
LOOK: /absolute/path/to/canary_file.dat
FORMAT: the {string} number is {integer}
```

The integer on disk did not exist until the command succeeded. An agent cannot interpolate it from prompt context, recall it from earlier turns, or quote a static test value. It must read the target file.

## Basic Usage

```bash
# Mint a store if not already created
zcabs mint

# Wrap test runners
zcabs wrap -- pytest -q
zcabs wrap -- npm test
zcabs wrap -- python -m unittest discover -s tests -v
```

## Behavior

- **Failure**: returns the child process exit code directly without printing protocol headers.
- **Success**: rotates the canary capability in the store and appends protocol headers.

## Writing LOOK Headers to a File

In automated continuous integration pipelines or test harnesses where test suites produce extensive console logs, separate protocol headers from standard output:

```bash
zcabs wrap --look-file /tmp/canary_look.txt -q -- pytest -q
```

The exit code matches the test runner. The protocol headers write directly to `/tmp/canary_look.txt`. Stale files from previous runs are removed before execution begins to ensure fail-closed operation.

## Verifying the Run

Verify that candidate text contains the matching canary integer:

```bash
# Verify transcript file
zcabs verify transcript.txt --key canary

# Verify direct candidate string
zcabs verify -t "$AGENT_RESPONSE" --key canary

# Quiet check for shell scripts
zcabs verify -t "$AGENT_RESPONSE" --key canary -q
```
