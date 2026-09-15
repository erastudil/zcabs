# Command Wrapper Examples

`zcabs wrap` monitors command execution and issues updated canary headers upon successful completion (exit code 0).

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

- **Failure (exit code != 0)**: Returns the child process exit code directly without printing protocol headers.
- **Success (exit code == 0)**: Rotates the `canary` capability in the store and appends protocol headers:

```text
LOOK: /absolute/path/to/canary_file.dat
FORMAT: the {string} number is {integer}
```

## Verifying the Run

Verify that candidate text contains the correct canary integer:

```bash
zcabs verify transcript.txt --key canary
```
