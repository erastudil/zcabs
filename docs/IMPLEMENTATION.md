---
title: "zcabs — implementation"
version: "1.0.0"
status: normative-adjacent
license: AGPL-3.0-or-later
---

# implementation

SPEC is the protocol. This file is how you wire it into a coding agent, a test command, and CI.

Python 3.10+, stdlib only:

```
python -m pip install -e .
zcabs mint
zcabs look
zcabs wrap -- pytest -q
zcabs verify transcript.txt --key canary
zcabs scan .
```

From the repo, no install:

```
# unix
PYTHONPATH=src python -m zcabs check

# powershell
$env:PYTHONPATH = "src"
python -m zcabs check
```

---

## 1. coding agent

Mint once per machine or per project. Keep the home **outside** the git tree.

```
zcabs mint --home ~/.zcabs
```

Inject `zcabs prompt` into the system prompt, or the LOOK block you are about to demand.

When the turn must prove work:

1. Host runs `zcabs wrap -- <the command>`.
2. Host appends the printed LOOK/FORMAT to the agent.
3. Agent reads LOOK or runs `zcabs observe canary`.
4. Agent speaks `the canary number is <integer>`.
5. Host runs `zcabs verify transcript --key canary`. Fail closed ends the turn as incomplete.

Do not put the integer in the system prompt. Do not ask the model to invent a canary. Do not take "tests passed" as proof.

Identity is the same protocol with `--key identity`. Use it when the agent must prove it is on this install, not a replay of a golden.

---

## 2. tools

If the agent has a tool list, add one tool:

| name | args | returns |
|---|---|---|
| `zcabs` | `key` | `string=integer` for that key, or `ERROR: unknown key` |

That is `observe`. The agent still needs LOOK so it knows which key. `zcabs look --key canary` is host-side. The model does not receive the integer from `look`.

If the agent has `read_file`, LOOK is enough. Give it the one path. Do not give it the store directory.

---

## 3. wrap

```
zcabs wrap -- pytest -q
zcabs wrap -- npm test
zcabs wrap -- cargo test
```

The command runs in the current directory. On failure, wrap is silent and returns the command's code. On success, stdout ends with LOOK/FORMAT for `canary`.

Capture the full transcript. Verify the canary against that transcript, not against a summary the model wrote.

---

## 4. CI

Scan every pull request. Verify stays on the machine that minted the store. Do not upload the store.

```yaml
- uses: erastudil/zcabs/action@v1
  with:
    mode: scan
    path: .
```

Same as:

```
PYTHONPATH=src python -m zcabs scan .
```

---

## 5. javascript

`js/zcabs.js` is the protocol in one module. Memory store by default. Node tests inject `node:fs`. LOOK is a path or a memory key. It is not a fake `/proc` path.

---

## 6. reserved headers

`LOOK:` and `FORMAT:` are protocol headers. Keep them on their own lines. Do not collide them with topic-comment `:` on the same line.

Sibling dialect: [progen](https://github.com/erastudil/progen). Progen does not define zcabs. This repo does.

---

## 7. host hardening

zcabs proves retrieval. It does not jail the agent.

- home mode `0700`, files `0600`
- do not mount the store into a sandbox that may `ls`
- do not log `observe` output into a file that later enters training
- rotate after privileged use
