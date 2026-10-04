# Coding Agent Integration Example

This example demonstrates how an orchestrator or test harness uses zcabs to verify agent execution.

## 1. Environment Setup

Mint a store outside the project directory:

```bash
zcabs mint
```

Inject the reference prompt into the agent's system instructions:

```bash
zcabs prompt
```

Provide the agent with access to read files or run `zcabs observe`.

## 2. Command Execution & Wrapping

When the agent triggers test verification:

```bash
zcabs wrap -- pytest -q
```

The wrapper runs the test suite. If tests fail, it exits with the test runner's non-zero return code. If tests pass, it rotates the `canary` integer and prints:

```text
LOOK: /path/to/f_xxxxxx.dat
FORMAT: the {string} number is {integer}
```

## 3. Observation & Verification

Append the wrapper output to the agent context. The agent inspects the file or calls `zcabs observe canary` and responds:

```text
the canary number is 847291
```

Verify the agent transcript against the store:

```bash
# Verify transcript file
zcabs verify transcript.txt --key canary

# Or verify candidate string directly
zcabs verify -t "$AGENT_RESPONSE" --key canary
```

The command exits with 0 on matching retrieval, confirming that the tests passed.

## 4. Programmatic Evaluation Harness

In an automated Python eval harness:

```python
import zcabs

with zcabs.Harness() as h:
    # 1. Provide prompt instruction
    system_prompt = f"{h.genome_prompt()}\n\n{h.look('canary')}"

    # 2. Wrap verification command
    res = h.wrap(["pytest", "-q"])
    assert res.ok

    # 3. Verify model output
    verification = h.verify(model_response, key="canary")
    assert verification.ok, verification.reason
```

