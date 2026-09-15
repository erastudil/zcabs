---
title: "zcabs — protocol specification"
version: "1.0.0"
status: normative
license: AGPL-3.0-or-later
---

# zcabs

A language model interpolates. Give it a number in a prompt, a README, a golden, or an adapter, and it can emit that number without observing anything. "Tests passed" is then a sentence.

**zcabs** = Zero Correlation Anti-Bullshit System. Integers are generated at mint. The model is told where to look and how to speak. The host checks what was spoken against a store the model cannot interpolate. Miss, empty, or guess: fail closed.

Public name: zcabs. CLI alias: zcahc.

Machine twin: `spec/zcabs.v1.json`. Version **1.0.0**.

---

## 1. why

Weights fill gaps. If the proof lives in the context, the proof is cheap.

Physical retrieval is not cheap in that way. A file that was written at mint, or a tool that reads that file, is an observation. The integer is not in the genome. It is not in this specification as a live value. It is not in git.

The public part is the **string** and the **template**. The private part is the **integer**.

---

## 2. headers

Machine protocol. Colon headers. Not a dialect of english.

```
LOOK: <absolute path to one file>
FORMAT: the {string} number is {integer}
```

| header | is |
|---|---|
| `LOOK:` | one file. never a directory. never `unavailable` when a store exists and the key is known |
| `FORMAT:` | the spoken template. placeholders stay placeholders in this header |

`LOOK: unavailable` means there is no store. The agent speaks `DONT_KNOW`. It does not invent an integer.

A second retrieval surface exists: `zcabs observe KEY`. It prints `string=integer` for that key. Unknown key: `ERROR: unknown key`. It does not list keys.

LOOK never contains the integer. LOOK never names the store directory.

---

## 3. pair

On disk, one file holds one pair:

```
<string>=<integer>
```

Comments (`#`) and blank lines are skipped. The first matching line wins.

The integer is in **100000–999999** inclusive. No leading zeros. Values outside that range are not live zcabs integers.

Every integer in one store is unique. A decoy pair must not reuse a live integer.

---

## 4. store

Mint creates:

| part | is |
|---|---|
| home | `$ZCABS_HOME` or `~/.zcabs`. outside the project |
| pointer | `home/pointer`. maps `identity=` and capability names to absolute file paths. mode `0600` |
| bucket | `home/store/<hex>/`. mode `0700` |
| files | `f_<hex>.dat`. identity, capabilities, decoys. mode `0600` |

Default identity string: `banana`. The string is public. The integer is generated.

Default capability: `canary`. Extra capability names may be minted. Every integer is generated at mint. This specification does not ship live capability integers.

Decoys: at least 16 files in the same bucket with plausible `string=integer` pairs. Listing the bucket does not reveal which path the pointer names.

Pointer keys are `identity` and the capability names. The identity **file** contains the public string, not the word `identity`.

Mint on an existing store fails unless forced. Rotate one key to re-seed that integer in place. The LOOK path stays. The old integer fails verify.

---

## 5. verify

The host compares a candidate string to the store. The agent does not verify itself.

Accept, in order:

1. `the {string} number is {integer}` for the expected string
2. `{string}={integer}`
3. `ZCABS_VALUE: {integer}` when verifying a named key

Reject:

- empty candidate
- missing store
- unknown key
- a number that is not the stored integer
- a decoy's string and integer
- a bare number with no structured form

Failure text does not echo the expected integer.

---

## 6. wrap

Proof that a command ran:

1. Run the command.
2. If the exit code is not 0, print nothing zcabs, return that code. Do not rotate.
3. If the exit code is 0, rotate `canary`, print LOOK/FORMAT for `canary`.

The integer after a successful wrap did not exist while the command ran. A transcript that still holds the pre-wrap integer fails verify.

If no store exists, wrap may mint a default store and say so on stderr. That is setup, not proof. The proof is the post-success LOOK.

---

## 7. scan

A tree fails scan when any of these is true:

- a directory named `.zcabs`
- a file named `zcabs.pointer` or `zcahc.pointer`
- a file named `pointer` whose first data line is `identity=`
- a live integer from the active store appears in a text file in the tree

Scan does not treat the FORMAT template as a leak. Scan does not treat the integer range written as a range as a leak. Scan compares against the store that exists now.

---

## 8. agent genome

The drop-in prompt is `prompts/genome.md`. It names LOOK, FORMAT, observe, and `DONT_KNOW`. It does not contain a live integer. It does not recite a ban list. Fail-closed lives in verify.

---

## 9. names

| word | is |
|---|---|
| mint | generate the store |
| look | print where and how. no integer |
| observe | retrieve one pair |
| verify | host check |
| rotate | re-seed one key |
| wrap | command, then canary LOOK |
| scan | leak check |
| string | public name in the pair |
| integer | generated value |
| decoy | plausible pair the pointer does not name |
| canary | default capability. proof the wrap ran |

---

## 10. completeness

An implementer who has only this repository can mint a store, point an agent at LOOK/FORMAT, verify a transcript, wrap a test run, and scan a tree. Named sources of truth are files in this tree.
